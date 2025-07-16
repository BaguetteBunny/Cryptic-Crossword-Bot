from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv('ENV_DISCORD_TOKEN')
TILE_SIZE = 64
ROWS = 15
COLS = 15
IMAGES_PATH = "assets/images/"
FONT_PATH = "assets/fonts/monogram-extended.ttf"
BANNER = "assets/bot_images/banner.jpg"
ICON = "assets/bot_images/icon.jpg"

CACHE_SIZE = 500
CACHE_TTL = 10800

MINIMUM_CROSSWORD_ID = 21_621
MAXIMUM_CROSSWORD_ID = 29_747