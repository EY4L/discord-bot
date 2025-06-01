import asyncio

from discord.ext import commands

from core.audio import get_audio_source
from core.queue_manager import queues


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def play_next(self, ctx, guild_id):
        if queues[guild_id]:
            title, source = queues[guild_id].popleft()
            ctx.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx, guild_id), self.bot.loop
                ),
            )
            await ctx.send(f"🎶 Now playing: **{title}**")
        else:
            await ctx.send("📭 Queue is empty. Leaving voice channel.")
            await ctx.voice_client.disconnect()

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await channel.connect()
                await ctx.send(f"✅ Joined {channel.name}")
            else:
                await ctx.send("⚠️ Already connected.")
        else:
            await ctx.send("❌ You must be in a voice channel to use this.")

    @commands.command()
    async def play(self, ctx, query):
        guild_id = ctx.guild.id
        if ctx.voice_client is None:
            await ctx.invoke(self.bot.get_command("join"))

        try:
            title, source = get_audio_source(query)
        except Exception as e:
            await ctx.send("❌ Could not retrieve audio.")
            return

        if guild_id not in queues:
            queues[guild_id] = []

        if not ctx.voice_client.is_playing():
            ctx.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx, guild_id), self.bot.loop
                ),
            )
            await ctx.send(f"🎶 Now playing: **{title}**")
        else:
            queues[guild_id].append((title, source))
            await ctx.send(f"➕ Added to queue: **{title}**")


    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped current song.")

    @commands.command()
    async def queue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in queues or not queues[guild_id]:
            await ctx.send("📭 Queue is empty.")
        else:
            titles = [title for title, _ in queues[guild_id]]
            queue_text = "\n".join(f"{i+1}. {title}" for i, title in enumerate(titles))
            await ctx.send(f"📃 **Upcoming songs:**\n{queue_text}")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            queues.pop(ctx.guild.id, None)
            await ctx.send("👋 Disconnected.")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()
            queues.pop(ctx.guild.id, None)
            await ctx.send("🛑 Stopped and cleared the queue.")


def setup(bot):
    bot.add_cog(Music(bot))
