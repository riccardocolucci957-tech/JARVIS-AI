import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
from PIL import Image

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #00ccff; font-family: 'Courier New', monospace; }
    .stChatMessage { border: 1px solid #00ccff; border-radius: 10px; background-color: #1a1a1a; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Recupero API Key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# --- SIDEBAR E GESTIONE PERSONALITÀ ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Chat Principale": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat Principale"

oggi = datetime.now().strftime("%d/%m/%Y")

with st.sidebar:
    st.title("⚙️ Pannello di Controllo")
    
    personalita = st.selectbox(
        "Protocollo di Personalità",
        ["Standard (Professionale)", "Tony Stark (Sarcastico/Geniale)", "Emergenza (Tattico/Rapido)"]
    )
    
    st.write("---")
    st.title("💬 Cronologia Chat")
    
    if st.button("➕ Nuova Chat", use_container_width=True):
        nuova_chiave = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[nuova_chiave] = []
        st.session_state.current_chat = nuova_chiave
        st.rerun()

    st.write("---")
    for nome_chat in list(st.session_state.chat_sessions.keys()):
        if st.button(nome_chat, use_container_width=True, key=f"btn_{nome_chat}"):
            st.session_state.current_chat = nome_chat
            st.rerun()

    st.write("---")
    voce_attiva = st.toggle("📢 Attiva Voce", value=True)
    st.info("Versione: 4.5 - Stark Vision")

# Configurazione Istruzioni di Sistema
if "Tony Stark" in personalita:
    system_instruction = f"""Sei J.A.R.V.I.S., l'intelligenza artificiale di Tony Stark. 
    Rispondi in italiano con un tono sarcastico, ironico, brillante ma estremamente efficiente. 
    Oggi è il {oggi}."""
elif "Emergenza" in personalita:
    system_instruction = f"""Sei J.A.R.V.I.S. in modalità Protocollo di Emergenza. 
    Rispondi in italiano in modo estremamente sintetico, freddo, militare e diretto al punto. 
    Oggi è il {oggi}."""
else:
    system_instruction = f"""Sei J.A.R.V.I.S., un'intelligenza artificiale avanzata e disponibile online. 
    Oggi è il {oggi}. Rispondi sempre in italiano in modo professionale e disponibile."""

# Utilizziamo il modello gemini-flash-latest che supporta anche le immagini (multimodale)
model = genai.GenerativeModel(
    model_name='gemini-flash-latest',
    system_instruction=system_instruction
)

# Funzione sintesi vocale
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

# Titolo principale
st.title(f"🤖 J.A.R.V.I.S. — [{st.session_state.current_chat}]")

# Recupera i messaggi della chat corrente
messaggi_correnti = st.session_state.chat_sessions[st.session_state.current_chat]

if not messaggi_correnti:
    messaggi_correnti.append({"role": "assistant", "content": f"Sistemi online in modalità '{personalita}'. Modulo visivo attivo. Come posso assisterti?"})

# Visualizza i messaggi della chat attiva (gestendo sia testo che immagini salvate)
for message in messaggi_correnti:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=300)
        st.markdown(message["content"])

# Selettore file immagine direttamente sopra la chat
uploaded_file = st.file_uploader("📷 Aggiungi un'immagine da analizzare (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

# Input dell'utente
if prompt := st.chat_input("Scrivi un comando o descrivi l'immagine..."):
    # Gestione dell'immagine caricata
    img_pil = None
    if uploaded_file is not None:
        img_pil = Image.open(uploaded_file)

    # Aggiunge il messaggio utente alla cronologia
    messaggi_correnti.append({"role": "user", "content": prompt, "image": img_pil})
    
    with st.chat_message("user"):
        if img_pil is not None:
            st.image(img_pil, width=300)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            # Prepara i contenuti da inviare a Gemini (supporta testo + immagine)
            contenuti_invio = []
            if img_pil is not None:
                contenuti_invio.append(img_pil)
            contenuti_invio.append(prompt)

            # Genera la risposta
            response = model.generate_content(contenuti_invio)
            st.markdown(response.text)
            
            messaggi_correnti.append({"role": "assistant", "content": response.text, "image": None})
            parla_testo(response.text)
            
    st.rerun()
