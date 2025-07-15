import discord
from discord.ext import commands
import constants as C
from generator import Generator
import logging
from cachetools import TTLCache
import datetime
import io

def load_crossword(user_id):
    # Buffer image generation
    buffer = io.BytesIO()
    games[user_id].canvas.save(buffer, format="PNG")
    buffer.seek(0)
    file = discord.File(fp=buffer, filename="crossword.png")

    # Generate crossword clues
    embed = discord.Embed(title=f"Made by {games[user_id].author}", description=games[user_id].description, colour=0x00b0f4, timestamp=datetime.datetime.now())
    embed.set_author(name=games[user_id].title, url="https://assets.guim.co.uk/static/frontend/icons/homescreen/apple-touch-icon-512.png", icon_url="https://i.pinimg.com/736x/63/79/d5/6379d5eecd5dbd3b4c2b425e802b537e.jpg")
    embed.set_footer(text=games[user_id].date, icon_url="https://assets.guim.co.uk/static/frontend/icons/homescreen/apple-touch-icon-512.png")
    return embed, file

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
games = TTLCache(maxsize=500, ttl=10800)  # 3 hours TTL

print("Starting bot...")
@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash command(s)")

@bot.tree.command(name="start", description="Start a new cryptic crossword game.")
async def start(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in games:
        await interaction.response.send_message("You already have a game running. Run the command `/stop` to stop.", ephemeral=True)
        return
    
    games[user_id] = Generator(user_id)
    await interaction.response.send_message("Loading cryptic crossword puzzle...", ephemeral=True)
    embed,file = load_crossword(user_id=interaction.user.id)
    await interaction.followup.send(embed=embed, file=file)


@bot.tree.command(name="solve", description="Solve a cryptic crossword clue.")
async def start(interaction: discord.Interaction, clue_number: int, word: str):
    user_id = interaction.user.id
    if user_id not in games:
        await interaction.response.send_message("You do not have a game running. Run the command `/start` to start.", ephemeral=True)
        return
    
    clue_number = interaction.data.get('options', [{}])[0].get('value')
    word = interaction.data.get('options', [{}])[1].get('value')

    result = games[user_id].write(clue_number, word)
    
    if result:
        await interaction.response.send_message(result, ephemeral=True)
    else:
        await interaction.response.send_message(f"Successfully wrote '{word}' for clue number {clue_number}.", ephemeral=True)
        embed,file = load_crossword(user_id=interaction.user.id)
        await interaction.followup.send(embed=embed, file=file)

@bot.tree.command(name="stop", description="Stop current cryptic crossword game.")
async def start(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in games:
        await interaction.response.send_message("You do not have a game running. Run the command `/start` to start.", ephemeral=True)
        return
    
    del games[user_id]
    await interaction.response.send_message("Your game has been stopped.", ephemeral=True)

try:
    bot.run(C.TOKEN)
except Exception as e:
    print(f"Bot failed to run: {e}")
