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
        self.haschar = []


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

        # Load assets
        self.assets = {
            "empty": Image.open(C.IMAGES_PATH+"empty.png").resize((C.TILE_SIZE, C.TILE_SIZE)),
            "font": ImageFont.truetype(C.FONT_PATH, 24),
            "letter_font": ImageFont.truetype(C.FONT_PATH, 64)
        }

        self.create_crossword()

    def crossword_exists(self, crid):
        req = requests.get(f"https://www.theguardian.com/crosswords/cryptic/{crid}.json")
        return req if 200 == req.status_code else False
    
    def create_crossword(self):
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
    
    def write(self, number, word):
        if number not in self.numbers:
            print(f"Number {number} not found in crossword.")
            return False
        
        idx = self.numbers.index(number)
        position = self.positions[idx]
        direction = self.directions[idx]
        
        if len(word) != len(self.solutions[idx]):
            print(f"Word length mismatch: There are {len(self.solutions[idx])} letters, not {len(word)}!")
            return False
        
        for i, char in enumerate(word):
            x, y = position["x"], position["y"]
            if direction == "across":
                self.grid[y][x + i] = char
                new_x = C.TILE_SIZE * (x + i)
                new_y = C.TILE_SIZE * y
            elif direction == "down":
                self.grid[y + i][x] = char
                new_x = C.TILE_SIZE * x
                new_y = C.TILE_SIZE * (y + i)
            
            if (new_x, new_y) in self.haschar:
                self.canvas.paste(self.assets["empty"], (new_x, new_y))
            self.draw.text((new_x+20, new_y+10), char, fill="black", font=self.assets["letter_font"])
            self.haschar.append((new_x, new_y))
        
        return True



test = Generator(23713)
test.write(1, "TESTS")
test.write(2, "TESTSTEST")
test.canvas.show()