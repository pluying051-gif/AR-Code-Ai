# -*- coding: utf-8 -*-
"""AR Code.Ai - الواجهة الرسومية | © Ahmed Al-Obaidi (AR Code) | @ar.code.1"""
import queue
import threading
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext

from config import APP_NAME, DEVELOPER, INSTAGRAM, VERSION, get_api_key
from core import AREngine, load_file

BG, PANEL, FG, ACCENT, USER = "#0d1117", "#161b22", "#e6edf3", "#58a6ff", "#3fb950"


class App(tk.Tk):
    def __init__(self, engine: AREngine):
        super().__init__()
        self.eng, self.q, self.files, self.busy = engine, queue.Queue(), [], False
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("920x700")
        self.configure(bg=BG)

        top = tk.Frame(self, bg=PANEL)
        top.pack(fill="x")
        tk.Label(top, text=f"  {APP_NAME}", bg=PANEL, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(side="left", pady=8)
        self.search_var = tk.BooleanVar(value=engine.search)
        tk.Checkbutton(top, text="بحث انترنت", variable=self.search_var, command=self.toggle_search,
                       bg=PANEL, fg=FG, selectcolor=PANEL, activebackground=PANEL, activeforeground=FG).pack(side="right", padx=8)
        for txt, cmd in (("حفظ", self.save), ("مسح", self.clear)):
            tk.Button(top, text=txt, command=cmd, bg=BG, fg=FG, relief="flat", padx=10).pack(side="right", padx=3)

        self.chat = scrolledtext.ScrolledText(self, wrap="word", bg=BG, fg=FG, font=("Segoe UI", 11),
                                              relief="flat", padx=12, pady=10, state="disabled")
        self.chat.pack(fill="both", expand=True)
        self.chat.tag_config("user", foreground=USER, font=("Segoe UI", 11, "bold"))
        self.chat.tag_config("bot", foreground=ACCENT, font=("Segoe UI", 11, "bold"))
        self.chat.tag_config("sys", foreground="#8b949e")

        self.info = tk.Label(self, text="", bg=BG, fg="#8b949e", anchor="w")
        self.info.pack(fill="x", padx=10)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=10, pady=6)
        tk.Button(bottom, text="📎", command=self.attach, bg=PANEL, fg=FG, relief="flat", width=3).pack(side="left")
        self.box = tk.Text(bottom, height=3, bg=PANEL, fg=FG, insertbackground=FG, relief="flat",
                           font=("Segoe UI", 11), wrap="word")
        self.box.pack(side="left", fill="x", expand=True, padx=6)
        self.box.bind("<Return>", self.on_enter)
        self.send_btn = tk.Button(bottom, text="إرسال", command=self.send, bg=ACCENT, fg="black", relief="flat", padx=14)
        self.send_btn.pack(side="left")

        tk.Label(self, text=f"© {DEVELOPER} | Instagram: @{INSTAGRAM} | All Rights Reserved",
                 bg=BG, fg="#6e7681", font=("Segoe UI", 8)).pack(pady=(0, 6))

        self.write(f"{APP_NAME}: أهلاً! أني {APP_NAME} من تطوير {DEVELOPER}. اسألني أي شي أو أرفق صورة/ملف.\n\n", "bot")
        self.after(40, self.poll)

    # ── مساعدات ──
    def write(self, text, tag=None):
        self.chat.config(state="normal")
        self.chat.insert("end", text, tag)
        self.chat.see("end")
        self.chat.config(state="disabled")

    def on_enter(self, e):
        if e.state & 0x1:  # Shift+Enter = سطر جديد
            return None
        self.send()
        return "break"

    def toggle_search(self):
        self.eng.set_search(self.search_var.get())

    def attach(self):
        for p in filedialog.askopenfilenames(title="اختر ملفات"):
            try:
                self.files.append(load_file(p))
            except Exception as e:
                messagebox.showerror("خطأ", str(e))
        self.info.config(text="مرفقات: " + ", ".join(f[0] for f in self.files) if self.files else "")

    def clear(self):
        self.eng.reset(); self.files.clear(); self.info.config(text="")
        self.chat.config(state="normal"); self.chat.delete("1.0", "end"); self.chat.config(state="disabled")
        self.write("تم مسح المحادثة.\n\n", "sys")

    def save(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            initialfile=f"AR_Code_Ai_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.eng.export_text())

    # ── الإرسال ──
    def send(self):
        text = self.box.get("1.0", "end").strip()
        if self.busy or (not text and not self.files):
            return
        self.box.delete("1.0", "end")
        files, self.files = self.files, []
        self.info.config(text="")
        self.write("أنت: ", "user")
        self.write(text + (f"  [📎 {len(files)}]" if files else "") + "\n\n")
        self.write(f"{APP_NAME}: ", "bot")
        self.busy = True
        self.send_btn.config(state="disabled")
        threading.Thread(target=self.worker, args=(text, files), daemon=True).start()

    def worker(self, text, files):
        try:
            for part in self.eng.stream(text, files):
                self.q.put(("chunk", part))
            self.q.put(("chunk", self.eng.sources_text()))
        except Exception as e:
            self.q.put(("chunk", f"\n⚠️ خطأ: {e}"))
        self.q.put(("done", ""))

    def poll(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "chunk":
                    self.write(data)
                else:
                    self.write("\n\n"); self.busy = False; self.send_btn.config(state="normal")
        except queue.Empty:
            pass
        self.after(40, self.poll)


def main():
    key = get_api_key(interactive=False)
    if not key:
        root = tk.Tk(); root.withdraw()
        key = (simpledialog.askstring(APP_NAME, "ادخل مفتاح Gemini API:", show="*") or "").strip()
        root.destroy()
    if not key:
        return
    App(AREngine(api_key=key)).mainloop()


if __name__ == "__main__":
    main()
