import pygame, random, sys, os, time, sqlite3
from PyQt5.QtWidgets import QInputDialog, QWidget, QApplication

con = sqlite3.connect(os.path.join("data", "ListofScore.db"))
cur = con.cursor()
fps = 5
clock = pygame.time.Clock()
pygame.init()
name = ""


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
        string_rendered = font.render(line, 1, pygame.Color('Black'))
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
    pygame.mixer.music.stop()
    lose = pygame.mixer.Sound("data/lose.wav")
    if not mute_status:
        lose.play()
    intro_text = ["Вы проиграли!", "",
                  "В следующий раз будьте аккуратнее и внимательнее!", "",
                  "Советы по игре:", "",
                  "Всегда смотрите, сколько мин осталось отметить ещё",
                  "Нажимайте, только если уверены, что в клетке нет мины",
                  "Пытайтесь рассуждать, думать логически",
                  "Если не уверены, то вы всегда можете отметить клетку знаком '?' и вернуться к ней позже",
                  "Больше тренируйтесь, и всё получится",
                  "Удачи!"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('Black'))
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


def Win_Screen():
    clock_image = load_image("clock.png", -1)
    clocking = pygame.sprite.Sprite(ui_sprites)
    clocking.image = clock_image
    clocking.rect = clocking.image.get_rect()
    clocking.rect.x = 180
    clocking.rect.y = 50
    tit2 = time.time()
    score = round(board_size ** 3 / count_bomb / round(tit2 - tit1))
    whoisiam = cur.execute('''SELECT * FROM ListofScore WHERE Name=?''', (name,)).fetchone()
    if whoisiam is None:
        cur.execute('''INSERT INTO ListofScore(Name, Score) VALUES(?, ?)''', (name, score))
    else:
        if whoisiam[1] < score:
            cur.execute('''UPDATE ListofScore
                            SET Score=?
                            WHERE Name=?''', (score, name))
    con.commit()
    result = cur.execute("""SELECT * FROM ListofScore
                ORDER BY Score DESC""").fetchmany(10)
    intro_text = ["Победа!!", "",
                  "Вы справились!",
                  "Ваш результат:",
                  f"{round(tit2 - tit1)} секунд(ы)!",
                  f"Количество очков: {score}", "",
                  "Лучшие результаты:", ""]
    for i in result:
        intro_text.append(f"{i[0]}..........{i[1]}")
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('Black'))
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


