import socket
import threading
import pygame
import sys
from time import sleep

server_ip = "192.168.1.19"
server_port = 6666
users = []

pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Client de Jeu Multijoueur")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Boutons
button_font = pygame.font.Font(None, 36)
button_text_join = button_font.render("Rejoindre", True, WHITE)
button_text_quit = button_font.render("Quitter", True, WHITE)
button_rect_join = pygame.Rect(220, 200, 200, 50)
button_rect_quit = pygame.Rect(220, 300, 200, 50)
button_color = RED
users_rect = pygame.Rect(120, 100, 400, 250)
users_text_font = pygame.font.Font(None, 24)

def connect_to_server(exit_event):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    print("Connecté au serveur")

    running_threads = True

    def send_message():
        while running_threads:
            # message = "position: 100,200"
            # client.send(bytes(message, "utf-8"))
            pygame.time.wait(10)

    def receive_response():
        while running_threads:
            response = client.recv(1024)
            print("Réponse du serveur:", response.decode("utf-8"))
            users.append(response.decode("utf-8"))
            if response.decode("utf-8") == "new_wave":
                users.clear()

    send_thread = threading.Thread(target=send_message)
    receive_thread = threading.Thread(target=receive_response)

    send_thread.start()
    receive_thread.start()


    while not exit_event.is_set():
        pass

    print("Quitting threads")

    running_threads = False
    client.send(b"exit")

    return

def display_lobby():
    exit_event = threading.Event()
    connect_thread = threading.Thread(target=connect_to_server, args=(exit_event,))
    connect_thread.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit_event.set()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_quit.collidepoint(event.pos):
                    running = False
                    exit_event.set()

        screen.fill(BLACK)
        pygame.draw.rect(screen, button_color, button_rect_quit)
        screen.blit(button_text_quit, (button_rect_quit.x + 20, button_rect_quit.y + 10))

        # Dessiner la zone de texte pour les utilisateurs connectés
        pygame.draw.rect(screen, BLUE, users_rect, 2)
        # Exemple d'utilisateurs connectés
        # users = ["User1", "User2", "User3"]
        y_offset = 0
        for user in users:
            user_text = users_text_font.render(user, True, WHITE)
            screen.blit(user_text, (users_rect.x + 10, users_rect.y + 10 + y_offset))
            y_offset += 30

        pygame.display.flip()

    connect_thread.join()


while True:

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_join.collidepoint(event.pos):
                    display_lobby()

        screen.fill(WHITE)
        pygame.draw.rect(screen, button_color, button_rect_join)
        screen.blit(button_text_join, (button_rect_join.x + 20, button_rect_join.y + 10))
        pygame.display.flip()
