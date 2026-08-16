import streamlit as st
from groq import Groq
from datetime import datetime
from PIL import Image
import base64
import io
import random

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Inizializzazione degli stati globali (senza login)
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# --- STILI CSS GENERALI (Manteniamo i tuoi stili e aggiungiamo le rimozioni di sistema) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* Disabilita selezione testo ovunque tranne nelle chat */
    * { -webkit-user-select: none; user-select: none; }
    .stChatMessage, input, textarea { -webkit-user-select: text !important; user-select: text !important; }
    
    @keyframes slideIn { from { opacity: 0; transform: translateX(-15px); } to { opacity: 1; transform: translateX(0); } }
    @keyframes glow { 0% { text-shadow: 0 0 5px rgba(0,204,255,0.2); } 50% { text-shadow: 0 0 20px rgba(0,204,255,0.8); } 100% { text-shadow: 0 0 5px rgba(0,204,255,0.2); } }

    .menu-container { animation: slideIn 0.35s ease-out; border-right: 1px solid rgba(0,204,255,0.2); padding-right: 15px; }
    .jarvis-title { color: #00ccff; text-align: center; font-family: 'Courier New', monospace; font-weight: bold; animation: slideIn 0.5s ease-out, glow 3s infinite; letter-spacing: 2px; pointer-events: none; margin-top: -10px; }
    
    .stChatMessage { border: 1px solid #00ccff; border-radius: 10px; background-color: #1a1a1a; animation: slideIn 0.3s ease-out; }
    
    /* Nascondi elementi Streamlit non necessari */
    [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer, [data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ... (il resto del tuo codice continua da qui, senza le parti di login)
