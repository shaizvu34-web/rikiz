#!/usr/bin/env python3
"""
בונה גרסה אחת עצמאית של האתר לשיתוף.

כל התמונות והגופנים מוטמעים כ-data URI, כך שהקובץ עומד בפני עצמו בלי
שום בקשה לרשת. התמונות מוקטנות תחילה כדי שהעמוד ייטען מהר גם בסלולר.

שימוש:  python3 tools/build-share.py
פלט:    share.html
"""
import base64, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, ".build-img")
MAX_W = 900           # רוחב מרבי לתמונות מוצר
JPEG_Q = 62

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".woff2": "font/woff2"}


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as f:
        return f"data:{MIME[ext]};base64," + base64.b64encode(f.read()).decode()


def shrink(rel):
    """מקטין תמונה לתיקייה זמנית ומחזיר את הנתיב אליה."""
    src = os.path.join(ROOT, rel)
    # רוחב נוכחי — אסור להגדיל תמונה, זה רק מנפח את הקובץ
    info = subprocess.run(["sips", "-g", "pixelWidth", src],
                          capture_output=True, text=True).stdout
    width = int(re.search(r"pixelWidth:\s*(\d+)", info).group(1))
    if rel.lower().endswith(".png"):
        # PNG עם שקיפות — סיפס מאבד איכות, ומעבר ל-500 פיקסל אין צורך בשיתוף
        from PIL import Image
        im = Image.open(src)
        if im.width <= 500:
            return src
        os.makedirs(TMP, exist_ok=True)
        dst = os.path.join(TMP, rel.replace("/", "_"))
        im.resize((500, round(500 * im.height / im.width)), Image.LANCZOS).save(dst, optimize=True)
        return dst

    dst = os.path.join(TMP, rel.replace("/", "_"))
    os.makedirs(TMP, exist_ok=True)
    shutil.copy(src, dst)
    args = ["sips"]
    if width > MAX_W:
        args += ["-Z", str(MAX_W)]
    if not rel.lower().endswith(".png"):
        args += ["-s", "formatOptions", str(JPEG_Q)]
    subprocess.run(args + [dst], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dst


def main():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

    # 1. גופן: מחליף את קובץ ה-CSS החיצוני בסגנון מוטמע עם data URI
    font_css = open(os.path.join(ROOT, "fonts/frank-ruhl-libre.css"), encoding="utf-8").read()
    for rel in sorted(set(re.findall(r"url\((fonts/[^)]+\.woff2)\)", font_css))):
        font_css = font_css.replace(f"url({rel})", f"url({data_uri(os.path.join(ROOT, rel))})")
    html = html.replace('<link rel="stylesheet" href="fonts/frank-ruhl-libre.css">',
                        f"<style>\n{font_css}\n</style>")

    # קבצי CSS ו-JS מקומיים מוטמעים גם הם — ארטיפקט חייב לעמוד בפני עצמו
    for rel in re.findall(r'<link rel="stylesheet" href="([^"/]+\.css)">', html):
        css = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        html = html.replace(f'<link rel="stylesheet" href="{rel}">', f"<style>\n{css}\n</style>")
    for rel in re.findall(r'<script src="([^"/]+\.js)"></script>', html):
        js = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        html = html.replace(f'<script src="{rel}"></script>', f"<script>\n{js}\n</script>")

    # 2. תמונות
    used = sorted(set(re.findall(r'src="(images/[^"]+)"', html)))
    total = 0
    for rel in used:
        small = shrink(rel)
        uri = data_uri(small)
        total += len(uri)
        html = html.replace(f'src="{rel}"', f'src="{uri}"')
    shutil.rmtree(TMP, ignore_errors=True)

    # 3. פירוק המעטפת — הארטיפקט מספק doctype/head/body בעצמו
    html = re.sub(r"^.*?<title>", "<title>", html, flags=re.S)
    html = html.replace("</head>\n<body>", "").replace("</body>\n</html>", "")
    html = html.replace("</head>", "").replace("<body>", "")
    html = html.replace("</body>", "").replace("</html>", "")

    # ה-dir היה על תגית html שכבר לא בידינו — מעבירים אותו ל-CSS
    html = html.replace("<style>\n  :root {", "<style>\n  html { direction: rtl; }\n  :root {", 1)

    out = os.path.join(ROOT, "share.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"{len(used)} תמונות · {total/1024/1024:.2f}MB מתוכן · סה\"כ {os.path.getsize(out)/1024/1024:.2f}MB")
    print(out)


if __name__ == "__main__":
    main()
