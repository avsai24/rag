from conversation import add_conversation, delete_conversations, load_conversations
from query_vectordb import generate_vector_db_response
from instruction import INSTRUCTION_TEMPLATE
from langchain.prompts import PromptTemplate
import streamlit as st
import requests
import asyncio

FASTAPI_URL = "http://127.0.0.1:8000/generate"

def model_name():
    options = ["llama3.2", "deepseek-r1"]
    st.sidebar.selectbox("Choose a model", options, key="model_name")

def initialize_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = load_conversations()

def render_sidebar():
    model_name()
    if st.sidebar.button("Delete All Conversations"):
        delete_conversations()
        st.session_state.conversation = []  
        st.sidebar.success("All conversations deleted successfully.")
    
    if st.sidebar.button("View Session Data"):
        st.sidebar.write("### Current Session Data:")
        st.sidebar.write(st.session_state)

def render_ui():
    st.title("RAG Using Streamlit & FastAPI")
    st.write("---")
    render_sidebar()
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
    model_name = st.session_state.model_name
    vector_db_response = await generate_vector_db_response(prompt)
    
    prompt_template = PromptTemplate(
        input_variables=["context", "instructions", "question"],
        template="{context}, {instructions} Question: {question}"
    )
    full_prompt = prompt_template.format(
        context=vector_db_response,
        instructions=INSTRUCTION_TEMPLATE,
        question=prompt
    )

    # full_prompt = f""" {vector_db_response}, {INSTRUCTION_TEMPLATE} Question: {prompt} """
    payload = {
        "prompt": "\n".join(
            [f"User: {entry['user']}\nModel: {entry['model']}" for entry in st.session_state.conversation]
        ) + "\n" + full_prompt,
    }
    print(full_prompt)
    print("--------------------------------------------------------")
    print(payload)
    model_response = call_fastapi_endpoint(payload,model_name)
    add_conversation(prompt, model_response,model_name)
    st.session_state.conversation.append({"user": prompt, "model": model_response, "model_name":model_name})
   
    with st.chat_message("user"):
        st.markdown(f"{prompt}") 

    with st.chat_message("assistant"):
        st.markdown(f"{model_response}")

def call_fastapi_endpoint(payload,model_name):
    try:
        payload["model"] = model_name
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