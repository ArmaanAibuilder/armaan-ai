import streamlit as st
import storage
from ai_core import get_reply, MODEL

st.set_page_config(page_title="Armaan AI", page_icon="🤖", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1050px; padding-top: 1.6rem;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.25);}
.chat-title {font-size: 2rem; font-weight: 750; margin-bottom: .2rem;}
.subtle {opacity: .72; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

if "chat_id" not in st.session_state:
    chats = storage.list_conversations()
    st.session_state.chat_id = chats[0]["id"] if chats else storage.create_conversation()

def start_new_chat():
    st.session_state.chat_id = storage.create_conversation()

with st.sidebar:
    st.title("🤖 Armaan AI")
    st.caption("Local AI • Free to use")
    if st.button("＋ New chat", use_container_width=True):
        start_new_chat()
        st.rerun()
    st.divider()
    st.subheader("Your chats")
    for chat in storage.list_conversations():
        label = chat["title"] or "New Chat"
        if len(label) > 34:
            label = label[:31] + "..."
        if st.button(label, key=f"chat_{chat['id']}", use_container_width=True,
                      type="primary" if chat["id"] == st.session_state.chat_id else "secondary"):
            st.session_state.chat_id = chat["id"]
            st.rerun()
    st.divider()
    st.subheader("🧠 Saved memory")
    st.caption("Add facts Armaan AI should remember across chats. Don't save secrets.")
    with st.form("add_memory_form", clear_on_submit=True):
        memory_text = st.text_input("Remember this", placeholder="I am learning Python.")
        if st.form_submit_button("Save memory") and memory_text.strip():
            storage.add_memory(memory_text)
            st.rerun()
    for memory in storage.list_memories():
        left, right = st.columns([5, 1])
        left.write(memory["content"])
        if right.button("✕", key=f"memory_{memory['id']}"):
            storage.delete_memory(memory["id"])
            st.rerun()
    st.divider()
    st.caption(f"Model: {MODEL}")
    st.caption("Chats and saved memories stay in armaan_ai.db on this Mac.")
    with st.expander("Delete current chat"):
        st.warning("This permanently deletes this chat and its messages.")
        if st.button("Delete chat", key="delete_current", use_container_width=True):
            storage.delete_conversation(st.session_state.chat_id)
            chats = storage.list_conversations()
            st.session_state.chat_id = chats[0]["id"] if chats else storage.create_conversation()
            st.rerun()

st.markdown('<div class="chat-title">Armaan AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Ask questions, build projects, or get help with code.</div>', unsafe_allow_html=True)
st.write("")
chat_id = st.session_state.chat_id
messages = storage.get_messages(chat_id)
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Message Armaan AI...")
if prompt and prompt.strip():
    prompt = prompt.strip()
    storage.add_message(chat_id, "user", prompt)
    history = storage.get_messages(chat_id)
    api_messages = [{"role": m["role"], "content": m["content"]} for m in history]
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Armaan AI is thinking..."):
            try:
                memories = [m["content"] for m in storage.list_memories()]
                reply = get_reply(api_messages)
                reply = ("I couldn't reach Ollama. Make sure the Ollama app is open and "
                         f"the `{MODEL}` model is installed.\n\nTechnical detail: `{exc}`")
            st.markdown(reply)
    storage.add_message(chat_id, "assistant", reply)
    st.rerun()
