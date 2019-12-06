import pygame
import neat
import time
import os
import random

pygame.font.init()

Window_Width = 1200  # Ширина окна
Window_Height = 700  # Высота окна

Bird_imgs = [pygame.image.load(os.path.join('Images', 'Zaz1.png')),
             pygame.image.load(os.path.join('Images', 'Zaz2.png')),
             pygame.image.load(os.path.join('Images', 'Zaz3.png'))]

Pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join('D:/Flappy_Renat/Images', 'pipe.png')))
Base_img = pygame.transform.scale2x(pygame.image.load(os.path.join('D:/Flappy_Renat/Images', 'base.png')))
BackGround_img = pygame.transform.scale2x(pygame.image.load(os.path.join('D:/Flappy_Renat/Images', 'bg.png')))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    """"
    Класс летающего объекта в Flappy Bird
    """
    IMAGES = Bird_imgs
    Max_Rotation = 25   # Максимальный угол поворота
    Rotation_Changing = 15  # Изменение угола поворота
    Animation_Time = 3  # Время смены изображений (анимация)

    def __init__(self, x_coordinate, y_coordinate):
        """"
        Инициализация объектов
        входной параметр x_coordinate - начальная x-координата птицы (int)
        входной параметр у_coordinate - начальная y-координата птицы (int)
        :return: None
        """
        self.x_coordinate = x_coordinate  # Текущая x-координата объекта
        self.y_coordinate = y_coordinate  # Текущая y-координата объекта
        self.tilt = 0  # Текущий угол поворота объекта
        self.tick_count = 0  # Текущее значение счетчика для рассчета движения объекта
        self.velocity = 0  # Текущая скорость объекта
        self.height = y_coordinate
        self.img_count = 0  # Текущее значение сетчика для изображения
        self.image = self.IMAGES[0]  # Текущееизображение

    def jump(self):
        """"
        Функция, с помощью которой реализуется прыжок птички
        при прыжке изменяется скорость объекта иобнуляется счетчик
         :return: None
        """
        self.velocity = -5  # Задаем скорость при прыжке
        self.tick_count = 0  # Обнуляем счетчик
        self.height = self.y_coordinate

    def move(self):
        """"
        Функция, которая отвечает за движение птички
        Перемещение рассчитывается стандартно S(t) = Vt + at^2
        :return: None
        """
        self.tick_count += 1
        displacement = self.velocity * self.tick_count + 0.5 * self.tick_count ** 2  # Переменная, отвечающая за
        # смещение птички
        if displacement >= 19:
            displacement = 19
        if displacement < 0:
            displacement -= 2

        self.y_coordinate = self.y_coordinate + displacement

        if displacement < 0 or self.y_coordinate < self.height + 50:
            """"
            Если вектор перемещения направлен вверх повернем обект вверх на максимальный угол поворота
            Иначе будем уменьшать угол поворота объекта до -90 градусов
            """
            if self.tilt < self.Max_Rotation:
                self.tilt += self.Rotation_Changing * 1.5
            if self.tilt > self.Max_Rotation:
                self.tilt = self.Max_Rotation
        else:
            if self.tilt > -90:
                self.tilt -= self.Rotation_Changing

    def draw(self, window):
        """"
        Функция отвечающая за прорисовку объекта
        входной параметр: window: (окно, в котором будет прорисована птичка)
        Выходной параметр: None
        """
        self.img_count += 1

        """"
        Блок 1. Анимация объекта
        """
        if self.img_count < self.Animation_Time:
            self.image = self. IMAGES[0]
        elif self.img_count < self.Animation_Time * 2:
            self.image = self. IMAGES[1]
        elif self.img_count < self.Animation_Time * 3:
            self.image = self. IMAGES[2]
        elif self.img_count < self.Animation_Time * 4:
            self.image = self. IMAGES[1]
        elif self.img_count < self.Animation_Time * 4 + 1:
            self.image = self. IMAGES[0]
            self.img_count = 0

        if self.tilt <= -80:  # Если угол меньше -80 градусв перестаем махать крыльями
            self.image = self.IMAGES[1]
            self.img_count = self.Animation_Time * 2

        """"
        Блок 2. Поворот объекта
        """
        rotated_image = pygame.transform.rotate(self.image, self.tilt)
        new_rect = rotated_image.get_rect(center=self.image.get_rect(topleft=(self.x_coordinate, self.y_coordinate)).center)
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        """"
        Функция, возвражающая маску птицы
        """
        return pygame.mask.from_surface(self.image)


