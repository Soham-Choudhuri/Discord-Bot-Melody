import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp

# Options for yt-dlp to only get the audio stream info
YDL_OPTIONS = {
    'format': 'bestaudio/best', # Selects the best audio stream
    'extract_flat': 'in_playlist', # Necessary for better playlist support
    'restrictfilenames': True,
    'noplaylist': True,
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
    'options': '-vn' # no video
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Event to sync application interface commands when bot is ready
@bot.event
async def on_ready():
    print(f'Bot is logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# 1. Music Streaming Command
@bot.tree.command(name="stream", description="Plays a song from a YouTube URL or search query.")
@app_commands.describe(url="The YouTube/YouTube Music URL or search query.")
async def play_command(interaction: discord.Interaction, url: str):
    await interaction.response.defer(thinking=True) 

    # Checking if the user is in a voice channel or not
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        return await interaction.followup.send("You need to be in a **Voice Channel** for me to play music!")

    voice_channel = interaction.user.voice.channel
    
    # Handling Voice Channel Connection
    vc = interaction.guild.voice_client
    if vc is None:
        # Bot is not in a voice channel, connect to the user's channel
        vc = await voice_channel.connect()
    
    elif vc.channel != voice_channel:
        # Bot is in a different channel, move to the user's channel
        await vc.move_to(voice_channel)
    
    # Check if music is already playing (I will add Queue later here)
    if vc.is_playing():
        vc.stop()

    # Extracting Audio Stream URL using yt-dlp
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
            # Using ytdl.extract_info to get all stream data
            info = ydl.extract_info(url, download=False)
            audio_url = info['url'] 
            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', 'Unknown Artist')

    except Exception as e:
        print(f"YTDL Error: {e}")
        return await interaction.followup.send(f"An error occurred while fetching the song: `{e}`")

    # Playing the Audio
    try:
        # Streaming audio source from the extracted URL
        source = discord.FFmpegOpusAudio(audio_url, **FFMPEG_OPTIONS)
        
        # Callback function for when the song finishes
        async def after_playing(error):
            if error:
                print(f'Player error: {error}')
            else:
                # Send a message to the channel that the song has finished
                channel = interaction.channel
                await channel.send(f"**End of Playback**")

        # Playing the audio source
        vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(after_playing(e), bot.loop))
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

try:
    TOKEN = os.environ['DISCORD_BOT_TOKEN']
except KeyError:
    print("🚨 ERROR: DISCORD_BOT_TOKEN environment variable not found.")
    print("Please set the environment variable to your bot's token.")
    exit()

# Start the bot. This is the code that connects to Discord.
bot.run(TOKEN)