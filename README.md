# IS-636-Group-Project
Group_4_Project of IS 636
# Chat Application

A simple Python chat server and GUI client with JSON logging.

## Project Structure

- `chat_server.py` — TCP chat server (supports multiple simultaneous clients, JSON-line logging)
- `chat_client.py` — Tkinter GUI chat client (connects to server, sends nickname, receives broadcasts)
- `chat_log.txt` — Server log file (JSON-formatted event logs)
- `README.md` — This file

## Features Implemented

### Core Messaging
- **Multiple Clients**: Server accepts multiple simultaneous TCP client connections and broadcasts messages to all connected clients
- **Chat IDs**: Server assigns unique IDs (`Client-1`, `Client-2`, etc.) to each connected client
- **Nicknames**: Clients send a nickname on connect; server stores and displays it with each message
- **Timestamps**: All messages and events include timestamps in `YYYY-MM-DD HH:MM:SS` format
### User Interface & Logging
- **GUI Client**: Tkinter-based GUI with scrollable chat window, message entry field, and send button
- **Chat Logging**: Server logs all events and messages to `chat_log.txt` in JSON-lines format (one JSON object per line)
- **Graceful Disconnect**: Clients can type `exit` to disconnect; server handles `KeyboardInterrupt` to notify and close all clients

### Code Quality
- **Thread Safety**: Server uses locks (`clients_lock`, `log_lock`) to safely manage concurrent client access and log writes
- **Error Handling**: Both server and client include exception handling and debug mode for troubleshooting

## Features Not Implemented

- UDP-based chat (current implementation is TCP only)
- Message framing robustness (relies on `recv` boundaries; length-prefix or newline framing would be more robust)
- Private messaging or channels
- `/who` command or message history retrieval
- Authentication or user persistence
- Encryption / TLS

## Requirements

- Python 3.8+
- Tkinter (should be included with standard Python distributions)

## Protocol Overview

Simple text-based protocol:

1. **Client connects** and sends: `NICK|<nickname>` (e.g., `NICK|Alice`)
2. **Server responds** with: `ID|<assigned_id>` (e.g., `ID|Client-1`)
3. **Server announces** to all clients: `[YYYY-MM-DD HH:MM:SS] [SERVER]: Client-1 (Alice) has joined the chat.`
4. **Client sends message**: plain text, e.g., `Hello everyone`
5. **Server broadcasts**: `[YYYY-MM-DD HH:MM:SS] [Client-1 | Alice]: Hello everyone`
6. **Client exits** by typing `exit` (case-insensitive) and server closes connection

## How to Run

### Start the Server (PowerShell)

```powershell
python .\chat_server.py 5000
```

Replace `5000` with any available port between 1025 and 65535.

**Expected output:**
```
[INFO] Server listening on port 5000...
[INFO] Connected to ('127.0.0.1', 54321) as Client-1 (Alice)
```

### Start the Client (PowerShell)

```powershell
python .\chat_client.py 5000
```

To connect to a remote server:
```powershell
python .\chat_client.py 5000 192.168.1.100
```

A Tkinter GUI window will appear. A dialog will prompt for your nickname, then the chat window opens.

### Multiple Clients

Open multiple PowerShell windows and run the client command in each to simulate multiple users chatting.

## Log Format

`chat_log.txt` contains JSON-lines format (one JSON object per line):

```json
{"timestamp":"2025-11-27 12:34:56","event":"connect","id":"Client-1","nick":"Alice","addr":"('127.0.0.1', 55906)"}
{"timestamp":"2025-11-27 12:35:10","event":"message","id":"Client-1","nick":"Alice","message":"Hello everyone"}
{"timestamp":"2025-11-27 12:36:00","event":"disconnect","id":"Client-1","nick":"Alice"}
{"timestamp":"2025-11-27 12:37:15","event":"shutdown"}
```

**Event types:**
- `connect` — Client joined (includes `id`, `nick`, `addr`)
- `message` — Chat message received (includes `id`, `nick`, `message`)
- `disconnect` — Client left (includes `id`, `nick`)
- `shutdown` — Server shut down

## Troubleshooting

### GUI doesn't appear or tkinter import fails
Check that Tkinter is available:
```powershell
python -c "import tkinter; print('tkinter OK', tkinter.TkVersion)"
```

If missing, reinstall Python with tcl/tk support or use a Python distribution that includes Tk.

### Client cannot connect to server
Verify the server is running and listening on the correct port:
```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 5000
```

Check firewall settings if connecting from a different machine.

### View live server logs (PowerShell)
```powershell
Get-Content .\chat_log.txt -Wait -Tail 20
```

This will show the last 20 lines and continuously display new entries.

### Enable client debug output
Run client with `--debug` flag to see tracebacks on connection or receive errors:
```powershell
python .\chat_client.py 5000 --debug
```

## Check Syntax

Verify the code has no syntax errors:
```powershell
python -m py_compile .\chat_server.py
python -m py_compile .\chat_client.py
```

No output means no errors.

## Architecture

### Server (`chat_server.py`)

- Creates a TCP socket and listens on the specified port
- Spawns a new thread for each connected client
- Maintains a dictionary of connected clients (`clients`)
- Broadcasts messages to all connected clients
- Logs events to `chat_log.txt` in JSON format
- Gracefully handles client disconnects and server shutdown

### Client (`chat_client.py`)

- Connects to the server via TCP socket
- Presents a Tkinter GUI with chat history and message entry
- Receives messages in a background thread
- Sends user input to the server
- Displays server messages and chat announcements in real time

## Future Enhancements

Possible improvements:

1. **Message Framing**: Use newline-terminated or length-prefixed messages for robustness
2. **UDP Variant**: Implement a UDP-based chat (stateless, no guaranteed delivery)
3. **Commands**: Add `/who` to list connected users, `/msg <id>` for private messages
4. **History**: Allow clients to request recent message history on connect
5. **Encryption**: Add TLS/SSL for secure communication
6. **Persistence**: Store user info and message history in a database
7. **Unit Tests**: Add test suite for server and client functions
8. **CLI Client**: Implement a command-line client as alternative to GUI
