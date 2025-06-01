import asyncio

from discord.ext import commands

from core.audio import get_audio_source
from core.queue_manager import queues


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store current position in seconds per guild
        self.current_pos = {}
        # Store current song title and query per guild to reload on seek
        self.current_song = {}

    async def play_next(self, ctx, guild_id, start_time=0):
        if queues[guild_id]:
            title, query = queues[guild_id].popleft()
            source = get_audio_source(query, start_time=start_time)[1]
            self.current_pos[guild_id] = start_time
            self.current_song[guild_id] = (title, query)
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
            self.current_pos.pop(guild_id, None)
            self.current_song.pop(guild_id, None)

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
    async def play(self, ctx, *, query):
        guild_id = ctx.guild.id
        if ctx.voice_client is None:
            await ctx.invoke(self.bot.get_command("join"))

        try:
            title, source = get_audio_source(query)
        except Exception:
            await ctx.send("❌ Could not retrieve audio.")
            return

        if guild_id not in queues:
            queues[guild_id] = []

        if not ctx.voice_client.is_playing():
            self.current_pos[guild_id] = 0
            self.current_song[guild_id] = (title, query)
            ctx.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx, guild_id), self.bot.loop
                ),
            )
            await ctx.send(f"🎶 Now playing: **{title}**")
        else:
            queues[guild_id].append((title, query))
            await ctx.send(f"➕ Added to queue: **{title}**")

    @commands.command()
    async def forward(self, ctx, seconds: int):
        """Skip forward by a number of seconds."""
        guild_id = ctx.guild.id
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            await ctx.send("⚠️ Nothing is currently playing.")
            return

        if guild_id not in self.current_pos or guild_id not in self.current_song:
            await ctx.send("⚠️ Cannot skip forward right now.")
            return

        new_pos = self.current_pos[guild_id] + seconds
        # Optionally add checks here for song length if you track it
        vc.stop()
        title, query = self.current_song[guild_id]
        source = get_audio_source(query, start_time=new_pos)[1]
        self.current_pos[guild_id] = new_pos
        vc.play(source)
        await ctx.send(f"⏩ Skipped forward {seconds} seconds in **{title}**")

    @commands.command()
    async def back(self, ctx, seconds: int):
        """Skip backward by a number of seconds."""
        guild_id = ctx.guild.id
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            await ctx.send("⚠️ Nothing is currently playing.")
            return

        if guild_id not in self.current_pos or guild_id not in self.current_song:
            await ctx.send("⚠️ Cannot skip backward right now.")
            return

        new_pos = self.current_pos[guild_id] - seconds
        if new_pos < 0:
            new_pos = 0
        vc.stop()
        title, query = self.current_song[guild_id]
        source = get_audio_source(query, start_time=new_pos)[1]
        self.current_pos[guild_id] = new_pos
        vc.play(source)
        await ctx.send(f"⏪ Skipped backward {seconds} seconds in **{title}**")


    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            guild_id = ctx.guild.id
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped current song.")
            await self.play_next(ctx, guild_id)
        else:
            await ctx.send("⚠️ Nothing is currently playing.")


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


async def setup(bot):
    await bot.add_cog(Music(bot))
