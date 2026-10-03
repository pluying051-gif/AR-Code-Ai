# -*- coding: utf-8 -*-
"""AR Code.Ai - الإعدادات | © Ahmed Al-Obaidi (AR Code) | Instagram: @ar.code.1"""
import os
import getpass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

APP_NAME = "AR Code.Ai"
DEVELOPER = "Ahmed Al-Obaidi (AR Code)"
INSTAGRAM = "ar.code.1"
VERSION = "2.0"
MODEL = os.getenv("AR_MODEL", "gemini-2.5-flash")


def get_api_key(interactive: bool = True) -> str:
    """يقرأ المفتاح من GEMINI_API_KEY أو ملف .env، وإذا ما لقاه يسألك بدون ما يظهر."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key and interactive:
        key = getpass.getpass("ادخل مفتاح Gemini API (ما راح يظهر وانت تكتبه): ").strip()
    return key
