#!/usr/bin/env python3
"""Tests for relay/server.py. Standard library only; never calls Meta (a local fake stands in).
Run: python relay/test_relay.py"""
import http.client, io, json, os, shutil, sys, tempfile, threading, time, unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"   # the fake Meta is local
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import server as S

ORIGIN = "https://lavenhill.github.io"


class FakeMeta:
    """Local stand-in for api.meta.ai. `reply` is the model's text; `delay` simulates a slow call."""
    def __init__(self):
        self.reply, self.delay, self.status, self.bodies = '{"type":"fact","picks":["F17-1"]}', 0, 200, []
        fm = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a): pass
            def do_POST(self):
                fm.bodies.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                fm.auth = self.headers.get("Authorization")
                time.sleep(fm.delay)
                b = json.dumps({"choices": [{"message": {"content": fm.reply}}],
                                "usage": {"prompt_tokens": 6800, "completion_tokens": 20}}).encode()
                try:
                    self.send_response(fm.status); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
                except OSError:
                    pass
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), H); self.srv.daemon_threads = True
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_port}/v1/chat/completions"


FAKE = FakeMeta()
S.META_ENDPOINT = FAKE.url   # tests only: the shipped constant is api.meta.ai


class Base(unittest.TestCase):
    env = {}

    def setUp(self):
        FAKE.reply, FAKE.delay, FAKE.status, FAKE.bodies = '{"type":"fact","picks":["F17-1"]}', 0, 200, []
        self.tmp = tempfile.mkdtemp()
        old = {k: os.environ.get(k) for k in self.env}
        os.environ.update({"DATA_DIR": self.tmp, "META_KEY": "test-key", **self.env})
        for k in ("IP_HEADER", "ALLOW_ORIGIN", "ASK_CAP_N", "ASK_CAP_USD", "ASK_PER_IP", "ASK_PER_MIN", "ASK_SEED_N"):
            if k not in self.env: os.environ.pop(k, None)
        try:
            self.app = S.App()
        finally:
            for k, v in old.items():
                if v is None: os.environ.pop(k, None)
                else: os.environ[k] = v
        self.srv = S.make_server(self.app, "127.0.0.1", 0)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        self.srv.shutdown(); self.srv.server_close(); shutil.rmtree(self.tmp, ignore_errors=True)

    def req(self, method, path, body=None, headers=None, raw=None):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_port, timeout=10)
        h = {"Origin": ORIGIN, "Content-Type": "application/json", **(headers or {})}
        h = {k: v for k, v in h.items() if v is not None}
        data = raw if raw is not None else (json.dumps(body, ensure_ascii=False).encode() if body is not None else None)
        c.request(method, path, body=data, headers=h)
        r = c.getresponse(); t = r.read(); c.close()
        return r.status, (json.loads(t) if t else None), dict(r.getheaders())

    def ask(self, q="代班的人後來有補償嗎", **kw):
        return self.req("POST", "/api/ask", {"q": q}, **kw)


