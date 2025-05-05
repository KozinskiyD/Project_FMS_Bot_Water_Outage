import datetime
import aiosqlite

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description="Зарегестрироваться и начать работу"
        ),
        BotCommand(
            command="show_data",
            description="Показать отслеживаемые районы"
        ),
        BotCommand(
            command="add_dis",
            description="Добавить район в список отслеживаемых"
        ),
        BotCommand(
            command="remove_dis",
            description="Удалить район из списка отслеживаемых"
        ),
        BotCommand(
            command="update_time",
            description="Изменить вермя увеломления"
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def add_to_database(telegram_id, username):
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, username TEXT, date TEXT, Октябрьский TEXT, Железнодорожный TEXT, Центральный TEXT, Советский TEXT, Ленинский TEXT, Кировский TEXT, Свердловский TEXT, date_parsing TEXT)")
        cursor = await db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        data = await cursor.fetchone()
        if data is not None:
            return
    date = f'{datetime.date.today()}'
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(
            "INSERT INTO users (telegram_id, username, date, Октябрьский, Железнодорожный, Центральный, Советский, Ленинский, Кировский, Свердловский, date_parsing) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (telegram_id, username, date, False, False, False, False, False, False, False, "Понедельник"))
        await db.commit()


async def add_district_to_database(name_district, user_id):
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(f"UPDATE users SET {name_district} = ? WHERE telegram_id = ?", (True, user_id))
        await db.commit()
        return


async def remove_district_from_database(name_district, user_id):
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(f"UPDATE users SET {name_district} = ? WHERE telegram_id = ?", (False, user_id))
        await db.commit()
        return


async def update_time_parsing(time_par, user_id):
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(f"UPDATE users SET date_parsing = ? WHERE telegram_id = ?", (time_par, user_id))
        await db.commit()
        return
