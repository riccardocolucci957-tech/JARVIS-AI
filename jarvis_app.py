import streamlit as st
from groq import Groq
from datetime import datetime
from PIL import Image
import base64
import io
import random

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Inizializzazione dello stato di autenticazione e del menu
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# --- SCHERMATA DI ACCESSO / REGISTRAZIONE (GOOGLE & APPLE) ---
if not st.session_state.logged_in:
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        .login-card {
            background-color: #161b22;
            padding: 40px;
            border-radius: 15px;
            border: 1px solid rgba(0,204,255,0.3);
            text-align: center;
            box-shadow: 0 0 20px rgba(0,204,255,0.1);
        }
        .login-title {
            color: #00ccff;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .login-subtitle {
            color: #8b949e;
            font-size: 14px;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="login-card">
                <h1 class="login-title">🤖 J.A.R.V.I.S.</h1>
                <p class="login-subtitle">Autenticazione di Sicurezza Richiesta</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Pulsante Google
        if st.button("🌐  Accedi / Registrati con Google", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
            
        # Pulsante Apple
        if st.button("  Accedi / Registrati con Apple", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
            
    st.stop()

# --- STILI CSS GENERALI DELL'APP ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    * {
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }

    .stChatMessage, input, textarea {
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
        -ms-user-select: text !important;
        user-select: text !important;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-15px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes glow {
        0% { text-shadow: 0 0 5px rgba(0,204,255,0.2); }
        50% { text-shadow: 0 0 20px rgba(0,204,255,0.8); }
        100% { text-shadow: 0 0 5px rgba(0,204,255,0.2); }
    }

    .menu-container {
        animation: slideIn 0.35s ease-out;
        border-right: 1px solid rgba(0,204,255,0.2);
        padding-right: 15px;
    }

    .jarvis-title {
        color: #00ccff;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        animation: slideIn 0.5s ease-out, glow 3s infinite;
        letter-spacing: 2px;
        pointer-events: none;
        margin-top: -10px;
    }

    .stChatMessage { 
        border: 1px solid #00ccff; 
        border-radius: 10px; 
        background-color: #1a1a1a; 
        animation: slideIn 0.3s ease-out;
    }

    .suggestion-container {
        animation: slideIn 0.4s ease-out;
        margin-bottom: 10px;
    }

    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    #MainMenu { visibility: hidden !important; display: none !important; } 
    footer { visibility: hidden !important; display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Recupero API Key protetta
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Configura GROQ_API_KEY nei Secrets di Streamlit.")
    st.stop()

# Inizializzazione sessione chat
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

# --- LAYOUT PRINCIPALE: PULSANTE LATERALE + MENU ANIMATO + CHAT ---
col_btn, col_rest = st.columns([0.8, 12])

with col_btn:
    btn_label = "◀" if st.session_state.show_sidebar else "▶"
    if st.button(btn_label, help="Apri/Chiudi Menu", use_container_width=True):
        st.session_state.show_sidebar = not st.session_state.show_sidebar
        st.rerun()

if st.session_state.show_sidebar:
    col_menu, col_chat = st.columns([2.5, 7.5])
    
    with col_menu:
        st.markdown('<div class="menu-container">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Controllo")
        personalita = st.selectbox("Protocollo", ["Standard (Professionale)", "Tony Stark (Sarcastico/Geniale)", "Emergenza (Tattico/Rapido)"])
        lingua = st.selectbox("🌐 Lingua", ["Italiano", "English", "Español", "Français", "Deutsch"])
        st.session_state.voce_attiva = st.toggle("📢 Attiva Voce", value=st.session_state.voce_attiva)
        
        st.write("---")
        st.markdown("### 💬 Canali di Sistema")
        
        for canale in canali_fissi:
            is_active = (canale == st.session_state.current_chat)
            button_type = "primary" if is_active else "secondary"
            if st.button(canale, use_container_width=True, type=button_type):
                st.session_state.current_chat = canale
                st.rerun()
                
        st.write("---")
        
        if st.button("🗑️ Svuota Chat Attiva", use_container_width=True):
            st.session_state.chat_sessions[st.session_state.current_chat] = []
            st.rerun()

        if st.button("🚪 Esci (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
        st.caption("🔒 Accesso protetto.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    col_chat = col_rest
    personalita = "Standard (Professionale)"
    lingua = "Italiano"

# --- AREA CHAT ---
with col_chat:
    if "Tony Stark" in personalita:
        base_prompt = "You are J.A.R.V.I.S., Tony Stark's AI. Answer with a brilliant, sarcastic tone, extremely sharp and tech-savvy."
    elif "Emergenza" in personalita:
        base_prompt = "J.A.R.V.I.S. Emergency Protocol. Answer in a concise, cold, military style."
    else:
        base_prompt = "J.A.R.V.I.S., advanced AI assistant. Answer professionally, with extreme technical precision and helpfulness."

    system_content = f"{base_prompt} Respond strictly in {lingua}. Date: {oggi}."

    def parla_testo(testo):
        if st.session_state.voce_attiva:
            t = testo.replace('"', "'").replace('\n', ' ')
            codice_lingua = {"Italiano": "it-IT", "English": "en-US", "Español": "es-ES", "Français": "fr-FR", "Deutsch": "de-DE"}.get(lingua, "it-IT")
            st.components.v1.html(f'<script>const s=window.speechSynthesis; const u=new SpeechSynthesisUtterance("{t}"); u.lang="{codice_lingua}"; s.speak(u);</script>', height=0)

    st.markdown(f"<h1 class='jarvis-title'>🤖 J.A.R.V.I.S. — [{st.session_state.current_chat}]</h1>", unsafe_allow_html=True)

    messaggi = st.session_state.chat_sessions[st.session_state.current_chat]

    for msg in messaggi:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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

    col_pop, col_in = st.columns([1, 15])

    with col_pop:
        with st.popover("➕", help="Allega immagine"):
            uploaded_file = st.file_uploader("Seleziona immagine", type=["png", "jpg", "jpeg"])
            if uploaded_file:
                st.session_state.uploaded_img_bytes = uploaded_file.getvalue()
                st.image(st.session_state.uploaded_img_bytes, width=150, caption="Pronta")
                if st.button("Rimuovi"):
                    st.session_state.uploaded_img_bytes = None
                    st.rerun()

    with col_in:
        prompt_digitato = st.chat_input("Scrivi un comando...")

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



