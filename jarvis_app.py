import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
from PIL import Image

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #00ccff; text-align: center; font-family: 'Courier New', monospace; }
    .stChatMessage { border: 1px solid #00ccff; border-radius: 10px; background-color: #1a1a1a; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Recupero API Key e inizializzazione del client Google GenAI
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- STATO DELLA SESSIONE ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Chat Principale": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat Principale"
if "voce_attiva" not in st.session_state:
    st.session_state.voce_attiva = True

oggi = datetime.now().strftime("%d/%m/%Y")

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Pannello di Controllo")
    personalita = st.selectbox("Protocollo", ["Standard (Professionale)", "Tony Stark (Sarcastico/Geniale)", "Emergenza (Tattico/Rapido)"])
    st.write("---")
    st.session_state.voce_attiva = st.toggle("📢 Attiva Voce", value=st.session_state.voce_attiva)
    st.write("---")
    st.title("💬 Cronologia")
    if st.button("➕ Nuova Chat", use_container_width=True):
        nuova_chiave = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[nuova_chiave] = []
        st.session_state.current_chat = nuova_chiave
        st.rerun()
    for nome_chat in list(st.session_state.chat_sessions.keys()):
        if st.button(nome_chat, use_container_width=True, key=f"btn_{nome_chat}"):
            st.session_state.current_chat = nome_chat
            st.rerun()

# --- CONFIGURAZIONE PERSONALITÀ ---
if "Tony Stark" in personalita:
    system_instruction = f"Sei J.A.R.V.I.S., l'intelligenza artificiale di Tony Stark. Rispondi in italiano con un tono sarcastico, ironico, brillante ma efficiente. Oggi è il {oggi}."
elif "Emergenza" in personalita:
    system_instruction = f"Sei J.A.R.V.I.S. in modalità Protocollo di Emergenza. Rispondi in italiano in modo sintetico, freddo e militare. Oggi è il {oggi}."
else:
    system_instruction = f"Sei J.A.R.V.I.S., un'intelligenza artificiale avanzata. Oggi è il {oggi}. Rispondi sempre in italiano in modo professionale e disponibile."

# --- FUNZIONE VOCE (TTS) ---
def parla_testo(testo):
    if st.session_state.voce_attiva:
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

# --- INTERFACCIA PRINCIPALE ---
st.title(f"🤖 J.A.R.V.I.S. — [{st.session_state.current_chat}]")

messaggi_correnti = st.session_state.chat_sessions[st.session_state.current_chat]
for message in messaggi_correnti:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"]: 
            st.image(message["image"], width=300)
        st.markdown(message["content"])

# --- INPUT AREA CON POPOVER PER IMMAGINE (+) ---
col_button, col_input = st.columns([1, 10])

with col_button:
    with st.popover("➕"):
        uploaded_file = st.file_uploader("Importa immagine", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

with col_input:
    prompt = st.chat_input("Scrivi un comando...")

if prompt:
    img_pil = None
    if uploaded_file:
        img_pil = Image.open(uploaded_file)
        img_pil.thumbnail((1024, 1024))
    
    messaggi_correnti.append({"role": "user", "content": prompt, "image": img_pil})
    
    with st.chat_message("user"):
        if img_pil: 
            st.image(img_pil, width=300)
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Elaborazione in corso..."):
            try:
                contenuti = [img_pil, prompt] if img_pil else [prompt]
                # Modello corretto e stabile
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=contenuti,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                ai_response = response.text
            except Exception as e:
                ai_response = f"⚠️ Errore API: {str(e)}"

        st.markdown(ai_response)
        messaggi_correnti.append({"role": "assistant", "content": ai_response})
        parla_testo(ai_response)
        
    st.rerun()
