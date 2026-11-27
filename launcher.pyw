"""
SynapseOS Lite — Launcher
Double-click this file to start. No terminal needed.
"""

import subprocess
import sys
import os
import tkinter as tk
from tkinter import font

# ── find synapse_os.py next to this launcher ──────────
BASE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(BASE, "synapse_os.py")

# ══════════════════════════════════════════════════════
#  WINDOW SETUP
# ══════════════════════════════════════════════════════
root = tk.Tk()
root.title("SynapseOS Lite")
root.geometry("520x620")
root.resizable(False, False)
root.configure(bg="#0d0d0d")

# center on screen
root.update_idletasks()
x = (root.winfo_screenwidth()  - 520) // 2
y = (root.winfo_screenheight() - 620) // 2
root.geometry(f"520x620+{x}+{y}")

# ── fonts ─────────────────────────────────────────────
title_font   = font.Font(family="Consolas", size=20, weight="bold")
sub_font     = font.Font(family="Consolas", size=11)
gesture_font = font.Font(family="Consolas", size=12)
hint_font    = font.Font(family="Consolas", size=10)
btn_font     = font.Font(family="Consolas", size=14, weight="bold")

# ══════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════
tk.Label(root, text="🖐  SynapseOS Lite",
         font=title_font, bg="#0d0d0d", fg="#00e676").pack(pady=(28, 4))

tk.Label(root, text="Control your PC with hand gestures — no mouse needed",
         font=hint_font, bg="#0d0d0d", fg="#555555").pack(pady=(0, 22))

# ── divider ───────────────────────────────────────────
tk.Frame(root, height=1, bg="#1e1e1e").pack(fill="x", padx=30)

# ══════════════════════════════════════════════════════
#  GESTURE CARDS
# ══════════════════════════════════════════════════════
gestures = [
    ("✊",  "FIST",      "Lock / Unlock the system",          "#ef5350"),
    ("☝️",  "1 FINGER",  "Move mouse cursor",                 "#42a5f5"),
    ("🤏",  "PINCH",     "Left click  (thumb close to index)","#ab47bc"),
    ("✌️",  "2 FINGERS", "Scroll — move hand up or down",     "#26c6da"),
    ("🤚",  "3 FINGERS", "Volume — raise = louder",           "#ffa726"),
]

card_frame = tk.Frame(root, bg="#0d0d0d")
card_frame.pack(padx=30, pady=18, fill="x")

for emoji, name, desc, color in gestures:
    row = tk.Frame(card_frame, bg="#141414", pady=10)
    row.pack(fill="x", pady=4)

    # left colored bar
    tk.Frame(row, width=4, bg=color).pack(side="left", fill="y", padx=(10, 12))

    # emoji
    tk.Label(row, text=emoji, font=font.Font(size=18),
             bg="#141414", width=2).pack(side="left")

    # text block
    text_block = tk.Frame(row, bg="#141414")
    text_block.pack(side="left", padx=8)

    tk.Label(text_block, text=name, font=font.Font(family="Consolas", size=11, weight="bold"),
             bg="#141414", fg=color, anchor="w").pack(anchor="w")
    tk.Label(text_block, text=desc, font=hint_font,
             bg="#141414", fg="#888888", anchor="w").pack(anchor="w")

# ── divider ───────────────────────────────────────────
tk.Frame(root, height=1, bg="#1e1e1e").pack(fill="x", padx=30, pady=(8, 0))

# ── tip ───────────────────────────────────────────────
tk.Label(root, text="💡  Hold each gesture steady for 0.2s before it activates",
         font=hint_font, bg="#0d0d0d", fg="#444444").pack(pady=(10, 4))
tk.Label(root, text="🎥  Make sure your webcam is connected and lit",
         font=hint_font, bg="#0d0d0d", fg="#444444").pack(pady=(0, 18))

# ══════════════════════════════════════════════════════
#  START BUTTON
# ══════════════════════════════════════════════════════
status_var = tk.StringVar(value="")

def start():
    if not os.path.exists(SCRIPT):
        status_var.set("❌  synapse_os.py not found next to this launcher")
        status_label.config(fg="#ef5350")
        return

    btn.config(state="disabled", text="  Starting…  ", bg="#1a1a1a", fg="#444")
    status_var.set("🟢  Camera window opening — press Q in it to quit")
    status_label.config(fg="#00e676")
    root.update()

    try:
        subprocess.Popen([sys.executable, SCRIPT])
    except Exception as e:
        status_var.set(f"❌  Error: {e}")
        status_label.config(fg="#ef5350")
        btn.config(state="normal", text="  ▶   START", bg="#00e676", fg="#0d0d0d")

btn = tk.Button(
    root, text="  ▶   START",
    font=btn_font,
    bg="#00e676", fg="#0d0d0d",
    activebackground="#00c853", activeforeground="#0d0d0d",
    relief="flat", padx=40, pady=14,
    cursor="hand2",
    command=start,
)
btn.pack(pady=(0, 10))

status_label = tk.Label(root, textvariable=status_var,
                        font=hint_font, bg="#0d0d0d", fg="#00e676")
status_label.pack()

# ── quit hint ─────────────────────────────────────────
tk.Label(root, text="Press  Q  inside the camera window to stop",
         font=hint_font, bg="#0d0d0d", fg="#333333").pack(pady=(12, 0))

root.mainloop()
