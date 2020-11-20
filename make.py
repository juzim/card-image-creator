from PIL import Image, ImageDraw, ImageFont
import glob
from pathlib import Path
from datetime import datetime
import fire
import yaml

CARD_WIDTH = 640
CARD_HEIGHT = 1010
CARD_BORDER_SIZE = 2
IMAGE_WIDTH = CARD_WIDTH - CARD_BORDER_SIZE * 2
IMAGE_HEIGHT = IMAGE_WIDTH
TEXT_BOX_HEIGHT = CARD_HEIGHT - IMAGE_HEIGHT
CANVAS_HEIGTH = 2480
CANVAS_WIDTH = 3507
FONT_PATH = Path('fonts')

SPACING_X = 40
SPACING_Y = 40

DEFAULT_OFFSET_X = 50
DEFAULT_OFFSET_Y = 50

EXTENSIONS = ['.png', '.jpg', '.jpeg']


ROOT = Path(__file__).parent.absolute()
INPUT_PATH = ROOT / 'images'
ARCHIVE_PATH = INPUT_PATH / 'archive'


def build_text_box() -> Image:
    text_box = Image.new('RGB', (CARD_WIDTH, TEXT_BOX_HEIGHT), color = (0,0,0))
    text_box_fill = Image.new('RGB', (CARD_WIDTH - CARD_BORDER_SIZE * 2, TEXT_BOX_HEIGHT - CARD_BORDER_SIZE * 2), color = (255,255,255))

    text_box.paste(text_box_fill, (CARD_BORDER_SIZE, CARD_BORDER_SIZE))

    return text_box


def get_font(lines: str, image: Image, card_config: dict):
    fontsize = 1  # starting font size

    # portion of image width you want text width to be
    img_fraction = 0.85
    
    font_family = str(FONT_PATH / (card_config['font'] if 'font' in card_config else 'default.otf'))

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

    pages = []


    text_box = build_text_box()
    page = None
    for filepath in glob.iglob(f'{INPUT_PATH}/*.*'):
        card_config = {}
        text = None

        path = Path(filepath)
        if not path.suffix in EXTENSIONS:
            continue

        print(f'Handling {filepath}')

        config_path = path.with_suffix('.txt')

        try:
            with config_path.open('r') as config_file:
                card_config = yaml.safe_load(config_file)
                print(f'Config found: {card_config}')
        except FileNotFoundError:
            pass

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
            card.paste(im, (CARD_BORDER_SIZE, CARD_BORDER_SIZE))

            card.paste(text_box, (0, IMAGE_HEIGHT - CARD_BORDER_SIZE))
            text = text.replace('__', "\n")
            font = get_font(text, card, card_config)

            drawn_card = ImageDraw.Draw(card)
            drawn_card.multiline_text(
                (int(CARD_WIDTH / 2), IMAGE_HEIGHT + 90), 
                text, 
                fill="black", 
                anchor="ms", 
                align='center', 
                font=font,
                spacing=40)

            if not page:
                page = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGTH), color = (255, 255, 255))
            
            page.paste(card, (offset_x, offset_y))
            offset_x += CARD_WIDTH 

            if (offset_x + CARD_WIDTH + DEFAULT_OFFSET_X > CANVAS_WIDTH):
                offset_x = DEFAULT_OFFSET_X
                offset_y += CARD_HEIGHT + SPACING_Y
            else:
                offset_x += SPACING_X

            if offset_y + CARD_HEIGHT + DEFAULT_OFFSET_Y > CANVAS_HEIGTH:
                offset_y = DEFAULT_OFFSET_Y
                offset_x = DEFAULT_OFFSET_X

                pages.append(page)
                page = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGTH), color = (255, 255, 255))
                
        # archive image
        path.replace(ARCHIVE_PATH / path.name)
        try:
           config_path.replace(ARCHIVE_PATH / config_path.name)
        except FileNotFoundError:
           pass
    if page:
        pages.append(page)

    if len(pages) == 0:
        print('No images found')
        return

    pages[0].save(Path('result') / f'cards_{datetime.now().strftime(f"%Y%m%d-%H%M")}.pdf', save_all=True, append_images=pages[1:])
    #canvas.save(Path('result') / f'cards_{datetime.now().strftime(f"%Y%m%d-%H%M")}.png')

if __name__ == '__main__':
  print("Start")
  fire.Fire(run)
  print("Done")
