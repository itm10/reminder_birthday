import asyncio
import os
import re

from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dotenv import load_dotenv

from databases.databases import create_table_email, insert_data, create_lavozim, insert_lavozim
from dispatchers.dispatchers import dp
from states.states import DATAS

load_dotenv()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer('Xush kelibsiz botga!\nIsmingizni kiriting:')
    await state.set_state(DATAS.first_name)


@dp.message(DATAS.first_name)
async def first_name(message: Message, state: FSMContext):
    await state.update_data({
        'first_name': message.text
    })
    await message.answer('Familiyangizni kiriting: ')
    await state.set_state(DATAS.last_name)


@dp.message(DATAS.last_name)
async def last_name(message: Message, state:FSMContext):
    await state.update_data({
        'last_name': message.text
    })
    await message.answer('Lavozimingiz:')
    await state.set_state(DATAS.lavozim)


@dp.message(DATAS.lavozim)
async def lavozim(message: Message, state: FSMContext):
    await state.update_data({
        'lavozim': message.text
    })
    await message.answer("Rasmingizni jo'nating")
    await state.set_state(DATAS.image)


@dp.message(DATAS.image)
async def lavozim(message: Message, state: FSMContext):
    await state.update_data({
        'image': message.photo[-1].file_id
    })
    await message.answer("Tug'ilgan kuningizni kiriting\nFormat: YYYY-DD-MM")
    await state.set_state(DATAS.birth_day)


@dp.message(DATAS.birth_day)
async def birthday(message: Message, state: FSMContext):
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    user_id = None

    if not date_pattern.match(message.text.strip()):
        await message.answer("Iltimos shu formatda tug'ilgan kuningizni kiriting\nFormat: YYYY-DD-MM.")
        await state.set_state(DATAS.birth_day)
        return
    await state.update_data({
        'birth_day': message.text
    })
    data = await state.get_data()
    lavozim_data = data['lavozim']

    if lavozim_data == 'admin':
        user_id = message.from_user.id
    lavozim_id = insert_lavozim(dict(lavozim=data['lavozim']))
    user_data = dict(
        first_name=data['first_name'],
        last_name=data['last_name'],
        lavozim=lavozim_id,
        birth_day=data['birth_day'],
        image=data['image'],
        chat_id=user_id
    )
    insert_data(user_data)
    await state.storage.close()
    await state.clear()
    await message.answer('Jarayon muvaffaqiyatli yakunlandi!')


async def main():
    token = os.getenv('TOKEN')
    bot = Bot(token)
    create_lavozim()
    create_table_email()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())