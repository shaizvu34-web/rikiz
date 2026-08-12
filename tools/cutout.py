#!/usr/bin/env python3
"""
מבודד מוצר מרקע סטודיו אחיד והופך את הרקע לשקוף.

הרעיון: לא סף בהירות גלובלי — כזה היה מוחק גם סוליות לבנות, שבהירות
מהרקע. במקום זה מציפים מהשוליים פנימה, וכל מה שלא מחובר לשוליים נשאר אטום.
הצל מתחת לכפכף מקבל שקיפות חלקית לפי המרחק מצבע הרקע, כך שהוא נשמר רך
ומתמזג בכל רקע שנשים מאחוריו.

שימוש:  python3 tools/cutout.py images/arch/*.jpg
פלט:    אותו שם עם סיומת .png
"""
import sys
from collections import deque
from PIL import Image, ImageFilter

SOFT_START = 8    # מתחת לזה = רקע נקי, שקוף לגמרי
SOFT_END = 34     # מעל לזה = תוכן מלא
REACH = 52        # עד כמה רחוק מצבע הרקע ההצפה עוד מתקדמת


def bg_color(px, w, h):
    """צבע הרקע = חציון הפיקסלים בשוליים."""
    edge = []
    for x in range(w):
        edge += [px[x, 0], px[x, h - 1]]
    for y in range(h):
        edge += [px[0, y], px[w - 1, y]]
    edge.sort(key=sum)
    return edge[len(edge) // 2]


def dist(c, b):
    return max(abs(c[0] - b[0]), abs(c[1] - b[1]), abs(c[2] - b[2]))


def cutout(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    bg = bg_color(px, w, h)

    # הצפה מהשוליים: מסמנת מה "בחוץ"
    outside = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))

    while q:
        x, y = q.popleft()
        i = y * w + x
        if outside[i]:
            continue
        if dist(px[x, y], bg) > REACH:
            continue
        outside[i] = 1
        if x > 0: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))

    # אלפא: פנים = אטום. חוץ = לפי המרחק מצבע הרקע, כדי לשמר את הצל.
    alpha = Image.new("L", (w, h))
    ap = alpha.load()
    span = SOFT_END - SOFT_START
    for y in range(h):
        for x in range(w):
            if not outside[y * w + x]:
                ap[x, y] = 255
                continue
            d = dist(px[x, y], bg)
            if d <= SOFT_START:
                ap[x, y] = 0
            elif d >= SOFT_END:
                ap[x, y] = 255
            else:
                ap[x, y] = int((d - SOFT_START) * 255 / span)

    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))
    im.putalpha(alpha)

    out = path.rsplit(".", 1)[0] + ".png"
    im.save(out)
    print(f"{path} → {out}   רקע={bg}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        cutout(p)
