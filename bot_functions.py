import aiosqlite

from aiogram import Router
from aiogram import Bot, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from const import data_districts, data_time_parsing
from keyboards import get_keyboard1, get_keyboard2, get_keyboard_delete_district
from handlers import set_commands, add_to_database, add_district_to_database, remove_district_from_database, \
    update_time_parsing


my_router = Router(name=__name__)


@my_router.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    await set_commands(bot)
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}!, Вы зарегестрированы на наш сервис, уведомляющий об отключении воды! Из приведённого ниже списка районов выбирите подходящие вам.",
        reply_markup=get_keyboard1(data_districts))
    # await message.answer(f"{variants}")
    talegram_id = message.from_user.id
    username = message.from_user.username
    await add_to_database(talegram_id, username)


@my_router.callback_query(F.data.in_(data_districts))
async def add_to_control_district(call: CallbackQuery):
    await call.message.answer(f'Вы выбрали {call.data} район')
    # ЗДЕСЬ НАДО ОТОСЛАТЬ РАЙОН В БАЗУ
    await add_district_to_database(call.data, str(call.from_user.id))
    # ЗДЕСЬ ДОЛЖЕН БЫТЬ КОНЕЦ ДОБАВЛЕНИЯ
    await call.answer()


@my_router.callback_query(F.data.in_(data_time_parsing))
async def add_to_control_time(call: CallbackQuery):
    await call.message.answer(f'Вы выбрали {call.data}')
    await update_time_parsing(call.data, str(call.from_user.id))
    await call.answer()


@my_router.message(Command("add_dis"))
async def add_dis(message: Message, bot: Bot):
    id = message.from_user.id
    districts_not_added = []
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id,))

        res = await cur.fetchone()
        res = list(res)[3:-1]
        for el in range(len(res)):
            if res[el] == '0':
                districts_not_added.append(data_districts[el])

    await message.answer(
        "Из перечня районов выберите подходящий вам",
        reply_markup=get_keyboard1(districts_not_added), )


@my_router.message(Command("remove_dis"))
async def remove_dis(message: Message, bot: Bot):
    id = message.from_user.id
    districts_added = []
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id,))

        res = await cur.fetchone()
        res = list(res)[3:-1]
        for el in range(len(res)):
            if res[el] == '1':
                districts_added.append(data_districts[el])
    print(districts_added)

    await message.answer(
        "Из перечня районов выберите подходящий вам",
        reply_markup=get_keyboard_delete_district(districts_added), )


@my_router.message(Command("show_data"))
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
        f"В списке отслеживаемых районов находятся:\n{", ".join(data_show)}")

@my_router.message(Command("update_time"))
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
        reply_markup=get_keyboard2(), )