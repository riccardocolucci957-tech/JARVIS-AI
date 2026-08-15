{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Roman;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf0 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 import streamlit as st\
import google.generativeai as genai\
from datetime import datetime\
\
st.set_page_config(page_title="JARVIS AI", page_icon="\uc0\u55358 \u56598 ", layout="centered")\
\
# Leggiamo la chiave in modo sicuro dai "Secrets" di Streamlit\
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]\
genai.configure(api_key=GOOGLE_API_KEY)\
\
oggi = datetime.now().strftime("%d/%m/%Y")\
system_instruction = f"""\
Sei J.A.R.V.I.S., un'intelligenza artificiale avanzata. \
Oggi \'e8 il giorno \{oggi\}. Rispondi sempre in italiano.\
"""\
\
model = genai.GenerativeModel(\
    model_name='gemini-flash-latest',\
    system_instruction=system_instruction\
)\
\
st.title("\uc0\u55358 \u56598  J.A.R.V.I.S.")\
\
if "messages" not in st.session_state:\
    st.session_state.messages = [\{"role": "assistant", "content": "Sistemi online, Capo."\}]\
\
chat = model.start_chat(history=[])\
\
for message in st.session_state.messages:\
    with st.chat_message(message["role"]):\
        st.markdown(message["content"])\
\
if prompt := st.chat_input("Comando..."):\
    st.session_state.messages.append(\{"role": "user", "content": prompt\})\
    with st.chat_message("user"):\
        st.markdown(prompt)\
\
    with st.chat_message("assistant"):\
        response = chat.send_message(prompt)\
        st.markdown(response.text)\
        st.session_state.messages.append(\{"role": "assistant", "content": response.text\})}