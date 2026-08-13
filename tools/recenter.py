#!/usr/bin/env python3
"""
ממרכז מוצר בתוך פריים ביחס אחיד, בלי לחתוך אותו.

reframe.py חותך מתוך התמונה, ולכן כשהמוצר רחב כמעט כמו המקור אין לאן להזיז
אותו והוא נשאר לא ממורכז. כאן במקום לחתוך בונים קנבס חדש בגוון הרקע של
התמונה, ומדביקים עליו את המקור כך שמרכז המוצר נופל בדיוק במרכז הפריים.

שימוש:  python3 tools/recenter.py <מקור> <יעד> [--rotate 180]
"""
import sys
from collections import deque
from PIL import Image

ASPECT = 3 / 4      # רוחב חלקי גובה
FILL = 0.84         # איזה חלק מגובה הפריים המוצר תופס
REACH = 46
SCAN_W = 220


def analyze(im):
    """מחזיר (גבולות המוצר ביחסים, צבע הרקע)."""
    small = im.convert("RGB").resize((SCAN_W, int(SCAN_W * im.height / im.width)))
    w, h = small.size
    px = small.load()

    edge = [px[x, 0] for x in range(w)] + [px[x, h - 1] for x in range(w)] \
         + [px[0, y] for y in range(h)] + [px[w - 1, y] for y in range(h)]
    edge.sort(key=sum)
    bg = edge[len(edge) // 2]

    def far(c):
        return max(abs(c[0]-bg[0]), abs(c[1]-bg[1]), abs(c[2]-bg[2])) > REACH

    outside = bytearray(w * h)
    q = deque([(x, y) for x in range(w) for y in (0, h-1)]
            + [(x, y) for y in range(h) for x in (0, w-1)])
    while q:
        x, y = q.popleft()
        i = y * w + x
        if outside[i] or far(px[x, y]):
            continue
        outside[i] = 1
        if x: q.append((x-1, y))
        if x < w-1: q.append((x+1, y))
        if y: q.append((x, y-1))
        if y < h-1: q.append((x, y+1))

    pts = [(x, y) for y in range(h) for x in range(w) if not outside[y*w + x]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs)/w, min(ys)/h, (max(xs)+1)/w, (max(ys)+1)/h), bg


def main():
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGB")
    if "--rotate" in sys.argv:
        deg = int(sys.argv[sys.argv.index("--rotate") + 1])
        im = im.rotate(deg, expand=True)

    (x0, y0, x1, y1), bg = analyze(im)
    W, H = im.size
    prod_h = (y1 - y0) * H
    cx, cy = (x0 + x1) / 2 * W, (y0 + y1) / 2 * H

    out_h = round(prod_h / FILL)
    out_w = round(out_h * ASPECT)

    # ריפוד בשני שלבים. קודם משקפים רצועת רקע צרה מהקצה — לא את התמונה
    # כולה, אחרת נכנס לפריים עותק חלקי של הכפכף. אם עדיין חסר, מותחים את
    # שורת הפיקסלים החיצונית. ox/oy עוקבים אחרי מיקום המקור בתוך הקנבס.
    pad_x = min(max(0, round((out_w - W) / 2) + 2), max(1, round(x0 * W) - 3))
    pad_y = min(max(0, round((out_h - H) / 2) + 2), max(1, round(y0 * H) - 3))

    padded = Image.new("RGB", (W + 2 * pad_x, H + 2 * pad_y), bg)
    padded.paste(im, (pad_x, pad_y))
    if pad_x:
        padded.paste(im.crop((0, 0, pad_x, H)).transpose(Image.FLIP_LEFT_RIGHT), (0, pad_y))
        padded.paste(im.crop((W - pad_x, 0, W, H)).transpose(Image.FLIP_LEFT_RIGHT), (W + pad_x, pad_y))
    if pad_y:
        top_strip = padded.crop((0, pad_y, padded.width, 2 * pad_y))
        padded.paste(top_strip.transpose(Image.FLIP_TOP_BOTTOM), (0, 0))
        bot_strip = padded.crop((0, H, padded.width, H + pad_y))
        padded.paste(bot_strip.transpose(Image.FLIP_TOP_BOTTOM), (0, H + pad_y))
    ox, oy = pad_x, pad_y

    def stretch(img, need_w, need_h, ox, oy):
        w, h = img.size
        if w < need_w:
            extra = need_w - w; li = extra // 2
            new = Image.new("RGB", (need_w, h), bg)
            new.paste(img, (li, 0))
            if li:
                new.paste(img.crop((0, 0, 1, h)).resize((li, h)), (0, 0))
            if extra - li:
                new.paste(img.crop((w - 1, 0, w, h)).resize((extra - li, h)), (li + w, 0))
            img, ox = new, ox + li
        w, h = img.size
        if h < need_h:
            extra = need_h - h; ti = extra // 2
            new = Image.new("RGB", (w, need_h), bg)
            new.paste(img, (0, ti))
            if ti:
                new.paste(img.crop((0, 0, w, 1)).resize((w, ti)), (0, 0))
            if extra - ti:
                new.paste(img.crop((0, h - 1, w, h)).resize((w, extra - ti)), (0, ti + h))
            img, oy = new, oy + ti
        return img, ox, oy

    padded, ox, oy = stretch(padded, out_w, out_h, ox, oy)

    left = max(0, min(round(ox + cx - out_w / 2), padded.width - out_w))
    top = max(0, min(round(oy + cy - out_h / 2), padded.height - out_h))
    canvas = padded.crop((left, top, left + out_w, top + out_h))
    canvas.save(dst, quality=94, subsampling=0)

    print(f"{dst}: {out_w}x{out_h} · המוצר {(y1-y0)*100:.0f}% מגובה המקור · רקע {bg}")


if __name__ == "__main__":
    main()
