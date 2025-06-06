from urllib.parse import urlparse

import discord
from yt_dlp import YoutubeDL

ytdl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
}
ytdl = YoutubeDL(ytdl_opts)

def is_url(string: str) -> bool:
    try:
        result = urlparse(string)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False

def get_audio_source(query: str, start_time: int = 0):
    if not is_url(query):
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    else:
        info = ytdl.extract_info(query, download=False)

    # Prepare ffmpeg options, including seek start time (-ss)
    ffmpeg_options = {
        'before_options': f'-ss {start_time}',
        'options': '-vn'
    }

    source = discord.FFmpegPCMAudio(info['url'], **ffmpeg_options)

    return info['title'], source
