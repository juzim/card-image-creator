from PIL import Image, ImageDraw, ImageFont, ImageOps
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

CONFIG_KEY_CARD_TEXT_COLOR = 'text_color'
CONFIG_KEY_CARD_FONT_SIZE = 'font_size' 
CONFIG_KEY_CARD_MIN_FONT_SIZE = 'min_font_size' 
CONFIG_KEY_CARD_MAX_FONT_SIZE = 'max_font_size' 
CONFIG_KEY_CARD_TEXTS = 'texts'

EXTENSIONS = ['.png', '.jpg', '.jpeg']

ROOT = Path(__file__).parent.absolute()
INPUT_PATH = ROOT / 'images'
ARCHIVE_PATH = INPUT_PATH / 'archive'
CONFIG_PATH = ROOT / 'config.yaml'

def build_text_box(card_width: int, text_box_height: int, card_border_size: int) -> Image:
    text_box = Image.new('RGB', (card_width, text_box_height), color = (255,255,255))

    return text_box


def get_font(max_width: Image, card_config: dict, global_config: dict) -> ImageFont:
    lines = card_config['content']
    fontsize = card_config[CONFIG_KEY_CARD_FONT_SIZE] if CONFIG_KEY_CARD_FONT_SIZE in card_config else card_config[CONFIG_KEY_CARD_MIN_FONT_SIZE]  # starting font size

    # portion of image width you want text width to be
    img_fraction = 0.85
    font_name = card_config['font']
    font_path = Path(font_name)

    try:
        font_path = Path(global_config['font_folder'],  font_name)
        font = ImageFont.truetype(str(font_path), fontsize)
    except OSError:
        raise Exception(f'Font [{font_name}] not found in font_folder [{card_config["font_folder"]}]')

    if CONFIG_KEY_CARD_FONT_SIZE in card_config:
        return font

    while font.getsize_multiline(lines)[0] < img_fraction * max_width and fontsize <= card_config[CONFIG_KEY_CARD_MAX_FONT_SIZE] + 1:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(str(font_path), fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1

    return font

def get_config_path(path):
    return path.with_suffix('.yaml')

def handle_card(image_path: Path, card_config: dict, global_config):
    card_border_size = card_config['border_size']
    card_border_color = card_config['border_color']
    card_height = global_config['card_height'] - card_border_size * 2
    card_width = global_config['card_width'] - card_border_size * 2

    image_width = card_width 
    image_height = image_width # image can not be cropped yet
    text_box_height = card_height - image_height

    with Image.open(image_path) as im:
        im = im.convert('RGB')
        card = Image.new('RGB', (card_width, card_height), color = (255, 255, 255))

        im = im.resize((image_height, image_width))
        #card.paste(im, (card_border_size, card_border_size))
        card.paste(im, (0, 0))

        text_box = build_text_box(card_width, text_box_height, card_border_size)

        if not CONFIG_KEY_CARD_TEXTS in card_config:
            card_config[CONFIG_KEY_CARD_TEXTS] = [{'content': Path(image_path).stem}]

        texts = card_config[CONFIG_KEY_CARD_TEXTS]

        drawn_text_box = ImageDraw.Draw(text_box)

        text_margin_top = 30

        for text_config in texts:
            text_config = {**card_config['text_defaults'], **text_config}
            text_config['content'] = text_config['content'].replace('__', "\n").replace('_', ' ')

            font = get_font(card.size[0], text_config, global_config)
            # unreliable
            #if font.getsize_multiline(text)[1] + text_margin_top > text_box.size[1]:
            #   raise Exception(f'Text {font.getsize_multiline(text)[1]} does not fit box {text_box.size[1]}')

            font_size = font.getsize_multiline(text_config['content'])
            font_height = font_size[0]
            font_width = font_size[1]


            #line_box = build_text_box(card_width, text_box_height, 0)
            #drawn_line_box = ImageDraw.Draw(line_box)
            #drawn_line_box.rectangle((card_border_size, card_border_size, image_width, font_height), fill='pink')

            drawn_text_box.multiline_text(
                (int(card_width / 2), text_margin_top), 
                text_config['content'], 
                fill=text_config[CONFIG_KEY_CARD_TEXT_COLOR], 
                anchor="ma", 
                align='center', 
                font=font,
                spacing=40)
            
            #text_box.paste(text_box, (0, text_margin_top))
            text_margin_top += font.getsize_multiline(text_config['content'])[1] + 40


        text_box = ImageOps.expand(text_box, border=card_border_size, fill=card_border_color)
        card.paste(text_box, (0 - card_border_size, image_height))

        card = ImageOps.expand(card, border=card_border_size, fill=card_border_color)

        return card



def run(global_config: dict):
    page_margin_x = global_config[CONFIG_KEY_PAGE_MARGIN_X]
    page_margin_y = global_config[CONFIG_KEY_PAGE_MARGIN_Y]
    spacing_x = global_config[CONFIG_KEY_PAGE_SPACING_X]
    spacing_y = global_config[CONFIG_KEY_PAGE_SPACING_Y]
    offset_x = page_margin_x
    offset_y = page_margin_y    

    pages = []

    page = None
    for file in glob.iglob(f'{INPUT_PATH}/*.*'):
        path = Path(file)
        if not path.suffix in EXTENSIONS:
            continue

        print(f'Handling {path}')

        card_config = {**global_config['card']}

        config_path = get_config_path(path)
        loaded_card_config = None
        card = None

        try:
            with config_path.open('r') as config_file:
                loaded_card_config = yaml.safe_load(config_file)
                print(f'Custom config found: {str(config_path)}')
                card_config.update(loaded_card_config)
        except FileNotFoundError:
            pass

        card = handle_card(path, card_config, global_config) 

        if not page:
            page = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGTH), color = (255, 255, 255))
        
        page.paste(card, (offset_x, offset_y))
        card_height = global_config['card_height']
        card_width = global_config['card_width']

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
               config_path = get_config_path(path)
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
