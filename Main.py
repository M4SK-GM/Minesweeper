import pygame, random, sys, os
from copy import deepcopy

fps = 5
clock = pygame.time.Clock()
pygame.init()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join("data", name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    intro_text = ["Сапёр", "",
                  "Правила игры:",
                  "1. Число в ячейке показывает, сколько мин скрыто вокруг данной ячейки.",
                  "Это число поможет понять вам, где находятся безопасные ячейки, а где находятся бомбы.", "",
                  "2. Если рядом с открытой ячейкой есть пустая ячейка, то она откроется автоматически.", "",
                  "3. Если вы открыли ячейку с миной, то игра проиграна..", "",
                  "4. Что бы пометить ячейку, в которой находится бомба, нажмите её правой кнопкой мыши.", "",
                  "5. Если в ячейке указано число, оно показывает, сколько мин скрыто",
                  "в восьми ячейках вокруг данной. Это число помогает понять, где находятся безопасные ячейки.", ""]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(fps)


def End_Screen():
    intro_text = ["Вы проиграли!", "",
                  "В следующий раз будьте аккуратнее и внимательнее!"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(fps)


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.mark_board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255), (x,
                                                                       self.cell_size + self.left, y,
                                                                       self.cell_size + self.top, self.cell_size,
                                                                       self.cell_size),
                                 1)

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # cell - кортеж (x, y)
    def on_click(self, cell):
        self.open_cell(cell)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_x < 0 or cell_x >= self.width or cell_y < 0 or cell_y >= self.height:
            return None
        return cell_x, cell_y

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)

    def open_cell(self, cell):
        x, y = cell
        if self.board[x][y] == 10:
            End_Screen()
        if self.mark_board[x][y] == 1:
            return
        summa = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                elif x + i >= self.width or x + i < 0 or y + j >= self.height or y + j < 0:
                    continue
                elif self.board[x + i][y + j] == 10:
                    summa += 1
        self.board[x][y] = summa

        if summa == 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if x + i >= self.width or x + i < 0 or y + j >= self.height or y + j < 0:
                        continue
                    if self.board[x + i][y + j] == -1:
                        self.open_cell((x + i, y + j))


class Minesweeper(Board):
    def __init__(self, width, height, n):
        super().__init__(width, height)
        # вначале все клетки закрыты
        self.board = [[-1] * width for _ in range(height)]
        self.width = width
        self.height = height
        self.num_bomb = n

    def generate_board(self, position):
        x, y = self.get_cell(position)
        i = 0
        while i != self.num_bomb:
            randx = random.randint(0, self.width - 1)
            randy = random.randint(0, self.height - 1)
            if self.board[randy][randx] == -1 and (randx != x and randy != y):
                i += 1
                self.board[randy][randx] = 10

    def render(self):
        bomb_image = load_image("Bomb.png", -1)
        flag_image = load_image("flag.png", -1)
        for i in range(self.width):
            for j in range(self.height):
                if self.mark_board[i][j] == 1:
                    flag = pygame.sprite.Sprite(all_sprites)
                    flag.image = flag_image
                    flag.rect = flag.image.get_rect()
                    flag.rect.x = self.cell_size * i + self.left
                    flag.rect.y = self.cell_size * j + self.top
                elif self.board[i][j] == 10:
                    bomb = pygame.sprite.Sprite(all_sprites)
                    bomb.image = bomb_image
                    bomb.rect = bomb.image.get_rect()
                    bomb.rect.x = self.cell_size * i + self.left
                    bomb.rect.y = self.cell_size * j + self.top
                elif self.mark_board[i][j] == 0:
                    pygame.draw.rect(screen, (0, 0, 0),
                                     (self.cell_size * i + self.left, self.cell_size * j + self.top, self.cell_size - 2,
                                      self.cell_size - 2))
                if -1 < self.board[i][j] < 10:
                    font = pygame.font.Font(None, 50)
                    text = font.render(str(self.board[i][j]), 1, (100, 255, 100))
                    screen.blit(text, (self.cell_size * i + self.left, self.cell_size * j + self.top))
                pygame.draw.rect(screen, (255, 255, 255),
                                 (self.cell_size * i + self.left, self.cell_size * j + self.top, self.cell_size,
                                  self.cell_size), 1)

    def mark_cell(self, position):
        global count_flag
        x, y = self.get_cell(position)
        if self.mark_board[x][y] == 0 and not (0 < self.board[x][y] < 10):
            self.mark_board[x][y] = 1
            count_flag += 1
        else:
            self.mark_board[x][y] = 0
            for flag in all_sprites:
                x1, y1 = self.get_cell((flag.rect.x, flag.rect.y))
                if x == x1 and y == y1:
                    pygame.sprite.Sprite.kill(flag)
            count_flag -= 1


all_sprites = pygame.sprite.Group()
mineboard = Minesweeper(10, 10, 20)
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
running = True
boardready = False
count_flag = 0
start_screen()
screen.fill(pygame.Color('black'))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not boardready:
                    mineboard.generate_board(event.pos)
                    boardready = True
                mineboard.get_click(event.pos)
            elif event.button == 3:
                if not boardready:
                    continue
                mineboard.mark_cell(event.pos)
    all_sprites.draw(screen)
    mineboard.render()
    pygame.display.flip()

'''                if self.board[i][j] == 10:
                    bomb = pygame.sprite.Sprite(all_sprites)
                    bomb.image = bomb_image
                    bomb.rect = bomb.image.get_rect()
                    bomb.rect.x = self.cell_size * i + self.left
                    bomb.rect.y = self.cell_size * j + self.top'''
