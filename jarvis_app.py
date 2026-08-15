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

# --- FUNZIONE PER L'ANIMAZIONE DI ENTRATA ---
def animated_welcome():
    # Contenitore vuoto iniziale
    welcome_placeholder = st.empty()
    # Testo completo dell'animazione
    full_text = "Inizializzazione sistemi J.A.R.V.I.S. v.3.7...\n\nConnessione al cloud stabilita.\n\nSistemi online. Come posso aiutarti oggi?"
    
    current_text = ""
    # Ciclo per l'effetto "macchina da scrivere"
    for char in full_text:
        current_text += char
        # Aggiorna il contenuto del contenitore con codice formattato (monospaced)
        welcome_placeholder.markdown(f"<pre style='color: #00ccff; font-family: monospace;'>{current_text}</pre>", unsafe_allow_html=True)
        # Velocità dell'animazione (in secondi)
        time.sleep(0.03)
        
    # Aggiunge un piccolo ritardo alla fine prima di passare alla chat vera e propria
    time.sleep(0.5)
    # Rimuove l'animazione per far posto alla chat
    welcome_placeholder.empty()

# --- FINE FUNZIONE ANIMAZIONE ---


# Titolo principale
st.title("🤖 J.A.R.V.I.S.")

# Inizializzazione della chat e GESTIONE AVVIO (con animazione)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Esegui l'animazione di entrata solo al primo caricamento
    animated_welcome()
    # Imposta il primo messaggio di benvenuto visibile nella chat
    st.session_state.messages.append({"role": "assistant", "content": "Sistemi online. Come posso aiutarti oggi?"})


# Caricamento dello storico della chat (necessario per far funzionare l'app dopo l'animazione)
chat = model.start_chat(history=[])

# Visualizza tutti i messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Casella di input dell'utente
if prompt := st.chat_input("Scrivi un comando..."):
    # Aggiunge e visualizza il messaggio dell'utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ottiene e visualizza la risposta dell'IA
    with st.chat_message("assistant"):
        response = chat.send_message(prompt)
        st.markdown(response.text)
        # Aggiunge la risposta alla sessione
        st.session_state.messages.append({"role": "assistant", "content": response.text})
