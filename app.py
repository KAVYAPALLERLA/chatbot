import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
import os

# Set page config
st.set_page_config(
    page_title="Simple Chatbot",
    layout="wide"
)

llm = ChatGroq(
    groq_api_key=' ',
    model_name="llama3-70b-8192",
    temperature=0.6,
    max_tokens=1000)


def initialize_memory():
    """Initialize conversation memory"""
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
    return st.session_state.memory

def get_chat_response(llm, memory, user_input):
    """Get response using LangChain with memory"""
    try:
        # Get chat history
        messages = memory.chat_memory.messages
        
        # Add system message if it's the first interaction
        if not messages:
            system_msg = SystemMessage(content="You are a helpful assistant.")
            messages = [system_msg] + messages
        
        # Add current user message
        messages.append(HumanMessage(content=user_input))
        
        # Get response from LLM
        response = llm(messages)
        
        # Save to memory
        memory.save_context({"input": user_input}, {"output": response.content})
        
        return response.content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    st.title("Simple Chatbot")
    
    # Initialize components
    memory = initialize_memory()
    
    # Initialize chat messages for display
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message"):
        # Add user message to display history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display bot response
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response = get_chat_response(llm, memory, prompt)
                
                if response:
                    st.markdown(response)
                    # Add assistant response to display history
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Simple sidebar
    with st.sidebar:
        st.header("Settings")
        
        if st.button("Clear Chat"):
            st.session_state.chat_messages = []
            st.session_state.memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
            st.rerun()
        

if __name__ == "__main__":
    main()
