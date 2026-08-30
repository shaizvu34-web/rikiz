#!/usr/bin/env python3
"""
פורס את האתר ל-Netlify דרך ה-API, בלי CLI ובלי Node.

דורש טוקן אישי מ-https://app.netlify.com/user/applications#personal-access-tokens
שמור ב-~/.netlify-token (שורה אחת). הטוקן לא נכתב ללוג ולא נשמר בשום מקום אחר.

שימוש:  python3 tools/deploy-netlify.py [שם-האתר]
"""
import io
import json
import os
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.expanduser("~/.netlify-token")
API = "https://api.netlify.com/api/v1"

# מה עולה לאוויר. כל השאר — כלים, גיבויים והיסטוריית git — נשאר מקומי.
INCLUDE_FILES = ["index.html", "accessibility.html", "privacy.html",
                 "a11y.css", "a11y.js", "legal.css",
                 "entry-preview.html", "mobile-hero-trial.html"]  # תצוגת כניסה — לא מקושרת, noindex
INCLUDE_DIRS = ["images", "fonts"]
SKIP_SUFFIX = (".DS_Store",)


def token():
    if not os.path.exists(TOKEN_FILE):
        sys.exit("חסר ~/.netlify-token\n"
                 "צור טוקן ב-app.netlify.com/user/applications ואז:\n"
                 '  echo "הטוקן" > ~/.netlify-token && chmod 600 ~/.netlify-token')
    t = open(TOKEN_FILE).read().strip()
    if not t:
        sys.exit("קובץ הטוקן ריק.")
    return t


def call(path, data=None, method="GET", ctype="application/json"):
    url = path if path.startswith("http") else API + path
    body = data
    if isinstance(data, dict):
        body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": "Bearer " + token(),
        "Content-Type": ctype,
    })
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"Netlify החזיר {e.code}:\n{e.read().decode(errors='replace')[:500]}")


def build_zip():
    buf = io.BytesIO()
    n = 0
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in INCLUDE_FILES:
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                z.write(p, f); n += 1
        for d in INCLUDE_DIRS:
            for base, _, files in os.walk(os.path.join(ROOT, d)):
                for f in files:
                    if f.endswith(SKIP_SUFFIX):
                        continue
                    full = os.path.join(base, f)
                    z.write(full, os.path.relpath(full, ROOT)); n += 1
    return buf.getvalue(), n


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "rikiz"

    sites = call("/sites")
    site = next((s for s in sites if s.get("name") == name), None)
    if site:
        print(f"אתר קיים: {site['name']}")
    else:
        site = call("/sites", {"name": name}, "POST")
        print(f"אתר נוצר: {site['name']}")

    blob, count = build_zip()
    print(f"נארזו {count} קבצים · {len(blob)/1024/1024:.2f}MB")

    dep = call(f"/sites/{site['id']}/deploys", blob, "POST", "application/zip")
    print("סטטוס:", dep.get("state", "?"))
    print("כתובת:", site.get("ssl_url") or site.get("url") or f"https://{name}.netlify.app")


if __name__ == "__main__":
    main()
