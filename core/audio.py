from urllib.parse import urlparse

import discord
from yt_dlp import YoutubeDL

ytdl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
}

ytdl = YoutubeDL(ytdl_opts)


def is_url(string: str) -> bool:
    """Check if the string is a valid URL.

    Args:
        string (str): The string to check.

    Returns:
        bool: True if the string is a valid URL, False otherwise.
    """
    try:
        result = urlparse(string)
        return all([result.scheme in ("http", "https"), result.netloc])
    
    except ValueError:
        return False


def get_audio_source(
    query: str,
    start_time: int = 0,
) -> tuple[str, discord.AudioSource]:
    """Get an audio source from a query or URL.

    Args:
        query (str): The search query or URL.
        start_time (int, optional): The start time in seconds to seek to. Defaults to 0.

    Returns:
        tuple[str, discord.AudioSource]: A tuple containing the title of the audio and the audio source.
    """
    if not is_url(query):
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]

    else:
        info = ytdl.extract_info(query, download=False)

    ffmpeg_options = {"before_options": f"-ss {start_time}", "options": "-vn"}

    source = discord.FFmpegPCMAudio(info["url"], **ffmpeg_options)

    return info["title"], source
