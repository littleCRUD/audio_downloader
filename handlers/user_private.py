import asyncio
from aiogram import F, types, Router, Bot
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums.chat_action import ChatAction
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InputMediaPhoto, FSInputFile
from filters.chat_types import ChatTypeFilter
from kbds.inline import get_callback_btns
from subproc.converter import dowmload_audio



user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))



MAIN_KB = get_callback_btns(
        btns={"Скачать файл": "get_mp4_audio", 
              "Описание": "about_"}, sizes=(2,)
    )

# Ловим команду старт и отвечаем основным меню
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    if state:
        await state.clear()
    await message.answer_photo(
        photo="https://disk.yandex.ru/i/Qyrd_DlJsx8qkA",
        caption="<strong>Добро пожаловать в Youtube audio downloader!</strong>",
        reply_markup=MAIN_KB,
    )


# Ловим callback описание
@user_private_router.callback_query(StateFilter(None), F.data.startswith("about"))
async def about_menu(callback: types.CallbackQuery):
    caption = as_list(
        as_marked_section(
            Bold("Бот умеет:"),
            "Загружать аудио из видео Youtube по ссылке",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Ограничения:"),
            "Итоговый файл аудио не должен превышать 50МБ  ",
            marker="❌ ",
        ),
        sep="\n----------------------\n",
    ).as_html()

    image = InputMediaPhoto(
        media=callback.message.photo[0].file_id,
        caption=caption,
    )
    reply_murkup = get_callback_btns(btns={"Назад": "back_home_"}, sizes=(2,))
    await callback.message.edit_media(media=image, reply_markup=reply_murkup)
    await callback.answer()

# Ловим callback назад
@user_private_router.callback_query(StateFilter(None), F.data.startswith("back_home_"))
async def back_home(callback: types.CallbackQuery):
    image = InputMediaPhoto(
        media=callback.message.photo[0].file_id,
        caption="<strong>Добро пожаловать в Youtube audio downloader!</strong>",
    )
    await callback.message.edit_media(media=image, reply_markup=MAIN_KB)
    await callback.answer()


###################Микро FSM для загрузки аудио#############################


class GetAudio(StatesGroup):
    "Шаги загрузки аудио"
    add_url_mp4 = State()


# Ловим callback скачать файл
@user_private_router.callback_query(
    StateFilter(None), F.data.startswith("get_mp4_audio")
)
async def add_url_mp4(callback: types.CallbackQuery, state: FSMContext):
    if callback.message.photo:
        image = InputMediaPhoto(
            media=callback.message.photo[0].file_id,
            caption="",
        )
        await callback.message.edit_media(media=image)
    await callback.message.answer("Введите ссылку на видео из Youtube ⏬")
    await callback.answer()
    await state.set_state(GetAudio.add_url_mp4)


# Ловим ссылку на видео
@user_private_router.message(StateFilter(GetAudio.add_url_mp4), F.text)
async def download_audio_mp4(message: types.Message, state: FSMContext, bot: Bot):
    await asyncio.sleep(1)
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    message_id = message.message_id
    reply_markup=get_callback_btns(
                    btns={
                        "Скачать другой файл": "get_mp4_audio",
                        "На главную страницу": "to_home_",
                    }
                )
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.UPLOAD_DOCUMENT,
    )
    await message.answer("Скачиваю файл, это займет некоторое время.....")
    sender = ChatActionSender.upload_document(
        bot=message.bot,
        chat_id=message.chat.id,
    )
    async with sender:
        try:
            audio, title = await dowmload_audio(message.text)
            audio_file = FSInputFile(path=audio, filename=f"{title}.mp4")
            await message.answer_document(document=audio_file)
            await message.answer(
                text="ОК, вот ваш файл, приятного прослушивания 🎧",
                reply_markup=reply_markup,
            )
        except Exception as err:
            if type(err).__name__ == "RegexMatchError":
                await message.answer('Введите корректную ссылку на видео из Youtube ⏬')
                await bot.delete_message(chat_id=message.chat.id, message_id=message_id + 1)
                return
            else:
                await bot.delete_message(chat_id=message.chat.id, message_id=message_id + 1)
                await message.answer(
                    text='При отправке файла произошла ошибка 😪',
                    reply_markup=reply_markup,
                    )
                await state.clear()
                return
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id + 1)
    await state.clear()

# Ловим Callback возврата на главую страницу
@user_private_router.callback_query(StateFilter(None), F.data.startswith("to_home_"))
async def go_to_home(callback: types.CallbackQuery):
    await callback.message.answer_photo(
        photo="https://disk.yandex.ru/i/Qyrd_DlJsx8qkA",
        caption="<strong>Добро пожаловать в Youtube audio downloader!</strong>",
        reply_markup=MAIN_KB,
    )
    await callback.answer()
