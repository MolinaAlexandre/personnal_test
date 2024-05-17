import socket
import threading

# Configuration du serveur
server_ip = "127.0.0.1"
server_port = 6666

# Création du socket client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connexion au serveur
client.connect((server_ip, server_port))
print("Connecté au serveur")

# Boucle d'envoi de messages
while True:
    def send_message():
        while True:
            # Saisir un message depuis la console
            message = input("Entrez votre message (ou 'quit' pour quitter): ")

            # Envoyer le message au serveur
            client.send(bytes(message, "utf-8"))

            # Quitter la boucle si le message est 'quit'
            if message == "quit":
                break

    def receive_response():
        while True:
            # Recevoir la réponse du serveur
            response = client.recv(1024)
            print("Réponse du serveur:", response.decode("utf-8"))

    # Créer les threads
    send_thread = threading.Thread(target=send_message)
    receive_thread = threading.Thread(target=receive_response)

    # Démarrer les threads
    send_thread.start()
    receive_thread.start()

    # Attendre que les threads se terminent
    send_thread.join()
    receive_thread.join()

    # Fermer la connexion avec le serveur
    client.close()
