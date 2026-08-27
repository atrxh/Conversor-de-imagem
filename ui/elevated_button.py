import customtkinter as ctk

class ElevatedButton(ctk.CTkFrame):
    def __init__(self, master, text="", command=None, width=120, height=38, depth=5,
                 font=None, fg_color="#25252C", hover_color="#303038",
                 depth_color="#0A0A0D", text_color="#FFFFFF", border_color=None,
                 border_width=1, **kwargs):
        initial_state = kwargs.pop("state", "normal")
        super().__init__(master, width=width, height=height + depth, fg_color="transparent", **kwargs)
        self._width = width
        self._height = height
        self._depth = depth
        self._command = command
        self._fg = fg_color
        self._hover = hover_color
        self._depth_color = depth_color
        self._text = text_color
        self._text_value = text
        self._border = border_color or fg_color
        self._border_width = border_width
        self._font = font
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.base = ctk.CTkFrame(self, width=width, height=height + depth, corner_radius=0,
                                 fg_color=depth_color, border_width=border_width,
                                 border_color=depth_color)
        self.base.grid(row=0, column=0, sticky="nsew")
        self.face = ctk.CTkButton(self, text=text, command=self._press, width=width,
                                  height=height, font=font, fg_color=fg_color,
                                  hover_color=hover_color, text_color=text_color,
                                  border_width=border_width, border_color=self._border,
                                  corner_radius=0)
        self.face.grid(row=0, column=0, sticky="nsew", pady=(0, depth))
        self.face.bind("<ButtonPress-1>", self._button_down, add="+")
        self.face.bind("<ButtonRelease-1>", self._button_up, add="+")
        self.face.configure(state=initial_state)

    def _press(self):
        if self._command:
            self._command()

    def _button_down(self, _event=None):
        self.face.grid_configure(pady=(self._depth, 0))

    def _button_up(self, _event=None):
        self.face.grid_configure(pady=(0, self._depth))

    def configure(self, **kwargs):
        mapping = {
            "fg_color": "_fg", "hover_color": "_hover", "text_color": "_text",
            "depth_color": "_depth_color", "border_color": "_border"
        }
        for key, attr in mapping.items():
            if key in kwargs:
                setattr(self, attr, kwargs.pop(key))
        if "text" in kwargs:
            self._text_value = kwargs.pop("text")
            self.face.configure(text=self._text_value)
        if "state" in kwargs:
            self.face.configure(state=kwargs.pop("state"))
        if "font" in kwargs:
            self.face.configure(font=kwargs.pop("font"))
        self.face.configure(fg_color=self._fg, hover_color=self._hover,
                            text_color=self._text, border_color=self._border)
        self.base.configure(fg_color=self._depth_color, border_color=self._depth_color)
        if kwargs:
            super().configure(**kwargs)

    def cget(self, attribute):
        if attribute == "text":
            return self.face.cget("text")
        if attribute == "state":
            return self.face.cget("state")
        return super().cget(attribute)

    def apply_theme(self, fg_color, hover_color, depth_color, text_color, border_color):
        self._fg = fg_color
        self._hover = hover_color
        self._depth_color = depth_color
        self._text = text_color
        self._border = border_color
        self.face.configure(fg_color=fg_color, hover_color=hover_color,
                            text_color=text_color, border_color=border_color)
        self.base.configure(fg_color=depth_color, border_color=depth_color)
