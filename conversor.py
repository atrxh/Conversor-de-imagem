import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

ctk.set_appearance_mode("Dark")

class CyberConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("IMAGE CONVERTER // TERMINAL")
        self.geometry("850x480")
        self.resizable(False, False)
        self.configure(fg_color="#121212")

        self.caminhos_arquivos = []

        # Definição do Estilo
        self.FONT_MAIN = ("Consolas", 12)
        self.FONT_BOLD = ("Consolas", 12, "bold")
        self.FONT_HEADER = ("Consolas", 24, "bold")
        self.FONT_METRIC = ("Consolas", 10)

        self.COLOR_BG = "#121212"
        self.COLOR_CARD = "#1a1a1a"
        self.COLOR_BORDER = "#2e2e2e"
        self.COLOR_ACCENT = "#ff9d00"  # Laranja neon/âmbar
        self.COLOR_TEXT_MUTED = "#888888"

        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)

        # -----------------------------------------------------------------
        # PAINEL ESQUERDO (HERO / DASHBOARD)
        # -----------------------------------------------------------------
        self.frame_hero = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_hero.grid(row=0, column=0, padx=(30, 15), pady=30, sticky="nsew")

        self.lbl_hero_top = ctk.CTkLabel(
            self.frame_hero, 
            text="SISTEMA DE CONVERSÃO v1.0", 
            font=self.FONT_BOLD, 
            text_color=self.COLOR_ACCENT,
            anchor="w"
        )
        self.lbl_hero_top.pack(fill="x", pady=(10, 5))

        self.lbl_hero_title = ctk.CTkLabel(
            self.frame_hero, 
            text="CONVERTA\nSUAS IMAGENS\nEM SEGUNDOS", 
            font=self.FONT_HEADER, 
            text_color="white",
            justify="left",
            anchor="w"
        )
        self.lbl_hero_title.pack(fill="x", pady=(0, 15))

        self.lbl_hero_sub = ctk.CTkLabel(
            self.frame_hero, 
            text="PROCESSAMENTO LOCAL RÁPIDO. SELECIONE OS ARQUIVOS E ESCOLHA O FORMATO ALVO.", 
            font=self.FONT_METRIC, 
            text_color=self.COLOR_TEXT_MUTED,
            justify="left",
            wraplength=320,
            anchor="w"
        )
        self.lbl_hero_sub.pack(fill="x", pady=(0, 20))

        # Métricas no rodapé esquerdo
        self.frame_metrics = ctk.CTkFrame(self.frame_hero, fg_color="transparent")
        self.frame_metrics.pack(side="bottom", fill="x")

        self.lbl_metrics = ctk.CTkLabel(
            self.frame_metrics, 
            text="+100% OFFLINE   •   5 FORMATOS   •   LOTE", 
            font=self.FONT_BOLD, 
            text_color=self.COLOR_ACCENT,
            anchor="w"
        )
        self.lbl_metrics.pack(fill="x")

        # -----------------------------------------------------------------
        # PAINEL DIREITO (CONTROLES / HUD CONTAINER)
        # -----------------------------------------------------------------
        self.card_main = ctk.CTkFrame(
            self, 
            fg_color=self.COLOR_CARD, 
            border_width=1, 
            border_color=self.COLOR_BORDER,
            corner_radius=2
        )
        self.card_main.grid(row=0, column=1, padx=(15, 30), pady=30, sticky="nsew")
        self.card_main.grid_columnconfigure(0, weight=1)

        # Cabeçalho do HUD
        self.frame_hud_top = ctk.CTkFrame(
            self.card_main, 
            fg_color="#161616", 
            corner_radius=0, 
            border_width=1, 
            border_color=self.COLOR_BORDER
        )
        self.frame_hud_top.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            self.frame_hud_top, 
            text=" PAINEL DE CONTROLE", 
            font=self.FONT_BOLD, 
            text_color=self.COLOR_ACCENT
        ).pack(side="left", padx=10, pady=8)

        ctk.CTkLabel(
            self.frame_hud_top, 
            text="● AO VIVO ", 
            font=self.FONT_METRIC, 
            text_color="#ff9d00"
        ).pack(side="right", padx=10, pady=8)

        # Conteúdo do HUD
        self.frame_hud_content = ctk.CTkFrame(self.card_main, fg_color="transparent")
        self.frame_hud_content.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.frame_hud_content.grid_columnconfigure(0, weight=1)

        # 1. Seleção
        self.btn_selecionar = ctk.CTkButton(
            self.frame_hud_content, 
            text="> CARREGAR ARQUIVOS", 
            command=self.selecionar_imagens,
            font=self.FONT_BOLD,
            fg_color="transparent",
            hover_color="#252525",
            border_width=1,
            border_color=self.COLOR_ACCENT,
            text_color=self.COLOR_ACCENT,
            corner_radius=2,
            height=38
        )
        self.btn_selecionar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.lbl_arquivos_info = ctk.CTkLabel(
            self.frame_hud_content,
            text="ARQUIVOS SELECIONADOS: 0",
            font=self.FONT_METRIC,
            text_color=self.COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_arquivos_info.grid(row=1, column=0, sticky="w", pady=(0, 12))

        # Divisor
        ctk.CTkFrame(self.frame_hud_content, height=1, fg_color=self.COLOR_BORDER).grid(row=2, column=0, sticky="ew", pady=(0, 12))

        # 2. Formato de Saída
        self.frame_fmt = ctk.CTkFrame(self.frame_hud_content, fg_color="transparent")
        self.frame_fmt.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        
        ctk.CTkLabel(
            self.frame_fmt, 
            text="FORMATO ALVO:", 
            font=self.FONT_BOLD, 
            text_color="white"
        ).pack(side="left", padx=(0, 10))

        self.combo_formato = ctk.CTkOptionMenu(
            self.frame_fmt, 
            values=["JPEG", "PNG", "WEBP", "BMP", "GIF"],
            font=self.FONT_BOLD,
            fg_color="#222222",
            button_color=self.COLOR_BORDER,
            button_hover_color="#333333",
            dropdown_fg_color="#222222",
            corner_radius=2,
            width=110
        )
        self.combo_formato.set("JPEG")
        self.combo_formato.pack(side="left")

        # Divisor
        ctk.CTkFrame(self.frame_hud_content, height=1, fg_color=self.COLOR_BORDER).grid(row=4, column=0, sticky="ew", pady=(0, 12))

        # 3. Progresso
        self.progresso = ctk.CTkProgressBar(
            self.frame_hud_content, 
            height=6, 
            progress_color=self.COLOR_ACCENT, 
            fg_color="#222222",
            corner_radius=0
        )
        self.progresso.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        self.progresso.set(0)

        self.lbl_status = ctk.CTkLabel(
            self.frame_hud_content,
            text="AGUARDANDO AÇÃO...",
            font=self.FONT_METRIC,
            text_color=self.COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_status.grid(row=6, column=0, sticky="w", pady=(0, 15))

        # 4. Botão Executar
        self.btn_converter = ctk.CTkButton(
            self.frame_hud_content, 
            text="EXECUTAR CONVERSÃO", 
            command=self.converter_todas,
            font=self.FONT_BOLD,
            fg_color=self.COLOR_ACCENT,
            hover_color="#d68400",
            text_color="#121212",
            corner_radius=2,
            height=42
        )
        self.btn_converter.grid(row=7, column=0, sticky="ew")

    def selecionar_imagens(self):
        tipos = [("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"), ("Todos os arquivos", "*.*")]
        caminhos = filedialog.askopenfilenames(filetypes=tipos)
        if caminhos:
            self.caminhos_arquivos = list(caminhos)
            self.lbl_arquivos_info.configure(
                text=f"ARQUIVOS SELECIONADOS: {len(self.caminhos_arquivos)}",
                text_color="white"
            )
            self.progresso.set(0)

    def converter_todas(self):
        if not self.caminhos_arquivos:
            messagebox.showwarning("AVISO", "Nenhum arquivo selecionado.")
            return

        pasta_destino = filedialog.askdirectory(title="Diretório de Destino")
        if not pasta_destino:
            return

        formato_saida = self.combo_formato.get().lower()
        total = len(self.caminhos_arquivos)
        sucessos = 0

        self.btn_selecionar.configure(state="disabled")
        self.btn_converter.configure(state="disabled", text="PROCESSANDO...")

        for i, caminho in enumerate(self.caminhos_arquivos, start=1):
            try:
                with Image.open(caminho) as img:
                    nome_base = os.path.splitext(os.path.basename(caminho))[0]
                    caminho_saida = os.path.join(pasta_destino, f"{nome_base}_convertido.{formato_saida}")

                    if formato_saida in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(caminho_saida, format=formato_saida.upper())
                    sucessos += 1
            except Exception:
                pass

            val = i / total
            self.progresso.set(val)
            self.lbl_status.configure(text=f"PROGRESSO: {i}/{total} [{int(val*100)}%]", text_color="white")
            self.update_idletasks()

        self.btn_selecionar.configure(state="normal")
        self.btn_converter.configure(state="normal", text="EXECUTAR CONVERSÃO")
        messagebox.showinfo("CONCLUÍDO", f"Sucesso: {sucessos}/{total} arquivos convertidos.")

if __name__ == "__main__":
    app = CyberConverterApp()
    app.mainloop()