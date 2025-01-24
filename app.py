from conversation import add_conversation, delete_conversations, load_conversations
from query_vectordb import generate_vector_db_response
from instruction import INSTRUCTION_TEMPLATE
import streamlit as st
import requests
import asyncio

FASTAPI_URL = "http://127.0.0.1:8000/generate"

def initialize_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = load_conversations()

def render_sidebar():
    st.sidebar.title("Actions")
    
    if st.sidebar.button("Delete All Conversations"):
        delete_conversations()
        st.session_state.conversation = []  
        st.sidebar.success("All conversations deleted successfully.")
    
    if st.sidebar.button("View Session Data"):
        st.sidebar.write("### Current Session Data:")
        st.sidebar.write(st.session_state)

def render_ui():
    render_sidebar()
    st.title("LLaMA Model with Streamlit UI")
    st.markdown("---")
    display_conversation_history()
    chat_input_handler() 

def chat_input_handler():
    prompt = st.chat_input("Type your message...")
    if prompt:  
        asyncio.run(handle_generate_response(prompt))

def display_conversation_history():
    for entry in st.session_state.conversation:
        with st.chat_message("user"):
            st.markdown(f"{entry['user']}") 

        with st.chat_message("assistant"):
            st.markdown(f"{entry['model']}")

async def handle_generate_response(prompt):
    if not prompt.strip():
        st.warning("Please enter a prompt to generate a response.")
        return
    vector_db_response = await generate_vector_db_response(prompt)
    full_prompt = f""" {vector_db_response}, {INSTRUCTION_TEMPLATE} Question: {prompt} """
    payload = {
        "prompt": "\n".join(
            [f"User: {entry['user']}\nModel: {entry['model']}" for entry in st.session_state.conversation]
        ) + "\n" + full_prompt,
    }
    print(full_prompt)
    print("--------------------------------------------------------")
    print(payload)
    model_response = call_fastapi_endpoint(payload)
    add_conversation(prompt, model_response)
    st.session_state.conversation.append({"user": prompt, "model": model_response})
   
    with st.chat_message("user"):
        st.markdown(f"{prompt}") 

    with st.chat_message("assistant"):
        st.markdown(f"{model_response}")
def call_fastapi_endpoint(payload):
    try:
        response = requests.post(FASTAPI_URL, json=payload)
        print("---------response-------------")
        print(response.json())
        response.raise_for_status()
        return response.json().get("response", "No response received")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def main():
    initialize_session_state()
    render_ui()

if __name__ == "__main__":
    main()