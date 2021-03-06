from aiogram.dispatcher.storage import FSMContext
from telethon import TelegramClient
import logging
from config import TOKEN,  api_id, api_hash
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
clients = {}

class Telephone(StatesGroup):
    telephone = State()


class Kod(StatesGroup):
    kod = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await Telephone.telephone.set() 
    await bot.send_message(message.from_user.id, "Отправте номер телефона")


@dp.message_handler(state = Telephone.telephone)
async def proposalConfirm(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['telephone'] = message.text

    await Telephone.next()
    await Kod.kod.set() 

    clients[data['telephone']] = TelegramClient(data['telephone'], api_id, api_hash)
    
    await clients[data['telephone']].connect()
    await clients[data['telephone']].send_code_request(data['telephone'])


    await bot.send_message(message.from_user.id, 
        f"Оправте код пришедший на номер:\
        \n{data['telephone']}"
    )


@dp.message_handler(state = Kod.kod)
async def proposalConfirm(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['kod'] = message.text
        telephone = data['telephone']

    await Kod.next()
      
    
    await clients[data['telephone']].sign_up(data['kod'], first_name='анон', last_name='анон')
    clients[data['telephone']].disconnect()

    await bot.send_document(message.from_user.id, open(f'{telephone}.session', 'rb'))



if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
