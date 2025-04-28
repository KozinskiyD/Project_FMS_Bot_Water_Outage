from aiogram.utils.keyboard import InlineKeyboardBuilder

from const import data_time_parsing


def get_keyboard1(districts):
    keyboard_b = InlineKeyboardBuilder()
    for name_district in districts:
        keyboard_b.button(text=name_district, callback_data=name_district)
    keyboard_b.adjust(2, )
    return keyboard_b.as_markup()


def get_keyboard_delete_district(districts):
    keyboard_b = InlineKeyboardBuilder()
    for name_district in districts:
        keyboard_b.button(text=name_district, callback_data='удалить' + name_district)
    keyboard_b.adjust(2, )
    return keyboard_b.as_markup()


def get_keyboard2():
    keyboard_b = InlineKeyboardBuilder()
    for name_time in data_time_parsing:
        keyboard_b.button(text=name_time, callback_data=name_time)
    keyboard_b.adjust(3, )
    return keyboard_b.as_markup()