class Pipe:
    """
    Класс столбов
    """

    xCoord_Changing = 5  # Смещение по координате икс

    def __init__(self, x_coordinate):
        """
        Инициализирующая функция
        Входные параметры:  x_coordinate - координата икс
        Выходные параметры:  None
        """
        self.x_coordinate = x_coordinate  # Текущая координата по оси икс
        self.height = 0  # Текущая высота
        self.gap = 320  # Смещение по координате икс

        self.top = 0
        self.bottom = 0
        self.Pipe_Top = pygame.transform.flip(Pipe_img, False, True)  # Создание верхнего столба путем переворота
        # исходного изображения по вертикали  "pygame.transform.flip(SurFace, xbool, ybool)"
        self.Pipe_Bottom = Pipe_img  # Нижний столб

        self.passed = False  # Индикатор прохождение птицей столба
        self.set_height()

    def set_height(self):
        """
        Функция установки высоты столбов
        Выходные параметры:   None
        """
        self.height = random.randrange(50, 450)  # задаемся рандомной высотой столба
        self.top = self.height - self.Pipe_Top.get_height()  # расположение верхнего и нижнего столбцов
        self.bottom = self.height + self.gap

    def move(self):
        """
        Функция, отвечающая за движение столбов
        Выходные параметры:   None
        """
        self.x_coordinate -= self.xCoord_Changing

    def draw(self, window):
        """
        Функция, отвечающая за прорисовку столбов
        Входные параметры:  window (окно, в котором будут прорисованы столбы)
        Выходные параметры:   None
        """
        window.blit(self.Pipe_Top, (self.x_coordinate, self.top))
        window.blit(self.Pipe_Bottom, (self.x_coordinate, self.bottom))

    def collide(self, bird, window):
        """
        Функция-индикатор соприкосновения птицы и столба
        Входные параметры:  bird
        Выходные параметры:   True/False
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.Pipe_Top)
        bottom_mask = pygame.mask.from_surface(self.Pipe_Bottom)

        top_offset = (self.x_coordinate - bird.x_coordinate, self.top - round(bird.y_coordinate))
        bottom_offset = (self.x_coordinate - bird.x_coordinate, self.bottom - round(bird.y_coordinate))

        top_point = bird_mask.overlap(top_mask, top_offset)  # Индикатор пересечения птицы с верхним столбцом
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)  # Индикатор пересечения птицы с нижним столбцом

        if top_point or bottom_point:
            # Если произошло пересечение с одним из столбов - сообщаем в main
            return True

        return False


class Base:
    """
    Класс для базовой полоски снизу
    """
    xCoord_Changing = 5  # Изменение координаты икс
    width = Base_img.get_width()  # ширина базовой полоски
    img = Base_img  # изображение базовой полоски

    def __init__(self, y_position):
        self.y_position = y_position  # у-координаты базовой полоски
        self.start_x_position = 0  # начальная х - координата базовой полоски
        self.last_x_position = self.width  # крайняя ч-координата базовой полоски

    def move(self):
        """
        Функция, отвечающая за движение базовой полоски
        Входные параметры:  None
        Выходные параметры:   None
        """
        self.start_x_position -= self.xCoord_Changing
        self.last_x_position -= self.xCoord_Changing

        if self.start_x_position + self.width < 0:
            # базовая полоска повторяется вновь и вновь. Сразу после полного первого прохождения, начинается второе
            self.start_x_position = self.last_x_position + self.width
        if self.last_x_position + self.width < 0:
            self.last_x_position = self.start_x_position + self.width

    def draw(self, window):
        """
        Функция, отвечающая за прорисовку базовой полоски
        Входные параметры:  window (окно, в котором будет прорисована базовая плоска)
        Выходные параметры:   None
        """
        window.blit(self.img, (self.start_x_position, self.y_position))
        window.blit(self.img, (self.last_x_position, self.y_position))


def draw_window(window, bird, pipes, base, score):
    """
    Функция, отвечающая за прорисовку объектов на экране
    Входные параметры:  window (окно, в котором будут прорисованы объекты)
                        bird (объект - птичка);
                        pipes (объект - столбцы)
                        base (объект - базовая полоска)
                        score (объект - счет)
    Выходные параметры:   None
    """
    window.blit(BackGround_img, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    base.draw(window)
    bird.draw(window)

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))  # создаем счетчик (счет игры)
    window.blit(score_label, (Window_Width - score_label.get_width() - 15, 10))

    pygame.display.update()


def main():
    bird = Bird(200, 90)  # Координаты появления птички
    base = Base(650)  # высота появления базовой полоски
    pipes = [Pipe(1200)]  # Координата икс появления столбца
    score = 0

    window = pygame.display.set_mode((Window_Width, Window_Height))  # Формирование окна
    clock = pygame.time.Clock()  # Заводим счетчик

    start = False  # Триггер, отвечающий за начало игры. Когда нажимается K_SPACE, начинается движение
    loose = False  # Триггер, срабатывающий при касании птичкой базы или столбца
    run = True  # Триггер, отвечающий за работу игры

    while run:
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

            if event.type == pygame.KEYDOWN and not loose:
                # Привязка клавиши K_SPACE к изменению значения триггера start или действию jump
                if event.key == pygame.K_SPACE:
                    if not start:
                        start = True
                    bird.jump()

            if event.type == pygame.KEYDOWN:
                # Привязка клавиши K_ESCAPE к изменению значения триггера run
                if event.key == pygame.K_ESCAPE:
                    run = False
                    pygame.quit()
                    quit()
                    break

        if start:
            bird.move()
        if not loose:
            base.move()

            if start:
                bird.move()

                list_for_pipes_removing = []  # Список столбов, которые вышли за рамки изображения, их следует удалить
                add_pipe = False  # Триггер, отвечающий за создание новых столбцов
                for pipe in pipes:
                    pipe.move()
                    if pipe.collide(bird, window):
                        loose = True

                    if pipe.x_coordinate + pipe.Pipe_Top.get_width() < 0:
                        list_for_pipes_removing.append(pipe)
                    if not pipe.passed and pipe.x_coordinate < bird.x_coordinate:
                        pipe.passed = True
                        add_pipe = True

                if add_pipe:
                    score += 1
                    pipes.append(Pipe(1200))

            if bird.y_coordinate + bird.image.get_height() >= 650:
                 break

        draw_window(window, bird, pipes, base, score)
    pygame.quit()
    quit()


main()
