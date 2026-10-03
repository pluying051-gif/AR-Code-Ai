# -*- coding: utf-8 -*-
"""AR Code.Ai - واجهة الطرفية | © Ahmed Al-Obaidi (AR Code) | @ar.code.1"""
import sys
import datetime

from config import APP_NAME, DEVELOPER, INSTAGRAM, VERSION, get_api_key
from core import AREngine, load_file


class C:
    R = "\033[0m"; B = "\033[1m"; CY = "\033[96m"; G = "\033[92m"
    Y = "\033[93m"; RE = "\033[91m"; M = "\033[95m"


BANNER = f"""{C.CY}{C.B}
   ╔══════════════════════════════════════════════╗
   ║                AR Code.Ai  v{VERSION}                ║
   ╠══════════════════════════════════════════════╣
   ║  Developer : Ahmed Al-Obaidi (AR Code)       ║
   ║  Instagram : @{INSTAGRAM}                       ║
   ║  © All Rights Reserved                       ║
   ╚══════════════════════════════════════════════╝{C.R}
{C.Y}اكتب /help لعرض الأوامر{C.R}
"""

HELP = f"""{C.M}الأوامر:{C.R}
  /file <مسار>      إرفاق صورة/PDF/ملف كود للرسالة الجاية
  /search on|off    تشغيل أو ايقاف البحث بالانترنت
  /model <اسم>      تغيير الموديل (مثال: /model gemini-2.5-pro)
  /clear            مسح الذاكرة
  /save             حفظ المحادثة
  /about            معلومات المطور
  /exit             خروج
"""


def main():
    key = get_api_key()
    if not key:
        print("لازم مفتاح API."); sys.exit(1)
    eng = AREngine(api_key=key)
    files = []
    print(BANNER)

    while True:
        try:
            user = input(f"{C.G}{C.B}أنت ❯ {C.R}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{C.CY}مع السلامة! — {APP_NAME}{C.R}"); break
        if not user:
            continue

        if user.startswith("/"):
            cmd, *arg = user.split(maxsplit=1)
            arg = arg[0] if arg else ""
            cmd = cmd.lower()
            if cmd == "/exit": break
            elif cmd == "/help": print(HELP)
            elif cmd == "/about": print(f"{C.CY}{APP_NAME} v{VERSION}\nتطوير: {DEVELOPER}\nانستغرام: @{INSTAGRAM}{C.R}")
            elif cmd == "/clear": eng.reset(); files.clear(); print(f"{C.Y}تم مسح الذاكرة.{C.R}")
            elif cmd == "/search":
                eng.set_search(arg.lower() != "off")
                print(f"{C.Y}البحث بالانترنت: {'مشغّل' if eng.search else 'متوقف'}{C.R}")
            elif cmd == "/model":
                if arg: eng.set_model(arg); print(f"{C.Y}الموديل: {arg}{C.R}")
                else: print(f"الموديل الحالي: {eng.model}")
            elif cmd == "/file":
                try:
                    files.append(load_file(arg)); print(f"{C.Y}تم إرفاق: {files[-1][0]} — اكتب سؤالك الآن.{C.R}")
                except Exception as e:
                    print(f"{C.RE}{e}{C.R}")
            elif cmd == "/save":
                name = f"AR_Code_Ai_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
                with open(name, "w", encoding="utf-8") as f: f.write(eng.export_text())
                print(f"{C.G}تم الحفظ: {name}{C.R}")
            else:
                print(f"{C.RE}أمر غير معروف. اكتب /help{C.R}")
            continue

        print(f"{C.CY}{C.B}{APP_NAME} ❯ {C.R}", end="", flush=True)
        try:
            for part in eng.stream(user, files):
                print(part, end="", flush=True)
            print(eng.sources_text() + "\n")
            files.clear()
        except Exception as e:
            print(f"\n{C.RE}خطأ: {e}{C.R}\n")


if __name__ == "__main__":
    main()
