#!/bin/bash
# sandbox may reset: reinstall headless test deps
python3 -c "import playwright" 2>/dev/null || pip install -q playwright
[ -x /usr/bin/chromium ] || { sudo -n apt-get update -qq >/dev/null 2>&1; sudo -n apt-get install -y -qq chromium fonts-noto-cjk >/dev/null 2>&1; }
fc-list :lang=zh | grep -q . || sudo -n apt-get install -y -qq fonts-noto-cjk >/dev/null 2>&1
echo ready
