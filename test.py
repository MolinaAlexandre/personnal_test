import pygame
import sys
import threading
import socket

player_health = 10
playing = True
stop_event = threading.Event()

class Player2:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.size = 50
        self.color = color

def parse_data_and_get_position(data, player2):
    full_data = data.decode('utf-8')
    print("VALEUR RECUE : ", full_data)
    
    try:
        last_seven_chars = full_data[-7:]
        x, y = last_seven_chars.split(",")
        player2.x = int(x)
        player2.y = int(y)
    except Exception as e:
        print(f"Error parsing data: {e}")

def receive_data_from_server(client, player2, screen, player_size):
    while not stop_event.is_set():
        data = client.recv(1024)
        if not data:
            break
        parse_data_and_get_position(data, player2)
        p2_rect = pygame.draw.rect(screen, player2.color, (player2.x, player2.y, player_size, player_size))
        pygame.display.update(p2_rect)
    print("End of receive_data_from_server")

def send_player_position_to_server(client, player_rect):
    data = f"{player_rect.x},{player_rect.y}".encode()
    client.sendall(data)

def load_map(map_index):
    maps = [
        {
            'platforms': [
                pygame.Rect(0, 550, 200, 20),
                pygame.Rect(200, 450, 200, 20),
                pygame.Rect(400, 350, 100, 20),
                pygame.Rect(550, 250, 150, 20),
                pygame.Rect(700, 150, 100, 20)
            ],
            'start_point': pygame.Rect(50, 600 - 50, 50, 50),
            'end_point': pygame.Rect(750, 100, 50, 50)
        },
        {
            'platforms': [
                pygame.Rect(0, 500, 150, 20),
                pygame.Rect(200, 400, 200, 20),
                pygame.Rect(450, 300, 150, 20),
                pygame.Rect(650, 200, 100, 20),
                pygame.Rect(750, 100, 50, 20)
            ],
            'start_point': pygame.Rect(50, 600 - 50, 50, 50),
            'end_point': pygame.Rect(750, 50, 50, 50)
        }
    ]
    return maps[map_index]

def reduce_health():
    global player_health
    while player_health > 0 and not stop_event.is_set():
        player_health -= 1
        print(f"Health: {player_health}")
        pygame.time.delay(1000)
    print("End of reduce_health")

def MiniGame2(client):
    global playing
    global player_health
    pygame.init()

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

    player_size = 50
    player_speed = 5
    player_jump = -15
    gravity = 1
    player_velocity_y = 0
    is_jumping = False

    player2 = Player2(100, 100, RED)

    current_map = 0
    map_data = load_map(current_map)

    platforms = map_data['platforms']
    start_point = map_data['start_point']
    end_point = map_data['end_point']

    player_x = start_point.x
    player_y = start_point.y

    receive_thread = threading.Thread(target=receive_data_from_server, args=(client, player2, screen, player_size))
    receive_thread.start()

    health_thread = threading.Thread(target=reduce_health)
    health_thread.start()

    running = True
    clock = pygame.time.Clock()

    while running:
        if player_health <= 0:
            print("Vous avez perdu !")
            running = False
            playing = False
            stop_event.set()  # Set the event to stop the threads

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                playing = False
                stop_event.set()  # Set the event to stop the threads
        
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
        
        player_velocity_y += gravity
        player_y += player_velocity_y

        if player_y >= SCREEN_HEIGHT - player_size:
            player_y = SCREEN_HEIGHT - player_size
            player_velocity_y = 0
            is_jumping = False

        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for platform in platforms:
            if player_rect.colliderect(platform) and player_velocity_y > 0:
                player_y = platform.y - player_size
                player_velocity_y = 0
                is_jumping = False

        if player_rect.colliderect(end_point) and pygame.Rect(player2.x, player2.y, player_size, player_size).colliderect(end_point):
            print("Les deux joueurs ont atteint la sortie !")
            current_map += 1
            if current_map < 2:
                map_data = load_map(current_map)
                platforms = map_data['platforms']
                start_point = map_data['start_point']
                end_point = map_data['end_point']
                player_x = start_point.x
                player_y = start_point.y
                player2.x = start_point.x
                player2.y = start_point.y
                player_health = 10
            else:
                print("Toutes les cartes ont été complétées !")
                running = False
                playing = False
                stop_event.set()  # Set the event to stop the threads

        screen.fill(WHITE)
        pygame.draw.rect(screen, BLACK, player_rect)
        pygame.draw.rect(screen, player2.color, (player2.x, player2.y, player_size, player_size))
        for platform in platforms:
            pygame.draw.rect(screen, GREEN, platform)
        pygame.draw.rect(screen, RED, start_point)
        pygame.draw.rect(screen, BLUE, end_point)

        # Display health
        font = pygame.font.SysFont(None, 55)
        health_text = font.render(f'Health: {player_health}', True, RED)
        screen.blit(health_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    # Ensure all threads are stopped before quitting
    receive_thread.join()
    health_thread.join()

    pygame.quit()
    sys.exit()

