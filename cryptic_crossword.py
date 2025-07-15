import discord
from discord.ext import commands
import constants as C
import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

print("Starting bot...")
@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash command(s)")

@bot.tree.command(name="hello", description="Say hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention}!")

try:
    bot.run(C.TOKEN)
except Exception as e:
    print(f"Bot failed to run: {e}")
