#!/usr/bin/env python3
"""
מבצע התחברות ל-GitHub בזרימת Device Flow, בלי להעביר טוקן דרך הצ'אט.

הסקריפט מבקש קוד מ-GitHub, מדפיס אותו למסך, פותח את דף האישור בדפדפן,
ואז ממתין עד שהמשתמש מאשר. הטוקן שמתקבל מוזרם ישירות אל
`gh auth login --with-token` — הוא לא מודפס ולא נשמר בשום קובץ.
"""
import json, subprocess, sys, time, urllib.parse, urllib.request

CLIENT_ID = "178c6fc778ccc68e1d6a"      # המזהה הציבורי של GitHub CLI
GH = "/Users/shaizvulun/.local/bin/gh"


def post(url, **fields):
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=body, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    start = post("https://github.com/login/device/code",
                 client_id=CLIENT_ID, scope="repo read:org workflow")

    code = start["user_code"]
    url = start["verification_uri"]
    interval = int(start.get("interval", 5))

    print("=" * 44)
    print(f"   הקוד שלך:   {code}")
    print("=" * 44)
    print(f"הדף נפתח בדפדפן: {url}")
    print("הדבק שם את הקוד ואשר. אני ממתין...")
    sys.stdout.flush()

    subprocess.run(["open", "-a", "Google Chrome", url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    deadline = time.time() + int(start.get("expires_in", 900))
    while time.time() < deadline:
        time.sleep(interval)
        res = post("https://github.com/login/oauth/access_token",
                   client_id=CLIENT_ID, device_code=start["device_code"],
                   grant_type="urn:ietf:params:oauth:grant-type:device_code")
        err = res.get("error")
        if err == "authorization_pending":
            continue
        if err == "slow_down":
            interval += 5
            continue
        if err:
            sys.exit(f"נכשל: {res.get('error_description', err)}")

        token = res["access_token"]
        subprocess.run([GH, "auth", "login", "--with-token"],
                       input=token.encode(), check=True)
        subprocess.run([GH, "auth", "setup-git"], check=True)
        print("מחובר. הטוקן נשמר ב-Keychain ולא נחשף בשום מקום.")
        return

    sys.exit("פג תוקף הקוד. הרץ שוב.")


if __name__ == "__main__":
    main()
