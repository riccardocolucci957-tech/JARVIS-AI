import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime

# Configurazione stile CSS (Tema Neon/Dark)
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #00ccff; text-align: center; font-family: 'Courier New', monospace; }
    .stChatMessage { border: 1px solid #00ccff; border-radius: 10px; background-color: #1a1a1a; }
    </style>
""", unsafe_allow_html=True)

# Recupero API Key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-flash-latest')

# --- SIDEBAR E INDICATORI ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/36/Marvel_Studios_logo.svg", width=150)
    st.title("SISTEMA JARVIS")
    st.write("---")
    st.subheader("Stato Interno")
    st.progress(85, text="Stato Core IA")
    st.success("Connessione: STABILE")
    voce_attiva = st.toggle("📢 Attiva Voce", value=True)
    st.write("---")
    st.info("Versione: 4.0.2 - Stark Enterprise")

# --- FUNZIONI ---
def parla_testo(testo):
    if voce_attiva:
        testo_pulito = testo.replace('"', "'").replace('\n', ' ')
        js_code = f"""<script>
            const synth = window.speechSynthesis;
            const utterThis = new SpeechSynthesisUtterance("{testo_pulito}");
            utterThis.lang = 'it-IT';
            synth.speak(utterThis);
        </script>"""
        st.components.v1.html(js_code, height=0, width=0)

# Titolo e Animazione
if "init" not in st.session_state:
    st.title("🤖 J.A.R.V.I.S.")
    ph = st.empty()
    intro = "Inizializzazione core... Connessione neurale... Sistemi online."
    for i in range(len(intro)+1):
        ph.markdown(f"<h3 style='color:#00ccff'>{intro[:i]}</h3>", unsafe_allow_html=True)
        time.sleep(0.05)
    st.session_state.init = True
    ph.empty()

st.title("🤖 J.A.R.V.I.S.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistemi online. Pronto all'uso."}]

# Bottoni Comandi Rapidi
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Diagnostica"): prompt_rapido = "Fai una diagnostica del sistema."
with col2:
    if st.button("Meteo"): prompt_rapido = "Com'è il tempo oggi?"
with col3:
    if st.button("Curiosità"): prompt_rapido = "Raccontami una curiosità tecnologica."

# Gestione Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def elabora_risposta(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        response = model.generate_content(user_input)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        parla_testo(response.text)

if prompt := st.chat_input("Inserisci comando..."):
    elabora_risposta(prompt)
elif 'prompt_rapido' in locals():
    elabora_risposta(prompt_rapido)