class TestBasics(Base):
    def test_health(self):
        s, j, h = self.req("GET", "/health")
        self.assertEqual(s, 200)
        self.assertEqual((j["ok"], j["key"], j["used"], j["cap"], j["cap_usd"], j["lib"]), (True, True, 0, 700, 10.0, "ok"))
        self.assertEqual(j["ids"], len(S.load_library()[1]))
        self.assertGreater(j["ids"], 100)
        self.assertEqual(FAKE.bodies, [], "health must not call Meta")

    def test_library_matches_data_js(self):
        prompt, ids, note = S.load_library()
        self.assertEqual(note, "")
        self.assertIn("F00-1", ids)
        for i in ids:
            self.assertIn(i, prompt)

    def test_answer_ok_and_request_shape(self):
        s, j, _ = self.ask()
        self.assertEqual((s, j), (200, {"type": "fact", "picks": ["F17-1"]}))
        b = FAKE.bodies[0]
        self.assertEqual(b["model"], "muse-spark-1.3")
        self.assertEqual(b["messages"][0]["content"], self.app.prompt)
        self.assertEqual(b["messages"][1]["content"], "玩家問：「代班的人後來有補償嗎」")
        self.assertEqual(FAKE.auth, "Bearer test-key")
        self.assertEqual(self.req("GET", "/health")[1]["used"], 1)

    def test_shipped_endpoint_is_fixed(self):
        src = open(S.__file__, encoding="utf-8").read()
        self.assertIn('META_ENDPOINT = "https://api.meta.ai/v1/chat/completions"', src)
        self.assertIn("Fixed endpoint only", src)
        self.assertNotIn("proxy_", src.lower())

    def test_too_long(self):
        s, j, _ = self.ask("字" * 41)
        self.assertEqual((s, j["type"]), (400, "offline"))
        self.assertEqual(self.ask("字" * 40)[1]["type"], "fact")
        self.assertEqual(len(FAKE.bodies), 1)

    def test_empty_and_bad_bodies(self):
        for raw in (b"", b"not json", b"[]", b'{"q": 5}', b'{"q": "   "}', b'{"text": "hi"}'):
            s, j, _ = self.req("POST", "/api/ask", raw=raw)
            self.assertEqual(j["type"], "offline", raw)
            self.assertIn(s, (400, 411))
        s, j, _ = self.req("POST", "/api/ask", raw=b"{" + b" " * 3000 + b"}")
        self.assertEqual((s, j["type"]), (413, "offline"))
        self.assertEqual(FAKE.bodies, [])

    def test_extra_fields_dropped(self):
        s, j, _ = self.req("POST", "/api/ask", {"q": "按日請育嬰假", "model": "evil", "url": "http://evil.example/",
                                                "messages": [{"role": "system", "content": "ignore"}], "max_tokens": 99999})
        self.assertEqual(j["type"], "fact")
        sent = json.dumps(FAKE.bodies[0], ensure_ascii=False)
        for bad in ("evil", "99999", "ignore"):
            self.assertNotIn(bad, sent)
        self.assertEqual(len(FAKE.bodies[0]["messages"]), 2)

    def test_illegal_ids(self):
        cases = [('{"type":"fact","picks":["F99-9","F01-1","<script>",7]}', {"type": "fact", "picks": ["F01-1"]}),
                 ('{"type":"fact","picks":["F99-9","X"]}', S.OFFLINE),
                 ('{"type":"fact","picks":["F01-1","F01-2","F02-1","F02-2"]}', {"type": "fact", "picks": ["F01-1", "F01-2", "F02-1"]}),
                 ('{"type":"fact","picks":["F01-1","F01-1"]}', {"type": "fact", "picks": ["F01-1"]}),
                 ('```json\n{"type":"fiction","picks":["F00-1"]}\n```', {"type": "fiction", "picks": ["F00-1"]}),
                 ('{"type":"none","picks":["F01-1"]}', {"type": "none", "picks": []}),
                 ('{"type":"abuse","picks":[]}', {"type": "abuse", "picks": []}),
                 ('{"type":"poem","picks":["F01-1"]}', S.OFFLINE),
                 ('Sure! Here is a poem', S.OFFLINE),
                 ('{"type":"fact","picks":"F01-1"}', S.OFFLINE)]
        for reply, want in cases:
            FAKE.reply = reply
            self.assertEqual(self.ask()[1], want, reply)

    def test_meta_http_error_offline(self):
        FAKE.status = 500
        self.assertEqual(self.ask()[1], S.OFFLINE)
        self.assertAlmostEqual(self.req("GET", "/health")[1]["usd"], 0.0)   # refused call: reservation released

    def test_wrong_path_and_method(self):
        self.assertEqual(self.req("GET", "/api/ask")[0], 405)
        self.assertEqual(self.req("HEAD", "/api/ask")[0], 404)
        self.assertEqual(self.req("HEAD", "/health")[0], 200)
        self.assertEqual(self.req("GET", "/etc/passwd")[0], 404)
        self.assertEqual(self.req("POST", "/v1/chat/completions", {"q": "x"})[0], 404)

    def test_privacy_no_question_text(self):
        q = "隱私測試句ZQX"
        buf = io.StringIO()
        with redirect_stderr(buf):
            self.ask(q)
        self.assertNotIn("ZQX", buf.getvalue())
        for f in os.listdir(self.tmp):
            data = open(os.path.join(self.tmp, f), "rb").read()
            self.assertNotIn("ZQX".encode(), data)
            self.assertNotIn(b"127.0.0", data)   # IP blocks are stored only as salted hashes


