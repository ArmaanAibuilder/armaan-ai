
import ollama
import storage

MODEL = "llama3.2:3b"

SYSTEM_PROMPT = """
You are Armaan AI, a friendly, helpful AI assistant.
You help with coding, schoolwork, writing, learning, and creative projects.
Explain things clearly and accurately. Be encouraging and respectful.
"""


def get_reply(messages):
    memories = storage.list_memories()
    memory_text = "\n".join(
        f"- {item['content']}" for item in memories
    )

    system = SYSTEM_PROMPT
    if memory_text:
        system += "\n\nSaved memories about the user:\n" + memory_text

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            *messages,
        ],
    )
    return response["message"]["content"]


def show_chats():
    chats = storage.list_conversations()
    if not chats:
        print("No saved chats yet.")
        return

    print("\nSaved conversations:")
    for chat in chats:
        print(f"  {chat['id']}: {chat['title']}")
    print()


def main():
    chats = storage.list_conversations()

    if chats:
        chat_id = chats[0]["id"]
        print(f"Loaded saved chat #{chat_id}: {chats[0]['title']}")
    else:
        chat_id = storage.create_conversation("First Chat")
        print("Created your first saved chat!")

    print("\nArmaan AI is ready!")
    print("Commands: /new, /chats, /memory, /exit\n")

    while True:
        try:
            question = input("You: ").strip()

            if not question:
                continue

            if question.lower() in ("/exit", "exit", "quit"):
                print("Armaan AI: See you next time!")
                break

            if question.lower() == "/new":
                chat_id = storage.create_conversation()
                print(f"Started a new chat! Chat ID: {chat_id}\n")
                continue

            if question.lower() == "/chats":
                show_chats()
                continue

            if question.lower() == "/memory":
                memories = storage.list_memories()
                if memories:
                    print("\nSaved memories:")
                    for item in memories:
                        print(f"- {item['content']}")
                else:
                    print("No saved memories yet.")
                print()
                continue

            storage.add_message(chat_id, "user", question)

            saved_messages = storage.get_messages(chat_id)
            history = [
                {"role": item["role"], "content": item["content"]}
                for item in saved_messages
            ]

            answer = get_reply(history)
            storage.add_message(chat_id, "assistant", answer)

            print(f"\nArmaan AI: {answer}\n")

        except KeyboardInterrupt:
            print("\nArmaan AI stopped.")
            break

        except Exception as error:
            print(f"\nSomething went wrong: {error}\n")


if __name__ == "__main__":
    main()

