import asyncio
import os
import random

import discord
import nest_asyncio
from dotenv import find_dotenv, load_dotenv
from eight_ball import eight_ball_answer

nest_asyncio.apply()

# Loads the .env file that resides on the same level as the script.
load_dotenv(find_dotenv())

# GetAPI token from .env file
DISCORD_TOKEN = os.getenv("TOKEN")


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(
        self,
        message,
    ):
        # We do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith("$guess"):
            await message.channel.send("Guess a number between 1 and 10.")

            def is_correct(m):
                return m.author == message.author and m.content.isdigit()

            answer = random.randint(
                1,
                10,
            )

            try:
                guess = await self.wait_for(
                    "message",
                    check=is_correct,
                    timeout=5.0,
                )
            except asyncio.TimeoutError:
                return await message.channel.send(
                    f"Sorry, you took too long it was {answer}."
                )

            if int(guess.content) == answer:
                await message.channel.send("You are right!")
            else:
                await message.channel.send(f"Oops. It is actually {answer}.")

        if message.content.startswith("$8ball"):
            return message.channel.send(eight_ball_answer)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
