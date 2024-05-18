import socket
import threading
from time import sleep

# Liste pour stocker les connexions clients actives
clients = []

def send_users():
    for c in clients:
        c.send(bytes(f"new_wave", "utf-8"))
        for i in clients:
            peer_adr = i.getpeername()
            c.send(bytes(f"{peer_adr}", "utf-8"))
            sleep(0.1)

# Définition de la fonction de gestion des connexions clients
def handle_client(client_socket, addr):
    print(f"Connexion établie avec {addr}")
    clients.append(client_socket)
    send_users()
    
    while True:
        data = client_socket.recv(1024)
        if not data:
            print(f"Connexion fermée par {addr}")
            clients.remove(client_socket)
            send_users()
            break
        # print(f"Reçu de {addr}: {data.decode('utf-8')}")
        for c in clients:
            peer_adr = c.getpeername()
            peer_port = peer_adr[1]
            if peer_adr != addr:
                # print(f"Envoi à {c}: {data.decode('utf-8')}")
                message_to_send = f"Reçu de {addr}: {data.decode('utf-8')}"
                # c.send(bytes(message_to_send, "utf-8"))
            if data.decode("utf-8") == "exit":
                print(f"Déconnexion demandée par {addr}")
                clients.remove(client_socket)
                send_users()
                break

    client_socket.close()


server_ip = "0.0.0.0"
server_port = 6666

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))

server.listen(5)
print(f"Serveur en attente de connexions sur {server_ip}:{server_port}")

while True:
    client_socket, addr = server.accept()
    # Démarrer un thread pour gérer la connexion avec le client
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
