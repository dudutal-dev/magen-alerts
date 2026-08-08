# 🎸🎹 סטוריבורד דמות מנגנת — [שם הפרויקט]

דמות אחת, ניתנת לשימוש חוזר בכל שיר. נועלים אותה פעם אחת, ומזינים את
הידיים מחדש מהאקורדים/תווים של כל שיר (`hand_positions.py`).

---

## גיליון דמות (Character Sheet — זהה בכל פאנל, אל תשנה)
- **זהות:** [גיל, מבנה גוף, פנים, שיער, לבוש, פרט חתימה]
- **כלי נגינה:** [גיטרה: סוג/צבע/גוף | פסנתר: כנף/זקוף, צבע] — קבוע, לא משתנה
- **סגנון (ביטוי מדויק, חוזר מילה במילה):**
  - תלת-מימד ריאליסטי: "photorealistic 3D render, PBR materials, cinematic lighting, 50mm"
  - תלת-מימד מונפש: "stylized 3D character, soft global illumination, appealing proportions"
  - 2D / סל: "clean 2D cel animation, bold line art, flat shading"
  - [או סגנון אחר — בחר אחד ושמור עליו]
- **פלטת צבעים:** [2–4 צבעים]
- **זוויות הירו:** ¾ מלפנים · פרופיל · תקריב ידיים

---

## פאנל [מספר] — סקשן [intro/verse/chorus] · זמן [start]–[end]

**סוג פאנל:** [establishing / performance-medium / hands-close-up / emotion]

### פרומפט (להדבקה ב-GPT / Gemini / Midjourney)
> [Character Sheet block מודבק מילה במילה] — [סוג שוט + זווית] —
> [פעולה: מנגן/מזמר/נשען] — [הוראת ידיים מדויקת מלמטה] — [תאורה] —
> [פלטה] — [מצב רוח].

### 🖐️ מיקום ידיים (מ-`hand_positions.py` — חובה לדיוק)
**גיטרה:**
- **יד שמאל (fretting):** [placement string, למשל: "barres fret 1 with index, ..."] — אקורד **[chord]**
- **יד ימין:** [strum/pick לפי הקצב — downstroke על ביט חזק]
- דיאגרמת פריטים:
```
[הדבק את ה-diagram מהסקריפט]
```

**פסנתר:**
- **יד ימין:** [placement, למשל: "finger 1 on A4, 3 on C5, 5 on E5"] — אקורד **[chord]**
- **יד שמאל:** [רגיסטר נמוך / בס לפי notes.json]

### 🎼 תנועת גוף (מסונכרנת לקצב)
- נדנוד/נטייה **על הביט**; לין-אין גדול יותר על build/drop
- **החלפת אקורד** נופלת על [timestamp] — היד מחליקה/משנה צורה בדיוק שם

### 🎯 Sync
- פאנל מתוזמן ל: [timestamp] ([role מה-sync_map])
- החלפת אקורד הבאה: [timestamp] → [next chord]

### כלי מומלץ
- **סטיל:** [GPT-4o / Gemini Imagen / Midjourney] — [סיבה]
- **הנפשה:** [Sora / Veo / Kling / Runway] מה-keyframe (image-to-video),
  עם תיאור התנועה: הפריטה, החלקת היד בהחלפת אקורד, נדנוד הגוף על הביט
