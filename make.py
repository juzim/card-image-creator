from PIL import Image, ImageDraw, ImageFont
import glob
from pathlib import Path
from datetime import datetime
import yaml


PAGE_HEIGTH = 2480
PAGE_WIDTH = 3507

ARCHIVE = False

CONFIG_KEY_PAGE_HEIGHT = 'page_height' 
CONFIG_KEY_PAGE_WIDTH = 'page_width' 
CONFIG_KEY_PAGE_MARGIN_X = 'page_margin_x' 
CONFIG_KEY_PAGE_MARGIN_Y = 'page_margin_y' 
CONFIG_KEY_PAGE_SPACING_X = 'page_spacing_x' 
CONFIG_KEY_PAGE_SPACING_Y = 'page_spacing_y' 
CONFIG_KEY_CARD_TEXT_COLOR = 'card_text_color'
CONFIG_KEY_CARD_MIN_FONT_SIZE = 'card_min_font_size' 
CONFIG_KEY_CARD_MAX_FONT_SIZE = 'card_max_font_size' 
CONFIG_KEY_CARD_TEXT = 'card_text'

FONT_PATH = Path('fonts')

EXTENSIONS = ['.png', '.jpg', '.jpeg']

ROOT = Path(__file__).parent.absolute()
INPUT_PATH = ROOT / 'images'
ARCHIVE_PATH = INPUT_PATH / 'archive'
CONFIG_PATH = ROOT / 'config.yaml'

def build_text_box(card_width: int, text_box_height: int, card_border_size: int) -> Image:
    text_box = Image.new('RGB', (card_width, text_box_height), color = (0,0,0))
    text_box_fill = Image.new('RGB', (card_width - card_border_size * 2, text_box_height - card_border_size * 2), color = (255,255,255))

    text_box.paste(text_box_fill, (card_border_size, card_border_size))

    return text_box


def get_font(lines: str, image: Image, card_config: dict):
    fontsize = card_config[CONFIG_KEY_CARD_MIN_FONT_SIZE]  # starting font size

    # portion of image width you want text width to be
    img_fraction = 0.85
    
    font_family = str(FONT_PATH / (card_config['font'] if 'font' in card_config else 'default.otf'))

    font = ImageFont.truetype(font_family, fontsize)
    while font.getsize_multiline(lines)[0] < img_fraction*image.size[0] and fontsize <= card_config[CONFIG_KEY_CARD_MAX_FONT_SIZE]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(font_family, fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1

    return font

def run(config: dict):
    page_margin_x = config[CONFIG_KEY_PAGE_MARGIN_X]
    page_margin_y = config[CONFIG_KEY_PAGE_MARGIN_Y]
    spacing_x = config[CONFIG_KEY_PAGE_SPACING_X]
    spacing_y = config[CONFIG_KEY_PAGE_SPACING_Y]
    offset_x = page_margin_x
    offset_y = page_margin_y    

    pages = []

    page = None
    for filepath in glob.iglob(f'{INPUT_PATH}/*.*'):
        card_config = config
        text = None

        path = Path(filepath)
        if not path.suffix in EXTENSIONS:
            continue

        print(f'Handling {filepath}')

        config_path = path.with_suffix('.txt')
        try:
            with config_path.open('r') as config_file:
                loaded_card_config = yaml.safe_load(config_file)
                print(f'Config found: {loaded_card_config}')
                card_config = {**config, **loaded_card_config}
        except FileNotFoundError:
            pass
        
        card_border_size = card_config['card_border_size']
        card_height = card_config['card_height']
        card_width = card_config['card_width']
        image_width = card_width - card_border_size * 2
        image_height = image_width # image can not be cropped yet
        text_box_height = card_height - image_height
         
        with Image.open(path) as im:
            try:
                text = card_config[CONFIG_KEY_CARD_TEXT]
            except KeyError:
                text = Path(path).stem

            im = im.convert('RGB')
            card = Image.new('RGB', (card_width, card_height), color = (0, 0, 0))

            im = im.resize((image_width, image_width))
            card.paste(im, (card_border_size, card_border_size))

            text_box = build_text_box(card_width, text_box_height, card_border_size)
            card.paste(text_box, (0, image_height - card_border_size))
            text = text.replace('__', "\n")
            font = get_font(text, card, card_config)
            
            drawn_card = ImageDraw.Draw(card)
            drawn_card.multiline_text(
                (int(card_width / 2), image_height + 90), 
                text, 
                fill=card_config[CONFIG_KEY_CARD_TEXT_COLOR], 
                anchor="ms", 
                align='center', 
                font=font,
                spacing=40)

            if not page:
                page = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGTH), color = (255, 255, 255))
            
            page.paste(card, (offset_x, offset_y))
            offset_x += card_width 

            if (offset_x + card_width + page_margin_x > PAGE_WIDTH):
                offset_x = page_margin_x
                offset_y += card_height + spacing_y
            else:
                offset_x += spacing_x

            if offset_y + card_height + page_margin_y > PAGE_HEIGTH:
                offset_y = page_margin_y
                offset_x = page_margin_x

                pages.append(page)
                page = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGTH), color = (255, 255, 255))

        if ARCHIVE == True:
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

if __name__ == '__main__':
    print("Start")
    with CONFIG_PATH.open('r') as config_file:
        run(yaml.safe_load(config_file))
    print("Done")
