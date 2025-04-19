from core import ChillBot
from discord import Member, User
from pymongo.errors import PyMongoError

def get_rank_name(permission_level: int) -> str:
    rank_names = {
        '4': 'Куратор',
        '3': 'Гл. Модератор',
        '2': 'Модератор',
        '1': 'Хелпер',
        '0': 'Участник'
    }
    return rank_names.get(str(permission_level), f'Неизвестно ({permission_level})')

async def get_permissions(bot: ChillBot, member: User) -> int:
    try:
        user_data = await bot.config.DB.users.find_one({"id": member.id})
        if user_data:
            return user_data.get('perms', 0)
    except PyMongoError as e:
        print(f"Произошла ошибка при получении прав участника {member.id}: {e}")
    return 0

async def set_permissions(bot: ChillBot, member: Member, permissions: int) -> None:
    try:
        update_result = await bot.config.DB.users.update_one(
            {"id": member.id},
            {"$set": {"perms": permissions}},
            upsert=True
        )
        if update_result.upserted_id:
            print(f"Внесён новый участник {member.id} с правами {permissions}")
        else:
            print(f"Обновлён участник {member.id} с новыми правами {permissions}")
    except PyMongoError as e:
        print(f"Произошла ошибка в базе данных при участнике {member.id}: {e}")
