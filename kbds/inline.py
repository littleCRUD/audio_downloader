from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



# Функция создания обычной inline клавиатуры с минимальным набором параметров
def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    """
    Пример:
        get_callback_btns(
        btns={
            "Удалить": f"delete_",
            "Изменить": f"change_",
            },
            sizes=(2,)
        )
    """
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()
