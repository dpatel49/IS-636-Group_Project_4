import socket
import threading
import sys
import argparse
import traceback
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from datetime import datetime


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ChatClientGUI:
    def __init__(self, port, server_ip="127.0.0.1", debug=False):
        self.server_ip = server_ip
        self.port = port
        self.client = None
        self.chat_id = None
        self.nick = None
        self.debug = debug

        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Chat Client (GUI Version)")
        self.root.geometry("500x500")

        # Chat window (messages)
        self.chat_window = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state="disabled")
        self.chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Message input area
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.msg_entry = tk.Entry(self.input_frame, width=40)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Start client connection
        self.connect_to_server()

        # Start receiving thread
        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def connect_to_server(self):
        """Connect to server & send nickname."""
        try:
            # Create socket and connect (TLS removed)
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.server_ip, self.port))
        except Exception as e:
            if self.debug:
                traceback.print_exc()
            try:
                messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            except Exception:
                # If messagebox fails (headless), print to console
                print(f"Connection Error: {e}")
            try:
                self.root.destroy()
            except Exception:
                pass
            return

        # Ask for nickname
        self.nick = simpledialog.askstring("Nickname", "Enter your nickname:", parent=self.root)
        if not self.nick:
            self.nick = "Anonymous"

        # Send nickname to server
        self.client.sendall(f"NICK|{self.nick}".encode())

        self.display_message("[INFO] Connected to server...")

    def receive_messages(self):
        """Receive & display messages from server."""
        while True:
            try:
                msg = self.client.recv(4096).decode()
                if not msg:
                    break

                # Check for ID assignment
                if msg.startswith("ID|"):
                    self.chat_id = msg.split("|", 1)[1]
                    self.display_message(f"[INFO] Assigned chat ID: {self.chat_id}")
                    continue

                # Normal messages
                self.display_message(msg)

            except ConnectionResetError:
                self.display_message("[ERROR] Server disconnected.")
                break
            except Exception:
                if self.debug:
                    traceback.print_exc()
                break

    def send_message(self):
        """Send message to server."""
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        if msg.lower() == "exit":
            try:
                self.client.sendall("exit".encode())
            except:
                pass
            self.root.destroy()
            return

        try:
            self.client.sendall(msg.encode())
        except BrokenPipeError:
            self.display_message("[ERROR] Unable to send message.")
        except Exception:
            if self.debug:
                traceback.print_exc()

        self.msg_entry.delete(0, tk.END)

    def display_message(self, msg):
        """Display text in the chat window."""
        self.chat_window.config(state="normal")
        self.chat_window.insert(tk.END, msg + "\n")
        self.chat_window.yview(tk.END)
        self.chat_window.config(state="disabled")

    def on_close(self):
        """Gracefully exit."""
        try:
            if self.client:
                self.client.sendall("exit".encode())
        except:
            pass
        try:
            if self.client:
                self.client.close()
        except Exception:
            pass
        self.root.destroy()


# ---------- Program Entry Point ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat client GUI")
    parser.add_argument("port", type=int, help="Server port to connect to")
    parser.add_argument("server_ip", nargs="?", default="127.0.0.1", help="Server IP or hostname (default 127.0.0.1)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output to console")
    args = parser.parse_args()
    client_gui = ChatClientGUI(args.port, args.server_ip, debug=args.debug)
