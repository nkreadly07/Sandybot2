import discord
from discord.ext import commands
from redbot.core import commands as red_commands
from redbot.core.bot import Red
from discord.utils import get
from redbot.core import Config
import yt_dlp as youtube_dl  # Updated import
import asyncio

class Music(red_commands.Cog):
    """A cog for playing music in voice channels"""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Replace with your unique identifier
        self.queue = []

    @red_commands.command(name="mplay")
    async def play(self, ctx, url: str):
        """Play a song from a YouTube link."""
        voice_channel = ctx.author.voice.channel
        if not voice_channel:
            await ctx.send("You need to be in a voice channel to use this command.")
            return

        voice_client = get(self.bot.voice_clients, guild=ctx.guild)

        if not voice_client:
            voice_client = await voice_channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:  # No change here
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, method="fallback")

            if not voice_client.is_playing():
                voice_client.play(source, after=lambda e: print(f"Player error: {e}") if e else None)
                await ctx.send(f"Now playing: {info['title']}")
            else:
                self.queue.append((url2, info['title']))
                await ctx.send(f"Added to queue: {info['title']}")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @red_commands.command()
    async def stop(self, ctx):
        """Stop the music and disconnect."""
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I am not connected to any voice channel.")

    @red_commands.command()
    async def skip(self, ctx):
        """Skip the currently playing song."""
        voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Skipped the current song.")
        else:
            await ctx.send("No song is currently playing.")
