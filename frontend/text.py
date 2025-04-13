from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random


# Constants
WORDS_MAX = 100
SET_MAX = 30
SYMB_MAX = 100


# Messages
START = '''Привет! Я помогу тебе выучить английский язык. 
Просто отправь мне список слов на английском и я сам их переведу.

Например, попробуй отправить эти слова (можешь скопировать их):
<code>
coincidence
insufficient
acclaim
magnificient
accommodate
</code>
'''

REGISTER_AT_FIRST = 'Сначала зарегистрируйся, потом хуйнёй своей майся'
TRASH = 'Ну и к чему ты это высрал'
WORDS_INSERTED = 'Слова были успешно внесены, хотя лучше бы ты был успешным'
WORDS_ERROR = 'Что-то пошло не по плану('
CHANGE_CURRENT_STATE = 'Выбери сэт, на который хочешь поменять нынешний'
SET_SUCCESS = 'Сэт был успешно изменён тварь'
SET_ADD = 'Сэт был успешно добавлен урод'
SET_ERROR = 'Больно много сэтов хочешь сука'
SET_2_ERROR = 'Перед добавлением сэта напиши хотя бы одно слово'
LEARN_ERROR = 'Добавь хотя бы одно слово перед изучением'
FINISHED = 'Слова закончились тварь'
STOPPED = 'Ну ты и позорище'
EDIT_TRANSLATE_TEXT = 'Отправь свой вариант перевода'
EDIT_SUCC = 'Перевод был исправлен'
EDIT_ERR = 'Перевод должен быть умещён в 150 символов'
NO_FLAGS = 'У тебя нет помеченных слов'
DELETE_TEXT = 'Нажав на кнопку ты удалишь ВСЕ слова из всех сэтов, которые ты загрузил'
DELETE_SUCC = 'Слова были успешно удалены((('
WORD_WRITING = 'Слова обрабатываются...'
DELETE_WORD_TEXT = 'Ты действительно хочешь удалить это слово?'


# Tyler images
TYLER = [
    'https://yt3.ggpht.com/ytc/AKedOLTJFIX-7xrpMVyULJOJf2sqiwn9PRSiyrEIZC3y=s900-c-k-c0x00ffffff-no-rj',
    'https://imgix.bustle.com/rehost/2016/9/13/1fc6cd08-6bab-421b-908b-3253c18bd893.jpg?w=800&fit=crop&crop=faces&auto=format%2Ccompress&q=50&dpr=2',
    'https://yt3.ggpht.com/ytc/AKedOLTmUwY70GypVfoCJVO6RE33Tm-93wb0Jjwn9YH09g=s900-c-k-c0x00ffffff-no-rj',
    'https://wikiwarriors.org/mediawiki/images/thumb/a/ad/Deathofkevincrow.jpg/1200px-Deathofkevincrow.jpg',
    'https://phonoteka.org/uploads/posts/2022-09/1662151094_5-phonoteka-org-p-tailer-derden-oboi-pinterest-5.jpg',
    'https://u.livelib.ru/character/1000000242/o/76uchx3w/1394421836409-o.jpeg',
    'https://i.pinimg.com/originals/22/d3/63/22d3637fd04754eaefb1cbe4ace632d4.jpg'
]


# Markups
DELETE_MARKUP = InlineKeyboardBuilder()
DELETE_MARKUP.add(InlineKeyboardButton(text='💔 Удалить слова', callback_data='delete_all_words'))

EDIT_BUTTON = InlineKeyboardBuilder()
EDIT_BUTTON.add(InlineKeyboardButton(text='Вернуться к изучению', callback_data='back_to_learn'))

STOP_EDITING = InlineKeyboardBuilder()
STOP_EDITING.add(InlineKeyboardButton(text='Продолжить обучение', callback_data='continue_learning'))

# Functions
def get_menu_text(options, words):
    return f'''👤 Имя: {options[0].first_name}
🩸 Слов: {words}'''


def LEN_ERROR(phrase):
    return f'Во фразе {phrase[:20]}... превышено количество допустимых символов (больше ста нельзя)'


def MAX_WORDS_ERROR(change):
    if change == 1:
        return f'''Ты больше не можешь добавлять слова в этот сэт, твой лимит кончился, но не время паниковать,
        ущербный. Ты можешь либо создать новый сэт (максимум {SET_MAX}), либо удалить слова из этого сэта'''
    else:
        return f'Ты отправил слишком много слов, отправь на {change} меньше или создай новый сэт'


def get_menu_markup(swapped, cur_set):
    buttons = InlineKeyboardBuilder()
    buttons.add(InlineKeyboardButton(text=f'🪓 Текущий сэт: {cur_set}', callback_data='change_set'))
    buttons.add(InlineKeyboardButton(text=f"🌱 RU-EN: {'Да' if swapped else 'Нет'}", callback_data='swap_menu'))
    return buttons


