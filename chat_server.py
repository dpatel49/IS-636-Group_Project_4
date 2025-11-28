import socket
import threading
import sys
import argparse
import json
from datetime import datetime

# Global structures
clients = {}  # socket -> {"id": str, "nick": str}
clients_lock = threading.Lock()
next_id = 1
log_lock = threading.Lock()
LOG_FILE = "chat_log.txt"


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(event_type: str, **kwargs):
    """Write a JSON line describing an event to the log file (thread-safe).

    Example entry:
      {"timestamp":"...","event":"connect","id":"Client-1","nick":"Alice","addr":"('127.0.0.1', 55906)"}
    """
    entry = {"timestamp": timestamp(), "event": event_type}
    entry.update(kwargs)
    with log_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def broadcast(message: str, exclude_sock=None):
    """Send message to all connected clients except exclude_sock (if given)."""
    with clients_lock:
        for sock in list(clients.keys()):
            if sock is exclude_sock:
                continue
            try:
                sock.sendall(message.encode())
            except Exception:
                # If send fails, remove client
                remove_client(sock)

def remove_client(conn):
    """Remove client and close socket safely."""
    with clients_lock:
        info = clients.pop(conn, None)
    try:
        conn.close()
    except:
        pass
    if info:
        leave_msg = f"[{timestamp()}] [SERVER]: {info['id']} ({info['nick']}) has disconnected."
        print(leave_msg)
        log_event("disconnect", id=info.get("id"), nick=info.get("nick"))
        broadcast(leave_msg)

def handle_client(conn, addr):
    """Thread: handle a single client connection."""
    global next_id
    try:
        # Receive nickname as the first message with format "NICK|nickname"
        raw = conn.recv(1024).decode().strip()
        if not raw:
            conn.close()
            return

        if raw.startswith("NICK|"):
            nick = raw.split("|", 1)[1].strip() or "Anonymous"
        else:
            # If client didn't send NICK properly, treat raw as nickname
            nick = raw.strip() or "Anonymous"

        # Assign unique ID
        with clients_lock:
            assigned_id = f"Client-{next_id}"
            next_id += 1
            clients[conn] = {"id": assigned_id, "nick": nick}

        # Send assigned ID to client (so client can show its ID if it wants)
        conn.sendall(f"ID|{assigned_id}".encode())

        welcome = f"[{timestamp()}] [SERVER]: Welcome {nick}! You are {assigned_id}."
        conn.sendall(welcome.encode())
        print(f"[INFO] Connected to {addr} as {assigned_id} ({nick})")
        log_event("connect", id=assigned_id, nick=nick, addr=str(addr))

        # Announce to others
        broadcast(f"[{timestamp()}] [SERVER]: {assigned_id} ({nick}) has joined the chat.", exclude_sock=conn)

        while True:
            try:
                msg = conn.recv(4096).decode()
            except ConnectionResetError:
                break
            if not msg:
                # connection closed or empty; break to remove client
                break

            msg = msg.strip()
            if not msg:
                continue

            # If client intentionally exits, they might send "exit"
            if msg.lower() == "exit":
                try:
                    conn.sendall("Goodbye!".encode())
                except:
                    pass
                break

            # Format message and broadcast
            with clients_lock:
                sender = clients.get(conn, {"id": "Unknown", "nick": "Unknown"})
            formatted = f"[{timestamp()}] [{sender['id']} | {sender['nick']}]: {msg}"
            print(formatted)
            log_event("message", id=sender.get("id"), nick=sender.get("nick"), message=msg)
            broadcast(formatted, exclude_sock=None)

    except Exception as e:
        print(f"[ERROR] Exception in client handler: {e}")
    finally:
        remove_client(conn)


def main():
    parser = argparse.ArgumentParser(description="Simple chat server with JSON logging")
    parser.add_argument("port", type=int, help="Port to listen on (1025-65535)")
    args = parser.parse_args()

    port = args.port
    if port < 1025 or port > 65535:
        print("Error: Port must be an integer between 1025 and 65535.")
        sys.exit(1)


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"[INFO] Server listening on port {port}...")

    try:
        while True:
            conn, addr = server.accept()

            # Start a thread to handle this client
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[INFO] Server is shutting down.")
        log_event("shutdown")
        with clients_lock:
            for sock in list(clients.keys()):
                try:
                    sock.sendall("[SERVER]: Server is shutting down. Disconnecting...\n".encode())
                    sock.close()
                except:
                    pass
            clients.clear()
    finally:
        server.close()
        print("[INFO] Server socket closed.")

if __name__ == "__main__":
    main()
