import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import uuid
import os
import random
import streamlit.components.v1 as components

# --- CONFIGURACIÓN BASE DE DATOS ---
DB_NAME = "supermercado_v14.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (producto TEXT, marca TEXT, variante TEXT, presentacion TEXT, 
                           stock INTEGER, p_compra REAL, p_venta REAL, imagen TEXT,
                           PRIMARY KEY (producto, marca, variante, presentacion))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (transaccion_id TEXT, fecha TEXT, hora TEXT, producto TEXT, marca TEXT, 
                           variante TEXT, presentacion TEXT, cantidad INTEGER, p_venta REAL, total REAL, estado TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS apartados 
                          (id TEXT, cliente TEXT, fecha TEXT, producto TEXT, marca TEXT, 
                           variante TEXT, presentacion TEXT, cantidad INTEGER, estado TEXT)''')
        conn.commit()

def run_query(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def get_df(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(query, conn, params=params)

# --- FUNCIÓN PARA CARGAR 50 DATOS DE SUPERMERCADO ---
def cargar_50_datos():
    productos_base = [
        "Leche Entera", "Arroz Blanco", "Frijol Negro", "Aceite Vegetal", 
        "Detergente Líquido", "Jabón de Trastes", "Shampoo 2en1", "Papel Higiénico",
        "Pan de Caja", "Huevo Blanco", "Atún en Agua", "Pasta de Dientes",
        "Refresco de Cola", "Jugo de Naranja", "Cereal de Maíz", "Galletas Marías",
        "Café Soluble", "Azúcar Refinada", "Sal de Mesa", "Yogurt Natural",
        "Queso Panela", "Jamón de Pavo", "Salchicha de Viena", "Mayonesa",
        "Salsa de Tomate", "Harina de Trigo", "Mantequilla", "Suavizante de Telas"
    ]
    marcas = ["Premium", "Económica", "GreatBuy", "Lux", "CampoReal", "SuperPro"]
    variantes = ["Regular", "Familiar", "Individual", "Light", "Extra", "Orgánico"]
    unidades = ["1kg", "500g", "1L", "2L", "Paquete c/4", "Pza"]

    datos_inventario = []
    while len(datos_inventario) < 50:
        prod = random.choice(productos_base)
        marc = random.choice(marcas)
        var = random.choice(variantes)
        pres = random.choice(unidades)
        
        # Evitar duplicados en la llave primaria
        if not any(x[0] == prod and x[1] == marc and x[2] == var and x[3] == pres for x in datos_inventario):
            stock = random.randint(10, 100)
            p_compra = round(random.uniform(12.0, 180.0), 2)
            p_venta = round(p_compra * 1.30, 2) # Margen del 30%
            datos_inventario.append((prod, marc, var, pres, stock, p_compra, p_venta, ""))

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT OR REPLACE INTO inventario VALUES (?,?,?,?,?,?,?,?)', datos_inventario)
        conn.commit()

# --- FUNCIÓN DE IMPRESIÓN ---
def ejecutar_impresion(html_content):
    unique_id = str(uuid.uuid4())[:8]
    component_script = f"""
    <div id="ticket-{unique_id}" style="display:none;">{html_content}</div>
    <script>
        (function() {{
            var content = document.getElementById('ticket-{unique_id}').innerHTML;
            var win = window.open('', 'PRINT', 'height=600,width=400');
            win.document.write('<html><head><title>Imprimir Ticket</title></head><body>' + content + '</body></html>');
            win.document.close();
            win.focus();
            win.print();
            win.close();
        }})();
    </script>
    """
    components.html(component_script, height=0)

def generar_ticket_html(titulo, id_doc, items, total, cliente=None):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    rows = "".join([f"<tr><td>{it['producto']}</td><td align='center'>{it['cantidad']}</td><td align='right'>${it['subtotal']:,.2f}</td></tr>" for it in items])
    return f"""
    <div style="font-family: 'Courier New', monospace; width: 250px; padding: 10px; background: white; color: black; border: 1px solid #ddd;">
        <center><h2 style="margin:0;">SUPER MARKET</h2><p style="font-size:12px; margin:0;">Punto de Venta</p></center>
        <hr>
        <p style="font-size:11px;"><b>{titulo}</b>: #{id_doc}<br><b>Fecha:</b> {fecha}</p>
        {f'<p style="font-size:11px;"><b>Cliente:</b> {cliente}</p>' if cliente else ''}
        <table style="width:100%; font-size:10px;">
            <tr><th align="left">Prod</th><th align="center">Cant</th><th align="right">Subt</th></tr>
            {rows}
        </table>
        <hr><h3 align="right">TOTAL: ${total:,.2f}</h3>
        <center><p style="font-size:10px;">¡Gracias por su compra!</p></center>
    </div>
    """

# --- INICIALIZACIÓN ---
st.set_page_config(page_title="SuperMarket POS v14", layout="wide")
init_db()

if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'ticket_a_imprimir' not in st.session_state: st.session_state.ticket_a_imprimir = None

# --- NAVEGACIÓN ---
st.sidebar.title("🏪 SISTEMA POS")
menu = ["📦 Inventario", "🛒 Punto de Venta", "📝 Apartados", "📊 Corte de Caja", "📉 Historial", "🛠 Admin"]
choice = st.sidebar.selectbox("Seleccione opción", menu)

if st.session_state.ticket_a_imprimir:
    ejecutar_impresion(st.session_state.ticket_a_imprimir)
    st.session_state.ticket_a_imprimir = None

# --- LÓGICA DE SECCIONES ---

if choice == "📦 Inventario":
    st.header("Inventario de Productos")
    df_inv = get_df("SELECT * FROM inventario")
    if df_inv.empty:
        st.warning("El inventario está vacío.")
        if st.button("✨ Generar 50 Productos de Supermercado"):
            cargar_50_datos()
            st.rerun()
    else:
        st.dataframe(df_inv, use_container_width=True)

elif choice == "🛒 Punto de Venta":
    st.header("Ventanilla de Cobro")
    df_inv = get_df("SELECT * FROM inventario WHERE stock > 0")
    
    if not df_inv.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            prod_sel = st.selectbox("Producto", sorted(df_inv['producto'].unique()))
            df_f = df_inv[df_inv['producto'] == prod_sel]
            
            marc_sel = st.selectbox("Marca", sorted(df_f['marca'].unique()))
            df_f = df_f[df_f['marca'] == marc_sel]
            
            pres_sel = st.selectbox("Presentación", sorted(df_f['presentacion'].unique()))
            item = df_f[df_f['presentacion'] == pres_sel].iloc[0]
            
            st.info(f"Disponible: {item['stock']} | Precio: ${item['p_venta']:,.2f}")
            cant = st.number_input("Cantidad a vender", 1, int(item['stock']))
            
            if st.button("➕ Agregar a la cuenta", use_container_width=True):
                st.session_state.carrito.append({
                    'producto': item['producto'], 'marca': item['marca'], 'variante': item['variante'],
                    'presentacion': item['presentacion'], 'cantidad': int(cant), 
                    'precio': float(item['p_venta']), 'subtotal': float(item['p_venta']*cant)
                })
                st.rerun()
            
            if st.button("🗑️ Vaciar Carrito", type="secondary", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

        with c2:
            if st.session_state.carrito:
                st.subheader("Resumen de Compra")
                df_cart = pd.DataFrame(st.session_state.carrito)
                st.table(df_cart[['producto', 'presentacion', 'cantidad', 'subtotal']])
                total_v = sum(i['subtotal'] for i in st.session_state.carrito)
                
                if st.button(f"✅ Cobrar e Imprimir Ticket (${total_v:,.2f})", type="primary", use_container_width=True):
                    t_id = str(uuid.uuid4())[:8].upper()
                    now = datetime.now()
                    for i in st.session_state.carrito:
                        run_query("INSERT INTO ventas VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                                  (t_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), i['producto'], i['marca'], i['variante'], i['presentacion'], i['cantidad'], i['precio'], i['subtotal'], "COMPLETADA"))
                        run_query("UPDATE inventario SET stock = stock - ? WHERE producto=? AND marca=? AND presentacion=?", (i['cantidad'], i['producto'], i['marca'], i['presentacion']))
                    
                    st.session_state.ticket_a_imprimir = generar_ticket_html("TICKET DE VENTA", t_id, st.session_state.carrito, total_v)
                    st.session_state.carrito = []
                    st.success("Venta procesada con éxito.")
                    st.rerun()
    else:
        st.error("No hay productos con stock disponible.")

elif choice == "📝 Apartados":
    st.header("Pedidos / Apartados de Clientes")
    df_inv = get_df("SELECT * FROM inventario WHERE stock > 0")
    if not df_inv.empty:
        with st.form("ap_f"):
            cli = st.text_input("Nombre del Cliente")
            df_inv['lbl'] = df_inv['producto'] + " (" + df_inv['presentacion'] + ") - " + df_inv['marca']
            sel = st.selectbox("Seleccionar Producto", df_inv['lbl'])
            cnt = st.number_input("Cantidad", 1)
            if st.form_submit_button("Guardar Pedido"):
                r = df_inv[df_inv['lbl'] == sel].iloc[0]
                ap_id = "PED-" + str(uuid.uuid4())[:4].upper()
                run_query("INSERT INTO apartados VALUES (?,?,?,?,?,?,?,?,?)", 
                          (ap_id, cli, datetime.now().strftime("%Y-%m-%d"), r['producto'], r['marca'], r['variante'], r['presentacion'], cnt, "PENDIENTE"))
                run_query("UPDATE inventario SET stock = stock - ? WHERE producto=? AND marca=? AND presentacion=?", (cnt, r['producto'], r['marca'], r['presentacion']))
                st.session_state.ticket_a_imprimir = generar_ticket_html("VALE DE PEDIDO", ap_id, [{'producto': r['producto'], 'cantidad': cnt, 'subtotal': r['p_venta']*cnt}], r['p_venta']*cnt, cliente=cli)
                st.rerun()

elif choice == "📊 Corte de Caja":
    st.header("Reporte de Ventas y Utilidades")
    periodo = st.radio("Periodo:", ["Hoy", "Esta Semana", "Este Mes"], horizontal=True)
    hoy = datetime.now()
    if periodo == "Hoy": f_inicio = hoy.strftime("%Y-%m-%d")
    elif periodo == "Esta Semana": f_inicio = (hoy - timedelta(days=hoy.weekday())).strftime("%Y-%m-%d")
    else: f_inicio = hoy.strftime("%Y-%m-01")
    
    query_corte = """
        SELECT v.*, i.p_compra 
        FROM ventas v 
        LEFT JOIN inventario i ON v.producto = i.producto AND v.marca = i.marca AND v.presentacion = i.presentacion
        WHERE v.fecha >= ? AND v.estado = 'COMPLETADA'
    """
    df_corte = get_df(query_corte, (f_inicio,))
    
    if not df_corte.empty:
        total_ventas = df_corte['total'].sum()
        # Cálculo de utilidad basado en costo real
        total_costos = (df_corte['cantidad'] * df_corte['p_compra']).sum()
        utilidad = total_ventas - total_costos
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos Totales", f"${total_ventas:,.2f}")
        m2.metric("Inversión en Productos", f"${total_costos:,.2f}")
        m3.metric("Utilidad Estimada", f"${utilidad:,.2f}")
        st.dataframe(df_corte, use_container_width=True)
    else:
        st.info("No se registran ventas en el periodo seleccionado.")

elif choice == "📉 Historial":
    st.header("Bitácora General")
    tab1, tab2 = st.tabs(["Ventas Realizadas", "Pedidos / Apartados"])
    with tab1:
        st.dataframe(get_df("SELECT * FROM ventas ORDER BY fecha DESC, hora DESC"), use_container_width=True)
    with tab2:
        st.dataframe(get_df("SELECT * FROM apartados"), use_container_width=True)

elif choice == "🛠 Admin":
    st.header("Panel de Administración")
    with st.expander("Añadir Nuevo Producto Manualmente"):
        with st.form("adm"):
            c1, c2 = st.columns(2)
            p = c1.text_input("Nombre del Producto")
            m = c2.text_input("Marca")
            v = c1.text_input("Variante (ej. Light)")
            t = c2.text_input("Presentación (ej. 1kg)")
            s = st.number_input("Stock Inicial", 0)
            pc = st.number_input("Costo de Compra", 0.0)
            pv = st.number_input("Precio de Venta", 0.0)
            if st.form_submit_button("Registrar en Inventario"):
                if p and m:
                    run_query("INSERT OR REPLACE INTO inventario VALUES (?,?,?,?,?,?,?,?)", (p,m,v,t,s,pc,pv,""))
                    st.success(f"{p} registrado correctamente.")
                else: st.error("Producto y Marca son obligatorios.")
    
    if st.button("🔄 Resetear y Cargar 50 Productos Demo"):
        run_query("DELETE FROM inventario")
        cargar_50_datos()
        st.success("Inventario reiniciado con datos de supermercado.")
        st.rerun()