def get_sets_markup(sets):
    buttons = InlineKeyboardBuilder()
    sets = [sets[i:i + 3] for i in range(0, len(sets), 3)]
    for set_group in sets:
        buttons.row(*[InlineKeyboardButton(text=str(i), callback_data=f'set_cur_state_{i}') for i in set_group])
    buttons.row(InlineKeyboardButton(text='➕ Добавить новый сэт', callback_data='add_new_set'))
    return buttons


def mix_list(list_original):
    list = list_original[:]
    list_length = len(list)
    for i in range(list_length):
        index_aleatory = random.randint(0, list_length - 1)
        temp = list[i]
        list[i] = list[index_aleatory]
        list[index_aleatory] = temp
    return list


def get_learn_text(group, swapped, word, translated, index, words_count):
    if group['type'] == 'set':
        group = f'сэт № {group["set"]}'
    elif group['type'] == 'all':
        group = 'все слова'
    return f"""Текущий набор: <b>{group}</b>
RU-EN: <b>{'Да' if swapped else 'Нет'}</b>
Слов: <b>{index}/{words_count}</b>
➖➖➖➖➖➖
{word}
➖➖➖➖➖➖
<span class='tg-spoiler'>{translated}</span>"""


def get_learn_markup(word_id, flag):
    buttons = InlineKeyboardBuilder()
    buttons.row(InlineKeyboardButton(text='Следующее слово ➡️', callback_data='next_word'))
    buttons.row(
        InlineKeyboardButton(text='Удалить 😈', callback_data=f'delete_choice_{word_id}'),
        InlineKeyboardButton(text='Свап 💫', callback_data='swap'),
        InlineKeyboardButton(text='🚩' if flag else '🏳️', callback_data=f'flag_{word_id}'),
    )
    buttons.row(InlineKeyboardButton(text='❌ Остановиться (если чмо)', callback_data='stop_learning'))
    buttons.row(InlineKeyboardButton(text='🐡 Скорректировать перевод', callback_data=f'edit_translate'))
    return buttons


def swap_changed(after):
    return f"RU-EN режим {'включен' if after else 'выключен'}"


def get_delete_word_markup(word_id):
    DELETE_WORD_MARKUP = InlineKeyboardBuilder()
    DELETE_WORD_MARKUP.add(InlineKeyboardButton(text='Удалить', callback_data=f'delete_word_{word_id}'))
    DELETE_WORD_MARKUP.add(InlineKeyboardButton(text='Оставить', callback_data=f'next_word'))
    return DELETE_WORD_MARKUP


# Help message
HELP = f"""Этот бот создан, чтобы ты, ублюдок, cмог науиться спокойно разговаривать на английском языке.
Только ты и никто другой не может этого сделать за тебя, этот бот может лишь помочь тебе это сделать.
Схема очень простая: ты просматриваешь всевозможные ресурсы на английском языке (фильмы, сайты, книги)
на ТВОЁМ уровне и отправляешь в бота слова и выражения, которые тебе не известны. Если хочешь сразу загрузить
пачку слов пиши их черех Enter. В боте предусмотрена система сэтов, всего у одного пользователя может
быть {SET_MAX} сэтов, в каждом из которых {WORDS_MAX} слов, в которых максимум {SYMB_MAX} символов. Например: 
ты внёс в первый сэт 40 слов и через некоторое время ты их досканально выучил, потом ты хочешь загрузить 
ещё 40 слов, но когда ты будешь учить уже новые слова, старые слова будут лишь мешать процессу, поэтому 
эти новые слова лучше поместить в отдельный сэт, чтобы старые слова не мешались. Ещё тебе может пригодиться список 
комманд:
/menu - вызвать меню
/learn - начать обучение
/flags - вывести список отмеченных слов. Слова ты можешь отмечать во время обучения, нажав на белый флажок
/list - список слов EN-RU
/sw_list - список слов RU-EN
/swap - поменять режим обучения
/delete - удалить все слова"""

DELETE_TEXT = 'Нажав на кнопку ты удалишь ВСЕ слова из всех сэтов, которые ты загрузил'
DELETE_MARKUP = InlineKeyboardBuilder()
DELETE_MARKUP.add(InlineKeyboardButton(text='💔 Удалить слова', callback_data='delete_all_words'))
DELETE_SUCC = 'Слова были успешно удалены((('
EDIT_BUTTON = InlineKeyboardBuilder()
EDIT_BUTTON.add(InlineKeyboardButton(text='Вернуться к изучению', callback_data='back_to_learn'))
WORD_WRITING = 'Слова обрабатываются...'
DELETE_WORD_TEXT = 'Ты действительно хочешь удалить это слово?'

def get_delete_word_markup(word_id):
    DELETE_WORD_MARKUP = InlineKeyboardBuilder()
    DELETE_WORD_MARKUP.add(InlineKeyboardButton(text='Удалить', callback_data=f'delete_word_{word_id}'))
    DELETE_WORD_MARKUP.add(InlineKeyboardButton(text='Оставить', callback_data=f'next_word'))
    return DELETE_WORD_MARKUP