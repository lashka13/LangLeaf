from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession 
from sqlalchemy.orm import sessionmaker 
from .models import * 
import sqlalchemy as db 
from config import DATABASE_URL # DATABASE_URL - это ссылка на подключение к бд 

# Подключаем базу данных
engine = create_async_engine(DATABASE_URL, echo=True, future=True) 
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) 


async def init_db(): 
    """
    Запускаем генерацию таблиц и при надобности заносим супер админа
    """
    async with engine.begin() as conn: 
        await conn.run_sync(Base.metadata.create_all)