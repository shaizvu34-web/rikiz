#!/usr/bin/env python3
"""
פורס את share.html ל-Vercel דרך ה-API, בלי CLI ובלי Node.

דורש טוקן אישי מ-https://vercel.com/account/tokens, שמור ב-~/.vercel-token
(שורה אחת, בלי רווחים). הטוקן לא נשמר בשום מקום אחר ולא נכתב ללוג.

שימוש:  python3 tools/deploy-vercel.py [שם-הפרויקט]
"""
import base64, json, os, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.expanduser("~/.vercel-token")
API = "https://api.vercel.com/v13/deployments"


def token():
    if not os.path.exists(TOKEN_FILE):
        sys.exit(f"חסר קובץ טוקן: {TOKEN_FILE}\n"
                 f"צור טוקן ב-https://vercel.com/account/tokens ואז:\n"
                 f'  echo "הטוקן" > ~/.vercel-token && chmod 600 ~/.vercel-token')
    t = open(TOKEN_FILE).read().strip()
    if not t:
        sys.exit("קובץ הטוקן ריק.")
    return t


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "rikiz"
    src = os.path.join(ROOT, "share.html")
    if not os.path.exists(src):
        sys.exit("אין share.html — הרץ קודם: python3 tools/build-share.py")

    data = base64.b64encode(open(src, "rb").read()).decode()
    body = json.dumps({
        "name": name,
        "target": "production",
        "files": [{"file": "index.html", "data": data, "encoding": "base64"}],
        "projectSettings": {"framework": None},
    }).encode()

    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"Bearer {token()}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        sys.exit(f"Vercel החזיר {e.code}:\n{detail}")

    print("הפריסה נוצרה.")
    print("כתובת זמנית: https://" + res.get("url", "?"))
    for alias in res.get("alias") or []:
        print("כתובת קבועה:  https://" + alias)


if __name__ == "__main__":
    main()
