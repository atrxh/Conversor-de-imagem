import customtkinter as ctk
from config import THEMES

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.current = "dark"

    @property
    def colors(self):
        return THEMES[self.current]

    def toggle(self):
        self.current = "light" if self.current == "dark" else "dark"
        ctk.set_appearance_mode("Light" if self.current == "light" else "Dark")
        self.app.apply_theme()
