import discord
import aiohttp
import json
import os

from core import ChillBot
from discord.ext import commands, tasks

YOUTUBE_API_KEY = "."

YOUTUBE_CHANNELS = {
    "RedelOff": "UCQdX7MkmEpVluxJHy32zvXg",
    "MrIrbby": "UCwJiijyelx3wVZop6c0L_zQ",
    "keeperhouse": "UCScf3CwH_k_HMdXomZJWhQg",
    "skypl1ne": "UC3kzQZAfDHVRPniIKHmkvNA",
    "1x9pvp": "UC7d5-in3MUp3tVrOKCoUdBw"
}

DISCORD_CHANNEL_ID = 1257715719391674479
VIDEO_LOG_FILE = "video_log.json"

class YouTubePublisher(commands.Cog, name="YouTube Publisher Cog"):
    def __init__(self, bot):
        self.bot = bot
        self.posted_videos = self.load_posted_videos()
        self.check_videos.start()

    def load_posted_videos(self):
        if os.path.exists(VIDEO_LOG_FILE):
            with open(VIDEO_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_posted_videos(self):
        with open(VIDEO_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.posted_videos, f, ensure_ascii=False, indent=4)

    async def fetch_latest_video(self, session, channel_id):
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?key={YOUTUBE_API_KEY}"
            f"&channelId={channel_id}"
            f"&part=snippet"
            f"&order=date"
            f"&maxResults=1"
            f"&regionCode=US"
        )
        async with session.get(url) as resp:
            data = await resp.json()

            if "items" not in data or not data["items"]:
                return None, None

            item = data["items"][0]
            video_id = item["id"].get("videoId")
            video_title = item["snippet"]["title"]
            return video_id, video_title

    @tasks.loop(minutes=10)
    async def check_videos(self):
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            print("Не удалось найти канал для публикации.")
            return

        async with aiohttp.ClientSession() as session:
            for name, yt_id in YOUTUBE_CHANNELS.items():
                video_id, video_title = await self.fetch_latest_video(session, yt_id)
                if not video_id or not video_title:
                    continue

                if name not in self.posted_videos or self.posted_videos[name] != video_id:
                    self.posted_videos[name] = video_id
                    self.save_posted_videos()

                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    await channel.send(f"Хэй! {name} опубликовал новое видео **{video_title}**! Ссылка: {video_url}")
                    print(f"Опубликовано: {name} - {video_title} ({video_url})")

async def setup(bot: ChillBot):
    await bot.add_cog(YouTubePublisher(bot))
