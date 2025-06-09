import asyncio
from collections import deque

from discord.ext import commands

from core.audio import get_audio_source
from core.queue_manager import queues


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_pos = {}
        self.current_song = {}
        print("[Music] Cog initialized.")

    async def play_next(self, ctx, guild_id, start_time=0):
        if queues[guild_id]:
            title, query = queues[guild_id].popleft()
            print(f"[play_next] Next song: {title} ({query})")
            source = get_audio_source(query, start_time=start_time)[1]
            self.current_pos[guild_id] = start_time
            self.current_song[guild_id] = (title, query)
            ctx.voice_client.play(
                source,
                after=lambda _: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx, guild_id),
                    self.bot.loop,
                ),
            )
            await ctx.send(f"🎶 Now playing: **{title}**")
            await ctx.send(f"🎶 Now playing: **{title}**")

        else:
            print(f"[play_next] Queue empty for guild {guild_id}")
            await ctx.send("📭 Queue is empty. Leaving voice channel.")
            await ctx.voice_client.disconnect()
            self.current_pos.pop(guild_id, None)
            self.current_song.pop(guild_id, None)

    @commands.command()
    async def join(self, ctx):
        print(f"[join] Called by user {ctx.author}")
        if ctx.author.voice:
            channel = ctx.author.voice.channel

            if ctx.voice_client is None:
                await channel.connect()
                print(f"[join] Connected to {channel.name}")
                await ctx.send(f"✅ Joined {channel.name}")

            else:
                print("[join] Already connected.")
                await ctx.send("⚠️ Already connected.")

        else:
            print("[join] User not in a voice channel.")
            await ctx.send("❌ You must be in a voice channel to use this.")

    @commands.command()
    async def play(self, ctx, *, query):
        guild_id = ctx.guild.id
        print(f"[play] Called with query: {query}")

        if ctx.voice_client is None:
            print("[play] Not connected to voice, invoking join.")
            await ctx.invoke(self.bot.get_command("join"))

        try:
            title, source = get_audio_source(query)
            print(f"[play] Got audio source: {title}")

        except Exception as e:
            print(f"[play] Error getting audio source: {e}")
            await ctx.send("❌ Could not retrieve audio.")
            return

        if guild_id not in queues:
            queues[guild_id] = deque()
            print(f"[play] Created new queue for guild {guild_id}")

        if not ctx.voice_client.is_playing():
            print(f"[play] Nothing playing, starting {title}")
            self.current_pos[guild_id] = 0
            self.current_song[guild_id] = (title, query)
            ctx.voice_client.play(
                source,
                after=lambda _: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx, guild_id), self.bot.loop
                ),
            )
            await ctx.send(f"🎶 Now playing: **{title}**")

        else:
            print(f"[play] Already playing, adding {title} to queue")
            queues[guild_id].append((title, query))
            await ctx.send(f"➕ Added to queue: **{title}**")

    @commands.command()
    async def skip(self, ctx):
        print(f"[skip] Called in guild {ctx.guild.id}")
        if ctx.voice_client and ctx.voice_client.is_playing():
            guild_id = ctx.guild.id
            ctx.voice_client.stop()
            print("[skip] Skipped current song.")
            await ctx.send("⏭️ Skipped current song.")
            await self.play_next(ctx, guild_id)
        else:
            print("[skip] Nothing is currently playing.")
            await ctx.send("⚠️ Nothing is currently playing.")

    @commands.command()
    async def queue(self, ctx):
        print(f"[queue] Called in guild {ctx.guild.id}")
        guild_id = ctx.guild.id
        if guild_id not in queues or not queues[guild_id]:
            print("[queue] Queue is empty.")
            await ctx.send("📭 Queue is empty.")
        else:
            titles = [title for title, _ in queues[guild_id]]
            queue_text = "\n".join(f"{i+1}. {title}" for i, title in enumerate(titles))
            print(f"[queue] Upcoming songs: {titles}")
            await ctx.send(f"📃 **Upcoming songs:**\n{queue_text}")

    @commands.command()
    async def leave(self, ctx):
        print(f"[leave] Called in guild {ctx.guild.id}")
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            queues.pop(ctx.guild.id, None)
            print("[leave] Disconnected and cleared queue.")
            await ctx.send("👋 Disconnected.")

    @commands.command()
    async def stop(self, ctx):
        print(f"[stop] Called in guild {ctx.guild.id}")
        if ctx.voice_client:
            ctx.voice_client.stop()
            queues.pop(ctx.guild.id, None)
            print("[stop] Stopped playback and cleared queue.")
            await ctx.send("🛑 Stopped and cleared the queue.")


async def setup(bot):
    print("[setup] Adding Music cog.")
    await bot.add_cog(Music(bot))
