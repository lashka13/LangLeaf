import os
from dotenv import load_dotenv

# Конфиг нужен для подгрузки .env в переменные, которые уже напрямую импортируются в бота и бд

load_dotenv()

# Получаем константы
DATABASE_URL = os.getenv('DATABASE_URL') 
BOT_TOKEN = os.getenv('BOT_TOKEN')