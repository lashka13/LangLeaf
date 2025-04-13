import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.filters import StateFilter
from aiogram import F
from .text import *  # Текст на разных языках
from backend.database import init_db  # Функции бэкенда
import backend.cors as DB
from aiogram.fsm.state import State, StatesGroup
from random import choice
import deep_translator as ts

from config import BOT_TOKEN

# Инициализация бота
dp = Dispatcher()
bot = Bot(BOT_TOKEN)


class LearnState(StatesGroup):
    learn = State()
    edit_translate = State()


@dp.message(Command("start"))
async def start(message: types.Message):
    await DB.create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    await message.reply(START, parse_mode="HTML")


@dp.message(Command("learn_all"))
async def learn_all(message: types.Message, state: FSMContext):
    words = await DB.get_all_words(message.from_user.id)
    if len(words) > 0:
        words = mix_list(words)
        print(words)
        swapped = False
        await state.set_state(LearnState.learn)
        await state.set_data(
            {"words": words, "i": 0, "swap": swapped, "current_set": 0}
        )
        f_w = words[0][1] if swapped else words[0][0]
        s_w = words[0][0] if swapped else words[0][1]
        text = get_learn_text(
            {"type": "all", "set": 0}, swapped, f_w, s_w, 1, len(words)
        )
        markup = get_learn_markup(words[0][2], words[0][3])
        await message.answer(text, parse_mode="HTML", reply_markup=markup.as_markup())
    else:
        await message.reply(LEARN_ERROR)


@dp.message(Command("menu"))
async def menu(message: types.Message):
    options = await DB.get_menu(message.from_user.id)
    if options:
        words_count = await DB.get_words_count(message)
        markup = get_menu_markup(options[0].swapped, options[0].current_set)
        await message.answer_photo(
            caption=get_menu_text(options, words_count),
            photo=choice(TYLER),
            reply_markup=markup.as_markup(),
        )
    else:
        await message.reply(REGISTER_AT_FIRST)


@dp.message(Command("learn"))
async def learn(message: types.Message, state: FSMContext):
    current_set, swapped, words = await DB.get_words_by_set(message)
    if len(words) > 0:
        words = mix_list(words)
        print("WORDS!!!", words)
        await state.set_state(LearnState.learn)
        await state.set_data(
            {"words": words, "i": 0, "swap": swapped, "current_set": current_set}
        )
        f_w = words[0][1] if swapped else words[0][0]
        s_w = words[0][0] if swapped else words[0][1]
        print("LEARN END")
        text = get_learn_text(
            {"type": "set", "set": current_set}, swapped, f_w, s_w, 1, len(words)
        )
        markup = get_learn_markup(words[0][2], words[0][3])
        await message.answer(text, parse_mode="HTML", reply_markup=markup.as_markup())

    else:
        await message.reply(LEARN_ERROR)


@dp.message(Command("swap"), LearnState.learn)
async def swap_while_learning(message: types.Message, state: FSMContext):
    current_swap = (await state.get_data())["swap"]
    await DB.change_swap(message.from_user.id, current_swap)
    await state.update_data({"swap": not current_swap})
    await message.reply(swap_changed(not current_swap))


@dp.message(Command("swap"))
async def swap_not_state(message: types.Message):
    current_swap = await DB.change_swap(message.from_user.id)
    await message.reply(swap_changed(current_swap))


@dp.message(Command("list"))
async def list_words(message: types.Message):
    _, _, words = await DB.get_words_by_set(message)
    text = ""
    for word in words:
        text += word[0] + " - " + word[1] + "\n"
    await message.reply(text)


@dp.message(Command("sw_list"))
async def sw_list(message: types.Message):
    _, _, words = await DB.get_words_by_set(message)
    text = ""
    for word in words:
        text += word[1] + " - " + word[0] + "\n"
    await message.reply(text)