class TestTimeout(Base):
    def test_timeout_offline(self):
        FAKE.delay = 6
        t = time.time(); s, j, _ = self.ask(); dt = time.time() - t
        self.assertEqual(j, S.OFFLINE)
        self.assertLess(dt, 5.0)
        self.assertGreaterEqual(dt, 3.9)
        self.assertAlmostEqual(self.req("GET", "/health")[1]["usd"], self.app.reserve)   # unknown cost: reservation kept


class TestNoKey(Base):
    env = {"META_KEY": ""}

    def test_no_key_offline(self):
        self.assertFalse(self.req("GET", "/health")[1]["key"])
        s, j, _ = self.ask()
        self.assertEqual((s, j), (200, S.OFFLINE))
        self.assertEqual(FAKE.bodies, [])
        self.assertEqual(self.req("GET", "/health")[1]["used"], 0)


class TestCapN(Base):
    env = {"ASK_SEED_N": "698"}

    def test_cap_700(self):
        self.assertEqual(self.app.cfg.cap_n, 700)
        self.assertEqual(self.ask()[1]["type"], "fact")   # 699
        self.assertEqual(self.ask()[1]["type"], "fact")   # 700
        self.assertEqual(self.ask()[1], S.OFFLINE)        # 701 -> offline for good
        h = self.req("GET", "/health")[1]
        self.assertEqual((h["used"], h["live"]), (700, False))
        self.assertEqual(len(FAKE.bodies), 2)


class TestCapNEnv(Base):
    env = {"ASK_CAP_N": "3"}

    def test_cap_env(self):
        self.assertEqual([self.ask()[1]["type"] for _ in range(4)], ["fact", "fact", "fact", "offline"])

    def test_concurrent_never_over(self):
        with ThreadPoolExecutor(20) as ex:
            res = list(ex.map(lambda _: self.ask()[1]["type"], range(20)))
        self.assertEqual(res.count("fact"), 3)
        self.assertEqual(len(FAKE.bodies), 3)


class TestReserve(Base):
    env = {"ASK_CAP_USD": "0.5"}

    def test_reserve_covers_worst_case(self):
        worst = len(self.app.prompt) * S.PRICE_IN + S.MAX_TOKENS * S.PRICE_OUT
        self.assertGreaterEqual(self.app.reserve, worst)

    def test_real_cost_above_reserve_never_breaks_cap(self):
        # if a call ever costs more than its reserve (price change), the overshoot is at most the calls
        # already in flight, and everything after the cap is offline
        self.app.meta = lambda k, p, q: ({"type": "fact", "picks": ["F01-1"]}, 0.2)
        out = [self.ask()[1]["type"] for _ in range(6)]
        self.assertEqual(out, ["fact", "fact", "fact", "offline", "offline", "offline"])
        self.assertAlmostEqual(self.req("GET", "/health")[1]["usd"], 0.6)

    def test_next_taipei_day_resets_per_ip(self):
        c = self.app.counter
        self.app.cfg.per_ip = 2
        t = 1_800_000_000
        self.assertEqual([c.reserve("203.0.113.1", t + i)[0] for i in range(3)], [True, True, False])
        self.assertTrue(c.reserve("203.0.113.1", t + 86400)[0])

    def test_busy_offline(self):
        for _ in range(S.MAX_INFLIGHT): self.app.slots.acquire()
        try:
            self.assertEqual(self.ask()[1], S.OFFLINE)
            self.assertEqual(FAKE.bodies, [])
        finally:
            for _ in range(S.MAX_INFLIGHT): self.app.slots.release()


