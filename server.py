import socket
import threading
from time import sleep
from map import MiniGame1

clients = []
ingame = []
usernames = []

def send_users(addr):
    index = 0
    for c in clients:
        c.send(bytes("new_wave", "utf-8"))
        for u in usernames:
            sleep(0.2)
            c.send(bytes(f"{u['username']}", "utf-8"))
        index += 1

def add_users(addr, username):
    usernames.append({'addr': addr, 'username': username})

def del_users(addr):
    for u in usernames:
        if u['addr'] == addr:
            usernames.remove(u)
            break

def send_to_ingame():
    for c in clients:
        for u in ingame:
            if c.getpeername() == u:
                c.send(bytes("You are Ingame", "utf-8"))


def get_ingame_pos(message, sender_addr):
    for client_socket in clients:
        addr = client_socket.getpeername()
        if addr in ingame and addr != sender_addr:
            client_socket.send(bytes(message, "utf-8"))


def del_ingame_player(addr):
    for u in ingame:
        if u['addr'] == addr:
            ingame.remove(u)
            break

def check_before_launch():
    if len(usernames) == 2:
        for c in clients:
            c.send(bytes("start", "utf-8"))

def handle_client(client_socket, addr):
    clients.append(client_socket)
    
    while True:
        try :
            data = client_socket.recv(1024)
        except Exception as e:
            print(f"Receive response error: {e}")
            data = None

        if not data:
            clients.remove(client_socket)
            del_users(addr)
            del_ingame_player(addr)
            send_users(addr)
            break
        if (data.decode('utf-8') == "ingame"):
            ingame.append(addr)
            print("ingame : ",ingame)
            if len(ingame) == 2:
                for u in ingame:
                    del_users(u)
        if (client_socket.getpeername() in ingame):
            get_ingame_pos(data.decode('utf-8'), addr)
        else:
            add_users(addr, data.decode('utf-8'))
            send_users(addr)
            check_before_launch()

        for c in clients:
            peer_adr = c.getpeername()
            peer_port = peer_adr[1]
            if peer_adr != addr:
                message_to_send = f"Reçu de {addr}: {data.decode('utf-8')}"
            if data.decode("utf-8") == "exit":
                clients.remove(client_socket)
                del_users(addr)
                del_ingame_player(addr)
                send_users(addr)
                break

    client_socket.close()


server_ip = "192.168.1.42"
server_port = 6666

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))

server.listen(5)
print(f"Serveur en attente de connexions sur {server_ip}:{server_port}")

while True:
    client_socket, addr = server.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
