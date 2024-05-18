import socket
import threading
import pygame
import sys
from time import sleep
from map import MiniGame1
from test import MiniGame2

server_ip = "91.173.101.151"
server_port = 6666
users = []

client = None
start_game = 0

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

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLUE
        self.text = text
        self.txt_surface = button_font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = RED if self.active else BLUE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = BLUE
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = button_font.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

input_box = InputBox(220, 150, 200, 36)

def launch_game():
    mini_game = MiniGame2(client)

def connect_to_server(exit_event, launch_event, username, start_game):
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    print("Connecté au serveur")
    client.send(bytes(username, "utf-8"))

    running_threads = True

    def send_message():
        while running_threads:
            try:
                # Simulate sending data to the server
                pygame.time.wait(10)
            except Exception as e:
                print(f"Send message error: {e}")
                break

    def receive_response(start_game):
        while running_threads:
            try:
                response = client.recv(1024)
                if not response:
                    break
                print("Réponse du serveur:", response.decode("utf-8"))
                if response.decode("utf-8") == "start":
                    print("START DETECTED")
                    client.send(bytes("ingame", "utf-8"))
                    sleep(2)
                    exit_event.set()
                    launch_event.set()
                    break
                users.append(response.decode("utf-8"))
                if response.decode("utf-8") == "new_wave":
                    users.clear()
            except Exception as e:
                print(f"Receive response error: {e}")
                break

    send_thread = threading.Thread(target=send_message)
    receive_thread = threading.Thread(target=receive_response, args=(start_game,))

    send_thread.start()
    receive_thread.start()

    while not exit_event.is_set():
        sleep(0.1)

    print("Quitting threads")

    running_threads = False
    # client.close()

    send_thread.join()
    receive_thread.join()

    print("Threads stopped and socket closed")

def display_lobby(username, launch_event):
    exit_event = threading.Event()
    connect_thread = threading.Thread(target=connect_to_server, args=(exit_event, launch_event, username, start_game))
    connect_thread.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                exit_event.set()
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_quit.collidepoint(event.pos):
                    running = False
                    exit_event.set()

        screen.fill(BLACK)
        pygame.draw.rect(screen, button_color, button_rect_quit)
        screen.blit(button_text_quit, (button_rect_quit.x + 20, button_rect_quit.y + 10))

        pygame.draw.rect(screen, BLUE, users_rect, 2)
        y_offset = 0
        for user in users:
            user_text = users_text_font.render(user, True, WHITE)
            screen.blit(user_text, (users_rect.x + 10, users_rect.y + 10 + y_offset))
            y_offset += 30

        pygame.display.flip()

        if launch_event.is_set():
            running = False

    connect_thread.join()
    print("Fin de la connexion")

def game():
    launch_event = threading.Event()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if client is not None:
                    client.close()
                pygame.quit()
                print("Quitting")
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_join.collidepoint(event.pos):
                    display_lobby(input_box.text, launch_event)
                    if launch_event.is_set():
                        running = False

            input_box.handle_event(event)

        input_box.update()

        screen.fill(WHITE)
        input_box.draw(screen)
        pygame.draw.rect(screen, button_color, button_rect_join)
        screen.blit(button_text_join, (button_rect_join.x + 20, button_rect_join.y + 10))
        pygame.display.flip()

    launch_game()
    print("Fin du programme")

game()
