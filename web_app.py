```python
import streamlit as st
import storage
from ai_core import get_reply, MODEL

st.set_page_config(
    page_title="Armaan AI",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    max-width: 1050px;
    padding-top: 1.6rem;
}
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,.25);
}
.chat-title {
    font-size: 2rem;
    font-weight: 750;
    margin-bottom: .2rem;
}
.subtle {
    opacity: .72;
    font-size: .9rem;
}
</style>
""", unsafe_allow_html=True)


# Initialize the current conversation
if "chat_id" not in st.session_state:
    chats = storage.list_conversations()
    st.session_state.chat_id = (
        chats[0]["id"] if chats
        else storage.create_conversation()
    )


# Start a new conversation
def start_new_chat():
    st.session_state.chat_id = storage.create_conversation()


# Sidebar
with st.sidebar:
    st.title("🤖 Armaan AI")
    st.caption("AI assistant • Free to use")

    if st.button("＋ New chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.divider()
    st.subheader("Your chats")

    for chat in storage.list_conversations():
        label = chat["title"] or "New Chat"

        if len(label) > 34:
            label = label[:31] + "..."

        if st.button(
            label,
            key=f"chat_{chat['id']}",
            use_container_width=True,
            type=(
                "primary"
                if chat["id"] == st.session_state.chat_id
                else "secondary"
            )
        ):
            st.session_state.chat_id = chat["id"]
            st.rerun()

    st.divider()
    st.subheader("🧠 Saved memory")
    st.caption(
        "Add facts Armaan AI should remember across chats. "
        "Don't save secrets."
    )

    with st.form("add_memory_form", clear_on_submit=True):
        memory_text = st.text_input(
            "Remember this",
            placeholder="I am learning Python."
        )

        if st.form_submit_button("Save memory"):
            if memory_text.strip():
                storage.add_memory(memory_text.strip())
                st.rerun()

    for memory in storage.list_memories():
        left, right = st.columns([5, 1])
        left.write(memory["content"])

        if right.button("✕", key=f"memory_{memory['id']}"):
            storage.delete_memory(memory["id"])
            st.rerun()

    st.divider()
    st.caption(f"Model: {MODEL}")
    st.caption(
        "Conversation storage depends on the environment "
        "where Armaan AI is running."
    )

    with st.expander("Delete current chat"):
        st.warning(
            "This permanently deletes this chat and its messages."
        )

        if st.button(
            "Delete chat",
            key="delete_current",
            use_container_width=True
        ):
            storage.delete_conversation(st.session_state.chat_id)

            chats = storage.list_conversations()
            st.session_state.chat_id = (
                chats[0]["id"] if chats
                else storage.create_conversation()
            )

            st.rerun()


# Main chat interface
st.markdown(
    '<div class="chat-title">Armaan AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtle">'
    'Ask questions, build projects, or get help with code.'
    '</div>',
    unsafe_allow_html=True
)

st.write("")

chat_id = st.session_state.chat_id
messages = storage.get_messages(chat_id)

# Display conversation history
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# Handle a new message
prompt = st.chat_input("Message Armaan AI...")

if prompt and prompt.strip():
    prompt = prompt.strip()

    storage.add_message(chat_id, "user", prompt)

    history = storage.get_messages(chat_id)

    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m["role"] in ("user", "assistant")
    ]

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Armaan AI is thinking..."):
            try:
                reply = get_reply(api_messages)

                if not isinstance(reply, str) or not reply.strip():
                    reply = "I received an empty response. Please try again."

            except Exception as exc:
                reply = (
                    "I couldn't connect to the AI model.\n\n"
                    "Please check that the AI service is running "
                    "and the model is available.\n\n"
                    f"Technical detail: `{exc}`"
                )

            st.markdown(reply)

    storage.add_message(chat_id, "assistant", reply)
    st.rerun()
```
