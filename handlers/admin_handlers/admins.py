from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


from states.states import FindingPlayer, ChangingSkillPoints, ChangingBalance, ChoosingQuestMenu
from keyboards.inline import admin_menu, return_to_admin_menu, quest_menu
from utils.player_utils import player_settings, skill_level_calculator
from db.models import Player
from bot import bot


# creating container for queries
query_id_container = {}  # get rid of this shit


# getting to admin menu with command
async def open_admin_menu_m(message: types.Message, state: FSMContext = None):
    if state is not None:
        await state.finish()
    query_id_container.clear()
    await message.answer(text='Выберите один из пунктов меню:',
                         reply_markup=admin_menu)


# getting to admin menu with callback
async def open_admin_menu_c(query: types.CallbackQuery, state: FSMContext = None):
    if state is not None:
        await state.finish()
    query_id_container.clear()
    await bot.edit_message_text('Выберите один из пунктов меню:',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=admin_menu)
    await query.answer()


# searching player by id (setting fsm)
async def get_player_id(query: types.CallbackQuery):
    await bot.edit_message_text('Введите id игрока, которого вы хотите найти',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_admin_menu)
    await FindingPlayer.getting_player_id.set()
    await query.answer()


# getting player id to search player
async def find_player(message: types.Message, state: FSMContext):
    player = Player.select().where(Player.player_telegram_id == message.text)
    if player.exists():
        player = player.get()
        characteristics, player_settings_buttons = player_settings(player)
        await state.finish()
        last_message = await bot.send_message(chat_id=message.chat.id,
                                              text=characteristics,
                                              reply_markup=player_settings_buttons)
        await state.update_data(message=last_message)
        await FindingPlayer.getting_player_change.set()
    else:
        await message.answer('В базе данных не было найдено игрока с таким id')


# banning player
async def ban_player(query: types.CallbackQuery):
    player_id = query.data.split('_')[-1]
    player = Player.select().where(Player.player_telegram_id == player_id).get()
    player.player_ban = True
    player.save()
    characteristics, player_settings_buttons = player_settings(player)
    await bot.edit_message_text(characteristics,
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=player_settings_buttons)
    await query.answer('✅ Игрок заблокирован')


# unbanning player
async def unban_player(query: types.CallbackQuery):
    player_id = query.data.split('_')[-1]
    player = Player.select().where(Player.player_telegram_id == player_id).get()
    player.player_ban = False
    player.save()
    characteristics, player_settings_buttons = player_settings(player)
    await bot.edit_message_text(characteristics,
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=player_settings_buttons)
    await query.answer('✅ Игрок разблокирован')


# changing player's skill points (setting fsm)
async def get_player_skill_points(query: types.CallbackQuery, state: FSMContext):
    player_id = query.data.split('_')[-1]
    await bot.edit_message_text('Введите количество очков навыка, которое вы хотите назначить игроку',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_admin_menu)
    await state.update_data(player_id=player_id)
    await ChangingSkillPoints.getting_skill_points.set()
    await query.answer()


# getting num of skill points to set to player
async def change_player_skill_points(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_message = info['message']
    player = Player.select().where(Player.player_telegram_id == info['player_id']).get()
    skill_points = int(message.text)
    level, points_to_next_level = skill_level_calculator(skill_points=skill_points)
    player.player_skill_points, player.player_skill_points_to_next_level, player.player_skill_level = skill_points, points_to_next_level, level
    player.save()
    player_characteristics, player_buttons = player_settings(player=player)
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=message.chat.id,
                                          text=player_characteristics,
                                          reply_markup=player_buttons)
    await state.update_data(message=last_message)
    await FindingPlayer.getting_player_change.set()


# changing player's balance
async def get_player_balance(query: types.CallbackQuery, state: FSMContext):
    player_id = query.data.split('_')[-1]
    await bot.edit_message_text('Введите количество баланса (опыт), которое вы хотите назначить игроку',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_admin_menu)
    await state.update_data(player_id=player_id)
    await ChangingBalance.getting_balance.set()
    await query.answer()


# getting num of balance to set to player
async def change_player_balance(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_message = info['message']
    player = Player.select().where(Player.player_telegram_id == info['player_id']).get()
    balance = int(message.text)
    player.player_balance = balance
    player.save()
    player_characteristics, player_buttons = player_settings(player=player)
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=message.chat.id,
                                          text=player_characteristics,
                                          reply_markup=player_buttons)
    await state.update_data(message=last_message)
    await FindingPlayer.getting_player_change.set()


def register_admin_commands_callbacks(dp: Dispatcher):
    dp.register_message_handler(open_admin_menu_m, admin_message=True, commands='admin', state='*')
    dp.register_callback_query_handler(open_admin_menu_c, Text(equals='admin_menu'), admin_callback=True, state='*')
    dp.register_callback_query_handler(get_player_id, Text(equals='search_player_by_id'), admin_callback=True, state='*')
    dp.register_message_handler(find_player, admin_message=True, regexp=r'\d{1,10}', state=FindingPlayer.getting_player_id)
    dp.register_callback_query_handler(ban_player, Text(startswith='ban_player_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(unban_player, Text(startswith='unban_player_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(get_player_skill_points, Text(startswith='change_player_skill_points_'), admin_callback=True, state=FindingPlayer.getting_player_change)
    dp.register_message_handler(change_player_skill_points, admin_message=True, regexp=r'\b[-+]?\d+$', state=ChangingSkillPoints.getting_skill_points)
    dp.register_callback_query_handler(get_player_balance, Text(startswith='change_player_balance_'), admin_callback=True, state=FindingPlayer.getting_player_change)
    dp.register_message_handler(change_player_balance, admin_message=True, regexp=r'\b[-+]?\d+$', state=ChangingBalance.getting_balance)
