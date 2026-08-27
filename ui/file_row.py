from pathlib import Path
import customtkinter as ctk

from config import FONT_BADGE, FONT_ROW


class FileRow:
    def __init__(self, app, parent, path):
        self.app = app
        self.path = path
        self.var = ctk.StringVar(value=app.custom_names.get(path, Path(path).stem))

        self.frame = ctk.CTkFrame(parent, corner_radius=4, height=39, border_width=0)
        self.frame.pack(fill="x", padx=4, pady=2)
        self.frame.pack_propagate(False)

        ext = Path(path).suffix.replace(".", "").upper() or "IMG"
        self.badge = ctk.CTkLabel(self.frame, text=f" {ext} ", font=FONT_BADGE, corner_radius=3, width=42)
        self.badge.pack(side="left", padx=(6, 7), pady=5)

        self.entry = ctk.CTkEntry(
            self.frame,
            textvariable=self.var,
            font=FONT_ROW,
            border_width=0,
            corner_radius=3,
            justify="left",
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=1, pady=3)
        self.entry.bind("<FocusOut>", self.save_name)
        self.entry.bind("<Return>", self.save_name)

        self.remove = ctk.CTkButton(
            self.frame,
            text="✕",
            width=26,
            height=26,
            font=("Segoe UI", 11, "bold"),
            corner_radius=5,
            border_width=2,
            command=self.remove_row,
        )
        self.remove.pack(side="right", padx=(3, 4), pady=4)
        self.apply_theme()

    def save_name(self, _event=None):
        name = self.var.get().strip() or Path(self.path).stem
        name = Path(name).stem or Path(self.path).stem
        self.var.set(name)
        self.app.custom_names[self.path] = name

    def remove_row(self):
        self.save_name()
        self.app.remove_file(self.path)

    def apply_theme(self):
        c = self.app.theme.colors
        self.frame.configure(fg_color=c["row"], border_width=0)
        self.badge.configure(fg_color=c["badge"], text_color=c["text"], border_width=0)
        self.entry.configure(fg_color=c["input"], text_color=c["text"], placeholder_text_color=c["muted_2"], border_width=0)
        self.remove.configure(fg_color="transparent", hover_color=c["danger_hover"], text_color=c["muted"], border_width=0)
