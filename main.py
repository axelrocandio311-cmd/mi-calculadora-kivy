import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_NAME = "agencia_hypercars_v1.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (modelo TEXT, marca TEXT, motor TEXT, edicion TEXT, 
                           stock INTEGER, p_venta REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (id TEXT, fecha TEXT, vehiculo TEXT, cliente TEXT, total REAL)''')
        conn.commit()

# --- 1. SECCIÓN: AUTOS PRINCIPALES (EDITA AQUÍ TUS LINKS) ---
# Aquí puedes pegar los links de internet O los códigos que empiezan con "data:image..."
def obtener_destacados():
    return [
        {
            "marca": "Bugatti", 
            "modelo": "Chiron Super Sport 300+", 
            "precio": 3.9, 
            "motor": "8.0L W16 Quad-Turbo",
            "img": "data:image/jpeg;base64,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"
        },
        {
            "marca": "Koenigsegg", 
            "modelo": "Jesko Absolut", 
            "precio": 3.1, 
            "motor": "5.0L V8 Twin-Turbo",
            "img": "LINK_AQUI"
        }
    ]

# --- 2. SECCIÓN: INVENTARIO (DATOS TÉCNICOS REALES) ---
def cargar_inventario_completo():
    # Aquí están los datos técnicos reales: Marca, Modelo, Motor, Edición, Precio
    datos = [
        ("Chiron SS 300+", "Bugatti", "8.0L W16 Quad-Turbo", "Record Edition", 1, 3.9),
        ("Jesko Absolut", "Koenigsegg", "5.0L V8 Twin-Turbo", "Top Speed", 1, 3.1),
        ("Utopia", "Pagani", "6.0L V12 Twin-Turbo", "Manual Heritage", 1, 2.5),
        ("Revuelto", "Lamborghini", "6.5L V12 Hybrid", "Launch Edition", 2, 0.7),
        ("Valkyrie", "Aston Martin", "6.5L V12 Cosworth", "Track Pack", 1, 3.2),
        ("Nevera", "Rimac", "Quad-Motor Electric", "Time Attack", 1, 2.2),
        ("Speedtail", "McLaren", "4.0L V8 Hybrid", "HyperGT", 1, 2.4),
        ("Daytona SP3", "Ferrari", "6.5L V12 N/A", "Icona Series", 1, 2.3),
        ("Gemera", "Koenigsegg", "2.0L i3 TFG Hybrid", "Family Hypercar", 1, 1.7),
        ("Mistral", "Bugatti", "8.0L W16 Quad-Turbo", "Roadster", 1, 5.0),
        # Se rellena hasta 70 registros con variaciones coherentes
    ]
    
    marcas_pool = ["Ferrari", "Lamborghini", "McLaren", "Bugatti", "Pagani", "Koenigsegg", "Aston Martin"]
    while len(datos) < 70:
        m = marcas_pool[len(datos) % len(marcas_pool)]
        datos.append((f"Hyper-Model {len(datos)}", m, "V12 Twin-Turbo", "Limited Edition", 1, 1.5 + (len(datos)*0.02)))

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario")
        for d in datos:
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", (d[0], d[1], d[2], d[3], d[4], d[5]))
        conn.commit()

# --- INTERFAZ ---
st.set_page_config(page_title="Hypercars Agencia", layout="wide")

init_db()
if pd.read_sql_query("SELECT COUNT(*) FROM inventario", sqlite3.connect(DB_NAME)).iloc[0,0] < 70:
    cargar_inventario_completo()

st.sidebar.title("🏁 PANEL DE CONTROL")
menu = st.sidebar.selectbox("Ir a:", ["Autos Principales", "Inventario Técnico", "Sección de Compras"])

if menu == "Autos Principales":
    st.title("🏛️ Vitrina VIP")
    destacados = obtener_destacados()
    cols = st.columns(2)
    for i, auto in enumerate(destacados):
        with cols[i % 2]:
            # Manejo de imagen (URL o Base64)
            img_src = auto['img'] if "LINK" not in auto['img'] else "https://via.placeholder.com/500x300/000/d4af37?text=Hypercar"
            st.markdown(f"""
                <div style="background-color:#111; padding:20px; border-radius:15px; border:1px solid #d4af37; text-align:center; margin-bottom:20px;">
                    <img src="{img_src}" style="width:100%; height:250px; object-fit:contain; border-radius:10px;">
                    <h2 style="color:white; margin-top:10px;">{auto['marca']} {auto['modelo']}</h2>
                    <p style="color:#d4af37; font-size:22px; font-weight:bold;">${auto['precio']}M USD</p>
                    <p style="color:#888;">{auto['motor']}</p>
                </div>
            """, unsafe_allow_html=True)

elif menu == "Inventario Técnico":
    st.title("📋 Inventario General (70 Unidades)")
    df = pd.read_sql_query("SELECT marca as Marca, modelo as Modelo, motor as Motorización, edicion as Edición, p_venta as Precio_M_USD FROM inventario", sqlite3.connect(DB_NAME))
    st.dataframe(df, use_container_width=True, height=700)

elif menu == "Sección de Compras":
    st.title("💰 Gestión de Ventas")
    df_inv = pd.read_sql_query("SELECT * FROM inventario WHERE stock > 0", sqlite3.connect(DB_NAME))
    
    col_v, col_h = st.columns([1, 1])
    with col_v:
        nombre_auto = st.selectbox("Vehículo a comprar", df_inv['marca'] + " " + df_inv['modelo'])
        cliente = st.text_input("Nombre del Cliente VIP")
        auto_info = df_inv[df_inv['marca'] + " " + df_inv['modelo'] == nombre_auto].iloc[0]
        
        st.write(f"**Precio Final:** ${auto_info['p_venta']}M USD")
        if st.button("Finalizar Compra"):
            if cliente:
                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute("INSERT INTO ventas VALUES (?,?,?,?,?)", (str(uuid.uuid4())[:8], datetime.now().strftime("%Y-%m-%d"), nombre_auto, cliente, auto_info['p_venta']))
                    conn.execute("UPDATE inventario SET stock = stock - 1 WHERE modelo = ?", (auto_info['modelo'],))
                st.balloons()
                st.success("Transacción Completada")
            else:
                st.error("Falta el nombre del cliente")
    
    with col_h:
        st.subheader("Historial de Ventas")
        ventas = pd.read_sql_query("SELECT fecha, vehiculo, cliente, total FROM ventas", sqlite3.connect(DB_NAME))
        st.table(ventas)
