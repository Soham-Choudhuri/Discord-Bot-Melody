import os
import discord
from discord.ext import commands

# Enable necessary intents. message_content is needed to read message content for commands.
intents = discord.Intents.default()
intents.message_content = True 

# Use commands.Bot for a more robust command structure
bot = commands.Bot(command_prefix='!', intents=intents)

# Event that triggers when the bot successfully connects to Discord
@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')

# Bot Commands

@bot.command() # 'hello' command. Greets the user.
async def hello(ctx):
    """Responds with a greeting."""
    await ctx.send('Hello! I am Melody, Your personal Music Bot for Discord by Stryker (Soham).')

@bot.command() # 'echo' command. Repeats the user's message.
async def echo(ctx, *, message):
    """Repeats the message provided by the user."""
    await ctx.send(message)

# Create a custom command to play music from youtube music URL
@bot.command() # 'play' command. Plays music from a YouTube Music URL.
async def play(ctx, url):
    """Plays music from a YouTube Music URL."""
    # Placeholder implementation
    await ctx.send(f'Playing music from: {url}')

# --- 4. Running the Bot ---
# Retrieve the token from the environment variable for security.
try:
    TOKEN = os.environ['DISCORD_BOT_TOKEN']
except KeyError:
    print("🚨 ERROR: DISCORD_BOT_TOKEN environment variable not found.")
    print("Please set the environment variable to your bot's token.")
    exit()

# Start the bot. This is the code that connects to Discord.
# It should always be the last line in your script.
bot.run(TOKEN)