import os
import sys
import tempfile
import threading
import subprocess
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw

from config import (
    ACCENT, ACCENT_HOVER, DANGER, FONT_HUD, FONT_SMALL, FONT_SMALL_BOLD,
    FONT_SUBTITLE, FONT_TITLE, IMAGE_TYPES, SUCCESS, APP_NAME, APP_VERSION, ICON_NAME
)
from core.converter import ImageConverter
from theme import THEMES, ThemeManager
from ui.file_row import FileRow
from ui.elevated_button import ElevatedButton

class PixelShiftApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1180x760")
        self.minsize(1040, 700)
        self.resizable(True, True)

        self.theme = ThemeManager(self)
        self.files = []
        self.custom_names = {}
        self.rows = {}
        self.cancel_event = threading.Event()
        self.converter = ImageConverter()
        self.destination = None
        self.conversion_running = False

        self.set_window_icon()
        self.configure(fg_color=THEMES["dark"]["bg"])
        self._build_ui()
        self.apply_theme()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=42)
        self.grid_columnconfigure(1, weight=58)
        self.grid_rowconfigure(0, weight=1)

        self.left = ctk.CTkFrame(self, fg_color="transparent")
        self.left.grid(
            row=0, column=0, padx=(30, 15), pady=25, sticky="nsew"
        )

        self.brand_tag = ctk.CTkLabel(
            self.left, text="CORE ENGINE v2.4",
            font=FONT_HUD, anchor="w"
        )
        self.brand_tag.pack(fill="x", pady=(0, 2))

        self.title_label = ctk.CTkLabel(
            self.left, text=APP_NAME, font=FONT_TITLE, anchor="w"
        )
        self.title_label.pack(fill="x", pady=(0, 10))

        self.description = ctk.CTkLabel(
            self.left,
            text="Conversor de alto desempenho para imagens em lote.\nProcessamento 100% local.",
            font=FONT_SUBTITLE,
            justify="left",
            anchor="w",
        )
        self.description.pack(fill="x", pady=(0, 20))

        self.info_card = ctk.CTkFrame(
            self.left, corner_radius=7, border_width=1
        )
        self.info_card.pack(fill="x", pady=(0, 15))

        self.info_header = ctk.CTkLabel(
            self.info_card,
            text="ESPECIFICAÇÕES DO SISTEMA",
            font=FONT_HUD,
            anchor="w",
        )
        self.info_header.pack(fill="x", padx=15, pady=(13, 8))

        specs = [
            ("Formatos aceitos:", "PNG, JPG, WEBP, BMP, GIF"),
            ("Modo de Conversão:", "Paralelo / Lote"),
            ("Tratamento Alpha:", "Auto-RGB (Fundo Branco)"),
        ]
        self.spec_labels = []
        for label, value in specs:
            row = ctk.CTkFrame(self.info_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=5)
            l1 = ctk.CTkLabel(row, text=label, font=FONT_SUBTITLE, anchor="w")
            l1.pack(side="left")
            l2 = ctk.CTkLabel(row, text=value, font=FONT_HUD, anchor="e")
            l2.pack(side="right")
            self.spec_labels.extend([l1, l2])

        ctk.CTkFrame(self.info_card, height=10, fg_color="transparent").pack()

        self.right = ctk.CTkFrame(
            self, corner_radius=8, border_width=1
        )
        self.right.grid(
            row=0, column=1, padx=(15, 30), pady=25, sticky="nsew"
        )

        self.hud = ctk.CTkFrame(self.right, height=42, corner_radius=0)
        self.hud.pack(fill="x")
        self.hud.pack_propagate(False)

        self.hud_title = ctk.CTkLabel(
            self.hud, text=" PAINEL DE EXECUÇÃO",
            font=FONT_HUD, anchor="w"
        )
        self.hud_title.pack(side="left", padx=15)

        self.theme_button = ElevatedButton(
            self.hud,
            shadow_color=THEMES["dark"]["button_shadow"],
            text="☀  TEMA CLARO",
            command=self.toggle_theme,
            font=("Segoe UI", 10, "bold"),
            width=158,
            height=29,
            corner_radius=5,
        )
        self.theme_button.pack(side="right", padx=(4, 10), pady=7)

        self.ready = ctk.CTkLabel(
            self.hud, text="● READY", font=FONT_HUD
        )
        self.ready.pack(side="right", padx=15)

        self.body = ctk.CTkFrame(self.right, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=20, pady=13)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(2, weight=1, minsize=150)

        self.selection_header = self._section_header(self.body, "1. SELEÇÃO DE ARQUIVOS")
        self.selection_header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.clear_button = ElevatedButton(self.selection_header, shadow_color=THEMES["dark"]["button_shadow"], text="Limpar Fila", command=self.clear_queue, font=FONT_SMALL, width=78, height=24, corner_radius=4)
        self.clear_button.pack(side="right")

        self.add_button = ElevatedButton(self.body, shadow_color=THEMES["dark"]["button_shadow"], text="+ ADICIONAR IMAGENS", command=self.select_images, font=FONT_HUD, height=36, corner_radius=6, border_width=2)
        self.add_button.grid(row=1, column=0, sticky="ew", pady=(0, 7))

        self.file_list = ctk.CTkScrollableFrame(self.body, height=175, corner_radius=4, border_width=1)
        self.file_list.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        self.empty_label = ctk.CTkLabel(self.file_list, text="Nenhum arquivo na fila.", font=FONT_SUBTITLE)
        self.empty_label.pack(pady=42)

        self.rename_hint = ctk.CTkLabel(self.body, text="💡 Dica: depois de adicionar uma imagem, clique no nome para renomeá-la antes da conversão.", font=FONT_SMALL, justify="left", anchor="w", wraplength=700)
        self.rename_hint.grid(row=3, column=0, sticky="ew", pady=(0, 9))

        self.format_header = self._section_header(self.body, "2. FORMATO DESTINO")
        self.format_header.grid(row=4, column=0, sticky="ew", pady=(0, 5))
        self.folder_button = ElevatedButton(self.format_header, shadow_color=THEMES["dark"]["button_shadow"], text="📁  Abrir pasta de conversões", command=self.open_conversion_folder, font=("Segoe UI", 10), width=178, height=28, corner_radius=5)
        self.folder_button.pack(side="right")

        self.format_menu = ctk.CTkOptionMenu(self.body, values=["PNG", "JPEG", "WEBP", "BMP", "GIF"], font=FONT_HUD, height=36, corner_radius=4)
        self.format_menu.set("PNG")
        self.format_menu.grid(row=5, column=0, sticky="ew", pady=(0, 11))

        self.progress_header = self._section_header(self.body, "3. PROGRESSO DA OPERAÇÃO")
        self.progress_header.grid(row=6, column=0, sticky="ew", pady=(0, 5))
        self.progress = ctk.CTkProgressBar(self.body, height=7, corner_radius=2)
        self.progress.set(0)
        self.progress.grid(row=7, column=0, sticky="ew", pady=(0, 6))

        self.status = ctk.CTkLabel(self.body, text="Aguardando início...", font=FONT_SUBTITLE, anchor="w")
        self.status.grid(row=8, column=0, sticky="ew", pady=(0, 8))

        self.convert_button = ElevatedButton(self.body, shadow_color=THEMES["dark"]["accent_shadow"], text="INICIAR CONVERSÃO", command=self.start_conversion, font=FONT_HUD, height=42, corner_radius=6)
        self.convert_button.grid(row=9, column=0, sticky="ew", pady=(0, 6))
        self.cancel_button = ElevatedButton(self.body, shadow_color=THEMES["dark"]["button_shadow"], text="CANCELAR", command=self.cancel_conversion, font=FONT_SMALL_BOLD, height=28, corner_radius=4, state="disabled")
        self.cancel_button.grid(row=10, column=0, sticky="ew")

    def _section_header(self, parent, text):
        frame = ctk.CTkFrame(parent, fg_color="transparent", height=25)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_propagate(False)

        accent = ctk.CTkFrame(frame, width=3, height=15, corner_radius=1)
        accent.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="w")

        label = ctk.CTkLabel(
            frame, text=text, font=FONT_HUD, anchor="w"
        )
        label.grid(row=0, column=1, sticky="w")
        return frame

    def toggle_theme(self):
        self.theme.toggle()

    def apply_theme(self):
        """Atualiza apenas widgets existentes; nenhuma reconstrução da fila."""
        c = self.theme.colors

        self.configure(fg_color=c["bg"])
        self.right.configure(
            fg_color=c["card"],
            border_color=c["border_strong"],
        )
        self.info_card.configure(
            fg_color=c["card"],
            border_color=c["border_strong"],
        )
        self.hud.configure(fg_color=c["header"])
        self.body.configure(fg_color="transparent")

        for widget in [self.brand_tag, self.description, self.info_header,
                       self.title_label, self.hud_title, self.rename_hint,
                       self.status]:
            widget.configure(text_color=c["muted"] if widget in
                             [self.brand_tag, self.description, self.rename_hint,
                              self.status]
                             else c["text"])

        self.title_label.configure(text_color=c["text"])
        self.hud_title.configure(text_color=c["text"])
        self.info_header.configure(text_color=c["text"])
        for i, widget in enumerate(self.spec_labels):
            widget.configure(
                text_color=c["muted"] if i % 2 == 0 else c["text"]
            )

        self.ready.configure(text_color=SUCCESS)

        self.theme_button.configure(
            text="☾   TEMA ESCURO" if self.theme.current == "light" else "☀   TEMA CLARO",
            fg_color=c["button"],
            hover_color=c["button_hover"],
            border_width=2,
            border_color=c["button_border"],
            text_color=c["text"],
        )
        self.theme_button.set_shadow_color(c["button_shadow"])
        self.clear_button.configure(
            fg_color=c["button"],
            hover_color=c["button_hover"],
            border_width=2,
            border_color=c["button_border"],
            text_color=c["muted"],
        )
        self.clear_button.set_shadow_color(c["button_shadow"])
        self.folder_button.configure(
            fg_color=c["button"],
            hover_color=c["button_hover"],
            border_width=2,
            border_color=c["button_border"],
            text_color=c["text"],
        )
        self.folder_button.set_shadow_color(c["button_shadow"])
        self.add_button.configure(
            fg_color=c["button"],
            hover_color=c["button_hover"],
            border_width=2,
            border_color=c["button_border"],
            text_color=c["text"],
        )
        self.add_button.set_shadow_color(c["button_shadow"])
        self.format_menu.configure(
            fg_color=c["surface"],
            button_color=c["button"],
            button_hover_color=c["button_hover"],
            dropdown_fg_color=c["card"],
            dropdown_hover_color=c["surface_hover"],
            dropdown_text_color=c["text"],
            text_color=c["text"],
        )
        self.progress.configure(
            fg_color=c["surface"],
            progress_color=ACCENT,
        )
        self.cancel_button.configure(
            fg_color=c["button"],
            hover_color=c["danger_hover"],
            border_width=2,
            border_color=c["button_border"],
            text_color=c["muted"],
        )
        self.cancel_button.set_shadow_color(c["button_shadow"])
        self.convert_button.configure(
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            border_width=3,
            border_color="#5B21B6",
            text_color="#FFFFFF",
        )
        self.convert_button.set_shadow_color(c["accent_shadow"])

        self._apply_section_accents(c)
        self._apply_file_list_theme(c)

    def _apply_section_accents(self, c):
        for header in [self.selection_header, self.format_header,
                       self.progress_header]:
            for child in header.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    child.configure(fg_color=ACCENT)

    def _apply_file_list_theme(self, c):
        self.file_list.configure(
            fg_color=c["list_bg"],
            border_color=c["border_strong"],
            scrollbar_button_color=c["scroll"],
            scrollbar_button_hover_color=c["scroll_hover"],
        )
        self.empty_label.configure(text_color=c["muted"])

        for row in self.rows.values():
            row.apply_theme()

    def set_window_icon(self):
        try:
            base = getattr(
                sys, "_MEIPASS",
                os.path.dirname(os.path.abspath(__file__))
            )
            icon = os.path.join(base, ICON_NAME)

            if os.path.exists(icon):
                self.iconbitmap(icon)
                return

            fallback = os.path.join(
                tempfile.gettempdir(), "pixelshift_icon.ico"
            )
            sizes = [16, 24, 32, 48, 64, 128, 256]
            images = []

            for size in sizes:
                img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                s = size
                d.rounded_rectangle(
                    [s*.05, s*.05, s*.95, s*.95],
                    radius=s*.20,
                    fill=(20, 20, 27, 255),
                )
                purple = (139, 92, 246, 255)
                white = (237, 237, 242, 255)
                d.rectangle([s*.25, s*.25, s*.43, s*.43], fill=purple)
                d.rectangle([s*.50, s*.25, s*.68, s*.43], fill=white)
                d.rectangle([s*.25, s*.50, s*.43, s*.68], fill=white)
                d.rectangle([s*.50, s*.50, s*.78, s*.78], fill=purple)
                images.append(img)

            images[-1].save(
                fallback,
                format="ICO",
                sizes=[(s, s) for s in sizes],
            )
            self.iconbitmap(fallback)
        except Exception:
            pass

    def select_images(self):
        types = [
            ("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"),
            ("Todos os arquivos", "*.*"),
        ]
        paths = filedialog.askopenfilenames(filetypes=types)
        if not paths:
            return

        for path in paths:
            if path not in self.files:
                self.files.append(path)
                self.custom_names[path] = Path(path).stem

        self.progress.set(0)
        self.render_file_list()

    def render_file_list(self):
        for row in self.rows.values():
            row.frame.destroy()
        self.rows.clear()

        if not self.files:
            self.empty_label.pack(pady=42)
            self.status.configure(
                text="Aguardando início...",
                text_color=self.theme.colors["muted"],
            )
            return

        self.empty_label.pack_forget()
        for path in self.files:
            row = FileRow(self, self.file_list, path)
            self.rows[path] = row

        self.apply_theme()
        self.status.configure(
            text=f"{len(self.files)} arquivo(s) pronto(s). "
                 "Edite os nomes diretamente na lista.",
            text_color=SUCCESS,
        )

    def remove_file(self, path):
        if path in self.files:
            self.files.remove(path)
            self.custom_names.pop(path, None)
            self.render_file_list()

    def clear_queue(self):
        if self.conversion_running:
            return
        self.files.clear()
        self.custom_names.clear()
        self.render_file_list()
        self.progress.set(0)

    def get_conversion_folder(self):
        folder = Path.home() / "Downloads" / "Conversões"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def open_conversion_folder(self):
        folder = str(self.get_conversion_folder())
        try:
            os.startfile(folder)
        except AttributeError:
            if sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])

    def start_conversion(self):
        if self.conversion_running:
            return

        if not self.files:
            messagebox.showwarning(
                "ATENÇÃO",
                "Selecione ao menos um arquivo de imagem.",
            )
            return

        files = list(self.files)
        names = {
            path: self.custom_names.get(path, Path(path).stem)
            for path in files
        }
        fmt = self.format_menu.get().lower()
        destination = self.get_conversion_folder()

        self.cancel_event.clear()
        self.conversion_running = True
        self.destination = destination

        self.add_button.configure(state="disabled")
        self.clear_button.configure(state="disabled")
        self.convert_button.configure(
            state="disabled", text="CONVERTENDO..."
        )
        self.cancel_button.configure(state="normal")
        self.ready.configure(text="● PROCESSANDO", text_color=ACCENT)
        self.progress.set(0)

        threading.Thread(
            target=self._process_batch,
            args=(files, names, destination, fmt),
            daemon=True,
        ).start()

    def _process_batch(self, files, names, destination, fmt):
        def progress_callback(current, total, filename):
            self.after(0, self.update_progress, current, total, filename)

        total, success, errors = self.converter.convert_batch(
            files, names, destination, fmt, self.cancel_event, progress_callback
        )
        self.after(0, self.finish_conversion, total, success, errors)

    def update_progress(self, current, total, filename):
        value = current / total
        self.progress.set(value)
        self.status.configure(
            text=f"Processando: {current}/{total} "
                 f"({int(value * 100)}%) — {filename}",
            text_color=self.theme.colors["text"],
        )

    def cancel_conversion(self):
        if not self.conversion_running:
            return

        self.cancel_event.set()
        self.cancel_button.configure(state="disabled")
        self.status.configure(
            text="Cancelando...",
            text_color=DANGER,
        )

    def finish_conversion(self, total, success, errors):
        cancelled = self.cancel_event.is_set()
        self.conversion_running = False

        self.add_button.configure(state="normal")
        self.clear_button.configure(state="normal")
        self.convert_button.configure(
            state="normal", text="INICIAR CONVERSÃO"
        )
        self.cancel_button.configure(state="disabled")

        if cancelled:
            self.ready.configure(
                text="● CANCELADO", text_color=DANGER
            )
            self.status.configure(
                text=f"Cancelado — {len(success)} de {total} concluídas.",
                text_color=self.theme.colors["muted"],
            )
            return

        self.progress.set(1)
        self.ready.configure(text="● READY", text_color=SUCCESS)
        self.status.configure(
            text=f"Concluído — {len(success)} de {total} convertidas.",
            text_color=SUCCESS,
        )

        if errors:
            details = "\n".join(
                f"• {Path(path).name} — {error}"
                for path, error in errors[:10]
            )
            if len(errors) > 10:
                details += f"\n... e mais {len(errors) - 10} erro(s)."

            messagebox.showwarning(
                "CONCLUÍDO COM ERROS",
                f"{len(success)} convertidas e "
                f"{len(errors)} falharam.\n\n{details}",
            )
        else:
            messagebox.showinfo(
                "CONCLUÍDO",
                f"Processamento finalizado!\n"
                f"{len(success)} de {total} imagens convertidas.",
            )
