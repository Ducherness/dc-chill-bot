import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class Config:
    class Roles:
        helper = {1265558032906059907: 1}
        moderator = {1255888414788681779: 2}
        chief_moderator = {1255887370528624742: 3}
        curator = {1255888561023090760: 4}

    class Emojis:
        chillbot_yes = '✅'
        chillbot_no = '❌'
        chillbot_gold_ingot = '💛'
        chillbot_iron_ingot = '🩶'
        chillbot_exceptional = '🥐'
        chillbot_netherite_ingot = '🖤'
        chillbot_world_nether_star = '🧿'
        golden_apple = '🥭'
        apple = '🍎'
        anime_emoji = '🍬'

    class Token:
        main = os.getenv("TOKEN")

    MAIN_GUILD = 1349296495395995648

    TOKEN = Token.main

    MONGO_CLIENT = AsyncIOMotorClient(os.getenv("MONGODB"))

    DB = MONGO_CLIENT.ChillBot