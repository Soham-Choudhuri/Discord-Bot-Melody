import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands # Import the app_commands extension
import yt_dlp

# --- YTDL & FFmpeg Configuration ---
# Options for yt-dlp to only get the audio stream info
YDL_OPTIONS = {
    'format': 'bestaudio/best', # Selects the best audio stream
    'extract_flat': 'in_playlist', # Necessary for better playlist support
    'restrictfilenames': True,
    'noplaylist': True, # Keep this unless you want to handle playlists directly
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Options for FFmpeg to stream the audio
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn' # -vn means 'no video'
}

# --- Bot and Command Setup ---
# Use commands.Bot
intents = discord.Intents.default()
intents.message_content = True # Needed for standard commands, good practice
bot = commands.Bot(command_prefix='!', intents=intents)

# Event to sync commands when bot is ready
@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')
    # Sync slash commands globally (can take up to an hour) or to a specific guild (instant)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Music Streaming Command
@bot.tree.command(name="stream", description="Plays a song from a YouTube URL or search query.")
@app_commands.describe(url="The YouTube/YouTube Music URL or search query.")
async def play_command(interaction: discord.Interaction, url: str):
    # 1. Defer the response (since YTDL might take time)
    await interaction.response.defer(thinking=True) 

    # 2. Check if the user is in a voice channel
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        return await interaction.followup.send("You need to be in a **Voice Channel** for me to play music!")

    voice_channel = interaction.user.voice.channel
    
    # 3. Handle Voice Channel Connection/Movement
    vc = interaction.guild.voice_client
    if vc is None:
        # Bot is not in a voice channel, connect to the user's channel
        vc = await voice_channel.connect()
    elif vc.channel != voice_channel:
        # Bot is in a different channel, move to the user's channel
        await vc.move_to(voice_channel)
    
    # Check if music is already playing (you'd normally queue here)
    if vc.is_playing():
        vc.stop() # For simplicity, stop the current song

    # 4. Extract Audio Stream URL using yt-dlp
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # Using asyncio.to_thread
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)
        
            audio_url = info['url'] 
            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', 'Unknown Artist')
    except Exception as e:
        print(f"YTDL Error: {e}")
        return await interaction.followup.send(f"An error occurred while fetching the song: `{e}`")
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # Use ytdl.extract_info to get all stream data
            info = ydl.extract_info(url, download=False)
            
            # This line gets the best audio stream's URL
            # Note: For yt-dlp, 'url' might be the direct stream URL needed by FFmpeg
            audio_url = info['url'] 
            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', 'Unknown Artist')

    except Exception as e:
        print(f"YTDL Error: {e}")
        return await interaction.followup.send(f"An error occurred while fetching the song: `{e}`")

    # 5. Play the Audio
    try:
        # Create a streaming audio source from the extracted URL
        source = discord.FFmpegOpusAudio(audio_url, **FFMPEG_OPTIONS)
        
        # Play the audio source
        vc.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
        
        await interaction.followup.send(f"**Now Playing:** `{title} by {artist}`")

    except Exception as e:
        print(f"Playback Error: {e}")
        await interaction.followup.send(f"A playback error occurred: `{e}`")

# Music Stop Command
@bot.tree.command(name="stop", description="Stops the music and leaves the voice channel.")
async def stop_command(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc is None or not vc.is_connected():
        return await interaction.response.send_message("I'm not connected to any voice channel!")

    await vc.disconnect()
    await interaction.response.send_message("Disconnected from the voice channel and stopped playing music.")

# Retrieve the token from the environment variable for security.
try:
    TOKEN = os.environ['DISCORD_BOT_TOKEN']
except KeyError:
    print("🚨 ERROR: DISCORD_BOT_TOKEN environment variable not found.")
    print("Please set the environment variable to your bot's token.")
    exit()

# Start the bot. This is the code that connects to Discord.
bot.run(TOKEN)