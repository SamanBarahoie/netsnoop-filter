#!/usr/bin/env python3
import socket
import threading

HOST = "0.0.0.0"   # Listen on all interfaces
PORT = 12345       # Port to listen on

def handle_client(conn, addr):
    """
    Handle an individual client connection.
    This will accept the connection and simply keep it open
    so that a client in CLOSE_WAIT can be observed.
    """
    print(f"[+] Connection from {addr}")
    try:
        # Read until client closes or timeout
        conn.settimeout(120)
        while True:
            data = conn.recv(1024)
            if not data:
                # Client closed the socket: server sees EOF
                print(f"[-] Client {addr} closed connection")
                break
            # Optionally echo back
            # conn.sendall(data)
    except socket.timeout:
        print(f"[!] Connection from {addr} timed out")
    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        conn.close()
        print(f"[*] Closed connection to {addr}")

def start_server():
    """
    Start a simple TCP server that handles each client in a new thread.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    start_server()
