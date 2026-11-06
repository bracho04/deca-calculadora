import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import urllib3
import math
from pyDolarVenezuela import Monitor
from pyDolarVenezuela.pages import BCV

# Desactivar advertencias de SSL no verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS RESPONSIVOS ---
st.set_page_config(page_title="Corporación DECA, C.A.", layout="wide")

st.markdown("""
<style>
.main {
    background-color: #f8f9fa;
}
h1, h2, h3 {
    color: #1f2937;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
div.stButton > button {
    background-color: #2563eb; 
    color: white; 
    border-radius: 6px; 
    padding: 0.5rem 1rem; 
    font-weight: bold; 
    border: none;
    width: 100%;
}
div.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}
@media (max-width: 768px) {
    .stMetric {
        margin-bottom: 15px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN PARA OBTENER TASA DEL BCV ---
def obtener_tasa_bcv():
    try:
        monitor = Monitor(BCV, 'USD')
        return monitor.price
    except Exception as e:
        return 0.0

# --- PÁGINA DE LOGIN ---
def login():
    st.title("🔐 Acceso Seguro - Corporación DECA, C.A.")
    st.write("J-50116434-7")
    
    # Ejemplo de uso de la tasa
    tasa_bcv = obtener_tasa_bcv()
    st.info(f"Tasa BCV actual: {tasa_bcv}")

if __name__ == "__main__":
    login()
