import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_NAME = "agencia_hypercars_pro.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (modelo TEXT, marca TEXT, motor TEXT, edicion TEXT, 
                           stock INTEGER, p_compra REAL, p_venta REAL, imagen_url TEXT,
                           PRIMARY KEY (modelo, marca, edicion))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (transaccion_id TEXT, fecha TEXT, vehiculo TEXT, total REAL, cliente TEXT)''')
        conn.commit()

# --- DATOS REALES (AQUÍ METES LOS LINKS A MANO) ---
def cargar_70_hypercars():
    # FORMATO: (Modelo, Marca, Motor, Edición, Stock, Compra, Venta, "LINK_DE_GOOGLE_AQUÍ")
    autos = [
        ("Chiron Super Sport 300+", "Bugatti", "8.0L W16 Quad-Turbo", "Record Edition", 1, 3.2, 3.9, "https://tu-link-aqui.com/imagen.jpg"),
        ("Jesko Absolut", "Koenigsegg", "5.0L V8 Twin-Turbo", "Top Speed", 1, 2.5, 3.1, ""),
        ("Utopia", "Pagani", "6.0L V12 Twin-Turbo", "Manual Heritage", 1, 2.1, 2.5, ""),
        ("Veneno Roadster", "Lamborghini", "6.5L V12 N/A", "Anniversary", 1, 4.0, 4.5, ""),
        ("Valkyrie AMR Pro", "Aston Martin", "6.5L V12 Cosworth", "Track Only", 1, 3.1, 3.5, ""),
        ("Nevera", "Rimac", "Quad-Motor Electric", "Time Attack", 2, 1.8, 2.2, ""),
        ("Solus GT", "McLaren", "5.2L V10 N/A", "Single Seater", 1, 2.0, 2.4, ""),
        ("Daytona SP3", "Ferrari", "6.5L V12 N/A", "Icona Series", 1, 2.0, 2.3, ""),
        ("Gemera", "Koenigsegg", "2.0L i3 TFG Hybrid", "Founders Edition", 2, 1.5, 1.7, ""),
        ("Mistral", "Bugatti", "8.0L W16 Quad-Turbo", "Final W16", 1, 4.5, 5.0, ""),
        # ... Sigue llenando hasta los 70 registros
    ]
    
    # Relleno automático de marcas reales para completar los 70 (Tú puedes editar estos nombres abajo)
    marcas_pool = ["Ferrari", "Lamborghini", "McLaren", "Bugatti", "Pagani", "Koenigsegg", "Hennessey", "Aston Martin"]
    while len(autos) < 70:
        m = marcas_pool[len(autos) % len(marcas_pool)]
        autos.append((f"Hyper-Model {len(autos)}", m, "V12 Twin-Turbo", "Limited Edition", 1, 1.5, 1.9, ""))

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT OR REPLACE INTO inventario VALUES (?,?,?,?,?,?,?,?)', autos)
        conn.commit()

# --- ESTILOS CSS ---
def aplicar_estilos():
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .car-card {
            background-color: #1a1c23;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #d4af37;
            text-align: center;
            margin-bottom: 25px;
            transition: transform 0.3s;
        }
        .car-card:hover { transform: scale(1.02); }
        .img-container {
            width: 100%;
            height: 220px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #000;
            border-radius: 10px;
        }
        .img-container img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain; /* Mantiene proporción sin deformar */
        }
        .price-text {
            color: #d4af37;
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)

# --- LÓGICA PRINCIPAL ---
st.set_page_config(page_title="Hypercar Agency", layout="wide")
aplicar_estilos()
init_db()

# Carga inicial si la DB está vacía
db_check = sqlite3.connect(DB_NAME)
if pd.read_sql_query("SELECT COUNT(*) FROM inventario", db_check).iloc[0,0] == 0:
    cargar_70_hypercars()
db_check.close()

st.sidebar.title("💎 EXOTIC MOTORS")
menu = ["Autos Principales", "Inventario", "Cerrar Venta"]
choice = st.sidebar.selectbox("Navegación", menu)

if choice == "Autos Principales":
    st.title("🏛️ Showroom: Autos Principales")
    df = pd.read_sql_query("SELECT * FROM inventario", sqlite3.connect(DB_NAME))
    
    cols = st.columns(3)
    for idx, row in df.iterrows():
        with cols[idx % 3]:
            # Imagen por defecto si el link está vacío en el código
            img_src = row['imagen_url'] if row['imagen_url'] != "" else "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?q=80&w=1000&auto=format&fit=crop"
            
            st.markdown(f"""
                <div class="car-card">
                    <div class="img-container">
                        <img src="{img_src}">
                    </div>
                    <h2 style="color:white; margin-top:15px;">{row['marca']}</h2>
                    <h4 style="color:#aaa;">{row['modelo']}</h4>
                    <p class="price-text">${row['p_venta']:,.1f}M USD</p>
                    <p style="font-size:13px; color:#777;">{row['edicion']} | {row['motor']}</p>
                </div>
                """, unsafe_allow_html=True)

elif choice == "Inventario":
    st.title("📋 Registro Técnico de Inventario")
    df_inv = pd.read_sql_query("SELECT marca, modelo, edicion, motor, stock, p_venta FROM inventario", sqlite3.connect(DB_NAME))
    
    # Formateo visual de la tabla
    df_inv['p_venta'] = df_inv['p_venta'].apply(lambda x: f"${x:,.2f}M USD")
    st.dataframe(df_inv, use_container_width=True, height=700)

elif choice == "Cerrar Venta":
    st.title("🤝 Finalizar Negociación")
    
    with sqlite3.connect(DB_NAME) as conn:
        disponibles = pd.read_sql_query("SELECT * FROM inventario WHERE stock > 0", conn)
    
    c1, c2 = st.columns(2)
    with c1:
        seleccion = st.selectbox("Vehículo a Entregar", disponibles['marca'] + " " + disponibles['modelo'])
        cliente = st.text_input("Nombre del Cliente VIP")
        
        # Datos del auto seleccionado
        auto = disponibles[disponibles['marca'] + " " + disponibles['modelo'] == seleccion].iloc[0]
        
        st.info(f"**Monto de Operación:** ${auto['p_venta']:,.1f}M USD")
        
        if st.button("Confirmar Venta y Generar Registro"):
            if cliente:
                t_id = "TRANS-" + str(uuid.uuid4())[:6].upper()
                # Guardar venta
                with sqlite3.connect(DB_NAME) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO ventas VALUES (?,?,?,?,?)", 
                                  (t_id, datetime.now().strftime("%Y-%m-%d"), seleccion, auto['p_venta'], cliente))
                    cursor.execute("UPDATE inventario SET stock = stock - 1 WHERE modelo = ?", (auto['modelo'],))
                    conn.commit()
                st.balloons()
                st.success(f"Operación Exitosa: {seleccion} asignado a {cliente}.")
            else:
                st.error("Se requiere el nombre del adquirente.")

    with c2:
        st.subheader("Últimas Adquisiciones")
        historial = pd.read_sql_query("SELECT fecha, vehiculo, cliente FROM ventas ORDER BY fecha DESC", sqlite3.connect(DB_NAME))
        st.table(historial)
