import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="centered")

# Recupero API Key dai Secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# Configurazione dell'IA
oggi = datetime.now().strftime("%d/%m/%Y")
system_instruction = f"""
Sei J.A.R.V.I.S., un'intelligenza artificiale avanzata e disponibile online.
Oggi è il giorno {oggi}. Rispondi sempre in italiano in modo professionale e disponibile.
"""

model = genai.GenerativeModel(
    model_name='gemini-flash-latest',
    system_instruction=system_instruction
)

# --- CONTROLLO AUDIO (MEGAFONO) IN ALTO A DESTRA ---
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🤖 J.A.R.V.I.S.")
with col2:
    # Toggle con l'icona del megafono
    voce_attiva = st.toggle("📢 Voce", value=True)

# --- FUNZIONE PER LA VOCE (TEXT-TO-SPEECH DEL BROWSER) ---
def parla_testo(testo):
    if voce_attiva:
        # Puliamo il testo da caratteri che potrebbero rompere lo script JS
        testo_pulito = testo.replace('"', "'").replace('\n', ' ')
        js_code = f"""
        <script>
            const synth = window.speechSynthesis;
            const utterThis = new SpeechSynthesisUtterance("{testo_pulito}");
            utterThis.lang = 'it-IT';
            synth.speak(utterThis);
        </script>
        """
        st.components.v1.html(js_code, height=0, width=0)

# --- FUNZIONE PER L'ANIMAZIONE DI ENTRATA ---
def animated_welcome():
    welcome_placeholder = st.empty()
    full_text = "Inizializzazione sistemi J.A.R.V.I.S. v.3.7...\n\nConnessione al cloud stabilita.\n\nSistemi online. Come posso aiutarti oggi?"
    
    current_text = ""
    for char in full_text:
        current_text += char
        welcome_placeholder.markdown(f"<pre style='color: #00ccff; font-family: monospace;'>{current_text}</pre>", unsafe_allow_html=True)
        time.sleep(0.03)
        
    time.sleep(0.5)
    welcome_placeholder.empty()

# Inizializzazione della chat e gestione primo avvio
if "messages" not in st.session_state:
    st.session_state.messages = []
    animated_welcome()
    messaggio_iniziale = "Sistemi online. Come posso aiutarti oggi?"
    st.session_state.messages.append({"role": "assistant", "content": messaggio_iniziale})
    parla_testo(messaggio_iniziale)

chat = model.start_chat(history=[])

# Visualizza tutti i messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Casella di input dell'utente
if prompt := st.chat_input("Scrivi un comando..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        # Parla solo se il megafono è attivo
        parla_testo(response.text)
