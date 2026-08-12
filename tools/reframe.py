#!/usr/bin/env python3
"""
מיישר מסגור בין תמונות מוצר.

מזהה את גבולות הכפכף (הצפה מהשוליים, כמו ב-cutout.py), ואז חותך כל תמונה
ליחס אחיד כך שהמוצר יישב באותו גודל ובאותו מקום בפריים בכל הדגמים.
בלי זה כל תמונה מציגה את הכפכף בסקאלה אחרת והגריד נראה מבולגן.

שימוש:  python3 tools/reframe.py images/d16.jpg images/d17.jpg ...
        python3 tools/reframe.py --dry images/*.jpg     (רק מדפיס מה זוהה)
"""
import sys
from collections import deque
from PIL import Image

ASPECT = 3 / 4          # רוחב חלקי גובה של הפריים הסופי
FILL = 0.86             # איזה חלק מגובה הפריים המוצר תופס
REACH = 46              # מרחק צבע מרבי שעדיין נחשב רקע
SCAN_W = 220            # רוחב לניתוח — מספיק לזיהוי, מהיר בהרבה


def bbox(im):
    """מחזיר את גבולות המוצר ביחסים (0..1) של התמונה המקורית."""
    small = im.convert("RGB").resize((SCAN_W, int(SCAN_W * im.height / im.width)))
    w, h = small.size
    px = small.load()

    edge = [px[x, 0] for x in range(w)] + [px[x, h - 1] for x in range(w)] \
         + [px[0, y] for y in range(h)] + [px[w - 1, y] for y in range(h)]
    edge.sort(key=sum)
    bg = edge[len(edge) // 2]

    def far(c):
        return max(abs(c[0] - bg[0]), abs(c[1] - bg[1]), abs(c[2] - bg[2])) > REACH

    outside = bytearray(w * h)
    q = deque([(x, y) for x in range(w) for y in (0, h - 1)]
            + [(x, y) for y in range(h) for x in (0, w - 1)])
    while q:
        x, y = q.popleft()
        i = y * w + x
        if outside[i] or far(px[x, y]):
            continue
        outside[i] = 1
        if x: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))

    xs = [x for y in range(h) for x in range(w) if not outside[y * w + x]]
    ys = [y for y in range(h) for x in range(w) if not outside[y * w + x]]
    if not xs:
        return 0.0, 0.0, 1.0, 1.0
    return min(xs) / w, min(ys) / h, (max(xs) + 1) / w, (max(ys) + 1) / h


def reframe(path, dry=False):
    im = Image.open(path)
    x0, y0, x1, y1 = bbox(im)
    W, H = im.size
    cx, cy = (x0 + x1) / 2 * W, (y0 + y1) / 2 * H
    prod_h = (y1 - y0) * H

    out_h = prod_h / FILL
    out_w = out_h * ASPECT
    if out_w > W:                       # לא לחרוג מרוחב התמונה
        out_w, out_h = W, W / ASPECT

    left = round(min(max(cx - out_w / 2, 0), W - out_w))
    top = round(min(max(cy - out_h / 2, 0), H - out_h))
    box = (left, top, left + round(out_w), top + round(out_h))

    print(f"{path}: מוצר {(y1-y0)*100:.0f}% מהגובה · חיתוך {box[2]-box[0]}x{box[3]-box[1]} מ-{left},{top}")
    if not dry:
        im.crop(box).save(path, quality=88)


if __name__ == "__main__":
    args = sys.argv[1:]
    dry = "--dry" in args
    for p in [a for a in args if a != "--dry"]:
        reframe(p, dry)
