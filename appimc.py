import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from core.database import Database
from core.workouts import get_workout_by_bmi
from core.health_math import calculate_water_intake, calculate_bmr
from views.avatar_canvas import AvatarCanvas
from views.premium_modal import PremiumModal


def interpolate_color(hex_start, hex_end, factor):
    r1, g1, b1 = int(hex_start[1:3], 16), int(hex_start[3:5], 16), int(hex_start[5:7], 16)
    r2, g2, b2 = int(hex_end[1:3], 16), int(hex_end[3:5], 16), int(hex_end[5:7], 16)

    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)

    return f"#{r:02x}{g:02x}{b:02x}"


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.db = Database()
        self.current_user = None

        self.title("FitCheck Pro — Performance")
        self.geometry("1180x820")
        self.configure(fg_color="#0B0E14")

        self.is_premium = ctk.BooleanVar(value=False)
        self._build_ui()

    def _build_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, fg_color="#161B22", height=70, corner_radius=0)
        self.header.pack(fill="x", side="top")

        self.lbl_logo = ctk.CTkLabel(
            self.header,
            text="FITCHECK PRO",
            font=("Inter", 22, "bold"),
            text_color="#10B981",
        )
        self.lbl_logo.pack(side="left", padx=30)

        self.lbl_user = ctk.CTkLabel(
            self.header,
            text="🔒 Faça Login para começar",
            font=("Inter", 14, "bold"),
            text_color="#9CA3AF",
        )
        self.lbl_user.pack(side="right", padx=30)

        main_grid = ctk.CTkFrame(self, fg_color="transparent")
        main_grid.pack(fill="both", expand=True, padx=20, pady=20)

        # ================= COLUNA 1 =================
        self.col1 = ctk.CTkFrame(
            main_grid,
            fg_color="#161B22",
            corner_radius=12,
            border_color="#1F2937",
            border_width=1,
        )
        self.col1.pack(side="left", fill="both", expand=True, padx=8)

        self.frame_login = ctk.CTkFrame(self.col1, fg_color="transparent")
        self.frame_login.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            self.frame_login,
            text="1. Autenticação",
            font=("Inter", 16, "bold"),
            text_color="#10B981",
        ).pack(anchor="w", pady=(5, 15))

        self.input_user = ctk.CTkEntry(
            self.frame_login, placeholder_text="Usuário", height=40, fg_color="#0B0E14"
        )
        self.input_user.pack(fill="x", pady=6)

        self.input_pass = ctk.CTkEntry(
            self.frame_login, placeholder_text="Senha", show="*", height=40, fg_color="#0B0E14"
        )
        self.input_pass.pack(fill="x", pady=6)

        ctk.CTkLabel(
            self.frame_login, text="Gênero:", font=("Inter", 12), text_color="#F3F4F6"
        ).pack(anchor="w", pady=(10, 2))

        self.gender_var = ctk.StringVar(value="M")
        frame_gender = ctk.CTkFrame(self.frame_login, fg_color="transparent")
        frame_gender.pack(fill="x", pady=4)

        ctk.CTkRadioButton(
            frame_gender, text="Masc", variable=self.gender_var, value="M", fg_color="#10B981"
        ).pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(
            frame_gender, text="Fem", variable=self.gender_var, value="F", fg_color="#10B981"
        ).pack(side="left")

        ctk.CTkButton(
            self.frame_login,
            text="ENTRAR",
            height=40,
            font=("Inter", 13, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=self.handle_login,
        ).pack(fill="x", pady=(15, 6))

        ctk.CTkButton(
            self.frame_login,
            text="CRIAR NOVA CONTA",
            height=35,
            font=("Inter", 12),
            fg_color="transparent",
            border_color="#1F2937",
            border_width=1,
            command=self.handle_register,
        ).pack(fill="x", pady=4)

        self.lbl_auth_msg = ctk.CTkLabel(
            self.frame_login, text="", font=("Inter", 11), text_color="#EF4444"
        )
        self.lbl_auth_msg.pack(pady=5)

        # Frame de Cálculo Expandido
        self.frame_calc = ctk.CTkFrame(self.col1, fg_color="transparent")

        ctk.CTkLabel(
            self.frame_calc, text="1. Seus Dados", font=("Inter", 16, "bold"), text_color="#F3F4F6"
        ).pack(anchor="w", pady=(5, 8))

        self.input_peso = ctk.CTkEntry(
            self.frame_calc, placeholder_text="Peso (ex: 75.5) kg", height=40, fg_color="#0B0E14"
        )
        self.input_peso.pack(fill="x", pady=4)

        self.input_altura = ctk.CTkEntry(
            self.frame_calc, placeholder_text="Altura (ex: 1.75) m", height=40, fg_color="#0B0E14"
        )
        self.input_altura.pack(fill="x", pady=4)

        self.input_bf = ctk.CTkEntry(
            self.frame_calc, placeholder_text="% Gordura Corporal (BF)", height=40, fg_color="#0B0E14"
        )
        self.input_bf.configure(state="disabled")
        self.input_bf.pack(fill="x", pady=4)

        self.btn_calc = ctk.CTkButton(
            self.frame_calc,
            text="CALCULAR E SALVAR",
            height=42,
            font=("Inter", 13, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=self._execute,
        )
        self.btn_calc.pack(fill="x", pady=(8, 12))

        # CARD PREMIUM
        self.card_premium = ctk.CTkFrame(
            self.frame_calc,
            fg_color="#0B0E14",
            border_color="#FBBF24",
            border_width=1,
            corner_radius=8,
        )
        self.card_premium.pack(fill="x", pady=4, ipady=4)

        self.lbl_premium_title = ctk.CTkLabel(
            self.card_premium, text="👑 MODO PREMIUM", font=("Inter", 12, "bold"), text_color="#FBBF24"
        )
        self.lbl_premium_title.pack(pady=(6, 1))

        self.btn_premium_action = ctk.CTkButton(
            self.card_premium,
            text="Entre no Premium, basta clicar aqui!",
            font=("Inter", 11, "bold"),
            fg_color="#FBBF24",
            text_color="#000000",
            hover_color="#D97706",
            height=32,
            command=self._open_premium_modal,
        )
        self.btn_premium_action.pack(padx=10, pady=(2, 6), fill="x")

        # PAINEL DE CARDS METAS DIÁRIAS (Gasta mais espaço com estilo)
        self.card_metrics_grid = ctk.CTkFrame(
            self.frame_calc, fg_color="#0B0E14", border_color="#1F2937", border_width=1, corner_radius=10
        )
        self.card_metrics_grid.pack(fill="x", pady=12, ipady=8, ipadx=5)

        ctk.CTkLabel(
            self.card_metrics_grid, text="⚡ METAS DE METABOLISMO", font=("Inter", 12, "bold"), text_color="#38BDF8"
        ).pack(anchor="w", padx=12, pady=(8, 8))

        grid_inner = ctk.CTkFrame(self.card_metrics_grid, fg_color="transparent")
        grid_inner.pack(fill="x", padx=10, pady=2)

        # Box Água
        box_w = ctk.CTkFrame(grid_inner, fg_color="#161B22", corner_radius=8)
        box_w.pack(side="left", fill="both", expand=True, padx=4)
        ctk.CTkLabel(box_w, text="💧 ÁGUA", font=("Inter", 10, "bold"), text_color="#9CA3AF").pack(pady=(6, 0))
        self.lbl_val_water = ctk.CTkLabel(box_w, text="-- L", font=("Inter", 15, "bold"), text_color="#38BDF8")
        self.lbl_val_water.pack(pady=(0, 6))

        # Box Basal
        box_b = ctk.CTkFrame(grid_inner, fg_color="#161B22", corner_radius=8)
        box_b.pack(side="left", fill="both", expand=True, padx=4)
        ctk.CTkLabel(box_b, text="🔥 TMB", font=("Inter", 10, "bold"), text_color="#9CA3AF").pack(pady=(6, 0))
        self.lbl_val_bmr = ctk.CTkLabel(box_b, text="-- kcal", font=("Inter", 15, "bold"), text_color="#F59E0B")
        self.lbl_val_bmr.pack(pady=(0, 6))

        # ================= COLUNA 2 =================
        self.col2 = ctk.CTkFrame(
            main_grid,
            fg_color="#161B22",
            corner_radius=12,
            border_color="#1F2937",
            border_width=1,
        )
        self.col2.pack(side="left", fill="both", expand=True, padx=8)

        ctk.CTkLabel(
            self.col2,
            text="2. Projeção Corporal Visual",
            font=("Inter", 14, "bold"),
            text_color="#F3F4F6",
        ).pack(anchor="w", padx=20, pady=12)

        self.avatar = AvatarCanvas(self.col2, width=240, height=230)
        self.avatar.pack(pady=5)

        # PAINEL ANALÍTICO COMPOSIÇÃO CORPORAL
        self.card_body_metrics = ctk.CTkFrame(
            self.col2,
            fg_color="#0B0E14",
            border_color="#1F2937",
            border_width=1,
            corner_radius=10,
        )
        self.card_body_metrics.pack(fill="x", padx=15, pady=12, ipady=10)

        ctk.CTkLabel(
            self.card_body_metrics, text="📊 Régua do IMC & Nível", font=("Inter", 12, "bold"), text_color="#F3F4F6"
        ).pack(anchor="w", padx=12, pady=(8, 4))

        self.lbl_range_imc = ctk.CTkLabel(
            self.card_body_metrics, text="Aguardando cálculo...", font=("Inter", 11, "bold"), text_color="#9CA3AF"
        )
        self.lbl_range_imc.pack(anchor="w", padx=12)

        # Barra Visual de IMC
        self.bar_imc = ctk.CTkProgressBar(self.card_body_metrics, height=10, fg_color="#161B22", progress_color="#10B981")
        self.bar_imc.set(0)
        self.bar_imc.pack(fill="x", padx=12, pady=8)

        self.lbl_mass_split = ctk.CTkLabel(
            self.card_body_metrics, text="Massa Magra: -- kg  |  Gordura: -- kg", font=("Inter", 11), text_color="#9CA3AF"
        )
        self.lbl_mass_split.pack(anchor="w", padx=12, pady=(2, 6))

        # ================= COLUNA 3 =================
        col3 = ctk.CTkFrame(main_grid, fg_color="transparent")
        col3.pack(side="left", fill="both", expand=True, padx=8)

        # CARD RECOMENDAÇÃO INTELIGENTE REFORMULADA
        self.card_rec = ctk.CTkFrame(
            col3,
            fg_color="#161B22",
            corner_radius=12,
            border_color="#1F2937",
            border_width=1,
        )
        self.card_rec.pack(fill="x", pady=(0, 10), ipady=5)

        ctk.CTkLabel(
            self.card_rec,
            text="3. Diagnóstico & Plano Inteligente",
            font=("Inter", 14, "bold"),
            text_color="#F3F4F6",
        ).pack(anchor="w", padx=15, pady=(12, 6))

        self.lbl_status_tag = ctk.CTkLabel(
            self.card_rec,
            text="Aguardando Login...",
            font=("Inter", 13, "bold"),
            text_color="#10B981",
        )
        self.lbl_status_tag.pack(anchor="w", padx=15, pady=2)

        # Container dos 3 Pilares
        self.frame_pilares = ctk.CTkFrame(self.card_rec, fg_color="transparent")
        self.frame_pilares.pack(fill="x", padx=10, pady=8)

        # Pilar Treino
        self.card_p_treino = ctk.CTkFrame(self.frame_pilares, fg_color="#0B0E14", corner_radius=6)
        self.card_p_treino.pack(fill="x", pady=3)
        self.lbl_p_treino = ctk.CTkLabel(
            self.card_p_treino, text="🏋️ Treino: Faça login para gerar o plano", font=("Inter", 11), text_color="#D1D5DB", justify="left"
        )
        self.lbl_p_treino.pack(anchor="w", padx=10, pady=6)

        # Pilar Nutrição
        self.card_p_nutri = ctk.CTkFrame(self.frame_pilares, fg_color="#0B0E14", corner_radius=6)
        self.card_p_nutri.pack(fill="x", pady=3)
        self.lbl_p_nutri = ctk.CTkLabel(
            self.card_p_nutri, text="🥗 Nutrição: Insira os dados para ver macros", font=("Inter", 11), text_color="#D1D5DB", justify="left"
        )
        self.lbl_p_nutri.pack(anchor="w", padx=10, pady=6)

        # Pilar Cárdio
        self.card_p_cardio = ctk.CTkFrame(self.frame_pilares, fg_color="#0B0E14", corner_radius=6)
        self.card_p_cardio.pack(fill="x", pady=3)
        self.lbl_p_cardio = ctk.CTkLabel(
            self.card_p_cardio, text="🏃 Cárdio: Recomendações de aeróbico", font=("Inter", 11), text_color="#D1D5DB", justify="left"
        )
        self.lbl_p_cardio.pack(anchor="w", padx=10, pady=6)

        # ABAS
        self.tabview = ctk.CTkTabview(
            col3,
            fg_color="#161B22",
            segmented_button_selected_color="#10B981",
        )
        self.tabview.pack(fill="both", expand=True)

        self.tab_hist = self.tabview.add("📜 Histórico")
        self.tab_workout = self.tabview.add("🏋️ Treino Premium")

        self.box_hist = ctk.CTkTextbox(self.tab_hist, fg_color="#0B0E14", font=("Inter", 12))
        self.box_hist.pack(fill="both", expand=True, padx=10, pady=10)
        self.box_hist.configure(state="disabled")

        self.box_workout = ctk.CTkTextbox(self.tab_workout, fg_color="#0B0E14", font=("Inter", 12))
        self.box_workout.pack(fill="both", expand=True, padx=10, pady=10)
        self.box_workout.insert("1.0", "🔒 Ative o modo Premium 👑 para liberar seu treino.")
        self.box_workout.configure(state="disabled")

    def _open_premium_modal(self):
        if not self.is_premium.get():
            PremiumModal(self, on_success_callback=self._start_fade_to_gold)

    def _start_fade_to_gold(self):
        self.is_premium.set(True)
        self.input_bf.configure(state="normal")
        self.btn_premium_action.configure(
            text="Membro Premium Ativo 👑", state="disabled", fg_color="#1F2937", text_color="#FBBF24"
        )
        self._animate_theme_fade(step=0, total_steps=20)

    def _animate_theme_fade(self, step, total_steps):
        factor = step / total_steps

        bg_main = interpolate_color("#0B0E14", "#111111", factor)
        bg_card = interpolate_color("#161B22", "#1F1F1F", factor)
        border_gold = interpolate_color("#1F2937", "#D97706", factor)
        btn_green_to_gold = interpolate_color("#10B981", "#FBBF24", factor)

        self.configure(fg_color=bg_main)
        self.header.configure(fg_color=bg_card)
        self.col1.configure(fg_color=bg_card, border_color=border_gold)
        self.col2.configure(fg_color=bg_card, border_color=border_gold)
        self.card_rec.configure(fg_color=bg_card, border_color=border_gold)

        self.lbl_logo.configure(text_color=btn_green_to_gold)
        self.btn_calc.configure(fg_color=btn_green_to_gold, hover_color="#D97706", text_color="#000000")
        self.tabview.configure(fg_color=bg_card, segmented_button_selected_color=btn_green_to_gold)

        if step < total_steps:
            self.after(25, lambda: self._animate_theme_fade(step + 1, total_steps))
        else:
            self.lbl_logo.configure(text="FITCHECK PRO 👑")

    def handle_login(self):
        u, p = self.input_user.get().strip(), self.input_pass.get().strip()
        if not u or not p:
            self.lbl_auth_msg.configure(text="Preencha usuário e senha!", text_color="#EF4444")
            return

        user = self.db.authenticate_user(u, p)
        if user:
            self._on_login_success(user)
        else:
            self.lbl_auth_msg.configure(text="Usuário ou senha incorretos.", text_color="#EF4444")

    def handle_register(self):
        u, p, g = self.input_user.get().strip(), self.input_pass.get().strip(), self.gender_var.get()
        if not u or not p:
            self.lbl_auth_msg.configure(text="Preencha todos os campos!", text_color="#EF4444")
            return

        if self.db.register_user(u, p, g):
            user = self.db.authenticate_user(u, p)
            self._on_login_success(user)
        else:
            self.lbl_auth_msg.configure(text="Nome de usuário já existe.", text_color="#EF4444")

    def _on_login_success(self, user_tuple):
        self.current_user = user_tuple
        gen = "Masculino" if self.current_user[2] == "M" else "Feminino"
        color = "#FBBF24" if self.is_premium.get() else "#10B981"
        self.lbl_user.configure(text=f"👤 {self.current_user[1].upper()} ({gen})", text_color=color)

        self.frame_login.pack_forget()
        self.frame_calc.pack(fill="both", expand=True, padx=15, pady=15)

        self.lbl_status_tag.configure(text="Pronto para processar", text_color=color)
        self._load_history()

    def _execute(self):
        if not self.current_user:
            return

        try:
            w = float(self.input_peso.get().replace(",", "."))
            h = float(self.input_altura.get().replace(",", "."))
        except ValueError:
            self.lbl_status_tag.configure(text="⚠️ Erro nos dados", text_color="#EF4444")
            return

        bmi = w / (h**2)
        bf, lean_mass = 0.0, 0.0

        # Atualiza Metas da Coluna 1
        water = calculate_water_intake(w)
        bmr = calculate_bmr(w, h, self.current_user[2])
        self.lbl_val_water.configure(text=f"{water:.2f} L")
        self.lbl_val_bmr.configure(text=f"{bmr} kcal")

        # Atualiza Barra e Faixa de IMC
        if bmi < 18.5:
            cat_imc, color_imc, progress = "Abaixo do Peso", "#3B82F6", 0.2
        elif 18.5 <= bmi < 25:
            cat_imc, color_imc, progress = "Peso Normal", "#10B981", 0.5
        elif 25 <= bmi < 30:
            cat_imc, color_imc, progress = "Sobrepeso", "#F59E0B", 0.75
        else:
            cat_imc, color_imc, progress = "Obesidade", "#EF4444", 1.0

        self.lbl_range_imc.configure(text=f"Nível do IMC: {cat_imc} ({bmi:.1f})", text_color=color_imc)
        self.bar_imc.configure(progress_color=color_imc)
        self.bar_imc.set(progress)

        if self.is_premium.get():
            try:
                bf = float(self.input_bf.get().replace(",", "."))
                fat_mass = w * (bf / 100)
                lean_mass = w - fat_mass
                self.lbl_mass_split.configure(
                    text=f"Massa Magra: {lean_mass:.1f} kg  |  Gordura: {fat_mass:.1f} kg"
                )
            except ValueError:
                self.lbl_status_tag.configure(text="⚠️ Erro no % BF", text_color="#EF4444")
                return
        else:
            self.lbl_mass_split.configure(text="Massa Magra: -- kg  |  Gordura: -- kg (Modo Premium)")

        # Renderização do Avatar Visual
        gender = self.current_user[2]
        self.avatar.render_body(bmi=bmi, bf=bf, gender=gender)

        # RECOMENDAÇÃO INTELIGENTE AVANÇADA (Três Pilares)
        self.lbl_status_tag.configure(text=f"Diagnóstico Concluído — {cat_imc}", text_color=color_imc)

        if bmi < 18.5:
            self.lbl_p_treino.configure(text="🏋️ Treino: Hipertrofia com carga progressiva e menor volume.")
            self.lbl_p_nutri.configure(text=f"🥗 Nutrição: Superávit calórico (~{bmr + 400} kcal/dia).")
            self.lbl_p_cardio.configure(text="🏃 Cárdio: Moderado (15-20 min, 2x por semana).")
        elif 18.5 <= bmi < 25:
            self.lbl_p_treino.configure(text="🏋️ Treino: Musculação com intensidade para manutenção/ganho de massa.")
            self.lbl_p_nutri.configure(text=f"🥗 Nutrição: Dieta normocalórica (~{bmr + 200} kcal/dia).")
            self.lbl_p_cardio.configure(text="🏃 Cárdio: Regular (30 min, 3x por semana).")
        else:
            self.lbl_p_treino.configure(text="🏋️ Treino: Musculação de alta densidade e descansos curtos.")
            self.lbl_p_nutri.configure(text=f"🥗 Nutrição: Déficit calórico estratégico (~{max(1200, bmr - 300)} kcal/dia).")
            self.lbl_p_cardio.configure(text="🏃 Cárdio: Focado em queima (30-45 min, 4x por semana).")

        if self.is_premium.get():
            self._update_workout(bmi)

        self.db.add_history(self.current_user[0], w, h, bmi, bf, lean_mass)
        self._load_history()

    def _update_workout(self, bmi):
        category, plan = get_workout_by_bmi(bmi)
        self.box_workout.configure(state="normal")
        self.box_workout.delete("1.0", "end")

        self.box_workout.insert("end", f"🎯 TREINO CUSTOMIZADO ({category.upper()})\n\n")
        self.box_workout.insert("end", "EXERCÍCIOS:\n")
        for ex in plan["exercicios"]:
            self.box_workout.insert("end", f"{ex}\n")

        self.box_workout.insert("end", f"\n{plan['aerobico']}\n")
        self.box_workout.configure(state="disabled")

        self.tabview.set("🏋️ Treino Premium")

    def _load_history(self):
        if not self.current_user:
            return

        records = self.db.get_user_history(self.current_user[0])
        self.box_hist.configure(state="normal")
        self.box_hist.delete("1.0", "end")

        if not records:
            self.box_hist.insert("1.0", "Nenhuma medição salva ainda.")
        else:
            for r in records:
                dt, weight, bmi, bf, lean = r
                line = f"• {dt[:10]} | {weight}kg | IMC: {bmi:.1f}"
                if bf > 0:
                    line += f" | BF: {bf}% | MM: {lean:.1f}kg"
                self.box_hist.insert("end", line + "\n")

        self.box_hist.configure(state="disabled")


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = MainWindow()
    app.mainloop()
    # No topo do appimc.py, adicione a importação:
from views.qrcode_modal import QRCodeModal

# Dentro do método _build_ui() da MainWindow, adicione o botão no Header:
def _build_ui(self):
    self.header = ctk.CTkFrame(self, fg_color="#161B22", height=70, corner_radius=0)
    self.header.pack(fill="x", side="top")

    self.lbl_logo = ctk.CTkLabel(
        self.header,
        text="FITCHECK PRO",
        font=("Inter", 22, "bold"),
        text_color="#10B981",
    )
    self.lbl_logo.pack(side="left", padx=30)

    # BOTÃO COMPARTILHAR ADICIONADO AQUI
    self.btn_share = ctk.CTkButton(
        self.header,
        text="📲 COMPARTILHAR",
        font=("Inter", 11, "bold"),
        fg_color="#1F2937",
        hover_color="#374151",
        width=120,
        height=32,
        command=self._open_share_qr,
    )
    self.btn_share.pack(side="right", padx=(0, 20))

    self.lbl_user = ctk.CTkLabel(
        self.header,
        text="🔒 Faça Login para começar",
        font=("Inter", 14, "bold"),
        text_color="#9CA3AF",
    )
    self.lbl_user.pack(side="right", padx=10)

# Crie o método de abertura do modal dentro da MainWindow:
def _open_share_qr(self):
    # Substitua a URL abaixo pelo link real do seu repositório ou arquivo hospedado
    link_download = "https://github.com/seu-usuario/fitcheck-pro/releases"
    QRCodeModal(self, download_url=link_download)