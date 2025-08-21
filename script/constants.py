from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv('ENV_DISCORD_TOKEN')
TILE_SIZE = 64
ROWS = 15
COLS = 15
IMAGES_PATH = "./assets/images/"
FONT_PATH = "./assets/fonts/monogram-extended.ttf"
BANNER = "./assets/bot_images/banner.jpg"
ICON = "./assets/bot_images/icon.jpg"

CACHE_SIZE = 500
CACHE_TTL = 10800

MINIMUM_CROSSWORD_ID = 21_621
MAXIMUM_CROSSWORD_ID = 29_747

COMMANDS_INFO = {
    "start_crossword": [
        "Start a new cryptic crossword.",
        []
    ],
    "solve_crossword": [
        "Solve a cryptic crossword clue.",
        ["clue_number", "word", "direction"]
    ],
    "verify_crossword": [
        "Checks if your cryptic crossword solution is correct for a given clue number.",
        ["clue_number", "direction", "say_solution"]
    ],
    "stop_crossword": [
        "Stop current cryptic crossword game.",
        []
    ],
    "start_puzzle": [
        "Start a new cryptic puzzle.",
        []
    ],
    "solve_puzzle": [
        "Solve a cryptic puzzle clue.",
        ["word"]
    ],
    "stop_puzzle": [
        "Stop current cryptic puzzle game.",
        []
    ],
    "def": [
        "Search a word in the dictionary.",
        ["word"]
    ],
    "help": [
        "Shows a list of commands and their descriptions",
        []
    ]
}
