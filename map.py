import pygame

sand_color = (224, 205, 169)

class Text:
    def __init__(self, text, x, y, scale, font):
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(font, scale)
        self.text = self.font.render(text, True, (0, 0, 0))

    def draw_text(self, window):
        window.blit(self.text, (self.x, self.y))

    def is_clicked(self, mouse_pos):
        return self.text.get_rect(topleft=(self.x, self.y)).collidepoint(mouse_pos)

class Time:
    def __init__(self, font, scale, x, y, difficulty):
        self.difficulty = difficulty
        self.flame_added = False
        self.wait = True
        self._start_time = pygame.time.get_ticks()
        self.time = 0
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(font, scale)
        self.time_text = self.font.render("Temps écoulé : " + str(pygame.time.get_ticks() - self.time) + " secondes", True, (0, 0, 0))
    def update_time(self, window):
        self.flame_added = False
        self.time_text = self.font.render("Temps écoulé : " + str(self.time) + " secondes", True, (0, 0, 0))
        window.blit(self.time_text, (self.x + 50, self.y))
        self.time = int((pygame.time.get_ticks() - self._start_time) / 1000)
        if self.time % self.difficulty != 0:
            self.wait = False
        if self.time % self.difficulty == 0 and self.wait == False:
            self.flame = 1
            self.wait = True
            self.flame_added = True

    def reset(self):
        self._start_time = pygame.time.get_ticks()
        self.flame_added = False
        self.wait = True

class Flame(pygame.sprite.Sprite):
    def __init__(self, flame_img, x, y):
        super().__init__()
        self.image = pygame.image.load(flame_img).convert_alpha()
        self.image = pygame.transform.rotate(self.image, -90)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Boxes(pygame.sprite.Sprite):
    def __init__(self, font_box, x, y):
        super().__init__()
        self.image = pygame.image.load(font_box).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Doors():
    def __init__(self, door_img, x, y):
        self.spritesheet = pygame.image.load(door_img).convert_alpha()
        self.images = self.load_images(self.spritesheet)
        self.current_state = 'closed'
        self.image = self.images[self.current_state]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.animation_frames = ["closed", "opening", "opened"]
        self.animation_index = 0
        self.animation_speed = 0.1
        self.last_update = pygame.time.get_ticks()

class Character():
    def __init__(self) -> None:
        pass


    def load_images(self, sheet):
        images = {
            'closed': self.get_image(sheet, 0, 0, 448 / 3 - 5, 176),
            'opening': self.get_image(sheet, 448 / 3 - 25, 0, 448 / 3 - 10, 176),
            'opened': self.get_image(sheet, 2 * (448 / 3) - 40, 0, 448 / 3 + 20, 176)
        }
        return images

    def get_image(self, sheet, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), (x, y, width, height))
        return pygame.transform.scale(image, (80, 80))

    def update(self, new_state):
        if new_state in self.images:
            self.current_state = new_state
            self.image = self.images[self.current_state]

    def make_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.animation_index += 1
            if self.animation_index >= len(self.animation_frames):
                self.animation_index = len(self.animation_frames) - 1
            self.current_state = self.animation_frames[self.animation_index]
            self.image = self.images[self.current_state]


def draw_doors(screen, _doors):
    for i in _doors:
        screen.blit(i.image, i.rect.topleft)

def fill_obstacles(colonne_obstacles, length_item, _boxes, _doors, _nb_lines):
    box_y = 0
    box_x = 0
    for nb_lines in range(_nb_lines):
        box_x = nb_lines * 200
        box_y = 0
        for item in range(length_item):
            if colonne_obstacles[nb_lines][item] == 'box':
                _boxes.add(Boxes("Assets/box.png", 500 + box_x, box_y))
                box_y += 200
            else:
                _doors.append(Doors("Assets/porte.png", 500 + box_x, box_y - 100))

def reset_obstacles(_core):
    for doors in _core._doors:
        doors.current_state = "closed"


