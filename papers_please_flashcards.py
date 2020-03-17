import pygame as pg
import random
from random import shuffle

# Screen Size:
WIDTH = 480
HEIGHT = 320

# Mouse Buttons
LEFT = 1
RIGHT = 3

# Colors
WHITE = 255, 255, 255
BLACK = 0, 0, 0
BRGRAY = 196, 196, 196
DKGRAY = 50, 50, 50

RED = 239, 33, 33
GREEN = 9, 186, 24
BLUE = 18, 122, 177

GRLILA = 54, 46, 66
DKLILA = 33, 29, 41

# Frames Per Second
FPS = 60

# Font
FONT = 'font/TragicMarker.otf'

# Flashcard Deck
deck = {
    "ARSTOTZKA": ["Orwetsch", "Ost-Grestin", "Paradisna"],
    "ANTEGRIA": ["St. Marmero", "Glorian", "Gross-Grouse"],
    "IMPOR": ["Enkyo", "Haihan", "Tsunkeido"],
    "KOLECHIEN": ["Jurko-Stadt", "Wedor", "West-Grestin"],
    "OBRISTAN": ["Skal", "Lorndas", "Mergerous"],
    "REPUBLIEN": ["Glorian Major", "Lesrenadi", "Bostan"],
    "V. FOERDERATION": ["Great Rapid", "Shingleton", "Korstia-Stadt"],
}

pg.init()

screen = pg.display.set_mode([WIDTH, HEIGHT])
clock = pg.time.Clock()


class Desk:

    def __init__(self, load_image=True):
        self.__image = None
        if load_image:
            self.__image = pg.image.load('image/desktop_bg.png').convert()
        self.__rect = pg.Rect(0, 0, WIDTH, HEIGHT)
        self.__setup = False

    def blit_to_screen(self):
        if self.__image is not None:
            screen.blit(self.__image, self.__rect)
        else:
            screen.fill(DKLILA)
        if self.__setup:
            if self.__image is None:
                self.hole.blit_to_screen()
                self.pattern.blit_to_screen()
            else:
                self.dashed_line.blit_to_screen()
            self.field_green.blit_to_screen()
            self.field_red.blit_to_screen()

    def set_up(self, sep_x_pos=325, flds_pos=(335, 25), flds_h=100):
        x, y = flds_pos
        if y + flds_h >= HEIGHT//2:
            flds_pos = x, HEIGHT//2 - flds_h
        self.__setup = True
        self.hole = DropArea(sep_x_pos, BLACK)
        self.pattern = Pattern(2, 12, sep_x_pos, GRLILA)
        self.dashed_line = Seperator(sep_x_pos, WHITE, 3, 50)
        self.field_green = Field(flds_pos, flds_h, GREEN, 3)
        self.field_red = Field(*Desk.mirror(flds_pos, flds_h), RED, 3)

    @staticmethod
    def mirror(pos, size, axis='x'):
        if axis == 'y':
            return (WIDTH - size - pos[0], pos[1]), size
        return (pos[0], HEIGHT - size - pos[1]), size


class Seperator:

    def __init__(self, x, color=WHITE, w=1, spl=1):
        self.__x = x
        self.__org_x = x
        self.__color = color
        self.__org_color = color
        self.__width = w
        self.__splits = spl
        self.__gap = 5
        self.__length = round((HEIGHT - self.__gap*(spl-1))/spl + 0.49)

    def get_x(self):
        return self.__x

    def add_x(self, value):
        self.__x += value

    def set_x(self, x):
        if x == 'original':
            self.__x = self.__org_x
        else:
            self.__x = x

    def set_color(self, color):
        if color == 'original':
            self.__color = self.__org_color
        else:
            self.__color = color

    def blit_to_screen(self):
        for i in range(0, self.__splits):
            pg.draw.line(
                screen,
                self.__color,
                [self.__x, i*(self.__length+self.__gap)],
                [self.__x, i*(self.__length+self.__gap) + self.__length],
                self.__width)


