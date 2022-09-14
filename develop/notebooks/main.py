import os
import random

import discord
import nest_asyncio
from dotenv import find_dotenv, load_dotenv

nest_asyncio.apply()
# Loads the .env file that resides on the same level as the script.
load_dotenv(find_dotenv())

# GetAPI token from .env file
DISCORD_TOKEN = os.getenv("TOKEN")

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
# connects to discord api
# Intents is the permission type of the bot, ensure it has everything in the developer portal
bot = discord.Client(intents=discord.Intents.all())


# # EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@bot.event
async def on_ready():
    # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
    guild_count = 0

    # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
    for guild in bot.guilds:
        # PRINT THE SERVER'S ID AND NAME.
        print(f"- {guild.id} (name: {guild.name})")

        # INCREMENTS THE GUILD COUNTER.
        guild_count = guild_count + 1

    # PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")


# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
# @bot.event
# async def on_message(message):

#     # If message contains 'hello testbot'
#     if message.content == "hello testbot":

#         # Send response
#         await message.channel.send("Hello, got any Shmeckles?")


@bot.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    print(f"Message {user_message} by {username} on {channel}")

    if message.author == bot.user:
        return

    if channel == "general":
        if user_message.lower() == "hello" or user_message.lower() == "hi":
            await message.channel.send(f"Hello {username} welcome to ye olde")
            return
        elif user_message.lower() == "bye":
            await message.channel.send(f"Bye {username}")
        elif user_message.lower() == "tell me a joke":
            jokes = [
                " Can someone please shed more\
            light on how my lamp got stolen?",
                "Why is she called llene? She\
                     stands on equal legs.",
                "What do you call a gazelle in a \
                     lions territory? Denzel.",
            ]
            await message.channel.send(random.choice(jokes))


# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)

# TODO: create feature which prints the total time users have been in a channel in discord and print the total time someone was in the chat when they've left
# %%
