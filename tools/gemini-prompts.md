# פרומפטים לג'מיני — RIKIZ

שלושה פרומפטים לייצור תמונות שמתאימות לשפה העיצובית של האתר.
כתובים באנגלית כי מודלי תמונה עובדים איתה טוב בהרבה.

**כלל אצבע:** אל תבקש טקסט בתוך התמונה. מודלים מעוותים אותיות, ובעברית זה
יוצא ג'יבריש. הלוגו מתווסף אחר כך — ככה בנינו גם את כרטיס התצוגה המקדימה.

---

## 1. תמונת המותג — שולחן העבודה

זו התמונה שמתמצתת את העסק: המלאכה, החומרים והתוצאה בפריים אחד.

```
Overhead flat-lay of an artisan's jewelry workbench, warm neutral stone-grey
seamless background (#E9EAE5), shot from directly above.

On the surface: three pairs of embellished flip-flop sandals arranged in a
loose diagonal — one white pair with pearls and gold crystals, one deep purple
pair with large iridescent rhinestones, one sand-beige pair with clear crystals
and gold settings. Each strap is hand-wrapped in fine satin thread with rows of
tiny rhinestones set along it.

Scattered around them, the tools of the craft: two wooden spools of ivory and
rose satin thread, fine steel tweezers, small sharp scissors, a shallow white
ceramic dish holding loose clear and gold crystals, a threaded needle, a soft
measuring tape curving through the frame, a few loose gold beads.

Single soft directional light from the upper left. Gentle, real contact shadows
under every object. Muted palette — the background and tools are quiet neutrals,
all the colour comes from the sandals and the sparkle of the stones.

Editorial product photography, high-end jewellery catalogue, shallow depth of
field, crisp macro detail on the crystals. 3:2 aspect ratio.

No text, no logos, no labels, no cardboard hang tags, no price tags, no hands.
```

---

## 2. הקולקציה — שורת מוצרים על לבן

לשימוש בראש העמוד או ברשתות. אותה זווית לכל זוג, בדיוק כמו במפרט הצילום.

```
Six pairs of embellished flip-flop sandals standing in a row on a seamless
pure white studio background, photographed at a consistent three-quarter angle,
each pair identically framed and lit.

The pairs are white, black, deep purple, royal blue, sand-beige and mustard
yellow. Every strap is hand-wrapped in satin thread and set with rows of clear
rhinestones in gold settings; some carry a small gold starfish or shell charm.

Soft directional studio light from the upper left, soft realistic drop shadows
grounding each pair. Clean, minimal, no props.

Luxury e-commerce product photography, sharp macro detail on the crystals,
even exposure across the row. 16:9 aspect ratio.

No text, no logos, no cardboard hang tags, no price tags, no hands, no clutter.
```

---

## 3. האריזה

התמונה שחסרה לנו — מוצר גמור בדרך ללקוחה.

```
A single pair of embellished sandals resting inside an open square translucent
frosted gift bag, on a warm neutral stone-grey surface (#E9EAE5).

The sandals are sand-beige with clear crystals and gold settings, visible
softly through the frosted material. The bag has a clean folded top and a
simple ribbon. Beside it, a small folded card and a length of satin ribbon.

Single soft directional light from the upper left, soft contact shadow beneath
the bag. Quiet, refined, luxurious. Nothing else in the frame.

Editorial packaging photography, shallow depth of field. 3:2 aspect ratio.

No text, no logos, no printed branding, no hands.
```

---

## אחרי שמקבלים תמונה

- **תמונת מותג ואווירה** — בסדר לשימוש באתר וברשתות.
- **תמונת מוצר** — לא להעלות כדף מוצר. היא מציגה זוג שלא קיים במלאי,
  וזו הצגה מטעה של סחורה. לזה יש את צילומי הסטודיו האמיתיים.
- להסרת רקע: `python3 tools/cutout.py <קובץ>`
- ליישור מסגור מול שאר הדגמים: `python3 tools/reframe.py <קובץ>`
