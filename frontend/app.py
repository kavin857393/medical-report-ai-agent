# frontend/app.py
import streamlit as st
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("🩺 Medical Report AI Chatbot")

# File Upload Section
st.subheader("Upload Medical Report (PDF)")
uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    logger.info(f"Uploading file: {uploaded_file.name}")
    try:
        response = requests.post("http://127.0.0.1:8000/upload/", files=files)
        if response.status_code == 200:
            st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
            st.session_state["current_file"] = uploaded_file.name
        else:
            st.error("❌ File upload failed!")
            logger.error(f"File upload failed: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        st.error("❌ Failed to connect to the backend server for upload.")
        logger.error(f"Upload request failed: {e}")

# Display current file
if "current_file" in st.session_state:
    st.info(f"Current file: {st.session_state['current_file']}")

# Chatbot Section
st.subheader("Ask Questions about the Medical Report")
query = st.text_input("Enter your question:")

if st.button("Ask"):
    if query:
        with st.spinner("⏳ Getting response from AI..."):
            logger.info(f"Sending query: {query}")
            try:
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    "http://127.0.0.1:8000/chat/",
                    json={"query": query},
                    headers=headers
                )
                if response.status_code == 200:
                    answer = response.json().get("response", "No response received.")
                    st.markdown(f"**🧠 AI Response:**\n\n> {answer}")
                else:
                    st.error("❌ Failed to get a response from the chatbot.")
                    logger.error(f"Chat query failed: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                st.error("❌ Failed to connect to the backend server for chat.")
                logger.error(f"Chat request failed: {e}")
    else:
        st.warning("⚠️ Please enter a question.")