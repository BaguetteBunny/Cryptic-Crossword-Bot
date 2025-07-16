import requests
import random
from PIL import Image, ImageDraw, ImageFont
import constants as C
from itertools import chain

class Generator:
    def __init__(self, user_id, crossword_id=0):
        self.user_id = user_id

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

        self.title = self.data["webTitle"].title()
        self.date = self.data["webPublicationDateDisplay"]
        self.author = str(self.data.get("author", {}).get("byline") or "Anonymous").title()

        self.across_puzzle_lines = {}
        self.down_puzzle_lines = {}
        self.haschar = []

        entries = self.data["crossword"]["entries"]

        self.description = ""        
        for entry in entries:
            direction = entry.get("direction")
            clue = entry.get("clue")
            number = entry.get("number")
            solution = entry.get("solution")
            position = entry.get("position")

            if direction == "across":
                self.across_puzzle_lines[number] = {"clue": clue, "direction": direction, "solution": solution, "position": position, "my_solution": ""}
            elif direction == "down":
                self.down_puzzle_lines[number] = {"clue": clue, "direction": direction, "solution": solution, "position": position, "my_solution": ""}

            symbol = "→" if direction == "across" else "↓"
            self.description += f"{number} {symbol} : {clue}\n"

            print(solution)


        # Load assets
        self.assets = {
            "empty": Image.open(C.IMAGES_PATH+"empty.png").resize((C.TILE_SIZE, C.TILE_SIZE)),
            "font": ImageFont.truetype(C.FONT_PATH, 24),
            "letter_font": ImageFont.truetype(C.FONT_PATH, 64)
        }

        self.create_crossword()

        """
        DEBUG HERE:
        self.debug_check_completion // Fills grid except last one
        """

    def crossword_exists(self, crid):
        req = requests.get(f"https://www.theguardian.com/crosswords/cryptic/{crid}.json")
        return req if 200 == req.status_code else False
    
    def create_crossword(self):
        canvas_width = C.COLS*C.TILE_SIZE
        canvas_height = C.ROWS*C.TILE_SIZE
        self.canvas = Image.new('RGB', (canvas_width, canvas_height), color='black')
        self.draw = ImageDraw.Draw(self.canvas)
        self.grid = [["!" for _ in range(C.COLS)] for _ in range(C.ROWS)]

        # Draw across puzzle lines
        for _, value in self.across_puzzle_lines.items():
            position = value["position"]
            solution = value["solution"]
            x, y = position["x"], position["y"]

            for i in range(len(solution)):
                new_x = C.TILE_SIZE*(x+i)
                new_y = C.TILE_SIZE*y
                self.canvas.paste(self.assets["empty"], (new_x, new_y))
                self.grid[y][x + i] = "?"

        # Draw down puzzle lines
        for _, value in self.down_puzzle_lines.items():
            position = value["position"]
            solution = value["solution"]
            x, y = position["x"], position["y"]

            for i in range(len(solution)):
                new_x = C.TILE_SIZE*x
                new_y = C.TILE_SIZE*(y+i)
                self.canvas.paste(self.assets["empty"], (new_x, new_y))
                self.grid[y + i][x] = "?"
        
        # Draw number labels
        drawn_labels = set()
        for key, value in chain(self.across_puzzle_lines.items(), self.down_puzzle_lines.items()):
            position = value["position"]
            x, y = position["x"], position["y"]

            if (x, y) not in drawn_labels:
                self.draw.text(
                    (C.TILE_SIZE * x+3, C.TILE_SIZE * y-1),
                    str(key),
                    fill="black",
                    font=self.assets["font"]
                )
                drawn_labels.add((x, y))
    
    def write(self, number, word, direction):
        if direction == "across":
            puzzle_line = self.across_puzzle_lines
        elif direction == "down":
            puzzle_line = self.down_puzzle_lines

        # Number exists
        if not 1 <= number <= max(max({int(k): v for k, v in self.across_puzzle_lines.items()}.keys()), max({int(k): v for k, v in self.down_puzzle_lines.items()}.keys())):
            return f"Number {number} not found in crossword."
        
        # Direction exists
        if number not in puzzle_line.keys():
            return f"Direction mismatch: Clue {number} cannot be completed {direction.lower()}."
        
        # Length exact
        if len(word) != len(puzzle_line[number]["solution"]):
            return f"Word length mismatch: There are {len(puzzle_line[number]['solution'])} letters, not {len(word)}!"
        
        # Draw letters
        puzzle_line[number]["my_solution"] = word.upper()
        for i, char in enumerate(puzzle_line[number]["my_solution"]):
            x, y = puzzle_line[number]["position"]["x"], puzzle_line[number]["position"]["y"]
            if direction == "across": # here
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

    def verify(self, number, direction):
        if direction == "across":
            puzzle_line = self.across_puzzle_lines
        elif direction == "down":
            puzzle_line = self.down_puzzle_lines

        if not 1 <= number <= max(max({int(k): v for k, v in self.across_puzzle_lines.items()}.keys()), max({int(k): v for k, v in self.down_puzzle_lines.items()}.keys())):
            return f"Number {number} not found in crossword."
        
        if number not in puzzle_line.keys():
            return f"Direction mismatch: Clue {number} cannot be completed {direction.lower()}."
        
        if puzzle_line[number]["my_solution"].upper() == "":
            return "You have not provided a solution for this clue yet."
        
        if puzzle_line[number]["my_solution"].upper() == puzzle_line[number]["solution"].upper():
            return "Yes! That's the correct answer."
        else:
            return "No, that is incorrect. Try again!"
        
    def check_complete(self):
        for number in self.across_puzzle_lines.keys():
            if self.across_puzzle_lines[number]["my_solution"].upper() != self.across_puzzle_lines[number]["solution"].upper():
                return
            
        for number in self.down_puzzle_lines.keys():
            if self.down_puzzle_lines[number]["my_solution"].upper() != self.down_puzzle_lines[number]["solution"].upper():
                return
            
        return "Congratulations! You've completed this crossword successfully!"
    
    def debug_check_completion(self):
        for number in self.across_puzzle_lines.keys():
            result = self.across_puzzle_lines[number]["solution"].upper()
            self.across_puzzle_lines[number]["my_solution"] = result
            self.write(number, result, direction="across")
            
        for number in list(self.down_puzzle_lines.keys())[:-1]:
            result = self.down_puzzle_lines[number]["solution"].upper()
            self.down_puzzle_lines[number]["my_solution"] = result
            self.write(number, result, direction="down")