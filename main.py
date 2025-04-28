import asyncio
import logging
import sys


import aiosqlite
import datetime

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
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


def get_keyboard1(districts):
    keyboard_b = InlineKeyboardBuilder()
    for name_district in districts:
        keyboard_b.button(text=name_district, callback_data=name_district)
    keyboard_b.adjust(2, )
    return keyboard_b.as_markup()


def get_keyboard_delete_district(districts):
    keyboard_b = InlineKeyboardBuilder()
    for name_district in districts:
        keyboard_b.button(text=name_district, callback_data='удалить'+ name_district)
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


async def remove_district_from_database(call: CallbackQuery):
    user_id = call.from_user.id
    name_district = call.data.replace('удалить', '')
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
        reply_markup=get_keyboard1(data_districts))
    # await message.answer(f"{variants}")
    talegram_id = message.from_user.id
    username = message.from_user.username
    await add_to_database(talegram_id, username)

@dp.message(F.text == 'тест')
async def test(message: Message):
    id = message.from_user.id
    districts_not_added = []
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id, ))

        res = await cur.fetchone()
        res = list(res)[3:-1]
        for el in range(len(res)):
            if res[el] == '0':
                districts_not_added.append(data_districts[el])

        print(res)
        print(districts_not_added)

###CALLBACK
@dp.callback_query(F.data.in_(data_districts))
async def add_to_control_district(call: CallbackQuery):
    await call.message.answer(f'Вы выбрали {call.data} район')
    # ЗДЕСЬ НАДО ОТОСЛАТЬ РАЙОН В БАЗУ
    await add_district_to_database(call.data, str(call.from_user.id))
    # ЗДЕСЬ ДОЛЖЕН БЫТЬ КОНЕЦ ДОБАВЛЕНИЯ
    await call.answer()


#@dp.callback_query(F.data.in_(data_districts))
#async def remove_from_control_district(call: CallbackQuery):
#    await call.message.answer(f'Вы выбрали {call.data} район')
#    await remove_district_from_database(call.data, str(call.from_user.id))
#    await call.answer()

@dp.callback_query(F.data.in_(data_time_parsing))
async def add_to_control_time(call: CallbackQuery):
    await call.message.answer(f'Вы выбрали {call.data}')
    await update_time_parsing(call.data, str(call.from_user.id))
    await call.answer()

###

@dp.message(Command("add_dis"))
async def add_dis(message: Message, bot: Bot):
    id = message.from_user.id
    districts_not_added = []
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id, ))

        res = await cur.fetchone()
        res = list(res)[3:-1]
        for el in range(len(res)):
            if res[el] == '0':
                districts_not_added.append(data_districts[el])

    await message.answer(
        "Из перечня районов выберите подходящий вам",
        reply_markup=get_keyboard1(districts_not_added),
    )


@dp.message(Command("remove_dis"))
async def remove_dis(message: Message, bot: Bot):
    id = message.from_user.id
    districts_added = []
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id, ))

        res = await cur.fetchone()
        res = list(res)[3:-1]
        for el in range(len(res)):
            if res[el] == '1':
                districts_added.append(data_districts[el])
    print(districts_added)

    await message.answer(
        "Из перечня районов выберите подходящий вам",
        reply_markup=get_keyboard_delete_district(districts_added),
    )


@dp.message(Command("show_data"))
async def show_data(message: Message, bot: Bot):
    id = message.from_user.id
    data_show = []
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id,))
        res = await cur.fetchone()
        res = list(res)[3:-1]
        for el in range(len(res)):
            if res[el] == '1':
                data_show.append(data_districts[el])
    await message.answer(
        f"В списке отслеживаемых районов находятся:\n{", ".join(data_show)}"
    )


@dp.message(Command("update_time"))
async def update_time(message: Message, bot: Bot):
    id = message.from_user.id
    the_day = ""
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id,))
        res = await cur.fetchone()
        res = list(res)[-1]
        the_day = res
        data_days = []
        for el in data_time_parsing:
            if el != the_day:
                data_days.append(el)
    await message.answer(
        "Из перечня дней выберите подходящий вам",
        reply_markup=get_keyboard2(),
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