class Pattern:

    def __init__(self, size, distance, spread_x, color):
        self.__size = size
        self.__distance = distance
        self.__spread_x = spread_x
        self.__color = color

    def blit_to_screen(self):
        pos_x = 0
        pos_y = self.__distance
        while True:
            pos_x += self.__distance
            if pos_x >= self.__spread_x - (self.__distance//2):
                pos_x = self.__distance
                pos_y += self.__distance
                if pos_y >= HEIGHT:
                    break
            rect = (pos_x, pos_y, self.__size, self.__size)
            pg.draw.rect(screen, self.__color, rect)


class DropArea:

    def __init__(self, x, color=BLACK):
        self.__color = color
        self.__rect = pg.Rect(x, 0, WIDTH - x, HEIGHT)

    def blit_to_screen(self):
        pg.draw.rect(screen, self.__color, self.__rect)


class Field:

    num_of_flds = 0

    def __init__(self, pos, h, color=WHITE, w=1):
        self.__color = color
        self.__org_color = color
        self.__width = w
        self.__rect = pg.Rect(pos[0], pos[1], WIDTH - pos[0] - w, h)
        Field.num_of_flds += 1
        self.__num = Field.num_of_flds

    def light_up(self, intensity):
        light_color_r = self.__org_color[0] + intensity
        light_color_g = self.__org_color[1] + intensity
        light_color_b = self.__org_color[2] + intensity
        if light_color_r > 255:
            light_color_r = 255
        if light_color_g > 255:
            light_color_g = 255
        if light_color_b > 255:
            light_color_b = 255
        self.__color = light_color_r, light_color_g, light_color_b

    def get_rect(self):
        return self.__rect

    def get_collision(self, mouse):
        return self.__rect.collidepoint(mouse)

    def set_color(self, color):
        if color == 'original':
            self.__color = self.__org_color
        else:
            self.__color = color

    def blit_to_screen(self):
        pg.draw.rect(screen, self.__color, self.__rect, self.__width)

    def __repr__(self):
        name = 'field_' + str(self.__num)
        return str('{}: <rect({}, {}, {}, {})>'.format(name, *self.__rect))


class Flashcard:

    __pos = 40, HEIGHT // 4  # start position of the deck
    __blit_amt = 0
    __active_card = None
    __org_image = pg.image.load('image/card.png').convert()
    __small_image = pg.image.load('image/card_small.png').convert()
    __small_image_deact = pg.image.load('image/card_small_deact.png').convert_alpha()
    __flip_images = []
    for i in range(1, 18):
        file = "image/flipping/card_flip_" + str(i) + ".png"
        image = pg.image.load(file).convert()
        __flip_images.append(image)

    deck = []
    rot_angles = {'green': [], 'red': []}
    fallen_card_locs = []
    repeat_list = []
    fwd_learning = False
    done = False
    redo = False

    def __init__(self, content):
        self.__image = self.__org_image
        self.__org_size = self.__image.get_rect().size
        self.__trigger_point = -350
        self.__virginity = True
        self.__inside = False
        self.__flip_counter = 0
        self.content = content
        self.grabbed = False
        self.is_flipping = False
        self.flipside = False
        self.shrinked = False
        if Flashcard.done:
            Flashcard.done = False

    def init(self):
        self.__size = self.__image.get_rect().size
        self.__size_d = self.__org_size[0] - self.__size[0]

        self.__rect = pg.Rect(self.__pos, self.__size)

        if self.__virginity:
            self.__rect = pg.Rect(self.__pos[0] - Flashcard.__blit_amt,
                                  self.__pos[1] - Flashcard.__blit_amt,
                                  self.__size[0],
                                  self.__size[1])

        if self.is_flipping:
            self.__rect = pg.Rect(self.__pos[0] + self.__size_d//2,
                                  self.__pos[1],
                                  self.__size[0],
                                  self.__size[1])

    def blit_to_screen(self, mouse, time=0, shadow=True):
        animation_time = 320  # in [ms]
        steps = len(Flashcard.__flip_images)

        animation_clock = time - self.__trigger_point
        increment = animation_time / steps

        if shadow:
            self.shadow()
        else:
            self.__shadow_offset = 0

        m_middle = (mouse[0] - self.__size[0]//2 - self.__shadow_offset,
                    mouse[1] - self.__size[1]//2 - self.__shadow_offset)

        if self.grabbed or (self.grabbed and self.__inside):
            self.__pos = (mouse[0] - self.__x_d - self.__shadow_offset,
                          mouse[1] - self.__y_d - self.__shadow_offset)

        if (self.grabbed and self.shrinked and not self.__inside
                or self.grabbed and not self.shrinked and self.__inside):
            self.__pos = m_middle

        if animation_clock <= animation_time:
            self.__pass_counter = 0
            for i in range(0, steps):
                if increment*i < animation_clock <= increment*(i+1):
                    self.__image = Flashcard.__flip_images[i]
                    break
        elif animation_clock > animation_time:
            self.is_flipping = False

        screen.blit(self.__image, self.__rect)
        Flashcard.__blit_amt += 1

        if Flashcard.__blit_amt >= len(Flashcard.deck) + 1:
            Flashcard.__blit_amt = 0

    def get_rect(self):
        return self.__rect

    def get_center(self):
        x = self.__pos[0] + self.__size[0]//2
        y = self.__pos[1] + self.__size[1]//2
        return x, y

    def get_collision(self, mouse):
        return self.__rect.collidepoint(mouse)

    def pick_up(self, mouse):
        self.grabbed = True
        self.__x_d = mouse[0] - self.__pos[0]
        self.__y_d = mouse[1] - self.__pos[1]
        if self.__virginity:
            self.__x_d += Flashcard.__blit_amt
            self.__y_d += Flashcard.__blit_amt
            self.__virginity = False

    def drop_down(self, mouse):
        self.grabbed = False
        m_middle = mouse[0] - self.__size[0]//2, mouse[1] - self.__size[1]//2
        self.__pos = mouse[0] - self.__x_d, mouse[1] - self.__y_d
        if self.shrinked and not self.__inside:
            self.__pos = m_middle
            self.__inside = True
        elif not self.shrinked and self.__inside:
            self.__pos = m_middle
            self.__inside = False

    def shrink(self):
        self.shrinked = True
        self.__image = self.__small_image

    def grow(self):
        self.shrinked = False
        self.__image = self.__org_image

    def shadow(self):
        self.__shadow_offset = 8  # it's virtually the shadow thickness
        s = pg.Surface((self.__size))
        s.set_alpha(160)
        s.fill(BLACK)

        if self.shrinked:
            self.__shadow_offset = 2

        if self.grabbed or self.is_flipping:
            screen.blit(s, (self.__rect[0] + self.__shadow_offset,
                            self.__rect[1] + self.__shadow_offset))

    def fall(self, determined_pos_x):
        self.__pos = determined_pos_x, self.__pos[1]

    def fall_into_field(self, field_rect):
        rot_angle = Flashcard.gen_rot_angle(field_rect)
        Flashcard.fallen_card_locs.append([field_rect, rot_angle])

    def flip(self, time):
        self.__trigger_point = time
        self.__flip_counter += 1
        self.flipside = True
        self.is_flipping = True
        if self.__flip_counter % 2 == 0:
            self.flipside = False

    def __move_off_screen(self):
        self.__pos = WIDTH + 1, HEIGHT + 1
        Flashcard.done = True

    def print(self, text, color=BLUE, size='normal', line=0):
        scale = 1
        tweak = 0
        if size == 'large':
            scale = 2
            tweak = 3

        margin = 25, 46 + tweak
        h = 17 * scale  # line-height in pxl
        w = 31 // scale  # maximum line-length in characters
        font = pg.font.Font(FONT, 18*scale)

        if self.shrinked:
            margin = 10, 17 + tweak
            h = 6 * scale
            font = pg.font.Font(FONT, 8*scale - tweak)

        if not self.is_flipping:
            textl = text.split('\n')
            textf = ''
            for part in textl:
                for c in range(len(part), w):
                    part = part + ' '
                textf = textf + part

            lines = round(len(textf)/w + 0.49)  # add 0.49 to provoke round up

            for l in range(0, lines):
                text_surf = font.render(textf[l*w: (l+1)*w], True, color)
                screen.blit(text_surf,
                            [(self.__rect[0] + margin[0],
                              self.__rect[1] + margin[1] + line*h),
                             text_surf.get_rect().size])
                line += 1

    def print_content(self):
        question = "Which locations belong to\n"
        if Flashcard.fwd_learning:
            if not self.flipside:
                self.print(question + self.content[0] + "?\n")
            else:
                self.print(self.content[0].upper() + ":\n\n"
                           + "- " + self.content[1][0] + "\n"
                           + "- " + self.content[1][1] + "\n"
                           + "- " + self.content[1][2], BLACK)
                # for i, element in enumerate(self.content[1]):
                #     self.print('- ' + element, line=i+2)
        else:
            if not self.flipside:
                self.print(self.content[0], size='large', line=1)
            else:
                self.print(self.content[1].upper(), RED, size='large', line=1)

    def __repr__(self):
        if Flashcard.fwd_learning:
            return str(self.content[0]) + ': ' + ', '.join(self.content[1])
        return str(self.content[0]) + ' --> ' + str(self.content[1].upper())

    @classmethod
    def pop(cls):  # get next_card
        if len(cls.deck) > 0:
            cls.__active_card = cls.deck.pop()
        elif len(Flashcard.deck) == 0:
            cls.__active_card.__move_off_screen()  # done
        return cls.__active_card

    @classmethod
    def gen_rot_angle(cls, field_rect):
        for key in cls.rot_angles:
            if len(cls.rot_angles[key]) > 9:
                cls.rot_angles[key] = cls.rot_angles[key][-3:]
        rot_angle = random.randrange(15, 180, 15)
        if field_rect.top < HEIGHT//2:
            while rot_angle == 90 or rot_angle in cls.rot_angles['green']:
                rot_angle = random.randrange(15, 180, 15)
            cls.rot_angles['green'].append(rot_angle)
            return cls.rot_angles['green'][-1]
        else:
            while rot_angle == 90 or rot_angle in cls.rot_angles['red']:
                rot_angle = random.randrange(15, 180, 15)
            cls.rot_angles['red'].append(rot_angle)
            return cls.rot_angles['red'][-1]

    @classmethod
    def blit_fallen_cards(cls):
        image = cls.__small_image_deact
        for rect, angle in cls.fallen_card_locs:
            rot_image = pg.transform.rotate(image, angle)
            screen.blit(rot_image, [rect[0]+10, rect[1]-10, rect[2], rect[3]])

    @staticmethod
    def get_list_from_dict(d, shuffling=False):
        lst = []
        for key, value in d.items():
            if Flashcard.fwd_learning:
                content = [key.lower().title(), value]
                lst.append(content)
            else:
                for element in value:
                    content = [element, key.lower().title()]
                    lst.append(content)
        if shuffling:
            shuffle(lst)
        return lst


def main():
    running = True
    time = 0

    desktop = Desk(load_image=False)
    desktop.set_up(sep_x_pos=325, flds_pos=(335, 15), flds_h=100)

    deck_content = Flashcard.get_list_from_dict(deck, shuffling=True)

    for content in deck_content:
        Flashcard.deck.append(Flashcard(content))
    card = Flashcard.pop()

    ''' MAIN LOOP '''

    while running:
        time = pg.time.get_ticks()
        mouse = pg.mouse.get_pos()
        pg.display.set_caption("Papers, Please - Flashcards - FPS: "
                               + str(round(clock.get_fps(), 1)))

        if Flashcard.done and Flashcard.redo:
            Flashcard.fallen_card_locs = [a  # Delete all cards in field_red
                                          for a in Flashcard.fallen_card_locs
                                          if a[0][1] < HEIGHT//2]
            Flashcard.rot_angles['red'] = []

            deck_content = list(Flashcard.repeat_list)

            for content in deck_content:
                Flashcard.deck.append(Flashcard(content))
            card = Flashcard.pop()

            Flashcard.repeat_list = []
            Flashcard.redo = False

        desktop.blit_to_screen()
        desktop.dashed_line.set_color('original')
        desktop.dashed_line.set_x('original')

        for i in range(0, len(Flashcard.deck)):
            Flashcard.deck[i].init()
            Flashcard.deck[i].blit_to_screen(mouse, shadow=False)

        if len(Flashcard.deck) != 0:
            deck_topcard = Flashcard.deck[-1]
            deck_topcard.print_content()

        card.init()

        ''' EVENT HANDLER '''

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False

            # Mouse Interactions:

            elif e.type == pg.MOUSEBUTTONDOWN and e.button == LEFT:
                if card.get_collision(mouse):
                    card.pick_up(mouse)
                    # print(card)
                if desktop.field_red.get_collision(mouse) and Flashcard.done:
                    Flashcard.redo = True
                    if len(Flashcard.repeat_list) == 0:
                        running = False  # quit main loop

            elif e.type == pg.MOUSEBUTTONUP and e.button == LEFT:
                if card.grabbed:
                    card.drop_down(mouse)

            elif e.type == pg.MOUSEBUTTONDOWN and e.button == RIGHT:
                if card.grabbed:
                    if card.get_rect().right < desktop.dashed_line.get_x():
                        if not card.is_flipping:
                            card.flip(time)
                    else:
                        desktop.dashed_line.set_color(RED)
                        desktop.dashed_line.add_x(5)

        ''' GAME LOGIC '''

        if (card.grabbed and mouse[0] > desktop.dashed_line.get_x()
                or card.get_rect().left > desktop.dashed_line.get_x()):
            card.shrink()

        elif card.get_rect().right < desktop.dashed_line.get_x():
            card.grow()

        if card.shrinked:
            if (card.get_rect().left < desktop.dashed_line.get_x()
                    and not card.grabbed):
                card.fall(desktop.dashed_line.get_x())

            if desktop.field_green.get_rect().collidepoint(card.get_center()):
                desktop.field_green.light_up(70)
                if not card.grabbed:
                    desktop.field_green.set_color('original')
                    card.fall_into_field(desktop.field_green.get_rect())
                    card = Flashcard.pop()
            else:
                desktop.field_green.set_color('original')

            if desktop.field_red.get_rect().collidepoint(card.get_center()):
                desktop.field_red.light_up(70)
                if not card.grabbed:
                    desktop.field_red.set_color('original')
                    card.fall_into_field(desktop.field_red.get_rect())
                    Flashcard.repeat_list.append(card.content)
                    card = Flashcard.pop()
            else:
                desktop.field_red.set_color('original')

        Flashcard.blit_fallen_cards()
        card.blit_to_screen(mouse, time)
        card.print_content()

        pg.display.update()
        clock.tick(FPS)

    pg.quit()


main()
