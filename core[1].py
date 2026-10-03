# -*- coding: utf-8 -*-
"""
AR Code.Ai - المحرك الرئيسي (ذاكرة + ملفات + صور + بحث انترنت)
© Ahmed Al-Obaidi (AR Code) | Instagram: @ar.code.1
"""
import mimetypes
from pathlib import Path

from google import genai
from google.genai import types

from config import APP_NAME, DEVELOPER, INSTAGRAM, MODEL

SYSTEM_PROMPT = f"""
أنت {APP_NAME}، مساعد ذكاء اصطناعي متقدم ومتكامل.
تم تطويرك وبرمجتك بواسطة المبرمج والمطور {DEVELOPER}، وحسابه على انستغرام @{INSTAGRAM}.
إذا سألك أحد من صنعك أو من طورك فجاوب بذلك بفخر.
قواعدك:
- رد بنفس لغة المستخدم وبأسلوب واضح ومفهوم.
- كن دقيقاً ومفصلاً عند الحاجة، ومختصراً في الأسئلة البسيطة.
- في البرمجة: اكتب كوداً نظيفاً وكاملاً وجاهزاً للنسخ مع شرح مبسط.
- عند تحليل الصور أو الملفات: وصف وحلل بدقة وأجب عن سؤال المستخدم.
- إذا لم تكن متأكداً من معلومة قل ذلك بصراحة ولا تخترع.
"""

TEXT_EXT = {
    ".txt", ".md", ".py", ".js", ".ts", ".json", ".csv", ".html", ".css", ".xml",
    ".yaml", ".yml", ".ini", ".log", ".java", ".c", ".cpp", ".cs", ".go", ".rs",
    ".php", ".sql", ".sh", ".bat", ".kt", ".swift", ".rb", ".toml",
}
MAX_BYTES = 18 * 1024 * 1024  # حد الملف المرفق


def load_file(path: str):
    """يرجع (الاسم, نوع الملف, البيانات)"""
    p = Path(path.strip().strip('"'))
    if not p.is_file():
        raise FileNotFoundError(f"الملف غير موجود: {p}")
    if p.stat().st_size > MAX_BYTES:
        raise ValueError("الملف كبير جداً (الحد 18 ميغا).")
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return (p.name, mime, p.read_bytes())


def make_part(name: str, mime: str, data: bytes) -> types.Part:
    ext = Path(name).suffix.lower()
    if ext in TEXT_EXT or mime.startswith("text/"):
        text = data.decode("utf-8", errors="replace")[:200_000]
        return types.Part.from_text(text=f"[محتوى الملف: {name}]\n{text}")
    if mime.startswith(("image/", "audio/", "video/")) or mime == "application/pdf":
        return types.Part.from_bytes(data=data, mime_type=mime)
    raise ValueError(f"نوع الملف غير مدعوم: {name} ({mime})")


class AREngine:
    def __init__(self, api_key=None, client=None, model=MODEL, search=True):
        self.client = client or genai.Client(api_key=api_key)
        self.model = model
        self.search = search
        self.sources = []
        self.chat = self._new_chat()

    def _config(self):
        tools = [types.Tool(google_search=types.GoogleSearch())] if self.search else None
        return types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT, temperature=0.7, tools=tools
        )

    def _new_chat(self, history=None):
        return self.client.chats.create(
            model=self.model, config=self._config(), history=history
        )

    # ── التحكم ──
    def reset(self):
        self.chat = self._new_chat()

    def set_model(self, model: str):
        self.model = model
        self.chat = self._new_chat(self.chat.get_history())

    def set_search(self, on: bool):
        self.search = on
        self.chat = self._new_chat(self.chat.get_history())

    # ── الإرسال ──
    def stream(self, text: str = "", files=None):
        """مولّد يرجع الرد قطعة قطعة. files = [(name, mime, bytes), ...]"""
        contents = [make_part(*f) for f in (files or [])]
        contents.append(text or "حلل المرفقات وأخبرني بالمهم فيها.")
        self.sources = []
        for chunk in self.chat.send_message_stream(contents):
            if chunk.text:
                yield chunk.text
            self._collect_sources(chunk)

    def ask(self, text: str = "", files=None) -> str:
        return "".join(self.stream(text, files))

    def _collect_sources(self, chunk):
        try:
            gm = chunk.candidates[0].grounding_metadata
            for g in (gm.grounding_chunks or []):
                if g.web and g.web.uri and g.web.uri not in [s[1] for s in self.sources]:
                    self.sources.append((g.web.title or g.web.uri, g.web.uri))
        except Exception:
            pass

    def sources_text(self) -> str:
        if not self.sources:
            return ""
        return "\n\nالمصادر:\n" + "\n".join(f"• {t}: {u}" for t, u in self.sources[:5])

    def export_text(self) -> str:
        lines = [f"{APP_NAME} | {DEVELOPER} | @{INSTAGRAM}", "=" * 50, ""]
        for m in self.chat.get_history():
            who = "أنت" if m.role == "user" else APP_NAME
            body = "".join(p.text or "" for p in m.parts)
            lines.append(f"[{who}]\n{body}\n")
        return "\n".join(lines)
