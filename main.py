import asyncio
import logging
import sys
from gc import callbacks


import aiosqlite
import datetime

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand, BotCommandScopeDefault


TOKEN = "7585641841:AAGbqpF4yYnwIlVEcNhjq5z1XhPFpzxny8c"
dp = Dispatcher()
data_districts = ["Октябрьский", "Железнодорожный", "Центральный", "Советский", "Ленинский", "Кировский",
                  "Свердловский"]
variants = ", ".join(data_districts)
data_time_parsing = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

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
            description="Добавить новый район в базу данных"
        ),
        BotCommand(
            command="remove_dis",
            description="Удалить район из базы данных"
        ),
        BotCommand(
            command="update_time",
            description="Измените вермя увеломления об отключении"
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def add_to_database(telegram_id, username):
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, username TEXT, date TEXT, Октябрьский TEXT UNIQUE, Железнодорожный TEXT UNIQUE, Центральный TEXT UNIQUE, Советский TEXT UNIQUE, Ленинский TEXT UNIQUE, Кировский TEXT UNIQUE, Свердловский TEXT UNIQUE, date_parsing TEXT UNIQUE)")
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


def get_keyboard1():
    keyboard_b = InlineKeyboardBuilder()
    for name_district in data_districts:
        keyboard_b.button(text=name_district, callback_data=name_district)
    keyboard_b.adjust(2, )
    return keyboard_b.as_markup()

def get_keyboard2():
    keyboard_b = InlineKeyboardBuilder()
    for name_time in data_time_parsing:
        keyboard_b.button(text=name_time, callback_data=name_time)
    keyboard_b.adjust(3, )
    return keyboard_b.as_markup()

#########################################
async def add_district_to_database(name_district, user_id):
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(f"UPDATE users SET {name_district} = ? WHERE telegram_id = ?", (True, user_id))
        await db.commit()
        return None

async def remove_distric_from_database(name_district, user_id):
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(f"UPDATE users SET {name_district} = ? WHERE telegram_id = ?", (False, user_id))
        await db.commit()
        return None

async def update_time_parsing(time_par, user_id):
    async with aiosqlite.connect('telegram.db') as db:
        await db.execute(f"UPDATE users SET {time_par} = ? WHERE  = ?", (time_par, user_id))
        await db.commit()
        return None
#########################################


@dp.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    await set_commands(bot)
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!, Вы зарегестрированы на наш сервис, уведомляющий об отключении воды! Из приведённого ниже списка районов выбирите подходящие вам.",
        reply_markup=get_keyboard1())
    # await message.answer(f"{variants}")
    talegram_id = message.from_user.id
    username = message.from_user.username
    await add_to_database(talegram_id, username)

@dp.message(F.text == 'тест')
async def test(message: Message):
    id = 504535913

    async with aiosqlite.connect('telegram.db').cursor() as db:
        res = await db.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id,))
        print(res.fetchall())




@dp.callback_query(F.data.in_(data_districts))
async def add_to_control_district(call: CallbackQuery):
    await call.message.answer(f'Вы выбрали {call.data} район')
    # ЗДЕСЬ НАДО ОТОСЛАТЬ РАЙОН В БАЗУ
    await add_district_to_database(call.data, str(call.from_user.id))
    # ЗДЕСЬ ДОЛЖЕН БЫТЬ КОНЕЦ ДОБАВЛЕНИЯ
    await call.answer()

@dp.callback_query(F.data.in_(data_time_parsing))
async def add_to_control_time(call: CallbackQuery):
    await call.message.answer(f'Вы выбрали {call.data}')
    await update_time_parsing(call.data, str(call.from_user.id))
    await call.answer()

###
async def add_dis(message: Message, bot: Bot):
    await message.answer(
        f"Из перечня районов выберите подходящий вам", reply=get_keyboard1()
    )
    talegram_id = message.from_user.id
    username = message.from_user.username
    await add_district_to_database()


@dp.message(Command("remove_dis"))
async def remove_dis(message: Message):
    await message.answer(
        f"Из перечня выберите районы для удаления из базы данных", reply=get_keyboard1()
    )
    talegram_id = message.from_user.id
    username = message.from_user.username
    await remove_distric_from_database()

async def update_time(message: Message, bot: Bot):
    await message.answer(
        f"Из перечня выберите день недели для получения уведомления"
    )
###




async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
