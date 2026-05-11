import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_NAME = "agencia_hypercars_visual.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (modelo TEXT, marca TEXT, motor TEXT, precio REAL)''')
        conn.commit()

# --- 1. SECCIÓN DE AUTOS PRINCIPALES (EDITA AQUÍ TUS LINKS) ---
# Aquí es donde pondrás manualmente los autos que quieres que brillen en la vitrina
def obtener_autos_principales():
    return [
        {
            "marca": "Bugatti", 
            "modelo": "Chiron Super Sport", 
            "precio": "3.9M USD", 
            "imagen": "LINK_DE_GOOGLE_AQUI"
        },
        {
            "marca": "Koenigsegg", 
            "modelo": "Jesko Absolut", 
            "precio": "3.1M USD", 
            "imagen": "LINK_DE_GOOGLE_AQUI"
        },
        {
            "marca": "Ferrari", 
            "modelo": "LaFerrari", 
            "precio": "4.0M USD", 
            "imagen": "LINK_DE_GOOGLE_AQUI"
        },
        {
            "marca": "Pagani", 
            "modelo": "Huayra BC", 
            "precio": "3.5M USD", 
            "imagen": "LINK_DE_GOOGLE_AQUI"
        }
    ]

# --- 2. SECCIÓN DE INVENTARIO (LOS 70 REGISTROS TÉCNICOS) ---
def cargar_70_registros_inventario():
    marcas = ["Ferrari", "Lamborghini", "McLaren", "Bugatti", "Pagani", "Koenigsegg", "Aston Martin", "Rimac"]
    autos_inv = []
    for i in range(1, 71):
        m = marcas[i % len(marcas)]
        autos_inv.append((f"Modelo Spec-{i}", m, "V12 / Hybrid", 1.5 + (i * 0.1)))
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario")
        cursor.executemany('INSERT INTO inventario VALUES (?,?,?,?)', autos_inv)
        conn.commit()

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Hypercar Agency", layout="wide")

st.markdown("""
    <style>
    .vitrina-card {
        background-color: #1a1c23;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #d4af37;
        text-align: center;
        margin-bottom: 25px;
    }
    .img-vitrina {
        width: 100%;
        height: 250px;
        background-color: #000;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .img-vitrina img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
    .precio-v { color: #d4af37; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

init_db()
cargar_70_registros_inventario()

# --- NAVEGACIÓN ---
st.sidebar.title("💎 EXOTIC MOTORS")
menu = st.sidebar.selectbox("Ir a:", ["Autos Principales", "Inventario"])

if menu == "Autos Principales":
    st.title("🏛️ Vitrina de Exhibición")
    st.write("Selección exclusiva de la agencia con imágenes reales.")
    
    autos_destacados = obtener_autos_principales()
    
    cols = st.columns(2) # Dos autos por fila para que se vean grandes
    for idx, auto in enumerate(autos_destacados):
        with cols[idx % 2]:
            # Imagen por defecto si no has puesto el link
            img_url = auto['imagen'] if "LINK" not in auto['imagen'] else "https://via.placeholder.com/600x400/000/d4af37?text=Hypercar+VIP"
            
            st.markdown(f"""
                <div class="vitrina-card">
                    <div class="img-vitrina"><img src="{img_url}"></div>
                    <h2 style="margin-top:15px; color:white;">{auto['marca']} {auto['modelo']}</h2>
                    <p class="precio-v">{auto['precio']}</p>
                </div>
            """, unsafe_allow_html=True)

elif menu == "Inventario":
    st.title("📋 Registro General de Inventario")
    st.write("Listado técnico de los 70 vehículos en stock.")
    
    df = pd.read_sql_query("SELECT marca as Marca, modelo as Modelo, motor as Motorización, precio as 'Precio (M USD)' FROM inventario", sqlite3.connect(DB_NAME))
    
    st.dataframe(df, use_container_width=True, height=800)
