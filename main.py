# command to export is pyinstaller --onefile --windowed --onedir main.py and then drag img folder into framework
import sys
import os
import pygame as pg
import pygame.font
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import wikipedia
import pyperclip

# variables
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
pg.font.init()

if getattr(sys, 'frozen', False):
    icon = pg.image.load(os.path.join(sys._MEIPASS, 'img/icon.png'))
    donate_icon = pg.image.load(os.path.join(sys._MEIPASS, 'img/donate.png'))
    copy_icon = pg.image.load(os.path.join(sys._MEIPASS, 'img/copy.png'))
else:
    icon = pg.image.load('img/icon.png')
    donate_icon = pg.image.load('img/donate.png')
    copy_icon = pg.image.load('img/copy.png')
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pg.display.set_caption('WikiNeedia')
pg.display.set_icon(icon.convert_alpha())
text_font = pg.font.SysFont('Futura', 15)
header_font = pg.font.SysFont('Futura', 32)
search_query = ''
result = 'Search something to get started!'
wrapped_result = []
color_inactive = pg.Color('#363432')
color_active = pg.Color('#997048')
bg_color = pg.Color('#F5FAFF')
sentences = 2
scroll_amount = 0
max_scroll = 50


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.donated = False

    def update(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0 and self.clicked:
            self.clicked = False
            self.donated = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def wrap_text(text, font, width):
    """Wrap text to fit inside a given width when rendered.

    :param text: The text to be wrapped.
    :param font: The font the text will be rendered in.
    :param width: The width to wrap to.

    """
    text_lines = text.replace('\t', '    ').split('\n')
    if width is None or width == 0:
        return text_lines

    wrapped_lines = []
    for line in text_lines:
        line = line.rstrip() + ' '
        if line == ' ':
            wrapped_lines.append(line)
            continue

        # Get the leftmost space ignoring leading whitespace
        start = len(line) - len(line.lstrip())
        start = line.index(' ', start)
        while start + 1 < len(line):
            # Get the next potential splitting point
            next = line.index(' ', start + 1)
            if font.size(line[:next])[0] <= width:
                start = next
            else:
                wrapped_lines.append(line[:start])
                line = line[start+1:]
                start = line.index(' ')
        line = line[:-1]
        if line:
            wrapped_lines.append(line)
    return wrapped_lines


def render_text_list(lines, font, surface, scroll_value, colour=(255, 255, 255)):
    """Draw multiline text to a single surface with a transparent background.

    Draw multiple lines of text in the given font onto a single surface
    with no background colour, and return the result.

    :param lines: The lines of text to render.
    :param font: The font to render in.
    :param colour: The colour to render the font in, default is white.

    """
    rendered = [font.render(line, True, colour).convert_alpha()
                for line in lines]

    line_height = font.get_linesize()
    width = max(line.get_width() for line in rendered)
    tops = [int(round(i * line_height)) for i in range(len(rendered))]
    height = tops[-1] + font.get_height()

    for y, line in zip(tops, rendered):
            surface.blit(line, (25, y - 410 + (10 * scroll_value)))

    return surface


def donate():
    wikipedia.donate()


donate_button = Button(530, 15, donate_icon, 0.5)
copy_button = Button(553, 60, copy_icon, 0.3)
textbox = TextBox(screen, 25, 50, 400, 32, fontSize=15, colour=color_inactive,
                  borderColour=color_active, textColour=color_active,
                  borderThickness=2, font=text_font)
sentence_slider = Slider(screen, 415, 32, 75, 10, min=1, max=10, step=1, colour=color_inactive, handleColour=color_active, initial=2, valueColour=color_active)
scroll_slider = Slider(screen, 5, 100, 10, 225, min=0, max=max_scroll, colour=color_inactive, handleColour=color_active, initial=max_scroll, radius=5, vertical=True)
output = TextBox(screen, 500, 23, 30, 30, fontSize=15, font=text_font, colour=color_inactive, textColour=color_active, borderColour=color_active)
output.disable()


def main():
    global result
    global wrapped_result
    global search_query
    global sentences
    global textbox
    clock = pg.time.Clock()
    done = False

    while not done:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    search_query = textbox.getText()
                    scroll_slider.setValue(max_scroll)

        if search_query != '':
            try:
                result = wikipedia.summary(search_query, sentences=sentences)
            except wikipedia.exceptions.DisambiguationError:
                result = 'Please be more specific!'
            except wikipedia.exceptions.PageError:
                result = 'That page does not exist!'
            except wikipedia.exceptions.HTTPTimeoutError:
                result = 'Connection timed out!'
            except wikipedia.exceptions.RedirectError:
                    result = 'The page title led to a redirect!'
            except wikipedia.exceptions.WikipediaException:
                 result = 'Oops! There has been an error! Please try again!'
            except ConnectionError:
                result = 'No connection!'

        wrapped_result = wrap_text(result, text_font, 550)
        screen.fill(bg_color)
        render_text_list(wrapped_result, text_font, screen, scroll_slider.getValue(), color_inactive)
        pygame.draw.rect(screen, bg_color, [0, 0, SCREEN_WIDTH, 85])
        draw_text('WikiNeedia', header_font, color_inactive, 25, 0)
        draw_text('Number of sentences: ', text_font, color_inactive, 250, 25)

        if donate_button.update(screen):
            if not donate_button.donated:
                donate_button.donated = True
                donate()

        if copy_button.update(screen):
            pyperclip.copy(result)

        sentences = sentence_slider.getValue()
        output.setText(sentences)
        pygame_widgets.update(events)
        pygame.display.update()
        clock.tick(60)


main()