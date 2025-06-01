import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is now running.")

async def main():
    async with bot:
        await bot.load_extension("cogs.music")
        await bot.start(DISCORD_TOKEN)

asyncio.run(main())
