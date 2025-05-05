from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_keyboard_add_district(districts):
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


def get_keyboard_update_time(times):
    keyboard_b = InlineKeyboardBuilder()
    for name_time in times:
        keyboard_b.button(text=name_time, callback_data='изменить' + name_time)
    keyboard_b.adjust(3, )
    return keyboard_b.as_markup()
