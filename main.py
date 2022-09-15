from config import Config

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from telethon import TelegramClient, events

from multiprocessing import Process
from time import sleep
import requests

import db_functions

storage = MemoryStorage()
bot = Bot(token=Config.bot_config_token)
dp = Dispatcher(bot, storage=storage)


class AddKeywordStates(StatesGroup):
    waiting_for_keyword = State()

class RemoveKeywordStates(StatesGroup):
    waiting_for_keyword = State()

class AddUnKeywordStates(StatesGroup):
    waiting_for_un_keyword = State()

class RemoveUnKeywordStates(StatesGroup):
    waiting_for_un_keyword = State()

class AddChatStates(StatesGroup):
    waiting_for_link = State()

class RemoveChatStates(StatesGroup):
    waiting_for_link = State()


# /start
@dp.message_handler(commands=['start'])
async def start(message):
    if db_functions.register_user(chat_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name):
        db_functions.set_status_on(user_id=db_functions.get_user_id(message.from_user.id))
    await help(message)

# /stop
@dp.message_handler(commands=['stop'])
async def stop(message):
    db_functions.set_status_off(user_id=db_functions.get_user_id(message.from_user.id))


# /help
@dp.message_handler(commands=['help'])
async def help(message):
    await message.answer('/show_keywords to show keywords\n/add_keyword to add keyword\n/remove_keyword to remove keyword\n\n/add_chat to add chat', reply_markup=None)


# /show_keywords
@dp.message_handler(commands=['show_keywords'])
async def show_keywords(message):
    keywords = db_functions.get_keywords(user_id=db_functions.get_user_id(chat_id=message.from_user.id))
    if not keywords:
        await message.answer('No keywords is set. Use /add_keyword.')
    else:
        message_answer_text = ''
        for keyword in keywords:
            message_answer_text += f'`{keyword["title"]}`\n'
        await message.answer(text=message_answer_text, parse_mode='MarkDown')


# /show_un_keywords
@dp.message_handler(commands=['show_un_keywords'])
async def show_un_keywords(message):
    keywords = db_functions.get_un_keywords(user_id=db_functions.get_user_id(chat_id=message.from_user.id))
    if not keywords:
        await message.answer('No unkeywords is set. Use /add_un_keyword.')
    else:
        message_answer_text = ''
        for keyword in keywords:
            message_answer_text += f'`{keyword["title"]}`\n'
        await message.answer(text=message_answer_text, parse_mode='MarkDown')


# /add_keyword
@dp.message_handler(commands=['add_keyword'])
async def add_keyword_start(message):
    await message.answer('Enter keyword')
    await AddKeywordStates.waiting_for_keyword.set()

@dp.message_handler(state=AddKeywordStates.waiting_for_keyword)
async def add_keyword_finish(message, state):
    db_functions.add_keyword(user_id=db_functions.get_user_id(chat_id=message.from_user.id), value=message.text)
    await state.finish()
    await message.answer('Success', reply_markup=types.ReplyKeyboardRemove())


# /remove_keyword
@dp.message_handler(commands=['remove_keyword'])
async def remove_keyword_start(message):
    await show_keywords(message)
    keywords = db_functions.get_keywords(user_id=db_functions.get_user_id(chat_id=message.from_user.id))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for keyword in keywords:
        keyboard.add(keyword['title'])
    await message.answer('Select keyword', reply_markup=keyboard)
    await RemoveKeywordStates.waiting_for_keyword.set()

@dp.message_handler(state=RemoveKeywordStates.waiting_for_keyword)
async def remove_keyword_finish(message, state):
    db_functions.remove_keyword(user_id=db_functions.get_user_id(chat_id=message.from_user.id), value=message.text)
    await state.finish()
    await message.answer('Success', reply_markup=types.ReplyKeyboardRemove())


# /add_un_keyword
@dp.message_handler(commands=['add_un_keyword'])
async def add_un_keyword_start(message):
    await message.answer('Enter keyword')
    await AddUnKeywordStates.waiting_for_un_keyword.set()

@dp.message_handler(state=AddUnKeywordStates.waiting_for_un_keyword)
async def add_un_keyword_finish(message, state):
    db_functions.add_un_keyword(user_id=db_functions.get_user_id(chat_id=message.from_user.id), value=message.text)
    await state.finish()
    await message.answer('Success', reply_markup=types.ReplyKeyboardRemove())


# /remove_un_keyword
@dp.message_handler(commands=['remove_un_keyword'])
async def remove_un_keyword_start(message):
    await show_un_keywords(message)
    keywords = db_functions.get_un_keywords(user_id=db_functions.get_user_id(chat_id=message.from_user.id))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for keyword in keywords:
        keyboard.add(keyword['title'])
    await message.answer('Select keyword', reply_markup=keyboard)
    await RemoveUnKeywordStates.waiting_for_un_keyword.set()


@dp.message_handler(state=RemoveUnKeywordStates.waiting_for_un_keyword)
async def remove_un_keyword_finish(message, state):
    db_functions.remove_un_keyword(user_id=db_functions.get_user_id(chat_id=message.from_user.id), value=message.text)
    await state.finish()
    await message.answer('Success', reply_markup=types.ReplyKeyboardRemove())


# /add_chat
# @dp.message_handler(commands=['add_chat'])
# async def add_chat_enter_link(message):
#     await message.answer('Enter chat link')
#     await AddChatStates.waiting_for_link.set()


# @dp.message_handler(state=AddChatStates.waiting_for_link)
# async def add_chat_finish(message, state):
#     db_functions.add_chat(message.text)
#     await message.answer('Success')
#     await state.finish()



def run_bot_config():
    executor.start_polling(dp, skip_updates=True)



def check_message(event):
    messages_to_user = []
    keywords = db_functions.get_keywords()
    for keyword in keywords:
        if keyword['title'].lower() in event.text.lower():
            print(messages_to_user)
            messages_to_user.append({'event': event, 'user_id': keyword['user_id']})
    return messages_to_user



def run_scraper(chats):
    client = TelegramClient('Sjoic', api_id=Config.api_id, api_hash=Config.api_hash)
    client.start()

    @client.on(events.NewMessage(chats=chats))
    async def handler(event):
        messages_to_user = check_message(event)
        for message in messages_to_user:
            await client.forward_messages(db_functions.get_chat_id(user_id=message['user_id']), message['event'].message)
    client.run_until_disconnected()


def send_message(text, chat_id):
    url = f'https://api.telegram.org/bot{Config.bot_sender_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, json=data)



def main():
    Process(target=run_bot_config).start()
    # while True:
    #     process = Process(target=run_scraper, args=([element[0] for element in db_functions.get_chats()],))
    #     process.start()
    #     sleep(300)
    #     process.kill()
    run_scraper([element[0] for element in db_functions.get_chats()])

if __name__ == '__main__':
    # run_scraper([])
    main()
