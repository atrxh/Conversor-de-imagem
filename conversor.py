import os
import tempfile
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw

ctk.set_appearance_mode("Dark")

class PixelShiftApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("PixelShift")
        self.geometry("920x640")
        self.resizable(False, False)
        self.configure(fg_color="#0B0B0E")

        # Aplica ícone dinâmico na barra de título
        self.definir_icone_janela()

        self.caminhos_arquivos = []

        # --- Paleta de Cores ---
        self.COLOR_BG = "#0B0B0E"
        self.COLOR_CARD = "#14141B"
        self.COLOR_BORDER = "#22222E"
        self.COLOR_SURFACE = "#1A1A24"
        
        self.COLOR_ACCENT = "#8B5CF6"        
        self.COLOR_ACCENT_HOVER = "#7C3AED"
        self.COLOR_DANGER_HOVER = "#EF4444"  
        
        self.COLOR_TEXT_WHITE = "#EDEDF2"
        self.COLOR_TEXT_MUTED = "#828292"
        self.COLOR_SUCCESS = "#10B981"

        # Tipografia
        self.FONT_TITLE = ("Segoe UI", 24, "bold")
        self.FONT_SUBTITLE = ("Segoe UI", 12)
        self.FONT_HUD = ("Consolas", 11, "bold")

        # Grid
        self.grid_columnconfigure(0, weight=40)
        self.grid_columnconfigure(1, weight=60)
        self.grid_rowconfigure(0, weight=1)

        # PAINEL ESQUERDO (Branding & Info)  
        self.frame_esquerda = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_esquerda.grid(row=0, column=0, padx=(30, 15), pady=25, sticky="nsew")

        self.lbl_brand_tag = ctk.CTkLabel(
            self.frame_esquerda, 
            text="CORE ENGINE v2.4", 
            font=self.FONT_HUD, 
            text_color=self.COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_brand_tag.pack(fill="x", pady=(0, 2))

        self.lbl_titulo = ctk.CTkLabel(
            self.frame_esquerda, 
            text="PixelShift", 
            font=self.FONT_TITLE, 
            text_color=self.COLOR_TEXT_WHITE,
            anchor="w"
        )
        self.lbl_titulo.pack(fill="x", pady=(0, 10))

        self.lbl_descricao = ctk.CTkLabel(
            self.frame_esquerda, 
            text="Conversor de alto desempenho para imagens em lote. Processamento 100% local.", 
            font=self.FONT_SUBTITLE, 
            text_color=self.COLOR_TEXT_MUTED,
            justify="left",
            wraplength=300,
            anchor="w"
        )
        self.lbl_descricao.pack(fill="x", pady=(0, 20))

        # Card de Especificações
        self.box_info = ctk.CTkFrame(
            self.frame_esquerda, 
            fg_color=self.COLOR_CARD, 
            border_width=1, 
            border_color=self.COLOR_BORDER,
            corner_radius=6
        )
        self.box_info.pack(fill="x", pady=(0, 15))

        self.lbl_info_header = ctk.CTkLabel(
            self.box_info, 
            text="ESPECIFICAÇÕES DO SISTEMA", 
            font=self.FONT_HUD, 
            text_color=self.COLOR_TEXT_WHITE
        )
        self.lbl_info_header.pack(anchor="w", padx=15, pady=(12, 8))

        info_specs = [
            ("Formatos aceitos:", "PNG, JPG, WEBP, BMP, GIF"),
            ("Modo de Conversão:", "Paralelo / Lote"),
            ("Tratamento Alpha:", "Auto-RGB (Fundo Branco)")
        ]

        for rotulo, valor in info_specs:
            f = ctk.CTkFrame(self.box_info, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(f, text=rotulo, font=self.FONT_SUBTITLE, text_color=self.COLOR_TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(f, text=valor, font=self.FONT_HUD, text_color=self.COLOR_TEXT_WHITE).pack(side="right")

        ctk.CTkFrame(self.box_info, height=10, fg_color="transparent").pack()

        # PAINEL DIREITO (Controles de Execução)
        self.card_operacional = ctk.CTkFrame(
            self, 
            fg_color=self.COLOR_CARD, 
            border_width=1, 
            border_color=self.COLOR_BORDER,
            corner_radius=8
        )
        self.card_operacional.grid(row=0, column=1, padx=(15, 30), pady=25, sticky="nsew")

        # Cabeçalho do HUD
        self.hud_top = ctk.CTkFrame(self.card_operacional, fg_color="#101017", corner_radius=0, height=38)
        self.hud_top.pack(fill="x")
        
        ctk.CTkLabel(
            self.hud_top, 
            text=" PAINEL DE EXECUÇÃO", 
            font=self.FONT_HUD, 
            text_color=self.COLOR_TEXT_WHITE
        ).pack(side="left", padx=15, pady=8)

        self.lbl_ready_status = ctk.CTkLabel(
            self.hud_top, 
            text="● READY ", 
            font=self.FONT_HUD, 
            text_color=self.COLOR_SUCCESS
        )
        self.lbl_ready_status.pack(side="right", padx=15, pady=8)

        self.body_op = ctk.CTkFrame(self.card_operacional, fg_color="transparent")
        self.body_op.pack(fill="both", expand=True, padx=20, pady=12)

        # Header da Seleção + Botão Limpar
        f_selecao_hdr = ctk.CTkFrame(self.body_op, fg_color="transparent")
        f_selecao_hdr.pack(fill="x", pady=(0, 4))
        
        ctk.CTkLabel(f_selecao_hdr, text="1. SELEÇÃO DE ARQUIVOS", font=self.FONT_HUD, text_color=self.COLOR_TEXT_MUTED).pack(side="left")
        
        self.btn_limpar = ctk.CTkButton(
            f_selecao_hdr, 
            text="Limpar Fila", 
            command=self.limpar_fila,
            font=("Segoe UI", 10),
            fg_color="transparent",
            hover_color="#222230",
            text_color=self.COLOR_TEXT_MUTED,
            width=60,
            height=18
        )
        self.btn_limpar.pack(side="right")

        # Botão para adicionar arquivos
        self.btn_selecionar = ctk.CTkButton(
            self.body_op, 
            text="+ ADICIONAR IMAGENS", 
            command=self.selecionar_imagens,
            font=self.FONT_HUD,
            fg_color=self.COLOR_SURFACE,
            hover_color="#222230",
            border_width=1,
            border_color=self.COLOR_BORDER,
            text_color=self.COLOR_TEXT_WHITE,
            corner_radius=4,
            height=34
        )
        self.btn_selecionar.pack(fill="x", pady=(0, 6))

        # Lista Rolável
        self.lista_container = ctk.CTkScrollableFrame(
            self.body_op,
            height=125,
            fg_color="#0F0F15",
            border_width=1,
            border_color=self.COLOR_BORDER,
            corner_radius=4
        )
        self.lista_container.pack(fill="x", pady=(0, 10))

        self.renderizar_lista_vazia()

        # Seleção de Formato
        ctk.CTkLabel(self.body_op, text="2. FORMATO DESTINO", font=self.FONT_HUD, text_color=self.COLOR_TEXT_MUTED, anchor="w").pack(fill="x", pady=(0, 4))

        self.combo_formato = ctk.CTkOptionMenu(
            self.body_op, 
            values=["PNG", "JPEG", "WEBP", "BMP", "GIF"],
            font=self.FONT_HUD,
            fg_color=self.COLOR_SURFACE,
            button_color=self.COLOR_BORDER,
            button_hover_color="#2D2D3F",
            dropdown_fg_color="#14141F",
            dropdown_hover_color="#222232",
            dropdown_text_color=self.COLOR_TEXT_WHITE,
            text_color=self.COLOR_TEXT_WHITE,
            corner_radius=4,
            height=34
        )
        self.combo_formato.set("PNG")
        self.combo_formato.pack(fill="x", pady=(0, 10))

        # Progresso
        ctk.CTkLabel(self.body_op, text="3. PROGRESSO DA OPERAÇÃO", font=self.FONT_HUD, text_color=self.COLOR_TEXT_MUTED, anchor="w").pack(fill="x", pady=(0, 4))

        self.progresso = ctk.CTkProgressBar(
            self.body_op, 
            height=6, 
            progress_color=self.COLOR_ACCENT, 
            fg_color=self.COLOR_SURFACE,
            corner_radius=2
        )
        self.progresso.pack(fill="x", pady=(0, 4))
        self.progresso.set(0)

        self.lbl_status = ctk.CTkLabel(
            self.body_op,
            text="Aguardando início...",
            font=self.FONT_SUBTITLE,
            text_color=self.COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_status.pack(fill="x", pady=(0, 10))

        # Botão de Ação Principal
        self.btn_converter = ctk.CTkButton(
            self.body_op, 
            text="INICIAR CONVERSÃO", 
            command=self.converter_todas,
            font=self.FONT_HUD,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_TEXT_WHITE,
            corner_radius=4,
            height=40
        )
        self.btn_converter.pack(fill="x", side="bottom")

    def definir_icone_janela(self):
        try:
            ico_path = os.path.join(tempfile.gettempdir(), "pixelshift_app_icon.ico")
            img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            draw.rounded_rectangle([2, 2, 29, 29], radius=7, fill=(139, 92, 246, 255))
            draw.rounded_rectangle([9, 9, 22, 22], radius=4, fill=(11, 11, 14, 255))
            draw.rectangle([18, 18, 22, 22], fill=(139, 92, 246, 255))
            
            img.save(ico_path, format="ICO")
            self.iconbitmap(ico_path)
        except Exception:
            pass

    def renderizar_lista_vazia(self):
        """Exibe mensagem quando a fila de arquivos está vazia."""
        for child in self.lista_container.winfo_children():
            child.destroy()
        
        lbl_empty = ctk.CTkLabel(
            self.lista_container,
            text="Nenhum arquivo na fila.",
            font=self.FONT_SUBTITLE,
            text_color=self.COLOR_TEXT_MUTED
        )
        lbl_empty.pack(pady=40)

    def atualizar_lista_interface(self):
        """Reconstrução dinâmica da lista de arquivos com botão de exclusão '✕' individual."""
        for child in self.lista_container.winfo_children():
            child.destroy()

        if not self.caminhos_arquivos:
            self.renderizar_lista_vazia()
            self.lbl_status.configure(text="Aguardando início...", text_color=self.COLOR_TEXT_MUTED)
            return

        for caminho in self.caminhos_arquivos:
            nome_arquivo = os.path.basename(caminho)
            extensao = os.path.splitext(nome_arquivo)[1].upper().replace(".", "")
            
            row_frame = ctk.CTkFrame(self.lista_container, fg_color=self.COLOR_SURFACE, corner_radius=4)
            row_frame.pack(fill="x", padx=4, pady=2)

            # Badge de Formato
            lbl_badge = ctk.CTkLabel(
                row_frame, 
                text=f" {extensao} ", 
                font=("Consolas", 9, "bold"), 
                fg_color="#262636", 
                text_color=self.COLOR_TEXT_WHITE,
                corner_radius=3
            )
            lbl_badge.pack(side="left", padx=(6, 8), pady=4)

            # Nome do Arquivo
            lbl_file = ctk.CTkLabel(
                row_frame, 
                text=nome_arquivo, 
                font=self.FONT_SUBTITLE, 
                text_color=self.COLOR_TEXT_WHITE,
                anchor="w"
            )
            lbl_file.pack(side="left", fill="x", expand=True, padx=2)

            # Botão "X" para remoção individual
            btn_remover = ctk.CTkButton(
                row_frame,
                text="✕",
                width=24,
                height=24,
                font=("Segoe UI", 11, "bold"),
                fg_color="transparent",
                hover_color=self.COLOR_DANGER_HOVER,
                text_color=self.COLOR_TEXT_MUTED,
                corner_radius=3,
                command=lambda p=caminho: self.remover_arquivo(p)
            )
            btn_remover.pack(side="right", padx=(0, 4))

        self.lbl_status.configure(text=f"{len(self.caminhos_arquivos)} arquivo(s) pronto(s).", text_color=self.COLOR_SUCCESS)

    def selecionar_imagens(self):
        """Abre a caixa de diálogo e adiciona novos arquivos à lista existente."""
        tipos = [("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"), ("Todos os arquivos", "*.*")]
        caminhos = filedialog.askopenfilenames(filetypes=tipos)
        
        if caminhos:
            # Adiciona novos caminhos evitando duplicatas
            for c in caminhos:
                if c not in self.caminhos_arquivos:
                    self.caminhos_arquivos.append(c)
            
            self.progresso.set(0)
            self.atualizar_lista_interface()

    def remover_arquivo(self, caminho):
        """Remove um arquivo específico da lista pelo botão '✕'."""
        if caminho in self.caminhos_arquivos:
            self.caminhos_arquivos.remove(caminho)
            self.atualizar_lista_interface()

    def limpar_fila(self):
        """Limpa toda a fila de arquivos."""
        self.caminhos_arquivos.clear()
        self.renderizar_lista_vazia()
        self.progresso.set(0)
        self.lbl_status.configure(text="Aguardando início...", text_color=self.COLOR_TEXT_MUTED)

    def converter_todas(self):
        """Executa a conversão dos arquivos."""
        if not self.caminhos_arquivos:
            messagebox.showwarning("ATENÇÃO", "Selecione ao menos um arquivo de imagem.")
            return

        pasta_destino = filedialog.askdirectory(title="Selecione a Pasta de Destino")
        if not pasta_destino:
            return

        formato_saida = self.combo_formato.get().lower()
        total = len(self.caminhos_arquivos)
        sucessos = 0

        self.btn_selecionar.configure(state="disabled")
        self.btn_converter.configure(state="disabled", text="CONVERTENDO...")

        for i, caminho in enumerate(self.caminhos_arquivos, start=1):
            try:
                with Image.open(caminho) as img:
                    nome_base = os.path.splitext(os.path.basename(caminho))[0]
                    caminho_saida = os.path.join(pasta_destino, f"{nome_base}_pixelshift.{formato_saida}")

                    if formato_saida in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(caminho_saida, format=formato_saida.upper())
                    sucessos += 1
            except Exception:
                pass

            val = i / total
            self.progresso.set(val)
            self.lbl_status.configure(text=f"Processando: {i}/{total} ({int(val * 100)}%)", text_color=self.COLOR_TEXT_WHITE)
            self.update_idletasks()

        self.btn_selecionar.configure(state="normal")
        self.btn_converter.configure(state="normal", text="INICIAR CONVERSÃO")
        messagebox.showinfo("CONCLUÍDO", f"Processamento finalizado!\n{sucessos} de {total} imagens convertidas.")

if __name__ == "__main__":
    app = PixelShiftApp()
    app.mainloop()