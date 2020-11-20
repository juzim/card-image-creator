from PIL import Image, ImageDraw, ImageFont
import glob
from pathlib import Path
from datetime import datetime
import fire

CARD_WIDTH = 640
CARD_HEIGHT = 1010
CARD_BORDER_SIZE = 2
IMAGE_WIDTH = CARD_WIDTH - CARD_BORDER_SIZE * 2
IMAGE_HEIGHT = IMAGE_WIDTH
TEXT_BOX_HEIGHT = CARD_HEIGHT - IMAGE_HEIGHT
CANVAS_HEIGTH = 3508
CANVAS_WIDTH = 2480

SPACING_X = 40
SPACING_Y = 40

DEFAULT_OFFSET_X = 20
DEFAULT_OFFSET_Y = 20

EXTENSIONS = ['png', 'jpg', 'jpeg']


ROOT = Path(__file__).parent.absolute()
INPUT_PATH = ROOT / 'images'
ARCHIVE_PATH = INPUT_PATH / 'archive'


def build_text_box() -> Image:
    text_box = Image.new('RGB', (CARD_WIDTH, TEXT_BOX_HEIGHT), color = (0,0,0))
    text_box_fill = Image.new('RGB', (CARD_WIDTH - CARD_BORDER_SIZE * 2, TEXT_BOX_HEIGHT - CARD_BORDER_SIZE * 2), color = (255,255,255))

    text_box.paste(text_box_fill, (CARD_BORDER_SIZE, CARD_BORDER_SIZE))

    return text_box


def get_font(lines: str, image: Image, font_family: str):
    fontsize = 1  # starting font size

    # portion of image width you want text width to be
    img_fraction = 0.85

    font = ImageFont.truetype(font_family, fontsize)
    while font.getsize_multiline(lines)[0] < img_fraction*image.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(font_family, fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1

    return font


def run():

    offset_x = DEFAULT_OFFSET_X
    offset_y = DEFAULT_OFFSET_Y
    canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGTH), color = (255, 255, 255))

    text_box = build_text_box()

    for filepath in glob.iglob(f'{INPUT_PATH}/*.*'):
        print(f'Handling {filepath}')

        path = Path(filepath)
        with Image.open(path) as im:
            text = Path(path).stem

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

            card.paste(text_box, (0, IMAGE_HEIGHT - CARD_BORDER_SIZE))
            text = text.replace('__', "\n")
            font = get_font(text, card, 'fonts/default.otf')

            drawn_card = ImageDraw.Draw(card)
            drawn_card.multiline_text(
                (int(CARD_WIDTH / 2), IMAGE_HEIGHT + 90), 
                text, 
                fill="black", 
                anchor="ms", 
                align='center', 
                font=font,
                spacing=40)

            canvas.paste(card, (offset_x, offset_y))
            offset_x += CARD_WIDTH + SPACING_X

            if (offset_x > CANVAS_WIDTH + SPACING_X):
                offset_x = DEFAULT_OFFSET_X
                offset_y += CARD_HEIGHT + SPACING_Y
        
        # archive image
        path.replace(ARCHIVE_PATH / path.name)

    canvas.save(Path('result') / f'cards_{datetime.now().strftime(f"%Y%m%d-%H%M")}.png')

if __name__ == '__main__':
  print("Start")
  fire.Fire(run)
  print("Done")
