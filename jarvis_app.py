import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #00ccff; font-family: 'Courier New', monospace; }
    .stChatMessage { border: 1px solid #00ccff; border-radius: 10px; background-color: #1a1a1a; }
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
    
    # Selettore di Personalità
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
    st.info("Versione: 4.3 - Stark OS")

# Imposta le istruzioni di sistema in base alla personalità scelta
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
    messaggi_correnti.append({"role": "assistant", "content": f"Sistemi online in modalità '{personalita}'. Come posso assisterti?"})

# Visualizza i messaggi della chat attiva
for message in messaggi_correnti:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dell'utente
if prompt := st.chat_input("Scrivi un comando..."):
    messaggi_correnti.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_history_gemini = [{"role": m["role"], "parts": [m["content"]]} for m in messaggi_correnti[:-1]]
        chat = model.start_chat(history=chat_history_gemini)
        
        response = chat.send_message(prompt)
        st.markdown(response.text)
        messaggi_correnti.append({"role": "assistant", "content": response.text})
        parla_testo(response.text)
    st.rerun()
