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

class Time:
    def __init__(self, font, scale, x, y, difficulty):
        self.difficulty = difficulty
        self.flame_added = False
        self.wait = True
        self.time = pygame.time.get_ticks()
        self.clock = pygame.time.Clock()
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(font, scale)
        self.time_text = self.font.render("Temps écoulé : " + str(pygame.time.get_ticks() - self.time) + " secondes", True, (0, 0, 0))
    def update_time(self, window):
        self.flame_added = False
        self.time_text = self.font.render("Temps écoulé : " + str(self.time) + " secondes", True, (0, 0, 0))
        window.blit(self.time_text, (self.x + 50, self.y))
        self.time = int((pygame.time.get_ticks() - self.time) / 1000)
        if self.time % self.difficulty != 0:
            self.wait = False
        if self.time % self.difficulty == 0 and self.wait == False:
            self.flame = 1
            self.wait = True
            self.flame_added = True

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

def main():
    pygame.init()
    running = True
    _screen = pygame.display.set_mode((1600, 800))
    flame_x = -50
    _time = Time("Assets/Roboto/Roboto-Black.ttf", 20, 1350, 10, 3)
    _flames = pygame.sprite.Group()
    _boxes = pygame.sprite.Group()
    _doors = [Doors("Assets/porte.png", 1520, 400)]
    colonne_obstacles = [['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door'],
                         ['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door'],
                         ['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door'],
                         ['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door'],
                         ['box', 'door', 'box', 'door', 'box', 'door', 'box', 'door']]
    length_item = len(colonne_obstacles[0])
    nb_lines = len(colonne_obstacles)

    fill_obstacles(colonne_obstacles, length_item, _boxes, _doors, nb_lines)
    _flames.add(Flame("Assets/flammes.png", flame_x, 0))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        _screen.fill(sand_color)
        _boxes.draw(_screen)
        draw_doors(_screen, _doors)
        _flames.draw(_screen)
        _time.update_time(_screen)
        if _time.flame_added:
            flame_x += 80
            _flames.add(Flame("Assets/flammes.png", flame_x, 0))
        pygame.display.flip()
    exit(0)

if __name__ == "__main__":
    main()
