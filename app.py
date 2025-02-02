import streamlit as st
import requests
import chromadb

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="farming_knowledge")

# NorskGPT API Configuration
API_KEY = "YOUR_API_KEY"
HEADERS = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}
NORSKGPT_API_URL = "https://api.norskgpt.com/api/v1/ai/chat/completions"

# Function to query NorskGPT
def ask_norskgpt(prompt, chat_history):
    data = {
        "model": "meta-llama-3.3-70b",  # Replace with the specific NorskGPT model if needed
        "messages": chat_history + [{"role": "user", "content": prompt}],
        "options": {"temperature": 0.7, "max_tokens": 800}
    }

    response = requests.post(NORSKGPT_API_URL, headers=HEADERS, json=data)
    
    if response.status_code == 200:
        return response.json().get("response", "No response received.")
    else:
        return f"❌ API Error: {response.status_code}"

# Function to retrieve relevant knowledge from ChromaDB
def retrieve_knowledge(query):
    results = collection.query(query_texts=[query], n_results=2)
    return [doc for doc in results["documents"][0]]

# Streamlit UI
st.title("🌾 Farmer's AI Advisor (Powered by NorskGPT)")
st.sidebar.write("ℹ️ **Chat with an AI trained on farming knowledge.**")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("💬 Ask a farming-related question:")
if st.button("Ask"):
    if user_input:
        retrieved_docs = retrieve_knowledge(user_input)
        knowledge_text = "\n".join(retrieved_docs)

        prompt = f"Using this knowledge: {knowledge_text}, answer: {user_input}"
        response = ask_norskgpt(prompt, st.session_state.chat_history)

        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response})

for chat in st.session_state.chat_history:
    role_icon = "👨‍🌾" if chat["role"] == "user" else "🤖"
    st.write(f"{role_icon} **{chat['role'].capitalize()}**: {chat['content']}")
