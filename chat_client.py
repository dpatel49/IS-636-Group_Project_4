import socket
import threading
import sys

def receive_messages(client_socket):
    """Thread function to continuously receive messages from the server."""
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            print("\nServer:", msg)
        except ConnectionResetError:
            print("\n[ERROR] Server closed the connection.")
            break
        except:
            break

def main():
    """Starts the chat client and connects to the server."""
    if len(sys.argv) != 2:
        print("Usage: python chat_client.py <port>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
        if port < 1025 or port > 65535:
            raise ValueError
    except ValueError:
        print("Error: Port must be an integer between 1025 and 65535.")
        sys.exit(1)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(("127.0.0.1", port))
        print("[INFO] Connected to server.")
        print("Type 'exit' to leave the chat.")
    except ConnectionRefusedError:
        print("[ERROR] Could not connect to the server. Is it running?")
        sys.exit(1)

    # Start a thread to listen for incoming messages
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    while True:
        msg = input("You: ")
        if msg.lower() == "exit":
            client.sendall(msg.encode())
            break
        client.sendall(msg.encode())

    client.close()
    print("[INFO] Disconnected from server.")


if __name__ == "__main__":
    main()
