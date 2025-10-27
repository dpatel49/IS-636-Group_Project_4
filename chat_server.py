import socket
import threading
import sys

def handle_client(conn, addr):
    """Handles sending and receiving messages from the connected client."""
    print(f"[INFO] Connected to client at {addr}")

    # Send welcome message
    conn.sendall("Welcome to the chat! Type 'exit' to disconnect.\n".encode())

    while True:
        # Receive message from client
        msg = conn.recv(1024).decode().strip()
        if not msg:
            continue

        if msg.lower() == "exit":
            print("[INFO] Client disconnected.")
            conn.sendall("Goodbyee!\n".encode())
            break

        print(f"Client: {msg}")

        # Get server reply
        reply = input("You: ")
        if reply.lower() == "exit":
            conn.sendall("Server is terminating the connection.\n".encode())
            break
        conn.sendall(reply.encode())

    conn.close()
    print("[INFO] Connection is closed.")


def main():
    """Begins the chat server and waits for one client connection."""
    if len(sys.argv) != 2:
        print("Usage: python chat_server.py <port>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
        if port < 1025 or port > 65535:
            raise ValueError
    except ValueError:
        print("Error: Port must be an integer between 1025 and 65535.")
        sys.exit(1)

    # Create a TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(1)
    print(f"[INFO] Server listening on port {port}...")

    try:
        conn, addr = server.accept()
        handle_client(conn, addr)
    except KeyboardInterrupt:
        print("\n[INFO] Server closing down considerately.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
