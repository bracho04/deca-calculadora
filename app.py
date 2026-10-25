import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import urllib3

# Desactivar advertencias de SSL no verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS ---
st.set_page_config(page_title="Corporación DECA, C.A.", layout="wide")

st.markdown("""
    <style>
    /* Estilo general del fondo y tipografía */
    .main {
        background-color: #f8f9fa;
    }
    /* Títulos principales */
    h1, h2, h3 {
        color: #1f2937;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Tarjetas de métricas personalizadas */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        text-align: center;
        border-left: 5px solid #2563eb;
    }
    /* Botones personalizados */
    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- PÁGINA DE LOGIN ---
def login():
    st.title("🔐 Acceso Seguro - Corporación DECA, C.A.")
    st.write("J-50116434-7")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        password = st.text_input("Introduce la contraseña:", type="password")
        if st.button("Iniciar Sesión"):
            if password == "deca1234": # Cambia esta contraseña cuando gustes
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
            if len(prices) > 1:
                filtered_prices = prices[1:]
                next_10_prices = filtered_prices[:10]
                average_binance = sum(next_10_prices) / len(next_10_prices) if next_10_prices else 0.0
            else:
                average_binance = 0.0
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
    col1.metric("Promedio Binance", f"{average_binance:.2f} VES")
    col2.metric("Tasa BCV Dólar", f"{tasa_usd:.2f} VES")
    col3.metric("Tasa BCV Euro", f"{tasa_eur:.2f} VES")
    col4.metric("Brecha Cambiaria", f"{brecha_cambiaria:.2f} %")

    st.write("---")

    # --- 5. CÁLCULO DE PRECIOS ---
    st.subheader("💰 Cálculo de Ajuste para Pagos")
    precio_usd = st.number_input("Introduce el costo del producto en USD ($):", min_value=0.0, format="%.2f")
    
    if st.button("Calcular Precio"):
        precio_en_bs_bcv = precio_usd * tasa_usd
        precio_ajustado = precio_en_bs_bcv / average_binance if average_binance > 0 else 0.0
        
        st.success("¡Cálculo realizado con éxito!")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Precio Base USD", f"{precio_usd:.2f} $")
        res_col2.metric("Precio en Bs (BCV)", f"{precio_en_bs_bcv:.2f} Bs")
        res_col3.metric("Equivalente P2P", f"{precio_ajustado:.2f} $")

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