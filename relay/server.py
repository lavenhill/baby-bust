#!/usr/bin/env python3
"""Ask relay for "Between Us and the Kids" (sources page, "Anything else to check?").

Browser -> this relay -> api.meta.ai only -> back to the browser as sentence IDs only.
Python 3.13 standard library, no packages. Start: `python relay/server.py`.

Env (all optional except META_KEY for live answers):
  META_KEY        Meta Model API key (never in the repo; /health shows key:true/false)
  SERVER_PORT     listen port (default 8080), host 0.0.0.0
  DATA_DIR        counter database folder (default: <repo>/../data, i.e. outside the imported repo folder)
  IP_HEADER       header set by the platform's reverse proxy with the client IP (e.g. X-Forwarded-For).
                  If set, requests without it are refused (they bypassed the proxy).
  ALLOW_ORIGIN    extra allowed browser origins, comma separated (https://lavenhill.github.io is built in)
  ASK_CAP_N       total live questions, ever (default 700); then offline for good
  ASK_CAP_USD     total spend cap in US$ (default 10); then offline for good
  ASK_PER_IP      questions per IP block (IPv4 /24, IPv6 /48) per Taipei day (default 30)
  ASK_PER_MIN     questions per minute, whole site (default 20)
  ASK_SEED_N      starting count when the database is created (default 0; use half the cap if the
                  database was lost after the first deployment)
  ASK_SALT        secret for hashing IP blocks (default: a random value kept in the database)
Privacy: question text is never stored or logged; only counts, money and salted hashes of IP blocks.
"""
# Fixed endpoint only. No user-supplied URL. Not a forward proxy.
META_ENDPOINT = "https://api.meta.ai/v1/chat/completions"

import hashlib, hmac, ipaddress, json, os, re, secrets, sqlite3, sys, threading, time, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MODEL = "muse-spark-1.3"
PRICE_IN, PRICE_OUT = 1.25e-6, 4.25e-6          # US$ per token (muse-spark-1.3)
MAX_TOKENS = 600                                  # bounds the cost of one call
RESERVE_MIN = 0.02                                # US$ booked before each call, settled to the real cost after
MAX_INFLIGHT = 8                                  # concurrent Meta calls; more -> offline at once
TIMEOUT_S = 4.0
MAX_Q = 40
MAX_BODY = 2048
TYPES = ("fact", "fiction", "none", "abuse")
BUILTIN_ORIGINS = ("https://lavenhill.github.io",)


def _load_dotenv():
    """Botkeep writes panel Environment values to a .env file in the server root
    instead of exporting them. Load KEY=VALUE lines (no override of real env)."""
    for d in (os.getcwd(), os.path.join(REPO, ".."), REPO):
        f = os.path.join(d, ".env")
        try:
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    if k.startswith("export "):
                        k = k[7:].strip()
                    v = v.strip()
                    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                        v = v[1:-1]
                    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k) and k not in os.environ:
                        os.environ[k] = v
        except OSError:
            continue


_load_dotenv()


def _env_int(name, default):
    try: return int(os.environ.get(name, default))
    except ValueError: return default


def _env_float(name, default):
    try: return float(os.environ.get(name, default))
    except ValueError: return default


class Config:
    def __init__(self):
        self.key = os.environ.get("META_KEY", "").strip()
        self.port = _env_int("SERVER_PORT", 8080)
        self.data_dir = os.environ.get("DATA_DIR") or os.path.join(REPO, "..", "data")
        self.ip_header = os.environ.get("IP_HEADER", "").strip()
        extra = [o.strip().rstrip("/") for o in os.environ.get("ALLOW_ORIGIN", "").split(",") if o.strip()]
        self.origins = set(BUILTIN_ORIGINS) | set(extra)
        self.cap_n = _env_int("ASK_CAP_N", 700)
        self.cap_usd = _env_float("ASK_CAP_USD", 10.0)
        self.per_ip = _env_int("ASK_PER_IP", 30)
        self.per_min = _env_int("ASK_PER_MIN", 20)
        self.seed_n = _env_int("ASK_SEED_N", 0)