class Board():
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
        global count_flag
        x, y = cell
        if self.mark_board[x][y] == 1 or self.mark_board[x][y] == -1:
            return
        if self.board[x][y] == 10:
            End_Screen()
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
                        if self.mark_board[x + i][y + j] == 1:
                            self.mark_board[x + i][y + j] = 0
                            for flag in all_sprites:
                                x1, y1 = self.get_cell((flag.rect.x, flag.rect.y))
                                if x + i == x1 and y + j == y1:
                                    pygame.sprite.Sprite.kill(flag)
                            count_flag -= 1
                        elif self.mark_board[x + i][y + j] == -1:
                            self.mark_board[x + i][y + j] = 0
                            for unready in all_sprites:
                                x1, y1 = self.get_cell((unready.rect.x, unready.rect.y))
                                if x + i == x1 and y + j == y1:
                                    pygame.sprite.Sprite.kill(unready)
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
        if self.get_cell(position) is None:
            return False
        x, y = self.get_cell(position)
        i = 0
        while i != self.num_bomb:
            randx = random.randint(0, self.width - 1)
            randy = random.randint(0, self.height - 1)
            if self.board[randy][randx] == -1 and (randx != x and randy != y):
                i += 1
                self.board[randy][randx] = 10
        return True

    def render(self):
        # Перечисление ресурсов
        flag_image = load_image("flag.png", -1)
        unready_image = load_image("unready.png", -1)
        clock_image = load_image("clock.png", -1)
        # Текст с оставшимися флажками
        font = pygame.font.Font(None, 50)
        text = font.render(str(self.num_bomb - count_flag), 1, (255, 255, 255))
        text_x = self.cell_size * self.width + self.top + 50
        text_y = 10
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        flag = pygame.sprite.Sprite(ui_sprites)
        flag.image = flag_image
        flag.rect = flag.image.get_rect()
        flag.rect.x = self.cell_size * self.width + self.top + 20
        flag.rect.y = 10
        # Отсчёт времени
        tit2 = time.time()
        font = pygame.font.Font(None, 50)
        text = font.render(str(round(tit2 - tit1)), 1, (255, 255, 255))
        text_x = self.cell_size * self.width + self.top + 50
        text_y = 50
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        clock = pygame.sprite.Sprite(ui_sprites)
        clock.image = clock_image
        clock.rect = clock.image.get_rect()
        clock.rect.x = self.cell_size * self.width + self.top + 20
        clock.rect.y = 50
        # Текущие очки
        font = pygame.font.Font(None, 30)
        if tit2 - tit1 > 1:
            text = font.render((f"Тек. количество очков: "
                                f"{round(board_size ** 4 / count_bomb / round(tit2 - tit1))}"), 1, (255, 255, 255))
        else:
            text = font.render((f"Тек. количество очков: "
                                f"0"), 1, (255, 255, 255))
        text_x = self.cell_size * self.width + self.top + 20
        text_y = 90
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (text_x, text_y))
        # Данные
        intro_text = ["Данные игрока:",
                      f"Имя: {name}",
                      f"Размер поля: {board_size}x{board_size}",
                      f"Количество мин на поле: {count_bomb}"]
        res = whoisiam = cur.execute('''SELECT Score FROM ListofScore WHERE Name=?''', (name,)).fetchone()
        if res is not None:
            intro_text.append(f"Прошлый рекорд: {res[0]} очков")
        else:
            intro_text.append("Прошлый рекорд: нет")
        font = pygame.font.Font(None, 30)
        text_coord_x = self.cell_size * self.width + self.top + 20
        text_coord_y = 130
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('White'))
            text_coord_y += 30
            screen.blit(string_rendered, (text_coord_x, text_coord_y))
        # Управление
        intro_text = ["Управление игры:",
                      "ЛКМ - открыть ячейку",
                      "ПКМ - сменить состояние ячейки",
                      "SPACE/Пробел - сменить песню",
                      "M - отключить звуки"]
        font = pygame.font.Font(None, 30)
        text_coord_x = self.cell_size * self.width + self.top + 20
        text_coord_y = 320
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('White'))
            text_coord_y += 30
            screen.blit(string_rendered, (text_coord_x, text_coord_y))
        # Правила
        intro_text = ["Правила игры:",
                      "1. Число в ячейке показывает, сколько мин скрыто вокруг данной ячейки.",
                      "Это число поможет понять вам, где находятся безопасные ячейки, а где находятся бомбы.",
                      "2. Если рядом с открытой ячейкой есть пустая ячейка, то она откроется автоматически.",
                      "3. Если вы открыли ячейку с миной, то игра проиграна..",
                      "4. Что бы пометить ячейку, в которой находится бомба, нажмите её правой кнопкой мыши.",
                      "5. Если в ячейке указано число, оно показывает, сколько мин скрыто в восьми ячейках вокруг данной.",
                      "Это число помогает понять, где находятся безопасные ячейки.",
                      "6.Игра продолжается до тех пор, пока вы не отметите все заминированные ячейки"]
        font = pygame.font.Font(None, 30)
        text_coord = self.cell_size * board_size + 30
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('White'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        for i in range(self.width):
            for j in range(self.height):
                if self.mark_board[i][j] == 1:
                    flag = pygame.sprite.Sprite(all_sprites)
                    flag.image = flag_image
                    flag.rect = flag.image.get_rect()
                    flag.rect.x = self.cell_size * i + self.left
                    flag.rect.y = self.cell_size * j + self.top
                elif self.mark_board[i][j] == -1:
                    unready = pygame.sprite.Sprite(all_sprites)
                    unready.image = unready_image
                    unready.rect = unready.image.get_rect()
                    unready.rect.x = self.cell_size * i + self.left
                    unready.rect.y = self.cell_size * j + self.top
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
        click = pygame.mixer.Sound("data/click.wav")
        if self.get_cell(position) is None:
            return
        x, y = self.get_cell(position)
        if self.mark_board[x][y] == 0 and not (0 < self.board[x][y] < 10):
            self.mark_board[x][y] = 1
            count_flag += 1
        elif self.mark_board[x][y] == 1:
            self.mark_board[x][y] = -1
            for flag in all_sprites:
                if self.get_cell((flag.rect.x, flag.rect.y)) is None:
                    continue
                x1, y1 = self.get_cell((flag.rect.x, flag.rect.y))
                if x == x1 and y == y1:
                    pygame.sprite.Sprite.kill(flag)
            count_flag -= 1
        else:
            self.mark_board[x][y] = 0
            for unready in all_sprites:
                if self.get_cell((unready.rect.x, unready.rect.y)) is None:
                    continue
                x1, y1 = self.get_cell((unready.rect.x, unready.rect.y))
                if x == x1 and y == y1:
                    pygame.sprite.Sprite.kill(unready)
        if not mute_status:
            click.play()

    def check_win(self):
        if count_flag != self.num_bomb:
            return
        for i in range(self.width):
            for j in range(self.height):
                if self.board[i][j] == 10:
                    if self.mark_board[i][j] != 1:
                        return
        Win_Screen()


count_bomb = 0
board_size = 0


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 150, 150)
        self.setWindowTitle('Диалоговые окна')
        self.run()
        self.show()

    def run(self):
        global name, board_size, count_bomb
        i, okBtnPressed = QInputDialog.getText(self, "Введите имя",
                                               "Как тебя зовут?")
        if okBtnPressed:
            name = i
            i, okBtnPressed = QInputDialog.getText(self, "Размеры поля",
                                                   "Какие размеры поля будут использоваться?(не больше 20)")
            if okBtnPressed:
                if i == "":
                    board_size = 10
                elif int(i) > 20:
                    board_size = 20
                else:
                    board_size = int(i)
                while count_bomb == 0:
                    i, okBtnPressed = QInputDialog.getText(self, "Количество бомб",
                                                           "Сколько бомб будет на поле?")
                    if i == "":
                        continue
                    if okBtnPressed and board_size * board_size > int(i):
                        count_bomb = int(i)