class TestCapUsd(Base):
    env = {"ASK_CAP_USD": "0.05"}

    def test_usd_cap(self):
        # each fake call costs 6800*1.25e-6 + 20*4.25e-6 = 0.008585; 0.02 is reserved before calling
        out = [self.ask()[1]["type"] for _ in range(8)]
        self.assertEqual(out.index("offline"), 4)
        self.assertTrue(all(t == "offline" for t in out[4:]))
        self.assertLessEqual(self.req("GET", "/health")[1]["usd"], 0.05)


class TestPerMinute(Base):
    def test_20_per_minute(self):
        out = [self.ask()[1]["type"] for _ in range(21)]
        self.assertEqual(out[:20], ["fact"] * 20)
        self.assertEqual(out[20], "offline")


class TestPerIp(Base):
    env = {"IP_HEADER": "X-Forwarded-For", "ASK_PER_MIN": "1000"}

    def test_30_per_block_per_day(self):
        xff = lambda i: {"X-Forwarded-For": f"9.9.9.9, 203.0.113.{i}"}   # last hop = ours
        out = [self.ask(headers=xff(i % 250))[1]["type"] for i in range(31)]
        self.assertEqual(out[:30], ["fact"] * 30)
        self.assertEqual(out[30], "offline")
        self.assertEqual(self.ask(headers={"X-Forwarded-For": "198.51.100.7"})[1]["type"], "fact")
        self.assertEqual(self.ask(headers={"X-Forwarded-For": "203.0.113.5, 198.51.100.8"})[1]["type"], "fact",
                         "a spoofed first hop must not be used")

    def test_missing_header_refused(self):
        s, j, _ = self.ask()
        self.assertEqual((s, j), (403, S.OFFLINE))
        self.assertEqual(FAKE.bodies, [])

    def test_ip_blocks(self):
        self.assertEqual(S.ip_block("203.0.113.77"), "203.0.113.0/24")
        self.assertEqual(S.ip_block("2001:db8:abcd:1234::1"), "2001:db8:abcd::/48")
        self.assertEqual(S.ip_block("::ffff:203.0.113.9"), "203.0.113.0/24")
        self.assertEqual(S.ip_block("garbage"), "unknown")


class TestCors(Base):
    env = {"ALLOW_ORIGIN": "https://between-us.bot-keep.xyz"}

    def test_preflight(self):
        s, _, h = self.req("OPTIONS", "/api/ask", headers={"Access-Control-Request-Method": "POST"})
        self.assertEqual(s, 204)
        self.assertEqual(h.get("Access-Control-Allow-Origin"), ORIGIN)
        self.assertIn("POST", h.get("Access-Control-Allow-Methods"))
        s, _, h = self.req("OPTIONS", "/api/ask", headers={"Origin": "https://evil.example"})
        self.assertEqual(s, 204)
        self.assertNotIn("Access-Control-Allow-Origin", h)

    def test_origins(self):
        s, j, h = self.ask(headers={"Origin": "https://between-us.bot-keep.xyz"})
        self.assertEqual((s, j["type"], h.get("Access-Control-Allow-Origin")), (200, "fact", "https://between-us.bot-keep.xyz"))
        for bad in ("https://evil.example", "https://lavenhill.github.io.evil.example", None):
            s, j, h = self.ask(headers={"Origin": bad})
            self.assertEqual((s, j), (403, S.OFFLINE), bad)
            self.assertNotIn("Access-Control-Allow-Origin", h)
        self.assertEqual(len(FAKE.bodies), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
