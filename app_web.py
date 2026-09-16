import streamlit as st

st.set_page_config(
    page_title="FitCheck Pro", page_icon="🏋️‍♂️", layout="centered"
)

# Estilização Customizada Dark/Verde
st.markdown(
    """
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    div.stButton > button { background-color: #10B981; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    div.stButton > button:hover { background-color: #059669; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🏋️‍♂️ FitCheck Pro")
st.caption("Análise de Composição Corporal e Saúde")

# Formulario de Cadastro e Dados
with st.form("fitcheck_form"):
    st.subheader("📋 Cadastro de Saúde")
    nome = st.text_input("Nome Completo")
    genero = st.selectbox("Gênero", ["Masculino", "Feminino"])

    col1, col2 = st.columns(2)
    with col1:
        peso = st.number_input(
            "Peso (kg)", min_value=10.0, max_value=300.0, value=70.0, step=0.5
        )
        idade = st.number_input("Idade", min_value=10, max_value=120, value=25)
    with col2:
        altura = st.number_input(
            "Altura (cm)",
            min_value=100.0,
            max_value=250.0,
            value=170.0,
            step=1.0,
        )
        fator_act = st.selectbox(
            "Nível de Atividade",
            ["Sedentário", "Leve", "Moderado", "Intenso"],
        )

    submit = st.form_submit_button("CALCULAR DIAGNÓSTICO")

if submit:
    if not nome:
        st.error("Por favor, preencha o seu nome.")
    else:
        # Lógica de Cálculos
        altura_m = altura / 100
        imc = peso / (altura_m**2)
        agua_ml = peso * 35

        # TMB (Harris-Benedict)
        if genero == "Masculino":
            tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
        else:
            tmb = 447.59 + (9.24 * peso) + (3.10 * altura) - (4.33 * idade)

        # Classificação IMC
        if imc < 18.5:
            status, cor = "Abaixo do Peso", "#3B82F6"
        elif 18.5 <= imc < 25:
            status, cor = "Peso Ideal", "#10B981"
        elif 25 <= imc < 30:
            status, cor = "Sobrepeso", "#F59E0B"
        else:
            status, cor = "Obesidade", "#EF4444"

        st.divider()
        st.success(f"Cadastro realizado com sucesso, {nome}!")

        # Métricas em Cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Seu IMC", f"{imc:.1f}", delta=status)
        m2.metric("Metabolismo Basal", f"{int(tmb)} kcal")
        m3.metric("Meta de Água", f"{agua_ml/1000:.2f} L/dia")

        st.progress(min(float(imc / 40), 1.0))