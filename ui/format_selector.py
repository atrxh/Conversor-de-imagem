import customtkinter as ctk


class FormatSelector(ctk.CTkFrame):
    def __init__(self, master, values, initial, font, command=None, **kwargs):
        super().__init__(master, corner_radius=0, border_width=1, **kwargs)
        self.values = values
        self.value = initial
        self.font = font
        self.command = command
        self.popup = None
        self.buttons = []
        self.colors = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.value_button = ctk.CTkButton(
            self,
            text=initial,
            font=font,
            anchor="w",
            corner_radius=0,
            border_width=0,
            command=self.toggle,
        )
        self.value_button.grid(row=0, column=0, sticky="nsew", padx=(1, 0), pady=1)

        self.arrow_button = ctk.CTkButton(
            self,
            text="▾",
            font=(font[0], font[1], "bold"),
            width=36,
            corner_radius=0,
            border_width=0,
            command=self.toggle,
        )
        self.arrow_button.grid(row=0, column=1, sticky="ns", padx=(0, 1), pady=1)

    def set(self, value):
        self.value = value
        self.value_button.configure(text=value)

    def get(self):
        return self.value

    def toggle(self):
        if self.popup is not None and self.popup.winfo_exists():
            self.close()
            return
        self.open()

    def open(self):
        self.popup = ctk.CTkToplevel(self)
        self.popup.overrideredirect(True)
        self.popup.transient(self.winfo_toplevel())
        self.popup.bind("<FocusOut>", self._focus_out)
        self.popup.bind("<Escape>", lambda _e: self.close())

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 3
        width = min(max(self.winfo_width(), 150), 190)
        height = len(self.values) * 28 + 2
        self.popup.geometry(f"{width}x{height}+{x}+{y}")

        self.panel = ctk.CTkFrame(self.popup, corner_radius=0, border_width=1)
        self.panel.pack(fill="both", expand=True)
        self.buttons.clear()

        for value in self.values:
            button = ctk.CTkButton(
                self.panel,
                text=value,
                font=self.font,
                anchor="w",
                height=27,
                corner_radius=0,
                border_width=0,
                command=lambda item=value: self.select(item),
            )
            button.pack(fill="x", padx=1, pady=0)
            self.buttons.append(button)

        self.apply_theme(self.colors)
        self.popup.focus_force()

    def select(self, value):
        self.set(value)
        self.close()
        if self.command:
            self.command(value)

    def close(self):
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = None

    def _focus_out(self, _event=None):
        if self.popup is not None:
            self.after(80, self.close)

    def apply_theme(self, colors=None):
        if colors is not None:
            self.colors = colors
        elif self.colors is None:
            return
        else:
            colors = self.colors

        self.configure(
            fg_color=colors["input"],
            border_color=colors["border_strong"],
        )
        self.value_button.configure(
            fg_color=colors["input"],
            hover_color=colors["surface_hover"],
            text_color=colors["text"],
        )
        self.arrow_button.configure(
            fg_color=colors["button"],
            hover_color=colors["button_hover"],
            text_color=colors["text"],
        )

        if self.popup is not None and self.popup.winfo_exists():
            self.panel.configure(
                fg_color=colors["card"],
                border_color=colors["border_strong"],
            )
            for button in self.buttons:
                button.configure(
                    fg_color=colors["card"],
                    hover_color=colors["surface_hover"],
                    text_color=colors["text"],
                )
