import streamlit as st
from groq import Groq
from datetime import datetime
from PIL import Image
import random

# Configurazione della pagina
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Inizializzazione autenticazione
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# Schermata di Login
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
        .login-title { color: #00ccff; font-family: 'Courier New', monospace; font-weight: bold; margin-bottom: 10px; }
        .login-subtitle { color: #8b949e; font-size: 14px; margin-bottom: 30px; }
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
        if st.button("🌐  Accedi / Registrati con Google", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
        if st.button("  Accedi / Registrati con Apple", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# Stili CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .jarvis-title { color: #00ccff; text-align: center; font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 2px; }
    .stChatMessage { border: 1px solid #00ccff; border-radius: 10px; background-color: #1a1a1a; }
    [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer, [data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Configurazione Groq Client con la nuova chiave aggiornata
try:
    API_KEY_GROQ = "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"
    client = Groq(api_key=API_KEY_GROQ)
except Exception as e:
    st.error(f"⚠️ Errore di inizializzazione client: {e}")
    st.stop()

canali_fissi = ["Chat Principale", "Analisi Tecnica", "Codice e Script"]
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {canale: [] for canale in canali_fissi}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat Principale"
if "voce_attiva" not in st.session_state:
    st.session_state.voce_attiva = True

oggi = datetime.now().strftime("%d/%m/%Y")
giorno_seed = datetime.now().strftime("%Y%m%d")

bancomat_domande = [
    "Fammi una battuta divertente sul mondo tech o sull'informatica.",
    "Che tempo fa oggi? Dammi un'analisi rapida.",
    "J.A.R.V.I.S., qual è il protocollo di sicurezza attivo oggi?",
    "Raccontami un aneddoto geniale su Tony Stark.",
    "Dammi un consiglio di programmazione o ottimizzazione hardware.",
    "Qual è lo stato attuale dei sistemi di bordo?"
]

random.seed(giorno_seed)
domande_del_giorno = random.sample(bancomat_domande, 3)

# Layout e Menu
col_btn, col_rest = st.columns([0.8, 12])
with col_btn:
    btn_label = "◀" if st.session_state.show_sidebar else "▶"
    if st.button(btn_label, help="Apri/Chiudi Menu", use_container_width=True):
        st.session_state.show_sidebar = not st.session_state.show_sidebar
        st.rerun()

if st.session_state.show_sidebar:
    col_menu, col_chat = st.columns([2.5, 7.5])
    with col_menu:
        st.markdown("### ⚙️ Controllo")
        personalita = st.selectbox("Protocollo", ["Standard (Professionale)", "Tony Stark (Sarcastico/Geniale)", "Emergenza (Tattico/Rapido)"])
        lingua = st.selectbox("🌐 Lingua", ["Italiano", "English", "Español", "Français", "Deutsch"])
        st.session_state.voce_attiva = st.toggle("📢 Attiva Voce", value=st.session_state.voce_attiva)
        st.write("---")
        for canale in canali_fissi:
            if st.button(canale, use_container_width=True, type="primary" if canale == st.session_state.current_chat else "secondary"):
                st.session_state.current_chat = canale
                st.rerun()
        if st.button("🗑️ Svuota Chat", use_container_width=True):
            st.session_state.chat_sessions[st.session_state.current_chat] = []
            st.rerun()
        if st.button("🚪 Esci (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
else:
    col_chat = col_rest
    personalita = "Standard (Professionale)"
    lingua = "Italiano"

# Area Chat
with col_chat:
    if "Tony Stark" in personalita:
        base_prompt = "You are J.A.R.V.I.S., Tony Stark's AI. Answer with a brilliant, sarcastic tone, extremely sharp and tech-savvy."
    elif "Emergenza" in personalita:
        base_prompt = "J.A.R.V.I.S. Emergency Protocol. Answer in a concise, cold, military style."
    else:
        base_prompt = "J.A.R.V.I.S., advanced AI assistant. Answer professionally, with extreme technical precision."

    system_instruction = f"{base_prompt} Respond strictly in {lingua}. Date: {oggi}."

    def parla_testo(testo):
        if st.session_state.voce_attiva:
            t = testo.replace('"', "'").replace('\n', ' ')
            codice_lingua = {"Italiano": "it-IT", "English": "en-US"}.get(lingua, "it-IT")
            st.components.v1.html(f'<script>const s=window.speechSynthesis; const u=new SpeechSynthesisUtterance("{t}"); u.lang="{codice_lingua}"; s.speak(u);</script>', height=0)

    st.markdown(f"<h1 class='jarvis-title'>🤖 J.A.R.V.I.S. — [{st.session_state.current_chat}]</h1>", unsafe_allow_html=True)

    messaggi = st.session_state.chat_sessions[st.session_state.current_chat]
    for msg in messaggi:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.caption("💡 Suggerimenti del giorno:")
    col_sug1, col_sug2, col_sug3 = st.columns(3)
    domanda_cliccata = None
    with col_sug1:
        if st.button(domande_del_giorno[0], use_container_width=True, key="sug_0"):
            domanda_cliccata = domande_del_giorno[0]
    with col_sug2:
        if st.button(domande_del_giorno[1], use_container_width=True, key="sug_1"):
            domanda_cliccata = domande_del_giorno[1]
    with col_sug3:
        if st.button(domande_del_giorno[2], use_container_width=True, key="sug_2"):
            domanda_cliccata = domande_del_giorno[2]

    # Input e invio
    prompt_digitato = st.chat_input("Scrivi un comando per J.A.R.V.I.S....")
    prompt = prompt_digitato if prompt_digitato else domanda_cliccata

    if prompt:
        messaggi.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("J.A.R.V.I.S. sta elaborando..."):
                try:
                    messages_payload = [{"role": "system", "content": system_instruction}]
                    for m in messaggi:
                        messages_payload.append({"role": m["role"], "content": m["content"]})

                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages_payload,
                        temperature=0.7,
                    )
                    resp = chat_completion.choices[0].message.content
                    
                    st.markdown(resp)
                    messaggi.append({"role": "assistant", "content": resp})
                    parla_testo(resp)
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Errore riscontrato: {e}")
