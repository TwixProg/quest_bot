from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


from utils.player_utils import update_player_information, create_new_player, get_player_characteristics
from keyboards.inline import main_menu, main_menu_for_admin, get_to_main_menu
from filters.filters import check_for_admin
from db.models import Player
from bot import bot

# creating container for queries
query_id_container = {}


# start handler
async def start_command(message: types.Message, state: FSMContext = None):
    if state is not None:
        await state.finish()
    query_id_container.clear()
    mm = main_menu
    player = Player.select().where(Player.player_telegram_id == message.from_user.id)
    if player.exists():
        update_player_information(player=player, message=message)
    else:
        create_new_player(player=Player, message=message)
    fullname = message.from_user.full_name
    await message.answer(
        f'Добро пожаловать в Ратушу Дарквиля, квестоман <strong>{fullname}</strong>. Здесь ты сможешь узнать последние вести города Дарквиль')
    if check_for_admin(admin_id=message.from_user.id):
        mm = main_menu_for_admin
    await message.answer('Выберите один из пунктов меню:', reply_markup=mm)


# showing player's characteristics
async def show_player_characteristics(query: types.CallbackQuery):
    player = Player.select().where(Player.player_telegram_id == query.from_user.id)
    if player.exists():
        player = player.get()
        player_characteristics = get_player_characteristics(player=player)
        await bot.edit_message_text(text=player_characteristics, chat_id=query.message.chat.id,
                                    message_id=query.message.message_id, reply_markup=get_to_main_menu)
        await query.answer()
    else:
        await query.answer('Просим вас запустить бота командой /start и попробовать снова')


# returning to main menu
async def return_to_main_menu(query: types.CallbackQuery, state: FSMContext = None):
    if state is not None:
        await state.finish()
    query_id_container.clear()
    mm = main_menu
    if check_for_admin(admin_id=query.from_user.id):
        mm = main_menu_for_admin
    await bot.edit_message_text('Выберите один из пунктов меню:',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=mm)
    await query.answer()


def register_user_commands_callbacks(dp: Dispatcher):
    dp.register_message_handler(start_command, is_direct_start=True, commands=['start'], state='*')
    dp.register_callback_query_handler(show_player_characteristics, Text(equals='show_characteristics'), is_direct_callback=True)
    dp.register_callback_query_handler(return_to_main_menu, Text(equals='get_to_main_menu'), is_direct_callback=True, state='*')
