#!/usr/bin/env python3
"""
בונה את חיתוכי הקשת מהצילומים המקוריים, בפריים אחיד.

כל עיבוד רץ פעם אחת על קובץ המקור ולא על תוצר קודם — עיבוד חוזר על חיתוך
שכבר עבר סף אלפא מכרסם את הקצוות. בסוף כל הזוגות מקבלים אותו גובה מוצר
ואותו גודל פריים, וזה מה שמייצר קשת סימטרית.

שימוש:  python3 tools/build-arch.py
"""
import os
import subprocess
import tempfile
from collections import deque

from PIL import Image, ImageFilter

SRC = os.path.expanduser("~/Downloads/rikiz-images")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images/real")

# שם יעד → (קובץ מקור, סיבוב במעלות)
PAIRS = {
    "d16": ("סטודיו כחול.jpeg", 0),
    "d17": ("סטודיו צהוב.jpeg", 0),
    "d18": ("סטודיו שחור .jpeg", 180),
    "d19": ("סטודיו שמנת.jpeg", 0),
    "d21": ("סטודיו משולב .jpeg", 0),
    "d24": ("וורוד סטודיו.png", 180),
}

PRODUCT_H = 900     # גובה אחיד לכל הזוגות
FILL = 0.88         # כמה מגובה הפריים המוצר תופס
MAX_W = 700         # רוחב מרבי לקובץ הסופי
REACH = 54
SOFT_LO, SOFT_HI = 8, 34


def cutout(im):
    """מסיר רקע בהצפה מהשוליים ומחזיר אלפא."""
    im = im.convert("RGB")
    w, h = im.size
    px = im.load()

    edge = [px[x, 0] for x in range(w)] + [px[x, h-1] for x in range(w)] \
         + [px[0, y] for y in range(h)] + [px[w-1, y] for y in range(h)]
    edge.sort(key=sum)
    bg = edge[len(edge) // 2]

    def dist(c):
        return max(abs(c[0]-bg[0]), abs(c[1]-bg[1]), abs(c[2]-bg[2]))

    outside = bytearray(w * h)
    q = deque([(x, y) for x in range(w) for y in (0, h-1)]
            + [(x, y) for y in range(h) for x in (0, w-1)])
    while q:
        x, y = q.popleft()
        i = y * w + x
        if outside[i] or dist(px[x, y]) > REACH:
            continue
        outside[i] = 1
        if x: q.append((x-1, y))
        if x < w-1: q.append((x+1, y))
        if y: q.append((x, y-1))
        if y < h-1: q.append((x, y+1))

    alpha = Image.new("L", (w, h))
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            # מה שההצפה סימנה כחוץ הוא רקע — שקוף לגמרי. סף רך כאן
            # היה הופך רעש ומדרגי רקע לכתמים אטומים סביב המוצר.
            ap[x, y] = 0 if outside[y*w + x] else 255
    return alpha


def keep_main(alpha):
    """משאיר רק את הגושים הגדולים — מסנן אבנים בודדות שמונחות על הרקע."""
    # רזולוציה גבוהה יותר ודגימה רכה: NEAREST על מסכה מנתק חיבורים דקים,
    # ואז חצי סוליה נספרת כגוש נפרד ונמחקת.
    SW = 340
    small = alpha.resize((SW, round(SW * alpha.height / alpha.width)), Image.BILINEAR)
    small = small.point(lambda v: 255 if v > 100 else 0)
    w, h = small.size
    px = small.load()
    seen = bytearray(w * h)
    comps = []
    for sy in range(h):
        for sx in range(w):
            i = sy * w + sx
            if seen[i] or not px[sx, sy]:
                continue
            q = deque([(sx, sy)]); seen[i] = 1; pts = []
            while q:
                x, y = q.popleft(); pts.append((x, y))
                for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny*w + nx
                        if not seen[j] and px[nx, ny]:
                            seen[j] = 1; q.append((nx, ny))
            comps.append(pts)
    if not comps:
        return alpha, 0
    comps.sort(key=len, reverse=True)
    keep = [c for c in comps if len(c) >= len(comps[0]) * 0.02]
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    for c in keep:
        for x, y in c:
            mp[x, y] = 255
    mask = mask.resize(alpha.size, Image.LANCZOS).point(lambda v: 255 if v > 110 else 0)
    return Image.composite(alpha, Image.new("L", alpha.size, 0), mask), len(comps) - len(keep)


def main():
    os.makedirs(OUT, exist_ok=True)
    products = {}

    for name, (fname, rot) in PAIRS.items():
        path = os.path.join(SRC, fname)
        im = Image.open(path)
        if rot:
            im = im.rotate(rot, expand=True)
        alpha = cutout(im)
        alpha, dropped = keep_main(alpha)
        alpha = alpha.filter(ImageFilter.GaussianBlur(0.8)).point(lambda v: 0 if v < 90 else v)
        rgba = im.convert("RGBA")
        rgba.putalpha(alpha)
        prod = rgba.crop(rgba.split()[3].getbbox())
        products[name] = prod
        print(f"{name}: מוצר {prod.width}x{prod.height} · יחס {prod.width/prod.height:.3f}"
              f"{f' · הוסרו {dropped} כתמים' if dropped else ''}")

    widest = max(p.width / p.height for p in products.values())
    frame_w = round(PRODUCT_H * widest) + 70
    frame_h = round(PRODUCT_H / FILL)
    print(f"\nפריים אחיד {frame_w}x{frame_h} · גובה מוצר {PRODUCT_H}")

    for name, prod in products.items():
        nw = round(PRODUCT_H * prod.width / prod.height)
        prod = prod.resize((nw, PRODUCT_H), Image.LANCZOS)
        canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        canvas.paste(prod, ((frame_w - nw) // 2, (frame_h - PRODUCT_H) // 2), prod)
        if canvas.width > MAX_W:
            canvas = canvas.resize((MAX_W, round(MAX_W * frame_h / frame_w)), Image.LANCZOS)
        canvas.save(os.path.join(OUT, f"{name}.png"), optimize=True)

    final = Image.open(os.path.join(OUT, "d16.png"))
    print(f"נשמרו {len(products)} קבצים בגודל {final.width}x{final.height}")


if __name__ == "__main__":
    main()