# ---------- sentence library: prompt from tools/sources_muse.py, allowed IDs from data.js ----------
def load_library():
    """Returns (system_prompt, allowed_ids, note). Live answers are off unless both sources agree."""
    try:
        sys.path.insert(0, os.path.join(REPO, "tools"))
        import sources_muse as M
        prompt, muse_ids = M.system_prompt(), list(M.IDS)
    except Exception as e:
        return "", frozenset(), "prompt: " + type(e).__name__
    try:
        txt = open(os.path.join(REPO, "data.js"), encoding="utf-8").read()
        data, _ = json.JSONDecoder().raw_decode(txt[txt.index("const DATA=") + len("const DATA="):])
        src = data["sources"]
        data_ids = [f"{cid}-{i + 1}" for cid in src["order"] for i in range(len(src["cards"][cid]["f"]))]
    except Exception as e:
        return "", frozenset(), "data.js: " + type(e).__name__
    if set(data_ids) != set(muse_ids):
        return "", frozenset(), f"mismatch data.js {len(data_ids)} vs sources_muse {len(muse_ids)}"
    return prompt, frozenset(data_ids), ""


def user_msg(q):
    return "玩家問：「" + q + "」"   # same wording as tools/sources_muse.py


# ---------- counters (SQLite; reserve first, then call Meta) ----------
def taipei_day(now=None):
    return time.strftime("%Y-%m-%d", time.gmtime((now or time.time()) + 8 * 3600))


def ip_block(ip):
    """IPv4 -> /24, IPv6 -> /48 (IPv4-mapped IPv6 counts as IPv4)."""
    try:
        a = ipaddress.ip_address(ip.strip().strip("[]").split("%")[0])
    except ValueError:
        return "unknown"
    if a.version == 6 and a.ipv4_mapped:
        a = a.ipv4_mapped
    return str(ipaddress.ip_network(f"{a}/{24 if a.version == 4 else 48}", strict=False))