@dp.message(StateFilter(LearnState.edit_translate))
async def edit_translate_text(message: types.Message, state: FSMContext):
    if len(message.text) <= 150:
        data = await state.get_data()
        word_id = data["words"][data["i"]][2]
        edited_id = data["edited_id"]
        await DB.edit_translate(word_id, message.text)
        await bot.delete_message(message.from_user.id, edited_id)
        await message.reply(EDIT_SUCC)
        await state.set_state(LearnState.learn)
        await state.set_data(data)
        await send_word(message, state, True)
    else:
        await message.reply(text=EDIT_ERR)


@dp.message(Command("flags"))
async def marked_words(message: types.Message):
    words = await DB.get_marked_words(message.from_user.id)
    if len(words) > 0:
        text = ""
        for word in words:
            text += word[0].word + " - " + word[0].translated + "\n"
        await message.reply(text)
    else:
        await message.reply(NO_FLAGS)


@dp.message(Command("help"))
async def help(message: types.Message):
    await message.reply(HELP)


@dp.message(Command("delete"))
async def delete_all_words(message: types.Message):
    await message.reply(text=DELETE_TEXT, reply_markup=DELETE_MARKUP.as_markup())


@dp.message(Command("export"))
async def export_words(message: types.Message):
    words = await DB.get_all_words(message.from_user.id)
    text = ""
    with open("db.txt", "w+") as file:
        for word in words:
            file.write(
                str(word[0].id)
                + "-----"
                + str(word[0].user_id)
                + "-----"
                + word[0].word
                + "-----"
                + word[0].translated
                + "-----"
                + str(word[0].set)
                + "-----"
                + str(word[0].flag)
                + "\n"
            )


@dp.message()
async def word_handler(message: types.Message):
    try:
        len_error = False
        cur_set = await DB.get_current_set(message)
        words_count = await DB.get_words_count(message, cur_set)
        cur_word_count = len([i for i in message.text.split("\n")])

        if words_count + cur_word_count > WORDS_MAX:
            await message.reply(
                MAX_WORDS_ERROR(words_count + cur_word_count - WORDS_MAX)
            )
        else:
            msg = await message.reply(WORD_WRITING)
            for phrase in message.text.split("\n"):
                if len(phrase) > SYMB_MAX:
                    len_error = True
                    break
                else:
                    tr_word = ts.GoogleTranslator(
                        source="en", target="ru"
                    ).translate(phrase)
                    await DB.write_new_word(message.from_user.id, phrase, tr_word, cur_set)
            if len_error:
                await message.reply(LEN_ERROR(phrase))
            else:
                await bot.delete_message(message.from_user.id, msg.message_id)
                await message.reply(WORDS_INSERTED)
    except Exception as e:
        print("ERROR!!!!", e)
        await message.reply(WORDS_ERROR)


@dp.message()
async def trash(message: types.Message):
    await message.reply(TRASH)


async def send_word(
    callback: types.CallbackQuery, state: FSMContext, from_message=False
):
    data = await state.get_data()
    index = data["i"]
    swapped = data["swap"]
    words = data["words"]
    current_set = data["current_set"]
    try:
        f_w = words[index + 1][1] if swapped else words[index + 1][0]
        s_w = words[index + 1][0] if swapped else words[index + 1][1]
        if current_set == 0:
            set_type = "all"
        else:
            set_type = "set"
        text = get_learn_text(
            {"type": set_type, "set": current_set},
            swapped,
            f_w,
            s_w,
            index + 2,
            len(words),
        )
        markup = get_learn_markup(words[index + 1][2], words[index + 1][3])
        await state.update_data({"i": index + 1})
        if from_message:
            await callback.delete()
        else:
            await callback.message.delete()
        await bot.send_message(
            callback.from_user.id, text=text, reply_markup=markup.as_markup(), parse_mode="HTML"
        )
    except IndexError:
        await state.clear()
        if from_message:
            await callback.reply(FINISHED)
        else:
            await callback.message.reply(FINISHED)


@dp.callback_query(F.data == "swap_menu")
async def swap_menu(callback: types.CallbackQuery):
    current_swap = await DB.change_swap(callback.from_user.id)
    options = await DB.get_menu(callback.from_user.id)
    markup = get_menu_markup(current_swap, options[0].current_set)
    await callback.message.edit_reply_markup(reply_markup=markup.as_markup())


