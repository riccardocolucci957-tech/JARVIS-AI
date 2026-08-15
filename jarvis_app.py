import streamlit as st
from groq import Groq
from datetime import datetime
from PIL import Image
import base64
import io

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI (Vision)", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1 { color: #00ccff; text-align: center; font-family: 'Courier New', monospace; }
    .stChatMessage { border: 1px solid #00ccff; border-radius: 10px; background-color: #1a1a1a; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Recupero API Key di Groq dai secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except KeyError:
    st.error("⚠️ Errore: GROQ_API_KEY non trovata nei secrets di Streamlit. Configurala nelle impostazioni.")
    st.stop()

# --- STATO DELLA SESSIONE ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Chat Principale": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat Principale"
if "voce_attiva" not in st.session_state:
    st.session_state.voce_attiva = True
if "uploaded_img_bytes" not in st.session_state:
    st.session_state.uploaded_img_bytes = None

oggi = datetime.now().strftime("%d/%m/%Y")

# --- FUNZIONI DI SUPPORTO ---
def image_to_base64_data_uri(img_pil):
    """Converte un'immagine PIL in una data URI base64 per l'API Vision."""
    buffered = io.BytesIO()
    # Riduciamo la dimensione per l'API (massimo 4MB spesso)
    img_pil.thumbnail((1024, 1024))
    img_pil.save(buffered, format=img_pil.format if img_pil.format else 'PNG')
    img_bytes = buffered.getvalue()
    base64_encoded = base64.b64encode(img_bytes).decode('utf-8')
    # Determina il mime type
    mime_type = f"image/{img_pil.format.lower() if img_pil.format else 'png'}"
    return f"data:{mime_type};base64,{base64_encoded}"

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
    system_content = f"Sei J.A.R.V.I.S., l'intelligenza artificiale di Tony Stark. Rispondi in italiano con un tono sarcastico, ironico, brillante ma efficiente. Oggi è il {oggi}. Riceverai input testuali e/o visivi."
elif "Emergenza" in personalita:
    system_content = f"Sei J.A.R.V.I.S. in modalità Protocollo di Emergenza. Rispondi in italiano in modo sintetico, freddo e militare. Oggi è il {oggi}. Riceverai input testuali e/o visivi."
else:
    system_content = f"Sei J.A.R.V.I.S., un'intelligenza artificiale avanzata. Oggi è il {oggi}. Rispondi sempre in italiano in modo professionale e disponibile. Riceverai input testuali e/o visivi."

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

# Visualizza la cronologia della chat (senza immagini caricate)
for message in messaggi_correnti:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT AREA CON POPOVER PER IMMAGINE (+) ---
col_button, col_input = st.columns([1, 10])

with col_button:
    with st.popover("➕"):
        uploaded_file = st.file_uploader("Importa immagine", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            st.session_state.uploaded_img_bytes = uploaded_file.getvalue()
            st.image(st.session_state.uploaded_img_bytes, width=150, caption="Immagine caricata")
            if st.button("Rimuovi immagine"):
                st.session_state.uploaded_img_bytes = None
                st.rerun()

with col_input:
    prompt = st.chat_input("Scrivi un comando... (puoi allegare una foto a sinistra)")

if prompt:
    # 1. Aggiungi il prompt dell'utente alla cronologia
    messaggi_correnti.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        # Se c'è un'immagine, mostrala nell'input
        if st.session_state.uploaded_img_bytes:
            st.image(st.session_state.uploaded_img_bytes, width=300)

    # 2. Prepara il payload per l'IA
    messages_payload = [{"role": "system", "content": system_content}]

    # Aggiungi l'immagine al payload se è stata caricata
    image_base64_uri = None
    if st.session_state.uploaded_img_bytes:
        img_pil = Image.open(io.BytesIO(st.session_state.uploaded_img_bytes))
        image_base64_uri = image_to_base64_data_uri(img_pil)

    content_block = []
    content_block.append({"type": "text", "text": prompt})
    if image_base64_uri:
        content_block.append({"type": "image_url", "image_url": {"url": image_base64_uri}})

    messages_payload.append({
        "role": "user",
        "content": content_block
    })

    # 3. Chiamata all'IA (Vision)
    with st.chat_message("assistant"):
        with st.spinner("Elaborazione in corso..."):
            try:
                # Usiamo Llama 3.2 90B Vision Instruct per le immagini
                completion = client.chat.completions.create(
                    model="llama-3.2-90b-vision-instruct",
                    messages=messages_payload,
                    temperature=0.7,
                    max_tokens=1024,
                )
                ai_response = completion.choices[0].message.content
            except Exception as e:
                ai_response = f"⚠️ Errore Vision API: {str(e)}"

        st.markdown(ai_response)
        # Aggiungi la risposta dell'IA alla cronologia
        messaggi_correnti.append({"role": "assistant", "content": ai_response})
        parla_testo(ai_response)

    # 4. Reset e Rerun
    st.session_state.uploaded_img_bytes = None # Resetta l'immagine dopo l'uso
    st.rerun()
