import streamlit as st
from groq import Groq
from datetime import datetime
from PIL import Image
import base64
import io
import random

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

# Stili CSS avanzati con effetti visivi e animazioni HUD
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes glow {
        0% { text-shadow: 0 0 5px rgba(0,204,255,0.2); }
        50% { text-shadow: 0 0 20px rgba(0,204,255,0.8); }
        100% { text-shadow: 0 0 5px rgba(0,204,255,0.2); }
    }

    .jarvis-title {
        color: #00ccff;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        animation: fadeIn 1.2s ease-out, glow 3s infinite;
        letter-spacing: 2px;
    }

    .stChatMessage { 
        border: 1px solid #00ccff; 
        border-radius: 10px; 
        background-color: #1a1a1a; 
        animation: fadeIn 0.4s ease-out;
    }

    .suggestion-container {
        animation: fadeIn 0.8s ease-out;
        margin-bottom: 10px;
    }

    #GithubIcon, .github-corner, a[href*="github.com"] {
        display: none !important;
    }

    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Recupero API Key protetta
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Configura GROQ_API_KEY nei Secrets di Streamlit.")
    st.stop()

# Inizializzazione sessione
canali_fissi = ["Chat Principale", "Analisi Tecnica", "Codice e Script"]

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {canale: [] for canale in canali_fissi}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat Principale"
if "voce_attiva" not in st.session_state:
    st.session_state.voce_attiva = True
if "uploaded_img_bytes" not in st.session_state:
    st.session_state.uploaded_img_bytes = None

oggi = datetime.now().strftime("%d/%m/%Y")
giorno_seed = datetime.now().strftime("%Y%m%d")

# --- GENERATORE DOMANDE GIORNALIERE ---
bancomat_domande = [
    "Fammi una battuta divertente sul mondo tech o sull'informatica.",
    "Che tempo fa oggi? Dammi un'analisi rapida.",
    "J.A.R.V.I.S., qual è il protocollo di sicurezza attivo oggi?",
    "Raccontami un aneddoto geniale su Tony Stark.",
    "Dammi un consiglio di programmazione o ottimizzazione hardware.",
    "Qual è lo stato attuale dei sistemi di bordo?",
    "Fammi una battuta caustica in stile Stark.",
    "Analizza la situazione globale con sarcasmo.",
    "Quali sono le priorità operative per oggi?"
]

random.seed(giorno_seed)
domande_del_giorno = random.sample(bancomat_domande, 3)

# --- SIDEBAR PULITA E ORDINATA ---
with st.sidebar:
    st.title("⚙️ Controllo")
    personalita = st.selectbox("Protocollo", ["Standard (Professionale)", "Tony Stark (Sarcastico/Geniale)", "Emergenza (Tattico/Rapido)"])
    st.session_state.voce_attiva = st.toggle("📢 Attiva Voce", value=st.session_state.voce_attiva)
    st.write("---")
    st.title("💬 Canali di Sistema")
    
    for canale in canali_fissi:
        is_active = (canale == st.session_state.current_chat)
        button_type = "primary" if is_active else "secondary"
        if st.button(canale, use_container_width=True, type=button_type):
            st.session_state.current_chat = canale
            st.rerun()
            
    st.write("---")
    st.caption("🔒 Configurazione protetta da amministratore.")

# --- LOGICA PERSONALITA ---
if "Tony Stark" in personalita:
    system_content = f"Sei J.A.R.V.I.S., AI di Tony Stark. Rispondi in italiano con tono sarcastico, geniale. Data: {oggi}."
elif "Emergenza" in personalita:
    system_content = f"J.A.R.V.I.S. Protocollo Emergenza. Rispondi in modo sintetico, freddo, militare. Data: {oggi}."
else:
    system_content = f"J.A.R.V.I.S., IA avanzata. Rispondi in modo professionale, preciso e disponibile. Data: {oggi}."

# --- FUNZIONE VOCE (TTS) ---
def parla_testo(testo):
    if st.session_state.voce_attiva:
        t = testo.replace('"', "'").replace('\n', ' ')
        st.components.v1.html(f'<script>const s=window.speechSynthesis; const u=new SpeechSynthesisUtterance("{t}"); u.lang="it-IT"; s.speak(u);</script>', height=0)

# --- INTERFACCIA CHAT PRINCIPALE CON TITOLO ANIMATO ---
st.markdown(f"<h1 class='jarvis-title'>🤖 J.A.R.V.I.S. — [{st.session_state.current_chat}]</h1>", unsafe_allow_html=True)

messaggi = st.session_state.chat_sessions[st.session_state.current_chat]