class Counter:
    def __init__(self, cfg, reserve=RESERVE_MIN):
        self.cfg, self.res = cfg, reserve
        os.makedirs(cfg.data_dir, exist_ok=True)
        self.path = os.path.join(cfg.data_dir, "ask_counts.sqlite3")
        with self._db() as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS total(id INTEGER PRIMARY KEY CHECK(id=1), n INTEGER, usd REAL)")
            c.execute("CREATE TABLE IF NOT EXISTS minute(b INTEGER PRIMARY KEY, n INTEGER)")
            c.execute("CREATE TABLE IF NOT EXISTS ipday(day TEXT, blk TEXT, n INTEGER, PRIMARY KEY(day, blk))")
            c.execute("BEGIN IMMEDIATE")
            if c.execute("SELECT 1 FROM total").fetchone() is None:
                c.execute("INSERT INTO total VALUES(1, ?, 0)", (max(0, cfg.seed_n),))
                c.execute("INSERT OR REPLACE INTO kv VALUES('salt', ?)", (secrets.token_hex(16),))
            c.execute("COMMIT")
            self.salt = os.environ.get("ASK_SALT") or c.execute("SELECT v FROM kv WHERE k='salt'").fetchone()[0]

    def _db(self):
        c = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        return _Closing(c)

    def totals(self):
        with self._db() as c:
            n, usd = c.execute("SELECT n, usd FROM total").fetchone()
        return n, usd

    def reserve(self, ip, now=None):
        """Atomically checks every limit and books one call + the reserve. Returns (ok, why)."""
        now = now or time.time()
        cfg, day, b = self.cfg, taipei_day(now), int(now // 60)
        blk = hmac.new(self.salt.encode(), ip_block(ip).encode(), hashlib.sha256).hexdigest()[:20]
        with self._db() as c:
            c.execute("BEGIN IMMEDIATE")
            try:
                n, usd = c.execute("SELECT n, usd FROM total").fetchone()
                if n >= cfg.cap_n: why = "cap_n"
                elif usd + self.res > cfg.cap_usd: why = "cap_usd"
                else:
                    m = (c.execute("SELECT n FROM minute WHERE b=?", (b,)).fetchone() or (0,))[0]
                    k = (c.execute("SELECT n FROM ipday WHERE day=? AND blk=?", (day, blk)).fetchone() or (0,))[0]
                    why = "per_min" if m >= cfg.per_min else "per_ip" if k >= cfg.per_ip else ""
                if why:
                    c.execute("ROLLBACK"); return False, why
                c.execute("UPDATE total SET n=n+1, usd=usd+?", (self.res,))
                c.execute("INSERT INTO minute VALUES(?,1) ON CONFLICT(b) DO UPDATE SET n=n+1", (b,))
                c.execute("INSERT INTO ipday VALUES(?,?,1) ON CONFLICT(day,blk) DO UPDATE SET n=n+1", (day, blk))
                c.execute("DELETE FROM minute WHERE b<?", (b - 5,))
                c.execute("DELETE FROM ipday WHERE day<?", (taipei_day(now - 2 * 86400),))
                c.execute("COMMIT")
                return True, ""
            except Exception:
                c.execute("ROLLBACK"); raise

    def settle(self, usd):
        """Replaces the reservation with the real cost (kept as-is when the cost is unknown)."""
        if usd is None: return
        with self._db() as c:
            c.execute("BEGIN IMMEDIATE")
            try:
                c.execute("UPDATE total SET usd=MAX(0, usd-?+?)", (self.res, usd))
                c.execute("COMMIT")
            except Exception:
                c.execute("ROLLBACK"); raise


class _Closing:
    def __init__(self, c): self.c = c
    def __enter__(self): return self.c
    def __exit__(self, *a): self.c.close()


# ---------- Meta call ----------
def call_meta(key, prompt, q):
    """Returns (parsed_json_or_None, usd_or_None). Hard 4-second deadline; never raises."""
    body = json.dumps({"model": MODEL, "reasoning_effort": "minimal", "max_tokens": MAX_TOKENS,
                       "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": user_msg(q)}]}).encode()
    req = urllib.request.Request(META_ENDPOINT, data=body, method="POST",
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    box = {}

    def run():
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                box["x"] = json.load(r)
        except urllib.error.HTTPError as e:
            box["http"] = e.code
        except Exception as e:
            box["err"] = type(e).__name__

    t = threading.Thread(target=run, daemon=True); t.start(); t.join(TIMEOUT_S)
    if t.is_alive() or "err" in box:
        return None, None          # timeout / network: cost unknown, keep the reservation
    if "http" in box:
        return None, 0.0           # Meta refused the call: nothing billed
    x = box.get("x") or {}
    u = x.get("usage") or {}
    usd = (u.get("prompt_tokens") or 0) * PRICE_IN + (u.get("completion_tokens") or 0) * PRICE_OUT if u else None
    try:
        raw = x["choices"][0]["message"]["content"]
        return json.loads(re.sub(r"^```(json)?|```$", "", raw.strip()).strip()), usd
    except Exception:
        return None, usd


def clean_answer(j, ids):
    """Only known sentence IDs, at most 3. Anything else -> offline."""
    off = {"type": "offline", "picks": []}
    if not isinstance(j, dict) or j.get("type") not in TYPES:
        return off
    t, picks = j["type"], j.get("picks")
    if t in ("none", "abuse"):
        return {"type": t, "picks": []}
    out = []
    for p in picks if isinstance(picks, list) else []:
        if isinstance(p, str) and p in ids and p not in out:
            out.append(p)
    return {"type": t, "picks": out[:3]} if out else off


# ---------- HTTP ----------
OFFLINE = {"type": "offline", "picks": []}


def reserve_for(prompt):
    """Worst case of one call: every prompt character counted as a token (Chinese text is ~0.75
    token per character) plus a full MAX_TOKENS answer, x1.5; never below RESERVE_MIN."""
    return round(max(RESERVE_MIN, 1.5 * (len(prompt) * PRICE_IN + MAX_TOKENS * PRICE_OUT)), 4)


class App:
    def __init__(self, cfg=None):
        self.cfg = cfg or Config()
        self.prompt, self.ids, self.lib_note = load_library()
        self.reserve = reserve_for(self.prompt)
        self.counter = Counter(self.cfg, self.reserve)
        self.slots = threading.BoundedSemaphore(MAX_INFLIGHT)
        self.meta = call_meta     # tests may replace this

    def live(self):
        return bool(self.cfg.key and self.ids)


class Handler(BaseHTTPRequestHandler):
    server_version = "bb-ask"
    sys_version = ""
    timeout = 10
    app = None   # set in make_server

    def log_message(self, fmt, *args):   # no IP, no query string, no question text
        sys.stderr.write("%s %s %s\n" % (time.strftime("%H:%M:%S"), self.command, self.path.split("?")[0][:40]))

    def log_request(self, code="-", size="-"):
        sys.stderr.write("%s %s %s %s\n" % (time.strftime("%H:%M:%S"), self.command, self.path.split("?")[0][:40], code))

    def _cors(self):
        o = (self.headers.get("Origin") or "").rstrip("/")
        if o in self.app.cfg.origins:
            self.send_header("Access-Control-Allow-Origin", o)
        self.send_header("Vary", "Origin")

    def _json(self, obj, status=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(b)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/health":
            a, (n, usd) = self.app, self.app.counter.totals()
            return self._json({"ok": True, "key": bool(a.cfg.key), "live": a.live() and n < a.cfg.cap_n,
                               "used": n, "cap": a.cfg.cap_n, "usd": round(usd, 4), "cap_usd": a.cfg.cap_usd,
                               "ids": len(a.ids), "lib": a.lib_note or "ok", "ip_header": bool(a.cfg.ip_header)})
        if path == "/api/ask":
            return self._json(OFFLINE, 405)
        self._json({"error": "not found"}, 404)

    def do_HEAD(self):
        if self.path.split("?")[0] == "/health":
            return self.do_GET()
        self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers()

    def client_ip(self):
        h = self.app.cfg.ip_header
        if not h:
            return self.client_address[0]
        v = self.headers.get(h)
        if not v:
            return None
        return [p.strip() for p in v.split(",") if p.strip()][-1]   # the hop our own proxy appended

    def do_POST(self):
        if self.path.split("?")[0] != "/api/ask":
            return self._json({"error": "not found"}, 404)
        a = self.app
        if (self.headers.get("Origin") or "").rstrip("/") not in a.cfg.origins:
            return self._json(OFFLINE, 403)
        ip = self.client_ip()
        if ip is None:
            return self._json(OFFLINE, 403)
        try:
            ln = int(self.headers.get("Content-Length") or "-1")
        except ValueError:
            ln = -1
        if ln < 0 or ln > MAX_BODY:
            return self._json(OFFLINE, 413 if ln > MAX_BODY else 411)
        try:
            j = json.loads(self.rfile.read(ln).decode("utf-8"))
        except Exception:
            return self._json(OFFLINE, 400)
        q = j.get("q") if isinstance(j, dict) else None            # every other field is dropped
        q = " ".join(q.split()) if isinstance(q, str) else ""
        if not q or len(q) > MAX_Q:
            return self._json(OFFLINE, 400)
        if not a.live():
            return self._json(OFFLINE)
        if not a.slots.acquire(blocking=False):
            return self._json(OFFLINE)
        try:
            ok, _why = a.counter.reserve(ip)
            if not ok:
                return self._json(OFFLINE)
            try:
                ans, usd = a.meta(a.cfg.key, a.prompt, q)
            except Exception:
                ans, usd = None, None
            a.counter.settle(usd)
        finally:
            a.slots.release()
        self._json(clean_answer(ans, a.ids))


def make_server(app=None, host="0.0.0.0", port=None):
    app = app or App()
    h = type("BoundHandler", (Handler,), {"app": app})
    srv = ThreadingHTTPServer((host, app.cfg.port if port is None else port), h)
    srv.daemon_threads = True
    return srv


if __name__ == "__main__":
    app = App()
    srv = make_server(app)
    n, usd = app.counter.totals()
    print(f"bb-ask on 0.0.0.0:{app.cfg.port} key={bool(app.cfg.key)} ids={len(app.ids)} lib={app.lib_note or 'ok'} "
          f"used={n}/{app.cfg.cap_n} usd={usd:.4f}/{app.cfg.cap_usd} reserve={app.reserve}", flush=True)
    if not app.cfg.ip_header:
        print("WARNING: IP_HEADER is not set; behind a reverse proxy every visitor shares one IP block.", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
