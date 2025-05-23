import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

# API Endpoints
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
TTS_URL = "https://api.groq.com/openai/v1/audio/speech"

# Headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Streamlit UI Setup
st.set_page_config(page_title="Voice Assistant 🤖🔊", page_icon="🧠", layout="centered")
st.title(" ByteBot 🔊")
st.markdown("Ask any question and listen to the response!")

# Initialize chat session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Show chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Get user input
user_input = st.chat_input("Type your question here...")

if user_input:
    # Display user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get response from LLaMA 3 8B
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(
                GROQ_CHAT_URL,
                headers=HEADERS,
                json={
                    "model": "llama3-8b-8192",
                    "messages": st.session_state.messages,
                    "temperature": 0.6
                }
            )

            if response.status_code == 200:
                bot_reply = response.json()["choices"][0]["message"]["content"]
                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})

                # Convert reply to speech using PlayAI TTS (Celeste voice)
                tts_response = requests.post(
                    TTS_URL,
                    headers=HEADERS,
                    json={
                        "model": "playai-tts",
                        "input": bot_reply,
                        "voice": "Celeste-PlayAI",
                        "response_format": "wav"
                    }
                )

                if tts_response.status_code == 200:
                    with open("reply.wav", "wb") as f:
                        f.write(tts_response.content)
                    st.audio("reply.wav", format="audio/wav")
                else:
                    st.error("TTS Error: " + tts_response.text)
            else:
                st.error("Error: " + response.text)