for msg in messaggi:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- SUGGERIMENTI RAPIDI GIORNALIERI ---
st.markdown("<div class='suggestion-container'></div>", unsafe_allow_html=True)
st.caption("💡 Suggerimenti del giorno (clicca per inviare):")
col_sug1, col_sug2, col_sug3 = st.columns(3)

domanda_cliccata = None
with col_sug1:
    if st.button(domande_del_giorno[0], use_container_width=True):
        domanda_cliccata = domande_del_giorno[0]
with col_sug2:
    if st.button(domande_del_giorno[1], use_container_width=True):
        domanda_cliccata = domande_del_giorno[1]
with col_sug3:
    if st.button(domande_del_giorno[2], use_container_width=True):
        domanda_cliccata = domande_del_giorno[2]

# --- AREA DI INPUT CON POPOVER "+" (IMMAGINE) E PULSANTE MICROFONO VOCALE ---
col_pop, col_mic, col_in = st.columns([1, 1, 15])

with col_pop:
    with st.popover("➕", help="Allega immagine"):
        uploaded_file = st.file_uploader("Seleziona immagine", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            st.session_state.uploaded_img_bytes = uploaded_file.getvalue()
            st.image(st.session_state.uploaded_img_bytes, width=150, caption="Pronta")
            if st.button("Rimuovi"):
                st.session_state.uploaded_img_bytes = None
                st.rerun()

with col_mic:
    # Componente HTML/JS per la dettatura vocale tramite Web Speech API del browser
    mic_html = """
    <div style="text-align: center;">
        <button id="micBtn" onclick="startDictation()" style="background-color: #1a1a1a; color: #00ccff; border: 1px solid #00ccff; border-radius: 5px; padding: 6px 10px; cursor: pointer; font-size: 16px;" title="Attiva microfono">🎤</button>
    </div>
    <script>
        function startDictation() {
            if (window.hasOwnProperty('webkitSpeechRecognition')) {
                var recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = "it-IT";
                
                document.getElementById('micBtn').style.backgroundColor = '#00ccff';
                document.getElementById('micBtn').style.color = '#000';
                
                recognition.onresult = function(e) {
                    var text = e.results[0][0].transcript;
                    // Troviamo l'input di Streamlit nella pagina per inserire il testo dettato
                    const inputElem = window.parent.document.querySelector('input[type="text"]');
                    if (inputElem) {
                        inputElem.value = text;
                        inputElem.dispatchEvent(new Event('input', { bubbles: true }));
                        // Simula invio premendo Invio
                        setTimeout(() => {
                            inputElem.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true}));
                        }, 500);
                    }
                    document.getElementById('micBtn').style.backgroundColor = '#1a1a1a';
                    document.getElementById('micBtn').style.color = '#00ccff';
                    recognition.stop();
                };
                
                recognition.onerror = function(e) {
                    document.getElementById('micBtn').style.backgroundColor = '#1a1a1a';
                    document.getElementById('micBtn').style.color = '#00ccff';
                    recognition.stop();
                };
                
                recognition.start();
            } else {
                alert("La dettatura vocale non è supportata da questo browser. Usa Google Chrome o Safari.");
            }
        }
    </script>
    """
    st.components.v1.html(mic_html, height=45)

with col_in:
    prompt_digitato = st.chat_input("Inserisci un comando o detta con il microfono...")

prompt = domanda_cliccata if domanda_cliccata else prompt_digitato

if st.session_state.uploaded_img_bytes:
    st.info("📎 Immagine allegata e pronta per l'invio.")

if prompt:
    messaggi.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if st.session_state.uploaded_img_bytes:
            st.image(st.session_state.uploaded_img_bytes, width=250)

    payload = [{"role": "system", "content": system_content}] + [{"role": m["role"], "content": m["content"]} for m in messaggi]

    with st.chat_message("assistant"):
        with st.spinner("Elaborazione in corso..."):
            try:
                if st.session_state.uploaded_img_bytes:
                    b64 = base64.b64encode(st.session_state.uploaded_img_bytes).decode()
                    payload[-1] = {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": prompt}, 
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]
                    }
                    resp = client.chat.completions.create(model="llama-3.2-90b-vision-instruct", messages=payload).choices[0].message.content
                else:
                    resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=payload).choices[0].message.content
                
                st.markdown(resp)
                messaggi.append({"role": "assistant", "content": resp})
                parla_testo(resp)
            except Exception as e:
                st.error(f"Errore di sistema: {e}")
                
    st.session_state.uploaded_img_bytes = None
    st.rerun()
    
