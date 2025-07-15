import requests
import random
from PIL import Image, ImageDraw, ImageFont
import constants as C

class Generator:
    def __init__(self, crossword_id=0):
        # Find valid crossword ID
        self.crossword_id = crossword_id
        if self.crossword_id > 21_621 and self.crossword_exists(self.crossword_id):
            self.crossword_request = self.crossword_exists(crossword_id)
        
        else:
            self.crossword_id = 0
            while not self.crossword_id:
                randomID = random.randint(21_621, 29_747)
                self.crossword_request = self.crossword_exists(randomID)
                if self.crossword_request:
                    self.crossword_id = randomID
                else:
                    print(f"Crossword with ID {randomID} does not exist, trying again...")
        print(f"Crossword ID found: {self.crossword_id}")

        # Extract important data from the crossword URL
        self.data = self.crossword_request.json()
        self.clues = []
        self.solutions = []
        self.directions = []
        self.positions = []
        self.numbers = []
        self.solved = []


        entries = self.data["crossword"]["entries"]
        for entry in entries:
            clue = entry.get("clue")
            solution = entry.get("solution")
            direction = entry.get("direction")
            position = entry.get("position")
            number = entry.get("number")

            print(f"{number} {direction.upper()} at ({position['x']}, {position['y']}): {clue} → {solution}")
        
        for entry in entries:
            self.clues.append(entry.get("clue"))
            self.solutions.append(entry.get("solution"))
            self.directions.append(entry.get("direction"))
            self.positions.append(entry.get("position"))
            self.numbers.append(entry.get("number"))
            self.solved.append(None)

        # Load assets
        self.assets = {
            "empty": Image.open(C.IMAGES_PATH+"empty.png").resize((C.TILE_SIZE, C.TILE_SIZE)),
            "full": Image.open(C.IMAGES_PATH+"full.png").resize((C.TILE_SIZE, C.TILE_SIZE)),
            "font": ImageFont.truetype(C.FONT_PATH, 24)
        }

        # Create canvas for the crossword
        canvas_width = C.COLS*C.TILE_SIZE
        canvas_height = C.ROWS*C.TILE_SIZE
        self.canvas = Image.new('RGB', (canvas_width, canvas_height), color='black')
        self.draw = ImageDraw.Draw(self.canvas)
        self.grid = [["!" for _ in range(C.COLS)] for _ in range(C.ROWS)]

        for position, direction, idx in zip(self.positions, self.directions, range(len(self.positions))):
            x, y = position["x"], position["y"]
            for i in range(len(self.solutions[idx])):
                if direction == "across":
                    new_x = C.TILE_SIZE*(x+i)
                    new_y = C.TILE_SIZE*y
                    self.canvas.paste(self.assets["empty"], (new_x, new_y))
                    self.grid[y][x + i] = "?"
                elif direction == "down":
                    new_x = C.TILE_SIZE*x
                    new_y = C.TILE_SIZE*(y+i)
                    self.canvas.paste(self.assets["empty"], (new_x, new_y))
                    self.grid[y + i][x] = "?"

        # Create text 
        drawn_labels = set()
        for position, direction, idx in zip(self.positions, self.directions, range(len(self.positions))):
            x, y = position["x"], position["y"]
            if (x, y) not in drawn_labels:
                self.draw.text(
                    (C.TILE_SIZE * x+3, C.TILE_SIZE * y-1),
                    str(self.numbers[idx]),
                    fill="black",
                    font=self.assets["font"]
                )
                drawn_labels.add((x, y))

    def crossword_exists(self, crid):
        req = requests.get(f"https://www.theguardian.com/crosswords/cryptic/{crid}.json")
        return req if 200 == req.status_code else False
    
    def draw_on_grid(self): ...



test = Generator(23713)
print(test.crossword_id)
test.canvas.show()