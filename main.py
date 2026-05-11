import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random
import streamlit.components.v1 as components

# --- CONFIGURACIÓN BASE DE DATOS ---
DB_NAME = "agencia_hypercars_v1.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Inventario de Hypercars
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (modelo TEXT, marca TEXT, motorizacion TEXT, edicion TEXT, 
                           stock INTEGER, p_compra REAL, p_venta REAL, imagen TEXT,
                           PRIMARY KEY (modelo, marca, motorizacion, edicion))''')
        # Registro de Ventas/Contratos
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (transaccion_id TEXT, fecha TEXT, hora TEXT, modelo TEXT, marca TEXT, 
                           motorizacion TEXT, edicion TEXT, cantidad INTEGER, p_venta REAL, total REAL, estado TEXT)''')
        # Reservas de Clientes VIP
        cursor.execute('''CREATE TABLE IF NOT EXISTS apartados 
                          (id TEXT, cliente TEXT, fecha TEXT, modelo TEXT, marca TEXT, 
                           motorizacion TEXT, edicion TEXT, cantidad INTEGER, estado TEXT)''')
        conn.commit()

def run_query(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def get_df(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(query, conn, params=params)

# --- CARGA DE DATOS DE LUJO ---
def cargar_datos_hypercars():
    marcas_lujo = {
        "Bugatti": ["Chiron Pur Sport", "Mistral", "Bolide", "Veyron SS"],
        "Koenigsegg": ["Jesko Absolut", "Gemera", "Regera"],
        "Pagani": ["Huayra Roadster BC", "Utopia", "Zonda Cinque"],
        "Ferrari": ["SF90 XX", "LaFerrari", "Daytona SP3"],
        "Lamborghini": ["Revuelto", "Veneno", "Sian FKP 37"],
        "McLaren": ["Senna GTR", "Speedtail", "P1 LM"]
    }
    motores = ["W16 Quad-Turbo", "V12 Hybrid", "V8 Twin-Turbo Hybrid", "Tri-Motor Electric"]
    ediciones = ["Limited 1 of 10", "Carbon Fiber Edition", "Track Only", "Heritage Edition"]

    datos_agencia = []
    while len(datos_agencia) < 20:
        marca = random.choice(list(marcas_lujo.keys()))
        modelo = random.choice(marcas_lujo[marca])
        motor = random.choice(motores)
        edit = random.choice(ediciones)
        
        if not any(x[0] == modelo and x[1] == marca and x[2] == motor and x[3] == edit for x in datos_agencia):
            stock = random.randint(1, 3) # Los hypercars son escasos
            p_compra = round(random.uniform(1500000.0, 5000000.0), 2)
            p_venta = round(p_compra * 1.25, 2) 
            datos_agencia.append((modelo, marca, motor, edit, stock, p_compra, p_venta, ""))

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT OR REPLACE INTO inventario VALUES (?,?,?,?,?,?,?,?)', datos_agencia)
        conn.commit()

# --- FUNCIÓN DE IMPRESIÓN DE CONTRATO/RECIBO ---
def ejecutar_impresion(html_content):
    unique_id = str(uuid.uuid4())[:8]
    component_script = f"""
    <div id="ticket-{unique_id}" style="display:none;">{html_content}</div>
    <script>
        (function() {{
            var content = document.getElementById('ticket-{unique_id}').innerHTML;
            var win = window.open('', 'PRINT', 'height=600,width=600');
            win.document.write('<html><head><title>Certificado de Adquisición</title></head><body>' + content + '</body></html>');
            win.document.close();
            win.focus();
            win.print();
            win.close();
        }})();
    </script>
    """
    components.html(component_script, height=0)

def generar_contrato_html(titulo, id_doc, items, total, cliente=None):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    rows = "".join([f"<tr><td>{it['producto']}</td><td align='center'>{it['cantidad']}</td><td align='right'>${it['subtotal']:,.2f}</td></tr>" for it in items])
    return f"""
    <div style="font-family: 'Times New Roman', serif; width: 450px; padding: 20px; background: #1a1a1a; color: #d4af37; border: 2px solid #d4af37;">
        <center>
            <h1 style="margin:0; letter-spacing: 5px;">EXOTIC MOTORS</h1>
            <p style="font-size:14px; margin:0; text-transform: uppercase;">Certificado de Venta Hypercars</p>
        </center>
        <hr style="border-color: #d4af37;">
        <p style="font-size:12px;"><b>REFERENCIA:</b> #{id_doc}<br><b>FECHA DE ENTREGA:</b> {fecha}</p>
        {f'<p style="font-size:14px;"><b>PROPIETARIO:</b> {cliente}</p>' if cliente else ''}
        <table style="width:100%; font-size:12px; color: white;">
            <tr style="border-bottom: 1px solid #d4af37;"><th align="left">Modelo</th><th align="center">Unidades</th><th align="right">Inversión</th></tr>
            {rows}
        </table>
        <hr style="border-color: #d4af37;">
        <h2 align="right">TOTAL: ${total:,.2f}</h2>
        <center><p style="font-size:12px; font-style: italic;">Bienvenido al club más exclusivo del mundo.</p></center>
    </div>
    """

# --- INICIALIZACIÓN ---
st.set_page_config(page_title="Hypercar Agency POS", layout="wide")
init_db()

if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'ticket_a_imprimir' not in st.session_state: st.session_state.ticket_a_imprimir = None

# --- NAVEGACIÓN ---
st.sidebar.markdown("<h1 style='color: #d4af37;'>🏎️ EXOTIC POS</h1>", unsafe_allow_html=True)
menu = ["📦 Showroom (Stock)", "💰 Cerrar Trato", "📝 Reservas VIP", "📊 Reporte Financiero", "📉 Historial", "🛠 Admin"]
choice = st.sidebar.selectbox("Panel de Gestión", menu)

if st.session_state.ticket_a_imprimir:
    ejecutar_impresion(st.session_state.ticket_a_imprimir)
    st.session_state.ticket_a_imprimir = None

# --- LÓGICA DE SECCIONES ---

if choice == "📦 Showroom (Stock)":
    st.header("Inventario de Hypercars Disponibles")
    df_inv = get_df("SELECT * FROM inventario")
    if df_inv.empty:
        st.warning("El showroom está vacío.")
        if st.button("✨ Importar Colección Inicial"):
            cargar_datos_hypercars()
            st.rerun()
    else:
        st.dataframe(df_inv.style.format({"p_compra": "${:,.2f}", "p_venta": "${:,.2f}"}), use_container_width=True)

elif choice == "💰 Cerrar Trato":
    st.header("Ventanilla de Adquisición")
    df_inv = get_df("SELECT * FROM inventario WHERE stock > 0")
    
    if not df_inv.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            marca_sel = st.selectbox("Marca", sorted(df_inv['marca'].unique()))
            df_f = df_inv[df_inv['marca'] == marca_sel]
            
            mod_sel = st.selectbox("Modelo", sorted(df_f['modelo'].unique()))
            df_f = df_f[df_f['modelo'] == mod_sel]
            
            edit_sel = st.selectbox("Edición", sorted(df_f['edicion'].unique()))
            item = df_f[df_f['edicion'] == edit_sel].iloc[0]
            
            st.success(f"Motor: {item['motorizacion']} | Unidades en Showroom: {item['stock']}")
            st.markdown(f"### Precio: **${item['p_venta']:,.2f}**")
            
            if st.button("🏎️ Añadir al Contrato", use_container_width=True):
                st.session_state.carrito.append({
                    'producto': f"{item['marca']} {item['modelo']}", 'marca': item['marca'], 
                    'motorizacion': item['motorizacion'], 'edicion': item['edicion'], 
                    'cantidad': 1, 'precio': float(item['p_venta']), 'subtotal': float(item['p_venta'])
                })
                st.rerun()
            
            if st.button("🗑️ Cancelar Selección", type="secondary", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

        with c2:
            if st.session_state.carrito:
                st.subheader("Resumen de Contrato")
                df_cart = pd.DataFrame(st.session_state.carrito)
                st.table(df_cart[['producto', 'edicion', 'precio']])
                total_v = sum(i['subtotal'] for i in st.session_state.carrito)
                
                cliente = st.text_input("Nombre del Adquiriente (Comprador)")
                if st.button(f"🧾 Formalizar Venta (${total_v:,.2f})", type="primary", use_container_width=True):
                    if cliente:
                        t_id = "SALE-" + str(uuid.uuid4())[:6].upper()
                        now = datetime.now()
                        for i in st.session_state.carrito:
                            run_query("INSERT INTO ventas VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                                      (t_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), i['producto'], i['marca'], i['motorizacion'], i['edicion'], i['cantidad'], i['precio'], i['subtotal'], "VENDIDO"))
                            run_query("UPDATE inventario SET stock = stock - ? WHERE modelo=? AND marca=? AND edicion=?", (i['cantidad'], i['producto'].replace(i['marca']+" ", ""), i['marca'], i['edicion']))
                        
                        st.session_state.ticket_a_imprimir = generar_contrato_html("CERTIFICADO DE ADQUISICIÓN", t_id, st.session_state.carrito, total_v, cliente=cliente)
                        st.session_state.carrito = []
                        st.success("Trato cerrado. Certificado generado.")
                        st.rerun()
                    else: st.error("Debe ingresar el nombre del cliente.")
    else:
        st.error("No hay vehículos con stock disponible.")

elif choice == "📊 Reporte Financiero":
    st.header("Corte de Caja de Lujo")
    query_corte = """
        SELECT v.*, i.p_compra 
        FROM ventas v 
        LEFT JOIN inventario i ON v.marca = i.marca AND v.edicion = i.edicion
        WHERE v.estado = 'VENDIDO'
    """
    df_corte = get_df(query_corte)
    
    if not df_corte.empty:
        total_ventas = df_corte['total'].sum()
        total_costos = (df_corte['cantidad'] * df_corte['p_compra']).sum()
        utilidad = total_ventas - total_costos
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Ventas Totales", f"${total_ventas:,.2f}")
        m2.metric("Inversión en Flota", f"${total_costos:,.2f}")
        m3.metric("Margen de Ganancia", f"${utilidad:,.2f}")
        st.dataframe(df_corte, use_container_width=True)
    else:
        st.info("No hay ventas registradas todavía.")

elif choice == "🛠 Admin":
    st.header("Panel de Adquisiciones de la Agencia")
    if st.button("🔄 Reiniciar Showroom (Datos Demo)"):
        run_query("DELETE FROM inventario")
        cargar_datos_hypercars()
        st.success("Showroom reiniciado con nuevos Hypercars.")
        st.rerun()
