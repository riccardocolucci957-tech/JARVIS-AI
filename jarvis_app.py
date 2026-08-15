import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="centered")

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

oggi = datetime.now().strftime("%d/%m/%Y")
system_instruction = f"""
Sei J.A.R.V.I.S., un'intelligenza artificiale avanzata. 
Oggi è il giorno {oggi}. Rispondi sempre in italiano.
"""

model = genai.GenerativeModel(
    model_name='gemini-flash-latest',
    system_instruction=system_instruction
)

st.title("🤖 J.A.R.V.I.S.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistemi online, Capo."}]

chat = model.start_chat(history=[])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Comando..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
