import customtkinter as ctk


class ElevatedButton:
    def __init__(self, parent, shadow_color, **kwargs):
        height = kwargs.get("height", 28)
        radius = kwargs.get("corner_radius", 5)
        self.frame = ctk.CTkFrame(
            parent,
            height=height + 4,
            corner_radius=radius + 1,
            fg_color=shadow_color,
        )
        self.frame.pack_propagate(False)

        self.button = ctk.CTkButton(
            self.frame,
            **kwargs,
        )
        self.button.place(x=0, y=0, relwidth=1, relheight=1)

    def pack(self, *args, **kwargs):
        return self.frame.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        return self.frame.grid(*args, **kwargs)

    def place(self, *args, **kwargs):
        return self.frame.place(*args, **kwargs)

    def configure(self, **kwargs):
        return self.button.configure(**kwargs)

    config = configure

    def cget(self, attribute):
        return self.button.cget(attribute)

    def set_shadow_color(self, color):
        self.frame.configure(fg_color=color)

    def winfo_children(self):
        return self.button.winfo_children()
