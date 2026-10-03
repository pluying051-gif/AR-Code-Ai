# AR Code.Ai 🤖

ذكاء اصطناعي متكامل بلغة Python يعتمد على Google Gemini.
An all-in-one AI assistant in Python powered by Google Gemini.

**Developer:** Ahmed Al-Obaidi (AR Code) | **Instagram:** [@ar.code.1](https://instagram.com/ar.code.1)

## المميزات | Features
- 💬 محادثة بذاكرة كاملة وردود تدريجية (Streaming)
- 🖼️ قراءة وتحليل الصور، PDF، الصوت، وملفات الكود
- 🌐 بحث مباشر بالانترنت مع عرض المصادر
- 🖥️ ثلاث واجهات: طرفية (CLI) • رسومية (GUI) • بوت تيليجرام

## التثبيت | Install
```bash
git clone https://github.com/USERNAME/AR-Code-Ai.git
cd AR-Code-Ai
pip install -r requirements.txt
cp .env.example .env      # ثم ضع مفتاحك داخل .env
```
مفتاح Gemini مجاني من: https://aistudio.google.com/apikey

## التشغيل | Run
```bash
python cli.py            # الطرفية
python gui.py            # الواجهة الرسومية
python telegram_bot.py   # بوت تيليجرام (يحتاج TELEGRAM_BOT_TOKEN من @BotFather)
```

## أوامر الطرفية
`/file <مسار>` `/search on|off` `/model <اسم>` `/clear` `/save` `/about` `/exit`

---
© Ahmed Al-Obaidi (AR Code) — All Rights Reserved.