class Core:
    def __init__(self):
        self._screen = pygame.display.set_mode((1600, 800))
        self.colonne_obstacles = [['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door'],
                                  ['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door'],
                                  ['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door'],
                                  ['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door'],
                                  ['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door']]
        self._doors = [Doors("Assets/porte.png", 1520, 400)]
        self._flames = pygame.sprite.Group()
        self._boxes = pygame.sprite.Group()
        self.running = True
        self.flame_x = -50
        self._time = Time("Assets/Roboto/Roboto-Black.ttf", 20, 1350, 10, 3)
        self.length_item = len(self.colonne_obstacles[0])
        self.nb_lines = len(self.colonne_obstacles)
        fill_obstacles(self.colonne_obstacles, self.length_item, self._boxes, self._doors, self.nb_lines)
        self._flames.add(Flame("Assets/flammes.png", self.flame_x, 0))
        self._state = "menu"
        self.game_over_bg = pygame.transform.scale(pygame.image.load("Assets/bg_game_over.jpg"), (1600, 800))
        self._menu = Text("MENU", 200, 100, 150, "Assets/Roboto/Roboto-Black.ttf")
        self._restart = Text("RESTART", 600, 100, 150, "Assets/Roboto/Roboto-Black.ttf")
        self._quit = Text("QUIT", 1200, 100, 150, "Assets/Roboto/Roboto-Black.ttf")
        self.mouse_pos = (0, 0)
        self.game_two = Text("Game_MULTI", 900, 100, 150, "Assets/Roboto/Roboto-Black.ttf")
        self.game_one = Text("Game_SOLO", 100, 100, 150, "Assets/Roboto/Roboto-Black.ttf")
        self.previous_state = "menu"

    def reset(self):
        self._time.reset()
        self._flames.empty()
        self._flames.add(Flame("Assets/flammes.png", self.flame_x, 0))
        self.flame_x = -50

    def update_state(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = pygame.mouse.get_pos()
                self.previous_state = self._state
                if (self._menu.is_clicked(self.mouse_pos)):
                    self.reset()
                    self._state = "menu"
                elif (self._restart.is_clicked(self.mouse_pos)):
                    self.reset()
                    self._state = self.previous_state
                elif (self._quit.is_clicked(self.mouse_pos)):
                    self.running = False
                elif (self.game_one.is_clicked(self.mouse_pos)):
                    self.reset()
                    self._state = "game_SOLO"
                elif (self.game_two.is_clicked(self.mouse_pos)):
                    self._state = "game_MULTI"

def game(_core):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _core.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            _core.reset()
            _core.previous_state = _core._state
            _core._state = "menu"
    _core._screen.fill(sand_color)
    _core._boxes.draw(_core._screen)
    draw_doors(_core._screen, _core._doors)
    _core._flames.draw(_core._screen)
    _core._time.update_time(_core._screen)
    if _core._time.flame_added:
        _core.flame_x += 80
        _core._flames.add(Flame("Assets/flammes.png", _core.flame_x, 0))
    pygame.display.flip()


def game_over(_core):
    _core.update_state()
    _core._screen.blit(_core.game_over_bg, (0, 0))
    _core._menu.draw_text(_core._screen)
    _core._restart.draw_text(_core._screen)
    _core._quit.draw_text(_core._screen)
    pygame.display.flip()

def menu(_core):
    _core.update_state()
    _core._screen.blit(_core.game_over_bg, (0, 0))
    _core.game_one.draw_text(_core._screen)
    _core.game_two.draw_text(_core._screen)
    pygame.display.flip()

def main():
    pygame.init()

    _core = Core()
    while _core.running:
        if _core._state == "menu":
            menu(_core)
        elif _core._state == "game_SOLO":
            game(_core)
        elif _core._state == "game_MULTI":
            game(_core)
        else:
            game_over(_core)
    exit(0)

if __name__ == "__main__":
    main()