@dp.callback_query(F.data == "delete_all_words")
async def delete_words_call(callback: types.CallbackQuery):
    await DB.delete_all_words(callback.from_user.id)
    await callback.message.reply(DELETE_SUCC)


@dp.callback_query(F.data == "swap", StateFilter(LearnState.learn))
async def swap_learning(callback: types.CallbackQuery, state: FSMContext):
    current_swap = (await state.get_data())["swap"]
    await DB.change_swap(callback.from_user.id, current_swap)
    await state.update_data({"swap": not current_swap})
    await send_word(callback, state)


@dp.callback_query(F.data == "next_word", StateFilter(LearnState.learn))
async def next_word(callback: types.CallbackQuery, state: FSMContext):
    await send_word(callback, state)


@dp.callback_query(
    lambda callback: callback.data.startswith("delete_choice_"), StateFilter(LearnState.learn)
)
async def delete_choice(callback: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        DELETE_WORD_TEXT, callback.from_user.id, callback.message.message_id
    )
    word_id = int(callback.data.split("_")[2])
    markup = get_delete_word_markup(word_id)
    await bot.edit_message_reply_markup(
        callback.from_user.id, callback.message.message_id, reply_markup=markup.as_markup()
    )


@dp.callback_query(
    lambda callback: callback.data.startswith("delete_word_"), StateFilter(LearnState.learn)
)
async def delete_word_callback(callback: types.CallbackQuery, state: FSMContext):
    await DB.delete_word(int(callback.data.split("_")[2]))
    await send_word(callback, state)


@dp.callback_query(F.data == "edit_translate", StateFilter(LearnState.learn))
async def edit_translate(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data["edited_id"] = callback.message.message_id
    await state.set_state(LearnState.edit_translate)
    await state.set_data(data)
    await callback.message.reply(EDIT_TRANSLATE_TEXT, reply_markup=EDIT_BUTTON.as_markup())


@dp.callback_query(F.data == "back_to_learn", StateFilter(LearnState.edit_translate))
async def back_to_learn(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    edited_id = data["edited_id"]
    await bot.delete_message(callback.from_user.id, edited_id)
    await state.set_state(LearnState.learn)
    await state.set_data(data)
    await send_word(callback, state)


@dp.callback_query(
    lambda callback: callback.data.startswith("flag_"), LearnState.learn
)
async def mark_words(callback: types.CallbackQuery, state: FSMContext):
    new_flag = await DB.mark_word(int(callback.data.split("_")[1]))
    data = await state.get_data()
    index = data["i"]
    words = data["words"]
    markup = get_learn_markup(words[index][2], new_flag)
    await bot.edit_message_reply_markup(
        chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=markup.as_markup()
    )


@dp.callback_query(lambda callback: callback.data.startswith("set_cur_state_"))
async def change_current_set_btn(callback: types.CallbackQuery):
    await DB.set_new_current_set(callback)
    await callback.message.reply(SET_SUCCESS)


@dp.callback_query(F.data == "stop_learning", StateFilter(LearnState.learn))
async def stop_learning(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(STOPPED)


@dp.callback_query(F.data == "change_set")
async def change_set(callback: types.CallbackQuery):
    await callback.message.delete()
    sets = await DB.get_sets(callback.from_user.id)
    markup = get_sets_markup(sets)
    await callback.message.answer_photo(
        caption=CHANGE_CURRENT_STATE, photo=choice(TYLER), reply_markup=markup.as_markup()
    )


@dp.callback_query(F.data == "add_new_set")
async def add_new_set(callback: types.CallbackQuery):
    res = await DB.add_new_set(callback)
    if res == 0:
        await callback.message.reply(SET_ADD)
    elif res == 1:
        await callback.message.reply(SET_ERROR)
    elif res == 2:
        await callback.message.reply(SET_2_ERROR)


async def main() -> None:
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
