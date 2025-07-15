from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv('ENV_DISCORD_TOKEN')
TILE_SIZE = 64
ROWS = 15
COLS = 15
IMAGES_PATH = "assets/images/"
FONT_PATH = "assets/fonts/monogram-extended.ttf"