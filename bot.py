import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from newsapi import NewsApiClient
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
NEWS_API_KEY = os.environ.get('NEWS_API_TOKEN')

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

top_headlines = newsapi.get_top_headlines(country='ru', language='ru')
articles = top_headlines['articles']

def message_preparation(current_article): # Текста сообщения и создание кнопок
    news_message = f"<b>{articles[current_article]['title']}</b>\n{articles[current_article]['description']}\n{articles[current_article]['url']}\nСтраница {current_article}\n"
    keyboard = InlineKeyboardMarkup()
    if current_article > 0:
        keyboard.add(InlineKeyboardButton("prev", callback_data="prev"))
    if current_article < len(articles) - 1:
        keyboard.add(InlineKeyboardButton("next", callback_data="next"))
    return news_message, keyboard

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Hello! I am your NewsTelegram bot. To get started, type /news")

@dp.message_handler(commands=['news']) # Отправка статьи
async def send_news(message: types.Message):
    current_article = 0
    news_message, keyboard = message_preparation(current_article)
    await message.reply(news_message, reply_markup=keyboard, parse_mode="HTML")
    current_article += 1
        
@dp.callback_query_handler(lambda c: c.data in ["prev", "next"])
async def process_callback_pagination(callback_query: types.CallbackQuery): # Изменение статьи при клике на кнопки
    current_article = int(callback_query.message.text.split(' ')[-1])
    if callback_query.data == "prev":
        current_article -= 1
    else:
        current_article += 1
    news_message, keyboard = message_preparation(current_article)
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=news_message,
                                reply_markup=keyboard,
                                parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)