all_sprites = pygame.sprite.Group()
ui_sprites = pygame.sprite.Group()
app = QApplication(sys.argv)
ex = Example()
ex.close()
if board_size == 0:
    board_size = 10
    board_count_bomb = 10
mineboard = Minesweeper(board_size, board_size, count_bomb)
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
running = True
boardready = False
count_flag = 0
start_screen()
screen.fill(pygame.Color('black'))
tit1 = time.time()
music_list = ["data/Hanging_Out.mp3", "data/Night_Snow.mp3", "data/Slow_Times_Over_Here.mp3"]
music = 0
pygame.mixer.music.load('data/Hanging_Out.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(loops=-1)
mute_status = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not boardready:
                    boardready = mineboard.generate_board(event.pos)
                mineboard.get_click(event.pos)
            elif event.button == 3:
                if not boardready:
                    continue
                mineboard.mark_cell(event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key == 32 and not mute_status:
                music = (music + 1) % 3
                pygame.mixer.music.load(music_list[music])
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(loops=-1)
            elif event.key == 109:
                if mute_status:
                    mute_status = False
                    music = (music + 1) % 3
                    pygame.mixer.music.load(music_list[music])
                    pygame.mixer.music.set_volume(0.1)
                    pygame.mixer.music.play(loops=-1)
                else:
                    mute_status = True
                    pygame.mixer.music.stop()

    screen.fill(pygame.Color('black'))
    all_sprites.draw(screen)
    ui_sprites.draw(screen)
    mineboard.check_win()
    mineboard.render()
    pygame.display.flip()
con.close()
