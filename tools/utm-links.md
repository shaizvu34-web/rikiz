# לינקי UTM לריקיז — מעקב מקורות תנועה

כל לינק שאתה מפרסם החוצה צריך לשאת תגי UTM. בלי זה, כל התנועה נכנסת ל־Umami
כ"ישיר / לא ידוע" ואי אפשר לדעת איזה ערוץ עובד.

**כתובת בסיס:** `https://rikiz.vercel.app/`

## מוסכמה קבועה

| פרמטר | מה שמים בו | דוגמאות |
|---|---|---|
| `utm_source` | מאיפה מגיעים (הפלטפורמה) | `instagram`, `facebook`, `meta`, `whatsapp`, `tiktok`, `google`, `card`, `newsletter`, `influencer` |
| `utm_medium` | סוג המיקום | `bio`, `story`, `post`, `reel`, `paid-social`, `status`, `dm`, `qr`, `email`, `referral` |
| `utm_campaign` | הקמפיין / החודש הספציפי | `always-on`, `2026-09`, `rosh-hashana`, `launch` |
| `utm_content` | (רשות) איזו מודעה / גרסה | שם המודעה, `v1` / `v2` לבדיקות |

כללי אצבע: הכול באנגלית קטנה, בלי רווחים (מקף במקום), עקבי — `instagram` תמיד, לא פעם `ig` פעם `insta`.

## לינקים מוכנים להעתקה

| ערוץ | לינק |
|---|---|
| אינסטגרם — לינק בביו | `https://rikiz.vercel.app/?utm_source=instagram&utm_medium=bio&utm_campaign=always-on` |
| אינסטגרם — סטיקר לינק בסטורי | `https://rikiz.vercel.app/?utm_source=instagram&utm_medium=story&utm_campaign=2026-09` |
| אינסטגרם — פוסט / ריל | `https://rikiz.vercel.app/?utm_source=instagram&utm_medium=post&utm_campaign=2026-09` |
| מודעה ממומנת מטא (אינסטגרם+פייסבוק) | `https://rikiz.vercel.app/?utm_source=meta&utm_medium=paid-social&utm_campaign=CAMPAIGN&utm_content=AD_NAME` |
| פייסבוק — פוסט אורגני | `https://rikiz.vercel.app/?utm_source=facebook&utm_medium=post&utm_campaign=2026-09` |
| וואטסאפ — סטטוס | `https://rikiz.vercel.app/?utm_source=whatsapp&utm_medium=status&utm_campaign=2026-09` |
| וואטסאפ — הודעה אישית / הפצה | `https://rikiz.vercel.app/?utm_source=whatsapp&utm_medium=dm&utm_campaign=2026-09` |
| טיקטוק — לינק בביו | `https://rikiz.vercel.app/?utm_source=tiktok&utm_medium=bio&utm_campaign=always-on` |
| QR על כרטיס ביקור / אריזה | `https://rikiz.vercel.app/?utm_source=card&utm_medium=qr&utm_campaign=print-2026` |
| ניוזלטר / מייל | `https://rikiz.vercel.app/?utm_source=newsletter&utm_medium=email&utm_campaign=2026-09` |
| שיתוף פעולה / משפיענית | `https://rikiz.vercel.app/?utm_source=influencer&utm_medium=referral&utm_campaign=NENAME` |

> החלף `2026-09` בחודש הרלוונטי, ו־`CAMPAIGN` / `AD_NAME` / `NENAME` בערכים אמיתיים.

### מודעות מטא — הדרך הנכונה
בכלי המודעות של מטא, בשדה **"פרמטרים של כתובת אתר"** של המודעה, הדבק:
```
utm_source=meta&utm_medium=paid-social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}
```
מטא ממלא את `{{campaign.name}}` ו־`{{ad.name}}` אוטומטית לכל מודעה.

## איך קוראים את התוצאות ב־Umami

- **כמה נכנסו ומאיפה:** לוח הבית → פאנל *Referrers*. שם רואים גם פירוט לפי
  `utm_source` / `utm_medium` / `utm_campaign`.
- **המרות (לחיצות וואטסאפ):** פאנל *Events* → האירוע `whatsapp`. לחיצה עליו
  מפרקת לפי `spot` — מאיזה כפתור באתר נלחץ (`fab`, `cta-bottom`, `header`,
  `collection:קשת` וכו').
- **מה שמעניין באמת:** סנן לפי מקור (למשל `utm_source=meta`) וראה כמה מתוך
  הכניסות שלו הגיעו לאירוע `whatsapp`. זה יחס ההמרה של הערוץ — לפיו מחליטים
  איפה לשים כסף.

## קיצור להפקת QR
כל מחולל QR חינמי (למשל qr-code-generator.com) — הדבק את לינק ה־UTM המלא,
הורד PNG, זהו.
