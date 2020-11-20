from PIL import Image, ImageDraw, ImageFont
import glob
from pathlib import Path

root = Path(__file__).parent.absolute()
image_path = root / 'images'

CARD_WIDTH = 640
CARD_HEIGHT = 1010
CARD_BORDER_SIZE = 2
IMAGE_WIDTH = CARD_WIDTH - CARD_BORDER_SIZE * 2
IMAGE_HEIGHT = IMAGE_WIDTH
TEXT_BOX_HEIGHT = CARD_HEIGHT - IMAGE_HEIGHT
CANVAS_HEIGTH = 3508
CANVAS_WIDTH = 2480
text_box = Image.new('RGB', (CARD_WIDTH, TEXT_BOX_HEIGHT), color = (0,0,0))
text_box_fill = Image.new('RGB', (CARD_WIDTH - CARD_BORDER_SIZE * 2, TEXT_BOX_HEIGHT - CARD_BORDER_SIZE * 2), color = (255,255,255))

text_box.paste(text_box_fill, (CARD_BORDER_SIZE, CARD_BORDER_SIZE))

SPACING_X = 40
SPACING_Y = 40

DEFAULT_OFFSET_X = 20
DEFAULT_OFFSET_Y = 20
offset_x = DEFAULT_OFFSET_X
offset_y = DEFAULT_OFFSET_Y

def wrap_text(text, width, font):
    text_lines = []
    text_line = []
    text = text.replace('__', ' [br] ')
    words = text.split()
    font_size = font.getsize(text)

    for word in words:
        if word == '[br]':
            text_lines.append(' '.join(text_line))
            text_line = []
            continue
        text_line.append(word)
        w, h = font.getsize(' '.join(text_line))
        if w > width:
            text_line.pop()
            text_lines.append(' '.join(text_line))
            text_line = [word]

    if len(text_line) > 0:
        text_lines.append(' '.join(text_line))

    return "\n".join(text_lines)

def get_font_size(lines, Image, font_family):
    fontsize = 1  # starting font size

    # portion of image width you want text width to be
    img_fraction = 0.50

    font = ImageFont.truetype(font_family, fontsize)
    while font.getsize_multiline(lines)[0] < img_fraction*image.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(font_family, fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1

    return font

canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGTH), color = (255, 255, 255))
print("Start")
for filepath in glob.iglob(r'images/*.*'):
    print(filepath)
    with Image.open(filepath) as im:
        text = Path(filepath).stem
        
        im = im.convert('RGB')
        card = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), color = (0, 0, 0))
        card_fill = Image.new('RGB', (
            CARD_WIDTH - CARD_BORDER_SIZE * 2, 
            CARD_HEIGHT - CARD_BORDER_SIZE * 2), 
            color = (255, 255, 255))

        card.paste(card_fill, (CARD_BORDER_SIZE, CARD_BORDER_SIZE))
        im = im.resize((IMAGE_WIDTH, IMAGE_WIDTH))
        #im = im.thumbnail((CARD_WIDTH,CARD_WIDTH), Image.ANTIALIAS)
        card.paste(im, (CARD_BORDER_SIZE, CARD_BORDER_SIZE))
        card_text = text_box.copy()
        
        card.paste(card_text, (0, IMAGE_HEIGHT - CARD_BORDER_SIZE))
        drawn_card = ImageDraw.Draw(card)
        font = ImageFont.truetype('fonts/default.otf', 60)
        text = wrap_text(text, card_text.size[1], font)
        #font = get_font_size(text, drawn_card, 'fonts/default.otf')

        drawn_card.multiline_text(
            (int(CARD_WIDTH / 2), IMAGE_HEIGHT + 90), 
            text, 
            fill="black", 
            anchor="ms", align='center', font=font,
            spacing=40)
        
        canvas.paste(card, (offset_x, offset_y))
        offset_x += CARD_WIDTH + SPACING_X

        if (offset_x > CANVAS_WIDTH + SPACING_X):
            offset_x = DEFAULT_OFFSET_X
            offset_y += CARD_HEIGHT + SPACING_Y


   
canvas.save('cards.png')

print("Done")