import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import queue
import storage
from ai_core import get_reply, MODEL

BG = "#171923"
PANEL = "#202433"
TEXT = "#f2f4f8"
ACCENT = "#7c83ff"
MUTED = "#aab0c0"

class ArmaanDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("Armaan AI")
        self.root.geometry("1000x720")
        self.root.minsize(720, 500)
        self.root.configure(bg=BG)
        self.busy = False
        self.events = queue.Queue()
        self.chat_id = None
        self.build_ui()
        chats = storage.list_conversations()
        self.chat_id = chats[0]["id"] if chats else storage.create_conversation()
        self.refresh_chat_list()
        self.load_messages()
        self.root.after(100, self.process_events)

    def build_ui(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        side = tk.Frame(outer, bg=PANEL, width=260)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="🤖 Armaan AI", bg=PANEL, fg=TEXT,
                 font=("Helvetica", 19, "bold")).pack(anchor="w", padx=16, pady=(18, 4))
        tk.Label(side, text="Local AI • Free to use", bg=PANEL, fg=MUTED,
                 font=("Helvetica", 10)).pack(anchor="w", padx=16, pady=(0, 14))
        ttk.Button(side, text="+ New chat", command=self.new_chat).pack(fill="x", padx=12, pady=(0, 8))
        ttk.Button(side, text="🧠 Manage saved memory", command=self.manage_memories).pack(fill="x", padx=12, pady=(0, 12))
        self.chat_list = tk.Listbox(side, bg=BG, fg=TEXT, selectbackground=ACCENT,
                                    activestyle="none", borderwidth=0,
                                    highlightthickness=0, font=("Helvetica", 11))
        self.chat_list.pack(fill="both", expand=True, padx=8, pady=4)
        self.chat_list.bind("<<ListboxSelect>>", self.select_chat)
        tk.Label(side, text=f"Model: {MODEL}", bg=PANEL, fg=MUTED,
                 font=("Helvetica", 9), wraplength=220).pack(anchor="w", padx=14, pady=12)
        ttk.Button(side, text="Delete selected chat", command=self.delete_chat).pack(fill="x", padx=12, pady=(0, 14))

        main = tk.Frame(outer, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        header = tk.Frame(main, bg=BG)
        header.pack(fill="x", padx=22, pady=(18, 8))
        tk.Label(header, text="Armaan AI", bg=BG, fg=TEXT,
                 font=("Helvetica", 20, "bold")).pack(anchor="w")
        tk.Label(header, text="Questions, coding, debugging, and ideas",
                 bg=BG, fg=MUTED, font=("Helvetica", 10)).pack(anchor="w", pady=(3, 0))
        self.transcript = tk.Text(main, bg=BG, fg=TEXT, insertbackground=TEXT,
                                  wrap="word", borderwidth=0, highlightthickness=0,
                                  font=("Helvetica", 12), padx=20, pady=14,
                                  state="disabled")
        self.transcript.pack(fill="both", expand=True, padx=6)
        self.transcript.tag_configure("user", foreground="#aeb3ff", font=("Helvetica", 12, "bold"),
                                      spacing1=12, spacing3=4)
        self.transcript.tag_configure("assistant", foreground="#83e0b1", font=("Helvetica", 12, "bold"),
                                      spacing1=12, spacing3=4)
        self.transcript.tag_configure("body", foreground=TEXT, lmargin1=12, lmargin2=12, spacing3=9)
        composer = tk.Frame(main, bg=PANEL)
        composer.pack(fill="x", padx=18, pady=16)
        self.entry = tk.Text(composer, height=3, wrap="word", bg=PANEL, fg=TEXT,
                             insertbackground=TEXT, borderwidth=0, highlightthickness=0,
                             font=("Helvetica", 12))
        self.entry.pack(side="left", fill="both", expand=True, padx=12, pady=10)
        self.entry.bind("<Command-Return>", self.send_event)
        self.entry.bind("<Control-Return>", self.send_event)
        self.send_button = ttk.Button(composer, text="Send", command=self.send_message)
        self.send_button.pack(side="right", padx=10, pady=10)
        self.status = tk.StringVar(value="Ready")
        tk.Label(main, textvariable=self.status, bg=BG, fg=MUTED,
                 font=("Helvetica", 9)).pack(anchor="w", padx=22, pady=(0, 8))

    def refresh_chat_list(self):
        self.chat_rows = storage.list_conversations()
        self.chat_list.delete(0, tk.END)
        for chat in self.chat_rows:
            self.chat_list.insert(tk.END, (chat["title"] or "New Chat")[:32])
        for i, chat in enumerate(self.chat_rows):
            if chat["id"] == self.chat_id:
                self.chat_list.selection_set(i)
                self.chat_list.activate(i)
                break

    def load_messages(self):
        self.transcript.configure(state="normal")
        self.transcript.delete("1.0", tk.END)
        for msg in storage.get_messages(self.chat_id):
            self.transcript.insert(tk.END, "You\n" if msg["role"] == "user" else "Armaan AI\n", msg["role"])
            self.transcript.insert(tk.END, msg["content"] + "\n\n", "body")
        self.transcript.configure(state="disabled")
        self.transcript.see(tk.END)

    def append_message(self, role, content):
        self.transcript.configure(state="normal")
        self.transcript.insert(tk.END, "You\n" if role == "user" else "Armaan AI\n", role)
        self.transcript.insert(tk.END, content + "\n\n", "body")
        self.transcript.configure(state="disabled")
        self.transcript.see(tk.END)

    def new_chat(self):
        if self.busy:
            messagebox.showinfo("Please wait", "Wait for the current answer to finish first.")
            return
        self.chat_id = storage.create_conversation()
        self.refresh_chat_list()
        self.load_messages()
        self.entry.focus_set()

    def select_chat(self, _event=None):
        if self.busy:
            return
        selected = self.chat_list.curselection()
        if selected and selected[0] < len(self.chat_rows):
            self.chat_id = self.chat_rows[selected[0]]["id"]
            self.load_messages()

    def delete_chat(self):
        if self.busy:
            messagebox.showinfo("Please wait", "Wait for the current answer to finish first.")
            return
        if not messagebox.askyesno("Delete chat", "Permanently delete this chat and its messages?"):
            return
        storage.delete_conversation(self.chat_id)
        chats = storage.list_conversations()
        self.chat_id = chats[0]["id"] if chats else storage.create_conversation()
        self.refresh_chat_list()
        self.load_messages()

    def manage_memories(self):
        win = tk.Toplevel(self.root)
        win.title("Saved memory")
        win.geometry("540x420")
        win.configure(bg=BG)
        tk.Label(win, text="Saved memory", bg=BG, fg=TEXT,
                 font=("Helvetica", 16, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(win, text="These notes can be used in every chat. Don't save passwords or secrets.",
                 bg=BG, fg=MUTED, wraplength=500, justify="left").pack(anchor="w", padx=16, pady=(0, 10))
        listing = tk.Listbox(win, bg=PANEL, fg=TEXT, selectbackground=ACCENT,
                             activestyle="none", borderwidth=0, highlightthickness=0)
        listing.pack(fill="both", expand=True, padx=16, pady=6)
        def refresh():
            listing.delete(0, tk.END)
            for mem in storage.list_memories():
                listing.insert(tk.END, mem["content"])
        def add():
            value = simpledialog.askstring("Add memory", "What should Armaan AI remember?", parent=win)
            if value and value.strip():
                storage.add_memory(value)
                refresh()
        def remove():
            selected = listing.curselection()
            if not selected:
                return
            memories = storage.list_memories()
            if selected[0] < len(memories):
                storage.delete_memory(memories[selected[0]]["id"])
                refresh()
        buttons = tk.Frame(win, bg=BG)
        buttons.pack(fill="x", padx=16, pady=12)
        ttk.Button(buttons, text="Add memory", command=add).pack(side="left")
        ttk.Button(buttons, text="Delete selected", command=remove).pack(side="left", padx=8)
        refresh()

    def send_event(self, _event=None):
        self.send_message()
        return "break"

    def send_message(self):
        if self.busy:
            return
        prompt = self.entry.get("1.0", "end").strip()
        if not prompt:
            return
        self.entry.delete("1.0", tk.END)
        storage.add_message(self.chat_id, "user", prompt)
        self.append_message("user", prompt)
        self.busy = True
        self.send_button.configure(state="disabled")
        self.status.set("Armaan AI is thinking...")
        chat_id = self.chat_id
        history = storage.get_messages(chat_id)
        api_messages = [{"role": m["role"], "content": m["content"]} for m in history]
        memories = [m["content"] for m in storage.list_memories()]
        threading.Thread(target=self.ask_model, args=(chat_id, api_messages, memories), daemon=True).start()

    def ask_model(self, chat_id, history, memories):
        try:
            reply = get_reply(history, memories)
        except Exception as exc:
            reply = ("I couldn't reach Ollama. Check that Ollama is open and that "
                     f"the {MODEL} model is installed.\n\nTechnical detail: {exc}")
        self.events.put((chat_id, reply))

    def process_events(self):
        try:
            while True:
                chat_id, reply = self.events.get_nowait()
                storage.add_message(chat_id, "assistant", reply)
                if chat_id == self.chat_id:
                    self.append_message("assistant", reply)
                self.busy = False
                self.send_button.configure(state="normal")
                self.status.set("Ready")
                self.refresh_chat_list()
        except queue.Empty:
            pass
        self.root.after(100, self.process_events)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArmaanDesktop(root)
    root.mainloop()
