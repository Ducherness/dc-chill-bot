import datetime

from core import ChillBot
from typing import Literal
from .formats import convert_time_to_seconds

CooldownType = Literal['global', 'local']

async def set_cooldown(bot: ChillBot, type: CooldownType, system: str, user_id: int, time: str | int) -> None:
    if isinstance(time, int):
        time_in_seconds = time
    else:
        time_in_seconds = convert_time_to_seconds(time)
    
    if time_in_seconds is None:
        raise ValueError(f"Invalid time format: {time}")

    end_time = round((datetime.datetime.utcnow() + datetime.timedelta(seconds=time_in_seconds)).timestamp())

    query = {"type": type, "system": system}
    if type == 'local':
        query["user_id"] = user_id

    collection = bot.config.DB.cooldowns
    await collection.delete_many(query)
    await collection.insert_one({**query, "end": end_time})

async def is_cooldown(bot: ChillBot, type: CooldownType, system: str, user_id: int) -> int | None:
    query = {"type": type, "system": system}
    if type == 'local':
        query["user_id"] = user_id

    collection = bot.config.DB.cooldowns
    data = await collection.find_one(query)
    if not data:
        return None

    now = datetime.datetime.utcnow().timestamp()
    if now >= data["end"]:
        await collection.delete_many(query)
        return None

    return int(data["end"] - now)
