import streamlit as st
from groq import Groq
from datetime import datetime
from PIL import Image
import base64
import io
import random

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Inizializzazione stati base
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Chat Principale": [], "Analisi Tecnica": [], "Codice e Script": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat Principale"
if "voce_attiva" not in st.session_state:
    st.session_state.voce_attiva = True
if "uploaded_img_bytes" not in st.session_state:
    st.session_state.uploaded_img_bytes = None

# --- STILI CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    * { -webkit-user-select: none; user-select: none; }
    .stChatMessage, input, textarea { -webkit-user-select: text !important; user-select: text !important; }
    .jarvis-title { color: #00ccff; text-align: center; font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 2px; }
    .stChatMessage { border: 1px solid #00ccff; border-radius: 10px; background-color: #1a1a1a; }
    [data-testid="stToolbar"], [data-testid="stDecoration"], footer, [data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Recupero API Key
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Configura GROQ_API_KEY nei Secrets di Streamlit.")
    st.stop()

# Utility
oggi = datetime.now().strftime("%d/%m/%Y")
bancomat_domande = ["Fammi una battuta tech.", "Che tempo fa oggi?", "J.A.R.V.I.S., stato sistemi?", "Consiglio di ottimizzazione hardware.", "Fammi una battuta in stile Stark."]
random.seed(datetime.now().strftime("%Y%m%d"))
domande_del_giorno = random.sample(bancomat_domande, 3)

# Layout
col_btn, col_rest = st.columns([0.8, 12])
with col_btn:
    if st.button("☰", help="Menu"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar
        st.rerun()

if st.session_state.show_sidebar:
    col_menu, col_chat = st.columns([2.5, 7.5])
    with col_menu:
        personalita = st.selectbox("Protocollo", ["Standard (Professionale)", "Tony Stark (Sarcastico)", "Emergenza (Tattico)"])
        lingua = st.selectbox("🌐 Lingua", ["Italiano", "English"])
        st.session_state.voce_attiva = st.toggle("📢 Attiva Voce", value=st.session_state.voce_attiva)
        for canale in st.session_state.chat_sessions.keys():
            if st.button(canale, use_container_width=True):
                st.session_state.current_chat = canale
                st.rerun()
else:
    col_chat = col_rest
    personalita = "Standard (Professionale)"
    lingua = "Italiano"

# Area Chat
with col_chat:
    st.markdown(f"<h1 class='jarvis-title'>🤖 J.A.R.V.I.S. — [{st.session_state.current_chat}]</h1>", unsafe_allow_html=True)
    
    messaggi = st.session_state.chat_sessions[st.session_state.current_chat]
    for msg in messaggi:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Scrivi un comando...")
    if prompt:
        messaggi.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Elaborazione..."):
                payload = [{"role": "system", "content": f"J.A.R.V.I.S. persona: {personalita}. Lingua: {lingua}."}] + messaggi
                resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=payload).choices[0].message.content
                st.markdown(resp)
                messaggi.append({"role": "assistant", "content": resp})
        st.rerun()


