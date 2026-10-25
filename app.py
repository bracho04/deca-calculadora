import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import urllib3
import math

# Desactivar advertencias de SSL no verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS RESPONSIVOS ---
st.set_page_config(page_title="Corporación DECA, C.A.", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #1f2937; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Botones adaptados para móviles */
    div.stButton > button {
        background-color: #2563eb; color: white; border-radius: 6px;
        padding: 0.5rem 1rem; font-weight: bold; border: none; width: 100%;
    }
    div.stButton > button:hover { background-color: #1d4ed8; color: white; }
    
    /* Contenedores adaptados para pantallas pequeñas */
    @media (max-width: 768px) {
        .stMetric {
            margin-bottom: 15px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- PÁGINA DE LOGIN ---
def login():
    st.title("🔐 Acceso Seguro - Corporación DECA, C.A.")
    st.write("J-50116434-7")
    
    col1, _ = st.columns([1, 2])
    with col1:
        password = st.text_input("Introduce la contraseña:", type="password")
        if st.button("Iniciar Sesión"):
            if password == "deca1234":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")

# --- APLICACIÓN PRINCIPAL ---
def main_app():
    st.title("📊 Calculadora de Precios y Tasas")
    st.markdown("### **Corporación DECA, C.A.** *(J-50116434-7)*")
    st.write("---")
    
    # --- 1. PROCESAMIENTO BINANCE P2P (USDT) ---
    url_binance = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    headers_binance = {'Content-Type': 'application/json'}
    payload = {
        "asset": "USDT", "fiat": "VES", "tradeType": "BUY",
        "merchantInclude": True, "rows": 20, "page": 1,
        "countries": [], "payTypes": []
    }
    
    try:
        response = requests.post(url_binance, headers=headers_binance, data=json.dumps(payload), timeout=5)
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            prices = [float(item['adv']['price']) for item in items]
            average_binance = sum(prices[1:11]) / 10 if len(prices) > 1 else 0.0
        else:
            average_binance = 0.0
    except:
        average_binance = 0.0

    # --- 2. TASA BCV (DÓLAR Y EURO) ---
    url_bcv = 'https://www.bcv.org.ve/'
    headers_bcv = {'User-Agent': 'Mozilla/5.0'}
    try:
        response_bcv = requests.get(url_bcv, headers=headers_bcv, verify=False, timeout=5)
        soup = BeautifulSoup(response_bcv.text, 'html.parser')
        div_usd = soup.find('div', id='dolar')
        tasa_usd = float(div_usd.find('strong').text.strip().replace(',', '.')) if div_usd else 0.0
        div_eur = soup.find('div', id='euro')
        tasa_eur = float(div_eur.find('strong').text.strip().replace(',', '.')) if div_eur else 0.0
    except:
        tasa_usd, tasa_eur = 0.0, 0.0

    # --- 3. CÁLCULO DE LA BRECHA ---
    brecha_cambiaria = ((average_binance - tasa_usd) / tasa_usd) * 100 if tasa_usd > 0 else 0.0

    # --- 4. MOSTRAR RESULTADOS DE TASAS ---
    st.subheader("📈 Tasas Actuales del Mercado")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Promedio Binance", f"{average_binance:.2f} VES")
    with col2: st.metric("Tasa BCV Dólar", f"{tasa_usd:.2f} VES")
    with col3: st.metric("Tasa BCV Euro", f"{tasa_eur:.2f} VES")
    with col4: st.metric("Brecha Cambiaria", f"{brecha_cambiaria:.2f} %")

    st.write("---")

    # --- 5. CÁLCULO DE PRECIOS ---
    st.subheader("💰 Valor a realizar descuento") # <- Subtítulo actualizado
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        precio_usd = st.number_input("Introduce el costo del producto en USD ($):", min_value=0.0, format="%.2f")
    with col_input2:
        porcentaje_descuento = st.number_input("Descuento por pago en divisa (%):", min_value=0.0, max_value=100.0, value=5.0, format="%.1f")
    
    if st.button("Calcular Precio"):
        precio_en_bs_bcv = precio_usd * tasa_usd
        precio_equivalente = precio_en_bs_bcv / average_binance if average_binance > 0 else 0.0
        
        # Aplicar descuento y redondear hacia arriba al entero superior
        precio_con_descuento = precio_equivalente * (1 - (porcentaje_descuento / 100))
        precio_redondeado = math.ceil(precio_con_descuento)
        
        st.success("¡Cálculo realizado con éxito!")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        with res_col1: st.metric("Precio Base USD", f"{precio_usd:.2f} $")
        with res_col2: st.metric("Precio en Bs (BCV)", f"{precio_en_bs_bcv:.2f} Bs")
        with res_col3: st.metric("Descuento para pagos en divisas", f"{precio_redondeado} $")

    st.write("---")
    if st.button("Cerrar Sesión"):
        st.session_state["logged_in"] = False
        st.rerun()

# --- LÓGICA DE CONTROL DE SESIÓN ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    main_app()