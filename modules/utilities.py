from core import ChillBot
from discord import Member, User
from pymongo.errors import PyMongoError

async def delete_ban(bot: ChillBot, member: User) -> None:
    try:
        result = await bot.config.DB.bans.delete_many({"_id": member.id})
        if result.deleted_count == 0:
            pass
    except PyMongoError as e:
        print(f"Error deleting ban for member {member.id}: {e}")

async def set_ban(bot: ChillBot, member: Member, moderator: User, timestamp: int, reason: str) -> None:
    try:
        if await bot.config.DB.bans.count_documents({"_id": member.id}) > 0:
            await delete_ban(bot, member)

        await bot.config.DB.bans.insert_one({
            "_id": member.id,
            "moderator_id": moderator.id,
            "timestamp": timestamp,
            "reason": reason
        })
    except PyMongoError as e:
        print(f"Error setting ban for member {member.id}: {e}")
