import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid
import streamlit.components.v1 as components

# --- CONFIGURACIÓN BASE DE DATOS ---
DB_NAME = "exotic_hypercars_real.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (modelo TEXT, marca TEXT, motor TEXT, edicion TEXT, 
                           stock INTEGER, p_compra REAL, p_venta REAL,
                           PRIMARY KEY (modelo, marca, edicion))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (transaccion_id TEXT, fecha TEXT, hora TEXT, vehiculo TEXT, 
                           cantidad INTEGER, p_venta REAL, total REAL, cliente TEXT)''')
        conn.commit()

def run_query(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

# --- DATOS REALES DE HYPERCARS ---
def cargar_inventario_real():
    # Estructura: (Modelo, Marca, Motor Exacto, Edición, Stock, P.Compra, P.Venta)
    # Precios en USD (Aproximados de mercado para unidades nuevas/colección)
    autos_reales = [
        ("Chiron Super Sport 300+", "Bugatti", "8.0L W16 Quad-Turbo", "Record Edition", 1, 3500000.0, 3900000.0),
        ("Jesko Absolut", "Koenigsegg", "5.0L V8 Twin-Turbo", "Top Speed Edition", 1, 2800000.0, 3100000.0),
        ("Huayra Roadster BC", "Pagani", "6.0L V12 Twin-Turbo (AMG)", "Benny Caiola Edition", 1, 3200000.0, 3500000.0),
        ("Revuelto", "Lamborghini", "6.5L V12 Hybrid", "Launch Edition", 2, 600000.0, 890000.0),
        ("Utopia", "Pagani", "6.0L V12 Twin-Turbo", "First Delivery", 1, 2200000.0, 2500000.0),
        ("SF90 XX Stradale", "Ferrari", "4.0L V8 Plug-in Hybrid", "XX Programme", 1, 850000.0, 1100000.0),
        ("Speedtail", "McLaren", "4.0L V8 Hybrid", "HyperGT Edition", 1, 2100000.0, 2400000.0),
        ("Valkyrie", "Aston Martin", "6.5L V12 Cosworth Hybrid", "Track Pack", 1, 3000000.0, 3250000.0),
        ("Nevera", "Rimac", "Quad-Motor Electric (1914 hp)", "Time Attack", 1, 2000000.0, 2200000.0),
        ("T.50", "Gordon Murray", "3.9L V12 Cosworth N/A", "Launch Edition", 1, 2500000.0, 2800000.0)
    ]
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT OR REPLACE INTO inventario VALUES (?,?,?,?,?,?,?)', autos_reales)
        conn.commit()

# --- FUNCIÓN DE IMPRESIÓN ---
def ejecutar_impresion(html_content):
    unique_id = str(uuid.uuid4())[:8]
    component_script = f"""
    <div id="ticket-{unique_id}" style="display:none;">{html_content}</div>
    <script>
        (function() {{
            var content = document.getElementById('ticket-{unique_id}').innerHTML;
            var win = window.open('', 'PRINT', 'height=600,width=800');
            win.document.write('<html><head><title>Contrato de Compra</title></head><body>' + content + '</body></html>');
            win.document.close();
            win.focus();
            win.print();
            win.close();
        }})();
    </script>
    """
    components.html(component_script, height=0)

def generar_ticket_html(titulo, id_doc, items, total, cliente):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    rows = "".join([f"<tr><td style='padding:10px; border-bottom:1px solid #eee;'>{it['vehiculo']}</td><td align='right'>${it['subtotal']:,.2f}</td></tr>" for it in items])
    return f"""
    <div style="font-family: 'Arial', sans-serif; width: 500px; padding: 30px; border: 5px solid #000; background: #fff; color: #333;">
        <center>
            <h1 style="margin:0; letter-spacing: 2px;">EXOTIC MOTORS</h1>
            <p style="font-size:12px; color: #666;">CERTIFICADO OFICIAL DE ADQUISICIÓN</p>
        </center>
        <hr>
        <p><b>ID DE TRACCIÓN:</b> {id_doc}</p>
        <p><b>PROPIETARIO:</b> {cliente}</p>
        <p><b>FECHA:</b> {fecha}</p>
        <table style="width:100%; margin-top:20px; border-collapse: collapse;">
            <thead><tr style="background:#f4f4f4;"><th align="left" style="padding:10px;">VEHÍCULO / MOTOR</th><th align="right" style="padding:10px;">MONTO (USD)</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        <h2 align="right" style="margin-top:30px; color: #b8860b;">TOTAL: ${total:,.2f}</h2>
        <p style="font-size:10px; color: #999; margin-top:50px; text-align:center;">Este documento acredita la propiedad legal del vehículo descrito arriba bajo las regulaciones de Exotic Motors S.A.</p>
    </div>
    """

# --- APP STREAMLIT ---
st.set_page_config(page_title="Hypercars Registry", layout="wide")
init_db()

# Cargar datos por primera vez si está vacío
if pd.read_sql_query("SELECT COUNT(*) FROM inventario", sqlite3.connect(DB_NAME)).iloc[0,0] == 0:
    cargar_inventario_real()

st.sidebar.title("🏎️ EXOTIC REGISTRY")
opcion = st.sidebar.selectbox("Menú", ["Showroom", "Cerrar Venta", "Historial de Dueños"])

if opcion == "Showroom":
    st.header("Disponibilidad de Hypercars")
    df = pd.read_sql_query("SELECT * FROM inventario", sqlite3.connect(DB_NAME))
    # Formateo de precios para visualización
    df['p_venta'] = df['p_venta'].apply(lambda x: f"${x:,.2f} USD")
    st.table(df)

elif opcion == "Cerrar Venta":
    st.header("Formalización de Venta")
    with sqlite3.connect(DB_NAME) as conn:
        inventario = pd.read_sql_query("SELECT * FROM inventario WHERE stock > 0", conn)
    
    if not inventario.empty:
        c1, c2 = st.columns(2)
        with c1:
            seleccion = st.selectbox("Seleccione Vehículo", inventario['marca'] + " " + inventario['modelo'] + " (" + inventario['edicion'] + ")")
            cliente = st.text_input("Nombre del Comprador")
            
            # Extraer info del seleccionado
            idx = inventario.index[inventario['marca'] + " " + inventario['modelo'] + " (" + inventario['edicion'] + ")" == seleccion][0]
            auto = inventario.iloc[idx]
            
            st.info(f"**Especificaciones:**\n\nMotor: {auto['motor']}\n\nPrecio: ${auto['p_venta']:,.2f} USD")
            
            if st.button("🤝 Cerrar Trato e Imprimir Contrato"):
                if cliente:
                    t_id = str(uuid.uuid4())[:8].upper()
                    now = datetime.now()
                    
                    # Registrar venta
                    run_query("INSERT INTO ventas VALUES (?,?,?,?,?,?,?,?)", 
                              (t_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), seleccion, 1, auto['p_venta'], auto['p_venta'], cliente))
                    
                    # Descontar stock
                    run_query("UPDATE inventario SET stock = stock - 1 WHERE modelo=? AND edicion=?", (auto['modelo'], auto['edicion']))
                    
                    # Generar Ticket
                    items_ticket = [{'vehiculo': f"{seleccion} - {auto['motor']}", 'subtotal': auto['p_venta']}]
                    html_ticket = generar_ticket_html("CONTRATO", t_id, items_ticket, auto['p_venta'], cliente)
                    ejecutar_impresion(html_ticket)
                    
                    st.success(f"¡Felicidades {cliente}! El {auto['modelo']} ha sido registrado a su nombre.")
                    st.rerun()
                else:
                    st.error("Es necesario el nombre del cliente para el contrato.")
    else:
        st.error("No hay unidades disponibles en el showroom.")

elif opcion == "Historial de Dueños":
    st.header("Registro Histórico de Ventas")
    df_ventas = pd.read_sql_query("SELECT * FROM ventas", sqlite3.connect(DB_NAME))
    if not df_ventas.empty:
        st.dataframe(df_ventas, use_container_width=True)
    else:
        st.write("No se han realizado transacciones aún.")
