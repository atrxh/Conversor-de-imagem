import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ConversorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Conversor de Imagens em Lote")
        self.geometry("500x380")
        self.resizable(False, False)

        self.caminhos_arquivos = []

        self.grid_columnconfigure(0, weight=1)

        # 1. Cabeçalho
        self.frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_topo.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        self.frame_topo.grid_columnconfigure(0, weight=1)

        self.lbl_titulo = ctk.CTkLabel(
            self.frame_topo, 
            text="Conversor em Lote", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_titulo.grid(row=0, column=0, sticky="w")

        self.switch_tema = ctk.CTkSwitch(
            self.frame_topo, 
            text="Modo Escuro", 
            command=self.alternar_tema
        )
        self.switch_tema.select()
        self.switch_tema.grid(row=0, column=1, sticky="e")

        # 2. Seleção de Arquivos
        self.btn_selecionar = ctk.CTkButton(
            self, 
            text="📁 Selecionar Imagem(ns)", 
            command=self.selecionar_imagens,
            height=35
        )
        self.btn_selecionar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.lbl_status = ctk.CTkLabel(
            self, 
            text="Nenhuma imagem selecionada", 
            text_color="gray", 
            wraplength=460
        )
        self.lbl_status.grid(row=2, column=0, padx=20, pady=5)

        # 3. Opções de Formato
        self.frame_opcoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_opcoes.grid(row=3, column=0, padx=20, pady=5)

        self.lbl_formato = ctk.CTkLabel(self.frame_opcoes, text="Converter para:")
        self.lbl_formato.pack(side="left", padx=(0, 10))

        self.combo_formato = ctk.CTkOptionMenu(
            self.frame_opcoes, 
            values=["JPEG", "PNG", "WEBP", "BMP", "GIF"]
        )
        self.combo_formato.set("JPEG")
        self.combo_formato.pack(side="left")

        # 4. Barra de Progresso (CTkProgressBar)
        self.progresso = ctk.CTkProgressBar(self, height=12)
        self.progresso.grid(row=4, column=0, padx=20, pady=15, sticky="ew")
        self.progresso.set(0)  # Inicia zerada (recebe valores de 0.0 a 1.0)

        # 5. Botão de Ação
        self.btn_converter = ctk.CTkButton(
            self, 
            text="⚡ Converter Todas e Salvar", 
            command=self.converter_todas,
            height=40,
            fg_color="#2FA572", 
            hover_color="#1E6B4A"
        )
        self.btn_converter.grid(row=5, column=0, padx=20, pady=(5, 20), sticky="ew")

    def alternar_tema(self):
        if self.switch_tema.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def selecionar_imagens(self):
        tipos = [("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"), ("Todos os arquivos", "*.*")]
        caminhos = filedialog.askopenfilenames(filetypes=tipos)
        
        if caminhos:
            self.caminhos_arquivos = list(caminhos)
            total = len(self.caminhos_arquivos)
            self.progresso.set(0)  # Reseta o progresso ao escolher novos arquivos
            
            if total == 1:
                nome = os.path.basename(self.caminhos_arquivos[0])
                texto = f"1 arquivo selecionado: {nome}"
            else:
                texto = f"{total} imagens selecionadas e prontas para conversão."

            self.lbl_status.configure(text=texto, text_color=("black", "white"))

    def converter_todas(self):
        if not self.caminhos_arquivos:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma imagem antes de converter!")
            return

        pasta_destino = filedialog.askdirectory(title="Selecione a pasta para salvar as imagens")

        if not pasta_destino:
            return

        formato_saida = self.combo_formato.get().lower()
        total = len(self.caminhos_arquivos)
        sucessos = 0
        erros = 0

        # Bloqueia os botões durante o processamento para evitar cliques repetidos
        self.btn_selecionar.configure(state="disabled")
        self.btn_converter.configure(state="disabled")

        for i, caminho in enumerate(self.caminhos_arquivos, start=1):
            try:
                with Image.open(caminho) as img:
                    nome_base = os.path.splitext(os.path.basename(caminho))[0]
                    nome_saida = f"{nome_base}_convertido.{formato_saida}"
                    caminho_saida = os.path.join(pasta_destino, nome_saida)

                    if formato_saida in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(caminho_saida, format=formato_saida.upper())
                    sucessos += 1
            except Exception:
                erros += 1

            # Calcula e atualiza a barra (valores de 0.0 a 1.0)
            valor_progresso = i / total
            self.progresso.set(valor_progresso)
            self.lbl_status.configure(text=f"Convertendo: {i} de {total} ({int(valor_progresso * 100)}%)")
            
            # Força a interface a renderizar cada avanço
            self.update_idletasks()

        # Libera os botões novamente
        self.btn_selecionar.configure(state="normal")
        self.btn_converter.configure(state="normal")

        # Exibe o resumo final
        mensagem = f"Processo concluído!\n\n✔ Imagens convertidas: {sucessos}"
        if erros > 0:
            mensagem += f"\n✖ Falhas: {erros}"
            
        messagebox.showinfo("Resultado", mensagem)

if __name__ == "__main__":
    app = ConversorApp()
    app.mainloop()