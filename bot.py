import os
import discord
from discord.ext import commands

# Enabling necessary intents. message_content is needed to read message content for commands.
intents = discord.Intents.default()
intents.message_content = True 

# Using commands.Bot for basic commands
bot = commands.Bot(command_prefix='!', intents=intents)

# Event to verify the connection to Discord
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

try:
    TOKEN = os.environ['DISCORD_BOT_TOKEN']
except KeyError:
    print("ERROR: DISCORD_BOT_TOKEN environment variable not found.")
    print("Please set the environment variable to your bot's token.")
    exit()

# Start the bot. This will connect to Discord.
bot.run(TOKEN)