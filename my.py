import logging
import asyncio
import sys
import json
import re
from aiogram import (Bot, Router, types, Dispatcher)
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)

tg_bot_token = '6968773120:AAE5y6SrhjTL8Y08HWAHf5z6oDRfYE-uNpo'
admin_id = '6013699226'

bot = Bot(tg_bot_token)
root_router = Router()

banned_users_file = 'banned_users.json'
banned_user_ids = set()

users_data_file = 'users_data.json'
users_data = {}

text = '...'


async def load_banned_users():
    global banned_user_ids
    try:
        with open(banned_users_file, 'r') as file:
            banned_user_ids = set(json.load(file))
    except FileNotFoundError:
        banned_user_ids = set()


async def save_banned_users():
    with open(banned_users_file, 'w') as file:
        json.dump(list(banned_user_ids), file)


async def load_users_data():
    global users_data
    try:
        with open(users_data_file, 'r') as file:
            users_data = json.load(file)
    except FileNotFoundError:
        users_data = {}


async def save_users_data():
    with open(users_data_file, 'w') as file:
        json.dump(users_data, file)


async def initialize():
    await load_banned_users()
    await load_users_data()


async def check_ban(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_user_ids:
        await message.answer("Вы заблокированы администратором.")
        return False
    return True


async def save_user_data(user: types.User):
    user_info = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name
    }
    users_data[user.id] = user_info
    await save_users_data()


def parse_command_args(command_text):
    parts = command_text.split(maxsplit=2)
    if len(parts) != 3:
        return None, None
    try:
        user_id = int(parts[1])
    except ValueError:
        return None, None
    return user_id, parts[2]


@root_router.message(CommandStart())
async def start(message: types.Message):
    if not await check_ban(message):
        return

    await save_user_data(message.from_user)

    user = message.from_user
    first_name = user.first_name if user.first_name else "Unknown"
    await message.answer(f'Привет, {first_name}! {text}',
                         reply_markup=types.ReplyKeyboardMarkup(
                             keyboard=[
                                 [types.KeyboardButton(text='Выбрать категорию'),
                                  types.KeyboardButton(text='Ознакомиться с материалами')]
                             ],
                             resize_keyboard=True
                         ))


@root_router.message(lambda message: message.text == 'Выбрать категорию')
async def msg_with_ctgs(message: types.Message):
    if not await check_ban(message):
        return

    await message.answer('Все категории:',
                         reply_markup=types.ReplyKeyboardMarkup(
                             keyboard=[
                                 [types.KeyboardButton(text='Категория 1'),
                                  types.KeyboardButton(text='Категория 2')]
                             ],
                             resize_keyboard=True
                         ))


@root_router.message(lambda message: message.text == 'Ознакомиться с материалами')
async def msg_to_admin(message: types.Message):
    if not await check_ban(message):
        return

    await message.answer('Канал для ознакомления с материалами - ')
    await save_user_data(message.from_user)

    user_id = message.from_user.id
    user_category = "Ознакомление с материалами"
    await send_approval_request(user_id, user_category)


async def send_approval_request(user_id: int, category: str):
    username = users_data[user_id].get('username', 'Unknown')


@root_router.message(lambda message: message.text == 'Категория 1')
async def msg_to_admin_category_1(message: types.Message):
    if not await check_ban(message):
        return

    await save_user_data(message.from_user)
    user_id = message.from_user.id
    await send_approval_request(user_id, 'Категория 1')

    user = message.from_user
    username = user.username if user.username else "Unknown"
    first_name = user.first_name if user.first_name else 'Unknown'
    await bot.send_message(admin_id, f'Новый пользователь!\n\n'
                                     f'<b>{"username":5}</b> | <b>{"ID":<15}</b> | <b>{"name":<7}</b> | <b>{"category":<9}</b>\n'
                                     f'@{username} | {user.id:<10} | {first_name:<10} | категория 1',
                           parse_mode=ParseMode.HTML)


@root_router.message(lambda message: message.text == 'Категория 2')
async def msg_to_admin_category_2(message: types.Message):
    if not await check_ban(message):
        return

    await save_user_data(message.from_user)
    user_id = message.from_user.id
    await send_approval_request(user_id, 'Категория 2')

    user = message.from_user
    username = user.username if user.username else "Unknown"
    first_name = user.first_name if user.first_name else 'Unknown'
    await bot.send_message(admin_id, f'Новый пользователь!\n\n'
                                     f'<b>{"username":5}</b> | <b>{"ID":<15}</b> | <b>{"name":<7}</b> | <b>{"category":<9}</b>\n'
                                     f'@{username} | {user.id:<10} | {first_name:<10} | категория 2',
                           parse_mode=ParseMode.HTML)


