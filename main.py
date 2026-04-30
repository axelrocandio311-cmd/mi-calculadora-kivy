import streamlit as st

# 1. CONFIGURACIÓN DE AGENCIA
st.set_page_config(
    page_title="Hiperpropulsor Élite | Distribuidor Privado",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. ESTILOS DE AGENCIA (CSS MEJORADO PARA LINKS DINÁMICOS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@200;400;700&display=swap');

    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    h1, h2, h3, .price { font-family: 'Cinzel', serif; }
    p, div { font-family: 'Inter', sans-serif; }

    .header-container {
        text-align: center;
        padding: 40px 0 20px 0;
        background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
        border-bottom: 1px solid #222;
        margin-bottom: 40px;
    }
    
    .main-title {
        font-size: 50px;
        letter-spacing: 10px;
        color: #ffffff;
        margin: 0;
        font-weight: 700;
    }

    .car-card {
        background: #111111;
        border: 1px solid #222;
        border-radius: 4px;
        margin-bottom: 20px;
        transition: 0.4s;
        overflow: hidden; /* Asegura que la imagen no se salga */
    }

    .car-card:hover { border-color: #9c854e; }

    /* CONTENEDOR DE IMAGEN UNIVERSAL */
    .img-frame {
        width: 100%;
        height: 230px;
        background-color: #1a1a1a;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .img-frame img {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Mantiene la proporción sin importar el link */
    }

    .car-info { padding: 20px; border-top: 1px solid #222; }

    .car-name {
        font-size: 18px;
        color: #ffffff;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .car-specs {
        color: #666;
        font-size: 11px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    .car-price {
        color: #9c854e;
        font-size: 18px;
        font-weight: 700;
    }

    .stButton > button {
        width: 100%;
        background-color: transparent !important;
        color: #9c854e !important;
        border: 1px solid #444 !important;
        border-radius: 0px !important;
        padding: 8px 0 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
    }

    .stButton > button:hover {
        border-color: #9c854e !important;
        background-color: #9c854e !important;
        color: #000 !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">HIPERPROPULSOR ÉLITE</h1>
        <p style="color: #9c854e; letter-spacing: 3px; font-size: 11px; margin-top: 10px;">
            SALA DE EXPOSICIÓN PRIVADA OFICIAL • COLECCIÓN 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

# 4. INVENTARIO (Ahora acepta links de Google Imágenes y otros formatos)
inventory = [
    {
        "brand": "Bugatti",
        "model": "ROADSTER W16 MISTRAL",
        "specs": "W16 QUADTURBO • 1600 CV • EDICIÓN BLACK CARBON",
        "price": "5.000.000 €",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Bugatti_Mistral_2.jpg/1280px-Bugatti_Mistral_2.jpg"
    },
    {
        "brand": "Koenigsegg",
        "model": "JESKO ABSOLUT",
        "specs": "V8 5.0L TT • 1280 CV • GRIS GRAFITO",
        "price": "3.400.000 €",
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRxYtWke6oNivDZHztvs4M2A2pm_bMa4ZDVqA&s"
    },
    {
        "brand": "Pagani",
        "model": "UTOPÍA",
        "specs": "MOTOR V12 DE 6.0 LITROS • 864 CV • TRANSMISIÓN MANUAL",
        "price": "2.200.000 €",
        "image": "https://hips.hearstapps.com/hmg-prod/images/pagani-utopia-1-1663059964.jpg?crop=0.667xw:1.00xh;0.144xw,0&resize=1200:*"
    },
    {
        "brand": "Rimac",
        "model": "ATAQUE CONTRARRELOJ DE NEVERA",
        "specs": "CUÁDRUPLE MOTOR ELÉCTRICO • 1914 CV • 0-100 KM/H: 1,8 S",
        "price": "2.100.000 €",
        "image": "data:image/jpeg;base64,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"
    },
    {
        "brand": "Lamborghini",
        "model": "REVUELTO",
        "specs": "V12 HÍBRIDO • 1.015 CV • GIALLO AUGE",
        "price": "600.000 €",
        "image": "data:image/jpeg;base64,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"
    },
    {
        "brand": "Ferrari",
        "model": "DAYTONA SP3",
        "specs": "V12 6.5L • 840 CV • ROJO MAGMA",
        "price": "2.300.000 €",
        "image": "https://acnews.blob.core.windows.net/imgnews/medium/NAZ_1e5ca3d1d6a84c199d7e867b766030ca.webp"
    }
]

# 5. RENDERIZADO DINÁMICO
rows = [inventory[i:i + 3] for i in range(0, len(inventory), 3)]

for row in rows:
    cols = st.columns(3)
    for i, car in enumerate(row):
        with cols[i]:
            # El uso de HTML directo con <img> permite que el navegador decodifique el link sin importar la extensión
            st.markdown(f"""
                <div class="car-card">
                    <div class="img-frame">
                        <img src="{car['image']}" loading="lazy">
                    </div>
                    <div class="car-info">
                        <div style="color: #666; font-size: 10px; font-weight: bold; margin-bottom: 2px;">{car['brand']}</div>
                        <div class="car-name">{car['model']}</div>
                        <div class="car-specs">{car['specs']}</div>
                        <div class="car-price">{car['price']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("SOLICITAR DOSSIER PRIVADO", key=f"btn_{car['model']}"):
                st.toast(f"Contactando con el agente para {car['brand']}...", icon="📨")
                st.success(f"Solicitud enviada para el {car['model']}.")

# Pie de página
st.markdown("""
    <div style="text-align:center; padding: 60px 0 30px 0; color: #333; font-size: 10px; letter-spacing: 2px;">
        © 2026 HIPERPROPULSOR ÉLITE • GESTIÓN DE ACTIVOS DE LUJO
    </div>
    """, unsafe_allow_html=True)
