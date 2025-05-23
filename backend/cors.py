from sqlalchemy import select, and_, update, delete
from backend.models import User, Word, Set
from backend.database import async_session_maker
from aiogram import types


async def create_user(
    user_id: int, username: str, first_name: str, last_name: str
) -> None:
    """
    Создаём запись пользователя
    """
    async with async_session_maker() as session:
        query = select(User.id).where(User.id == user_id)
        res = (await session.execute(query)).fetchone()
        if not res:
            user_object = User(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(user_object)
            await session.commit()


async def get_menu(user_id: int) -> User:
    """
    Получаем информацию о пользователе
    """
    async with async_session_maker() as session:
        query = select(User).where(User.id == user_id)
        res = (await session.execute(query)).fetchone()
        return res


async def get_current_set(message: types.Message) -> int:
    """
    Получаем текущий набор слов пользователя
    """
    async with async_session_maker() as session:
        query = select(User.current_set).where(User.id == message.from_user.id)
        return (await session.execute(query)).fetchone()[0]


async def write_new_word(user: int, word: str, translated: str, cur_set: int) -> None:
    """
    Добавляем новое слово в базу данных
    """
    async with async_session_maker() as session:
        word = Word(user_id=user, word=word, translated=translated, set=cur_set)
        session.add(word)
        await session.commit()


async def get_words_count(message: types.Message, cur_set: int = None) -> int:
    """
    Получаем количество слов пользователя
    """
    async with async_session_maker() as session:
        if cur_set:
            query = select(Word).where(
                and_(Word.user_id == message.from_user.id, Word.set == cur_set)
            )
        else:
            query = select(Word).where(Word.user_id == message.from_user.id)
        res = (await session.execute(query)).fetchall()
        return len(res)


async def get_sets(user_id: int) -> list:
    """
    Получаем список наборов слов пользователя
    """
    async with async_session_maker() as session:
        query = select(Set).where(Set.user_id == user_id)
        res = (await session.execute(query)).fetchall()
        return res


async def set_new_current_set(callback: types.CallbackQuery) -> None:
    """
    Устанавливаем новый текущий набор слов
    """
    async with async_session_maker() as session:
        new_set = callback.data.split("_")[3]
        stmt = (
            update(User)
            .where(User.id == callback.from_user.id)
            .values({"current_set": int(new_set)})
        )
        await session.execute(stmt)
        await session.commit()


async def add_new_set(user_id: int, title: str) -> int:
    """
    Добавляем новый набор слов
    """
    async with async_session_maker() as session:
        sets = await get_sets(user_id)
        if len(sets) < 10:
            try:
                stmt = (
                    update(User)
                    .where(User.id == user_id)
                    .values({"current_set": len(sets) + 1})
                )
                await session.execute(stmt)
                await session.commit()
                new_set_id = len(sets) + 1

                new_set = Set(user_id=user_id, title=title, set_id=new_set_id)
                session.add(new_set)
                await session.commit()

                return 0
            except IndexError:
                return 2
        return 1


async def get_words_by_set(message: types.Message) -> tuple:
    """
    Получаем слова из текущего набора
    """
    async with async_session_maker() as session:
        query = select(User).where(User.id == message.from_user.id)
        res = (await session.execute(query)).fetchone()
        set_id = res[0].current_set
        swapped = res[0].swapped
        query = select(
            Word.word, Word.translated, Word.id, Word.flag, Word.definitions
        ).where(and_(Word.user_id == message.from_user.id, Word.set == set_id))
        return set_id, swapped, (await session.execute(query)).fetchall()


async def delete_word(word_id: int) -> None:
    """
    Удаляем слово из базы данных
    """
    async with async_session_maker() as session:
        stmt = delete(Word).where(Word.id == word_id)
        await session.execute(stmt)
        await session.commit()


async def change_swap(user_id: int, current_swap: bool = None) -> bool:
    """
    Меняем режим отображения слов
    """
    async with async_session_maker() as session:
        if current_swap == None:
            query = select(User.swapped).where(User.id == user_id)
            current_swap = (await session.execute(query)).fetchone()[0]
        stmt = (
            update(User).where(User.id == user_id).values({"swapped": not current_swap})
        )
        await session.execute(stmt)
        await session.commit()
        return not current_swap


async def mark_word(word_id: int) -> bool:
    """
    Отмечаем слово флагом
    """
    async with async_session_maker() as session:
        query = select(Word.flag).where(Word.id == word_id)
        res = (await session.execute(query)).fetchone()[0]
        stmt = update(Word).where(Word.id == word_id).values({"flag": not res})
        await session.execute(stmt)
        await session.commit()
        return not res


async def get_marked_words(user_id: int) -> list:
    """
    Получаем отмеченные слова
    """
    async with async_session_maker() as session:
        query = select(Word).where(and_(Word.user_id == user_id, Word.flag == True))
        return (await session.execute(query)).fetchall()


async def edit_translate(word_id: int, translated: str) -> None:
    """
    Редактируем перевод слова
    """
    async with async_session_maker() as session:
        stmt = update(Word).where(Word.id == word_id).values({"translated": translated})
        await session.execute(stmt)
        await session.commit()


async def delete_all_words(user_id: int) -> None:
    """
    Удаляем все слова пользователя, меняем текущий набор на первый, удаляем остальные наборы
    """
    async with async_session_maker() as session:
        stmt = delete(Word).where(Word.user_id == user_id)
        stmt_2 = delete(Set).where(and_(Set.user_id == user_id, Set.set_id != 1))
        stmt_3 = update(User).where(User.id == user_id).values({"current_set": 1})
        await session.execute(stmt)
        await session.execute(stmt_2)
        await session.execute(stmt_3)
        await session.commit()


async def get_all_words(user_id: int) -> list:
    """
    Получаем все слова пользователя
    """
    async with async_session_maker() as session:
        query = select(Word).where(Word.user_id == user_id)
        return (await session.execute(query)).fetchall()


async def add_definitions(word_id: int, definitions: str) -> None:
    """
    Добавляем определения к слову
    """
    async with async_session_maker() as session:
        stmt = (
            update(Word).where(Word.id == word_id).values({"definitions": definitions})
        )
        await session.execute(stmt)
        await session.commit()


async def get_users():
    """
    Получаем всех пользователей
    """
    async with async_session_maker() as session:
        query = select(User)
        return (await session.execute(query)).fetchall()
