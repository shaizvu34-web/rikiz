#!/usr/bin/env python3
"""
פורס את כל אתר RIKIZ ל-Vercel כאתר סטטי (בלי build), דרך ה-API.
טוקן נקרא מ-~/.vercel-token. שימוש: python3 deploy-vercel-site.py [project-name]
"""
import base64, hashlib, json, os, sys, urllib.error, urllib.request

ROOT = os.path.expanduser("~/rikiz-site")
TOKEN = open(os.path.expanduser("~/.vercel-token")).read().strip()

# אותה רשימה כמו הפריסה ל-Netlify — רק מה שצריך לאוויר
INCLUDE_FILES = ["index.html", "accessibility.html", "privacy.html",
                 "a11y.css", "a11y.js", "legal.css"]
INCLUDE_DIRS = ["images", "fonts"]
SKIP = (".DS_Store",)


def gather():
    files = []
    for f in INCLUDE_FILES:
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            files.append((f, p))
    for d in INCLUDE_DIRS:
        for base, _, names in os.walk(os.path.join(ROOT, d)):
            for n in names:
                if n.endswith(SKIP):
                    continue
                full = os.path.join(base, n)
                rel = os.path.relpath(full, ROOT)
                files.append((rel, full))
    return files


def api(path, payload=None, method="POST"):
    url = "https://api.vercel.com" + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + TOKEN,
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Vercel {e.code}: {e.read().decode()[:600]}")


def upload(full):
    body = open(full, "rb").read()
    sha = hashlib.sha1(body).hexdigest()
    req = urllib.request.Request("https://api.vercel.com/v2/files", data=body,
                                 method="POST", headers={
        "Authorization": "Bearer " + TOKEN,
        "Content-Type": "application/octet-stream",
        "x-vercel-digest": sha,
    })
    urllib.request.urlopen(req, timeout=120).read()
    return sha, len(body)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "rikiz"
    files = gather()
    manifest = []
    for rel, full in files:
        sha, size = upload(full)
        manifest.append({"file": rel, "sha": sha, "size": size})
        print("  ↑", rel)
    dep = api("/v13/deployments", {
        "name": name,
        "files": manifest,
        "target": "production",
        "projectSettings": {"framework": None, "buildCommand": None,
                            "outputDirectory": ".", "installCommand": None},
    })
    print("\nstate:", dep.get("readyState") or dep.get("status"))
    print("url:  https://%s" % dep.get("url"))
    alias = dep.get("alias") or []
    for a in alias:
        print("alias: https://%s" % a)
    print("\nכתובת קבועה צפויה: https://%s.vercel.app" % name)


if __name__ == "__main__":
    main()
