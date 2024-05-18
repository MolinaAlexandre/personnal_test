import pygame
import sys
import threading
import socket
from time import sleep

class Player2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 50

def parse_data_and_get_position(data, player2):
    print("VALEUR RECUE : ", data.decode('utf-8'))
    try :
        x, y = data.decode().split(",")
        player2.x = int(x)
        player2.y = int(y)
    except Exception as e:
        print(f"Error parsing data: {e}")


def receive_data_from_server(client, player2):
    while True:
        data = client.recv(1024)
        parse_data_and_get_position(data, player2)

def send_player_position_to_server(client, player_rect):
    data = f"{player_rect.x},{player_rect.y}".encode()
    client.sendall(data)

def MiniGame2(client):
    # Initialisation de Pygame
    pygame.init()

    # Définition des dimensions de la fenêtre
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jeu de plateforme 2D")

    # Définition des couleurs
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)

    # Définition du joueur
    player_size = 50
    player_x = 50
    player_y = SCREEN_HEIGHT - player_size
    player_speed = 5
    player_jump = -15
    gravity = 1
    player_velocity_y = 0
    is_jumping = False

    # Création du deuxième joueur
    player2 = Player2(100, 100)

    # Définition des plateformes selon le schéma
    platforms = [
        pygame.Rect(0, 550, 200, 20),  # Plateforme de départ
        pygame.Rect(200, 450, 200, 20),
        pygame.Rect(400, 350, 100, 20),
        pygame.Rect(550, 250, 150, 20),
        pygame.Rect(700, 150, 100, 20)
    ]

    # Définition du point de départ et du point d'arrivée
    start_point = pygame.Rect(50, SCREEN_HEIGHT - player_size, player_size, player_size)
    end_point = pygame.Rect(750, 100, player_size, player_size)

    # Lancement du thread de réception
    receive_thread = threading.Thread(target=receive_data_from_server, args=(client, player2))
    receive_thread.start()

    # Boucle principale du jeu
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
            send_player_position_to_server(client, pygame.Rect(player_x, player_y, player_size, player_size))
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
            send_player_position_to_server(client, pygame.Rect(player_x, player_y, player_size, player_size))
        if keys[pygame.K_SPACE] and not is_jumping:
            is_jumping = True
            player_velocity_y = player_jump
            send_player_position_to_server(client, pygame.Rect(player_x, player_y, player_size, player_size))
        
        # Appliquer la gravité
        player_velocity_y += gravity
        player_y += player_velocity_y

        # Vérification des collisions avec le sol
        if player_y >= SCREEN_HEIGHT - player_size:
            player_y = SCREEN_HEIGHT - player_size
            player_velocity_y = 0
            is_jumping = False

        # Vérification des collisions avec les plateformes
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for platform in platforms:
            if player_rect.colliderect(platform) and player_velocity_y > 0:
                player_y = platform.y - player_size
                player_velocity_y = 0
                is_jumping = False

        # Vérification de la victoire
        if player_rect.colliderect(end_point):
            print("Vous avez gagné !")
            running = False

        # Dessiner tout
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLACK, player_rect)
        pygame.draw.rect(screen, BLACK, (player2.x, player2.y, player_size, player_size))  # Dessiner le deuxième joueur
        for platform in platforms:
            pygame.draw.rect(screen, GREEN, platform)
        pygame.draw.rect(screen, RED, start_point)
        pygame.draw.rect(screen, BLUE, end_point)

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit()
