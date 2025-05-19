import aiosqlite

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Router
from aiogram import Bot, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from apscheduler.triggers.cron import CronTrigger

from const import data_districts, data_time_parsing, data_emoji, parts_district, data_time_parsing_eg
from keyboards import get_keyboard_add_district, get_keyboard_update_time, get_keyboard_delete_district
from handlers import set_commands, add_to_database, add_district_to_database, remove_district_from_database, \
    update_time_parsing
from parser import api

my_router = Router(name=__name__)


@my_router.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    await set_commands(bot)
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! Вы зарегистрированы на наш сервис, уведомляющий об отключении воды! Из приведённого ниже списка районов выбирите подходящие вам.\nПосле регистрации не забудьте использовать команду <b>/start_parsing</b>!\nПеред использованием этой функции, настройте дополнительные данные!",
        reply_markup=get_keyboard_add_district(data_districts))
    talegram_id = message.from_user.id
    username = message.from_user.username
    await add_to_database(talegram_id, username)


@my_router.callback_query(F.data.in_(data_districts))
async def add_to_control_district(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer(f'Вы добавили {call.data} район')
    await add_district_to_database(call.data, str(call.from_user.id))
    await call.answer()


@my_router.callback_query(F.data.startswith('удалить'))
async def delete_from_control_district(call: CallbackQuery):
    await call.message.edit_reply_markup()
    name = call.data.replace('удалить', '')
    await call.message.answer(f'Вы удалили {name} район')
    await remove_district_from_database(name, str(call.from_user.id))
    await call.answer()


@my_router.callback_query(F.data.startswith('изменить'))
async def add_to_control_time(call: CallbackQuery):
    await call.message.edit_reply_markup()
    name = call.data.replace('изменить', '')
    await call.message.answer(f'Вы изменили время уведомления: {name}')
    await update_time_parsing(name, str(call.from_user.id))
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
        reply_markup=get_keyboard_add_district(districts_not_added), )


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
    await message.answer(
        "Из перечня районов выберите подходящий вам",
        reply_markup=get_keyboard_delete_district(districts_added))


@my_router.message(Command("update_time"))
async def update_time(message: Message, bot: Bot):
    id = message.from_user.id
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
        reply_markup=get_keyboard_update_time(data_days), )


@my_router.message(Command("show_data"))
async def show_data(message: Message, bot: Bot):
    id = message.from_user.id
    data_show = []
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id,))
        res = await cur.fetchone()
        day = list(res)[-1]
        res = list(res)[3:-1]
        for el in range(len(res)):
            if res[el] == '1':
                data_show.append(data_districts[el])
        data_text = [el for el in data_show]
        for ind in range(len(data_text)):
            data_text[ind] = data_emoji[ind] + "  " + data_text[ind]
    await message.answer(
        f"В списке отслеживаемых районов находятся:\n"
        f"<blockquote><b>{"\n".join(data_text)}</b></blockquote>"
        f"Время уведомления: <b>{day}</b>")


@my_router.message(Command("show_info"))
async def show_info(message: Message):
    id = message.from_user.id
    data_show = []
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id,))
        res = await cur.fetchone()
        res = list(res)[3:-1]
        for el in range(len(res)):
            if res[el] == '1':
                data_show.append(data_districts[el] + " район")
        data_text = []
        for dist in data_show:
            for stre in parts_district:
                info = api().find_data(dist, stre)
                if info == None:
                    continue
                if "водоснабжение" in info[0] and info[-1] != "отмена":
                    data_text.append(info)
            if len(data_text) == 0:
                await message.answer(
                    f"<b>{dist}:</b>\nПо данному запросу не была найдена информация по отключению воды"
                )
            else:
                await message.answer(f"<b>{dist}</b> - информация по отключению:")
                for el in data_text:
                    await message.answer(
                        f"<b>Организация:</b> {el[1]}\n"
                        f"<b>Номер телефона:</b> {el[2]}, {el[2]}\n"
                        f"<b>Улицы:\n</b>"
                        f"<blockquote>{el[4]}</blockquote>\n"
                        f"<b>Начало - Завершение:</b> {el[-2]} - {el[-1]}"
                    )



@my_router.message(Command("start_parsing"))
async def show_info_day(message: Message):
    id = message.from_user.id
    connect = await aiosqlite.connect('telegram.db')
    async with connect.cursor() as cur:
        await cur.execute(f"SELECT * FROM users WHERE telegram_id = ?", (id,))
        res = await cur.fetchone()
        day = list(res)[-1]
    sscheduler = AsyncIOScheduler()
    sscheduler.add_job(
        show_info,
        trigger="interval",
        seconds=3600 * 24 * 5,
        kwargs={'message': message}
    )
    sscheduler.start()
    sscheduler_day = AsyncIOScheduler()
    sscheduler_day.add_job(
        show_info,
        trigger=CronTrigger(day_of_week=data_time_parsing_eg[data_time_parsing.index(day)]),
        kwargs={'message': message}
    )
    sscheduler_day.start()