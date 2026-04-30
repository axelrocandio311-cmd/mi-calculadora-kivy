import streamlit as st

st.set_page_config(page_title="Executive Calculator", page_icon="⚖️", layout="centered")

# --- DISEÑO ELGANTE GAMA ALTA (CSS) ---
st.markdown("""
    <style>
    /* Fondo Obsidiana */
    .stApp {
        background-color: #050505;
    }
    
    .block-container {
        max-width: 480px !important;
        padding: 2.5rem !important;
        background-color: #0a0a0a;
        border-radius: 30px;
        border: 1px solid #1a1a1a;
        box-shadow: 0 40px 100px rgba(0,0,0,0.9);
        margin-top: 20px;
    }

    /* Pantalla Minimalista de Lujo */
    .calc-display {
        background-color: #000000;
        color: #fdfdfd;
        font-size: 75px;
        text-align: right;
        padding: 40px 20px;
        border-radius: 20px;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 200;
        margin-bottom: 30px;
        min-height: 140px;
        letter-spacing: -3px;
        border-bottom: 1px solid #222;
    }

    /* BOTONES XL - OCUPAN TODO EL ESPACIO */
    .stButton > button {
        width: 100% !important;
        height: 90px !important; 
        font-size: 26px !important;
        font-weight: 300 !important;
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #222 !important;
        border-radius: 18px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }

    /* Efecto al pasar el mouse (Sutil y Elegante) */
    .stButton > button:hover {
        background-color: #1a1a1a !important;
        border-color: #c5a059 !important; /* Brillo Dorado sutil */
        color: #c5a059 !important;
        transform: translateY(-3px);
    }

    /* Operadores en Oro Mate */
    div[data-testid="stHorizontalBlock"] div:last-child .stButton > button {
        background: linear-gradient(145deg, #c5a059, #8e6d31) !important;
        color: #000 !important;
        border: none !important;
        font-weight: 500 !important;
    }

    /* Botón AC (Gris Ceniza) */
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div:first-child .stButton > button {
        color: #666 !important;
    }

    /* Ajuste de Grid */
    div[data-testid="stHorizontalBlock"] {
        gap: 15px !important;
        margin-bottom: 15px !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA CORE ---
if 'calc_val' not in st.session_state:
    st.session_state.calc_val = "0"

def click_button(label):
    actual = st.session_state.calc_val
    if label == "AC":
        st.session_state.calc_val = "0"
    elif label == "=":
        try:
            expr = actual.replace('×', '*').replace('÷', '/')
            res = eval(expr)
            # Formato elegante para números largos
            st.session_state.calc_val = f"{res:g}" if isinstance(res, float) else str(res)
        except:
            st.session_state.calc_val = "Error"
    else:
        if actual == "0" or actual == "Error":
            st.session_state.calc_val = str(label)
        else:
            if len(actual) < 10:
                st.session_state.calc_val += str(label)

# Título Estético
st.markdown("<p style='text-align:center; color:#444; letter-spacing:5px; font-size:12px;'>PREMIUM CALCULATOR</p>", unsafe_allow_html=True)

# Pantalla
st.markdown(f'<div class="calc-display">{st.session_state.calc_val}</div>', unsafe_allow_html=True)

# Grid de botones XL
filas = [
    ['AC', '+/-', '%', '÷'],
    ['7', '8', '9', '×'],
    ['4', '5', '6', '-'],
    ['1', '2', '3', '+'],
    ['0', '.', '=']
]

for fila in filas:
    cols = st.columns(len(fila))
    for i, label in enumerate(fila):
        cols[i].button(label, key=f"btn_{label}_{filas.index(fila)}_{i}", 
                       on_click=click_button, args=(label,), 
                       use_container_width=True)
