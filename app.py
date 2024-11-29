import streamlit as st
import requests
import uuid

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"  # Make sure this matches your FastAPI server address

def start_session(organisation_id, user_id):
    response = requests.post(f"{API_URL.rstrip('/')}/api/start-session", json={
        "organisation_id": organisation_id,
        "user_id": user_id
    })
    return response.json()

def ask_question(question, user_id):
    response = requests.post(f"{API_URL}/api/ask", json={
        "question": question,
        "user_id": user_id
    })
    return response.json()

def end_session(user_id):
    response = requests.post(f"{API_URL}/api/end-session", json={"user_id": user_id})
    return response.json()

st.title("AI Copilot Chatbot")

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'organisation_id' not in st.session_state:
    st.session_state.organisation_id = "default_org"
if 'session_started' not in st.session_state:
    st.session_state.session_started = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Start session button
if not st.session_state.session_started:
    if st.button("Start Session"):
        try:
            session_info = start_session(st.session_state.organisation_id, st.session_state.user_id)
            st.session_state.session_started = True
            st.session_state.session_id = session_info['session_id']
            st.success(f"Session started with ID: {session_info['session_id']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to start session: {str(e)}")

# Chat interface
if st.session_state.session_started:
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input
    user_input = st.chat_input("Type your question here...")
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Get AI response
        with st.spinner("AI is thinking..."):
            response = ask_question(user_input, st.session_state.user_id)
        
        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response['answer']})
        with st.chat_message("assistant"):
            st.write(response['answer'])

    # End session button
    if st.button("End Session"):
        end_session(st.session_state.user_id)
        st.session_state.session_started = False
        st.session_state.chat_history = []
        st.success("Session ended successfully")

# Display session info
if st.session_state.session_started:
    st.sidebar.info(f"Session ID: {st.session_state.session_id}")
    st.sidebar.info(f"User ID: {st.session_state.user_id}")