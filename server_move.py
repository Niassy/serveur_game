import socket
import threading
import json
import os

# Render impose un port dans la variable d'environnement PORT
PORT = int(os.getenv("PORT", 5000))
HOST = "0.0.0.0"

players = {}
conns = {}
lock = threading.Lock()

def handle_client(conn, addr):
    addr_str = f"{addr[0]}:{addr[1]}"
    print(f"[+] Nouveau joueur : {addr_str}")

    with lock:
        color = "blue" if len(players) == 0 else "red"
        players[addr_str] = {"x": 50 if color=="blue" else 200,
                             "y": 50 if color=="blue" else 200,
                             "color": color}
        conns[addr_str] = conn

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            msg = json.loads(data.decode())

            with lock:
                players[addr_str]["x"] = msg["x"]
                players[addr_str]["y"] = msg["y"]

                game_state = json.dumps(players).encode()
                for c in conns.values():
                    try:
                        c.sendall(game_state)
                    except:
                        pass

    except Exception as e:
        print(f"ERREUR: {e}")

    finally:
        with lock:
            conns.pop(addr_str, None)
            players.pop(addr_str, None)
        conn.close()
        print(f"[-] Déconnecté : {addr_str}")

def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"SERVER RUNNING on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