# @root_router.message(Command('ban_list'))
# async def ban_list(message: types.Message):
#     if message.from_user.id != int(admin_id):
#         return
#
#     await load_banned_users()
#     if banned_user_ids:
#         banned_users_info = []
#         for user_id in banned_user_ids:
#             try:
#                 user_info = users_data.get(user_id, {})
#                 banned_users_info.append(f'{"":<3}{"username":<10} | {"ID":<19} | {"name":<7}\n'
#                                          f'@{user_info.get("username", "Unknown"):<10} | {user_info.get("id", "Unknown"):<15} | {user_info.get("first_name", "Unknown"):<7}')
#             except Exception as e:
#                 print(f"Ошибка при получении информации о пользователе с ID {user_id}: {e}")
#         if banned_users_info:
#             await message.answer(
#                 "Забаненные пользователи:\n\n" + banned_users_info[0] + "\n\n" + "\n\n".join(banned_users_info[1:]))
#         else:
#             await message.answer("Список забаненных пользователей пуст.")
#     else:
#         await message.answer("Список забаненных пользователей пуст.")


@root_router.message(Command('ban'))
async def ban_user(message: types.Message):
    if not await check_ban(message):
        return

    if message.from_user.id != int(admin_id):
        return

    if not message.text:
        await message.answer("Пожалуйста, укажите айди(ы) пользователей, которых вы хотите заблокировать.")
        return

    user_ids = re.findall(r'\d+', message.text)
    if not user_ids:
        await message.answer("Неверный формат айди пользователей.")
        return

    for user_id in user_ids:
        try:
            user_id = int(user_id)
            if user_id != int(admin_id):
                banned_user_ids.add(user_id)
            else:
                await message.answer("Нельзя забанить администратора.")
        except ValueError:
            await message.answer(f"Неверный формат айди: {user_id}.")
            continue

    await save_banned_users()
    await message.answer(f'Пользователи с ID {", ".join(str(user_id) for user_id in user_ids)} заблокированы.')


@root_router.message(Command('unban'))
async def unban_user(message: types.Message):
    if not await check_ban(message):
        return

    if message.from_user.id != int(admin_id):
        return

    user_id = re.search(r'/unban (\d+)', message.text)
    if user_id:
        user_id = int(user_id.group(1))
        if user_id in banned_user_ids:
            banned_user_ids.remove(user_id)
            await save_banned_users()
            await message.answer(f'Пользователь с ID {user_id} разблокирован.')
        else:
            await message.answer(f'Пользователь с ID {user_id} не был заблокирован.')
    else:
        await message.answer("Пожалуйста, укажите айди пользователя в формате /unban user_id.")


@root_router.message(Command('users_list'))
async def users_list(message: types.Message):
    if message.from_user.id != int(admin_id):
        return

    await load_users_data()
    await load_banned_users()

    print("Loaded users data:", users_data)
    print("Banned user IDs:", banned_user_ids)

    users_info = []
    for user_id, user_info in users_data.items():
        user_id = message.from_user.id
        status = "ЗАБАНЕН" if user_id in banned_user_ids else "НЕ ЗАБАНЕН"
        users_info.append(f'{"":<3}{"username":<10} | {"ID":<19} | {"name":<7} | {"status":<7}\n'
                          f'@{user_info.get("username", "Unknown"):<10} | {user_info.get("id", "Unknown"):<15} | {user_info.get("first_name", "Unknown"):<7} | {status:<7}')

    if users_info:
        await message.answer(
            "Пользователи:\n\n" + users_info[0] + "\n\n" + "\n\n".join(users_info[1:]))
    else:
        await message.answer("Список пользователей пуст.")


@root_router.message(Command('yes'))
async def approve_request(message: types.Message):
    if message.from_user.id != int(admin_id):
        return

    user_id, category = parse_command_args(message.text)
    if user_id is None or category is None:
        await message.answer("Неверный формат команды. Используйте /yes user_id category.")
        return

    username = users_data.get(user_id, {}).get('username', 'Unknown')
    await bot.send_message(user_id,
                           f"Ваш запрос одобрен администратором. Для покупки/связи свяжитесь с @{message.from_user.username}")
    await message.answer(f"Запрос пользователя @{username} на категорию '{category}' одобрен.")


@root_router.message(Command('no'))
async def reject_request(message: types.Message):
    if message.from_user.id != int(admin_id):
        return

    user_id, category = parse_command_args(message.text)
    if user_id is None or category is None:
        await message.answer("Неверный формат команды. Используйте /no user_id category.")
        return

    username = users_data.get(user_id, {}).get('username', 'Unknown')
    await bot.send_message(user_id,
                           f"Ваш запрос на категорию '{category}' отклонен администратором ")
    await message.answer(f"Запрос пользователя @{username} на категорию '{category}' отклонен.")


async def main():
    await initialize()

    bot = Bot(tg_bot_token)
    dp = Dispatcher()
    dp.include_router(root_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
