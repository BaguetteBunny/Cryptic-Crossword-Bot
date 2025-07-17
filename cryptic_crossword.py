import datetime, io, logging, discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import constants as C
from generator import Crossword, Puzzle
from cachetools import TTLCache

def load_crossword(user_id):
    # Buffer image generation
    buffer = io.BytesIO()
    crosswords[user_id].canvas.save(buffer, format="PNG")
    buffer.seek(0)
    file = discord.File(fp=buffer, filename="crossword.png")

    # Generate crossword clues
    embed = discord.Embed(title=f"Made by {crosswords[user_id].author}", description=crosswords[user_id].description, colour=0x00b0f4, timestamp=datetime.datetime.now())
    embed.set_author(name=crosswords[user_id].title, url="https://assets.guim.co.uk/static/frontend/icons/homescreen/apple-touch-icon-512.png", icon_url="https://i.pinimg.com/736x/63/79/d5/6379d5eecd5dbd3b4c2b425e802b537e.jpg")
    embed.set_footer(text=crosswords[user_id].date, icon_url="https://assets.guim.co.uk/static/frontend/icons/homescreen/apple-touch-icon-512.png")
    return embed, file

def load_puzzle(user_id, completed: bool):
    # Generate puzzle_clue
    desc = puzzles[user_id].completed_description if completed else puzzles[user_id].description
    embed = discord.Embed(title=f"Made by {puzzles[user_id].author}", description=desc, colour=0x00b0f4, timestamp=datetime.datetime.now())
    embed.set_author(name=puzzles[user_id].title, url="https://assets.guim.co.uk/static/frontend/icons/homescreen/apple-touch-icon-512.png", icon_url="https://i.pinimg.com/736x/63/79/d5/6379d5eecd5dbd3b4c2b425e802b537e.jpg")
    embed.set_footer(text=puzzles[user_id].date, icon_url="https://assets.guim.co.uk/static/frontend/icons/homescreen/apple-touch-icon-512.png")
    return embed

handler = logging.FileHandler(filename='log/discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
crosswords = TTLCache(maxsize=C.CACHE_SIZE, ttl=C.CACHE_TTL)
puzzles = TTLCache(maxsize=C.CACHE_SIZE, ttl=C.CACHE_TTL)  # 3 hours TTL

print("Starting bot...")
@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash command(s)")

@bot.tree.command(name="start_crossword", description="Start a new cryptic crossword.")
async def start(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in crosswords:
        await interaction.response.send_message("❌ You already have a cryptic crossword running. Run the command `/stop_crossword` to stop. ❌", ephemeral=True)
        return
    
    crosswords[user_id] = Crossword(user_id)
    await interaction.response.send_message("Loading cryptic crossword... 🖊️", ephemeral=True)
    embed,file = load_crossword(user_id=user_id)
    await interaction.followup.send(embed=embed, file=file)

@app_commands.choices(direction=[Choice(name="ACROSS", value="across"), Choice(name="DOWN", value="down")])
@bot.tree.command(name="solve_crossword", description="Solve a cryptic crossword clue.")
async def start(interaction: discord.Interaction, clue_number: int, word: str, direction: Choice[str]):
    user_id = interaction.user.id
    if user_id not in crosswords:
        await interaction.response.send_message("❌ You do not have a cryptic crossword running. Run the command `/start_crossword` to start. ❌", ephemeral=True)
        return
    
    clue_number = interaction.data.get('options', [{}])[0].get('value')
    word = interaction.data.get('options', [{}])[1].get('value')

    result = crosswords[user_id].write(clue_number, word, direction.value)
    
    if result:
        await interaction.response.send_message(result, ephemeral=True)
    else:
        await interaction.response.send_message(f"✔️ Successfully wrote '{word}' for clue number {clue_number}. ✔️", ephemeral=True)
        
        completion = crosswords[user_id].check_complete()
        embed,file = load_crossword(user_id=interaction.user.id)
        if completion:
            username = await bot.fetch_user(user_id)
            text = f"‼️ Congratulations! `{str(username)}` has completed their cryptic crossword successfully! 🥳🎉"
            await interaction.followup.send(content=text, file=file)
            del crosswords[user_id]
        else:
            await interaction.followup.send(embed=embed, file=file)

@app_commands.choices(direction=[Choice(name="ACROSS", value="across"), Choice(name="DOWN", value="down")])
@bot.tree.command(name="verify_crossword", description="Checks if your cryptic crossword solution is correct for a given clue number.")
async def start(interaction: discord.Interaction, clue_number: int, direction: Choice[str], say_solution: bool):
    user_id = interaction.user.id
    if user_id not in crosswords:
        await interaction.response.send_message("❌ You do not have a cryptic crossword running. Run the command `/start_crossword` to start. ❌", ephemeral=True)
        return
    
    clue_number = interaction.data.get('options', [{}])[0].get('value')
    await interaction.response.send_message(crosswords[user_id].verify(clue_number, direction.value, say_solution), ephemeral=True)

@bot.tree.command(name="stop_crossword", description="Stop current cryptic crossword game.")
async def start(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in crosswords:
        await interaction.response.send_message("❌ You do not have a cryptic crossword running. Run the command `/start_crossword` to start. ❌", ephemeral=True)
        return
    
    del crosswords[user_id]
    await interaction.response.send_message("❌ Your cryptic crossword has been stopped. ❌", ephemeral=True)

@bot.tree.command(name="start_puzzle", description="Start a new cryptic puzzle.")
async def start(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in puzzles:
        await interaction.response.send_message("❌ You already have a cryptic puzzle running. Run the command `/stop_puzzle` to stop. ❌", ephemeral=True)
        return
    
    puzzles[user_id] = Puzzle(user_id)
    await interaction.response.send_message("Loading cryptic puzzle... 🖊️", ephemeral=True)
    await interaction.followup.send(embed=load_puzzle(user_id=interaction.user.id, completed=False))

@bot.tree.command(name="solve_puzzle", description="Solve a cryptic puzzle clue.")
async def start(interaction: discord.Interaction, word: str):
    user_id = interaction.user.id
    if user_id not in puzzles:
        await interaction.response.send_message("❌ You do not have a cryptic puzzle running. Run the command `/start_puzzle` to start. ❌", ephemeral=True)
        return
    
    word = interaction.data.get('options', [{}])[0].get('value')

    result = puzzles[user_id].write(word)

    embed = load_puzzle(user_id=user_id, completed=False)
    if result == True:
        username = await bot.fetch_user(user_id)
        embed = load_puzzle(user_id=user_id, completed=True)
        await interaction.response.send_message(f"‼️ Congratulations! `{str(username)}` has completed their cryptic puzzle successfully! 🥳🎉", ephemeral=True)
        del puzzles[user_id]
    else:
        embed = load_puzzle(user_id=user_id, completed=False)
        await interaction.response.send_message(f"❌ No, that is incorrect. Try again! ❌", ephemeral=True)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="stop_puzzle", description="Stop current cryptic puzzle game.")
async def start(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in puzzles:
        await interaction.response.send_message("❌ You do not have a cryptic puzzle running. Run the command `/start_puzzle` to start. ❌", ephemeral=True)
        return
    
    await interaction.response.send_message(f"❌ Your cryptic puzzle has been stopped.\nThe correct answer was: **{puzzles[user_id].puzzle_line['solution'].upper()}**❌", ephemeral=True)
    del puzzles[user_id]

try:
    bot.run(C.TOKEN)
except Exception as e:
    print(f"Bot failed to run: {e}")
