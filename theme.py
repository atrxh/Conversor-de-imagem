import customtkinter as ctk

THEMES = {
    "dark": {
        "bg": "#0B0B0E", "card": "#14141B", "card_alt": "#111117",
        "surface": "#1A1A24", "surface_hover": "#222230", "list_bg": "#0F0F15",
        "row": "#181821", "header": "#101017", "border": "#2A2A38",
        "border_strong": "#3A3A4D", "badge": "#262636", "text": "#EDEDF2",
        "muted": "#828292", "muted_2": "#686879", "disabled": "#4F4F5B",
        "danger_hover": "#3A2025", "button": "#22222E", "button_hover": "#2D2D3F",
        "input": "#111117", "scroll": "#22222E", "scroll_hover": "#343448",
        "button_border": "#444458", "button_shadow": "#08080B", "accent_shadow": "#5B21B6",
    },
    "light": {
        "bg": "#F4F4F7", "card": "#FFFFFF", "card_alt": "#FAFAFC",
        "surface": "#F1F1F6", "surface_hover": "#E1E1EA", "list_bg": "#F7F7FA",
        "row": "#FFFFFF", "header": "#EEEEF4", "border": "#B8B9C8",
        "border_strong": "#9FA1B2", "badge": "#E2E2EA", "text": "#24242E",
        "muted": "#626275", "muted_2": "#777789", "disabled": "#A0A0AD",
        "danger_hover": "#F2DDE1", "button": "#D4D4DE", "button_hover": "#C8C8D4",
        "input": "#FFFFFF", "scroll": "#D5D5DF", "scroll_hover": "#BDBDCA",
        "button_border": "#9697A8", "button_shadow": "#A8A9B6", "accent_shadow": "#6D28D9",
    },
}


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
        return self.current
