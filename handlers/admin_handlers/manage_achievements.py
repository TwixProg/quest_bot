from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from keyboards.inline import achievement_menu_settings, return_to_achievement_menu
from states.states import AchievementCreating, AchievementNameChanging
from utils.quest_utils import achievement_info
from db.models import Achievement, MainQuest
from bot import bot


# creating container for queries
query_id_container = {}  # get rid of this shit


# open achievement menu
async def achievement_menu(query: types.CallbackQuery, state: FSMContext = None):
    if state is not None:
        await state.finish()
    query_id_container.clear()
    await bot.edit_message_text('Выберите один из пунктов меню',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=achievement_menu_settings)
    await query.answer()


# creating achievement
async def create_achievement(query: types.CallbackQuery):
    await bot.edit_message_text('Введите название нового достижения',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_achievement_menu)
    await AchievementCreating.getting_achievement_name.set()
    query_id_container['query'] = query
    await query.answer()


# get the name of the achievement and set it
async def getting_achievement_name(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer('Лимит 100 символов')
        return 0
    query = query_id_container['query']
    await state.update_data(achiev_name=message.text)
    await bot.edit_message_text('Создайте 6-ти значный уникальный код',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_achievement_menu)
    await AchievementCreating.next()


# get the achievement's shortcut-code
async def getting_achievement_shortcut(message: types.Message, state: FSMContext):
    if len(message.text) > 6:
        await message.answer('Лимит 6 символов')
        return 0
    query = query_id_container['query']
    achievement_name = await state.get_data()
    achievement_name = achievement_name['achiev_name']
    Achievement.create(achievement_name=achievement_name, achievement_shortcut=message.text)
    await message.answer('✅ создано')
    await bot.edit_message_text('Выберите один из пунктов меню',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=achievement_menu_settings)
    query_id_container.clear()
    await state.finish()


# open list with achievements
async def show_achievement_list(query: types.CallbackQuery):
    achievements = Achievement.select()
    if achievements.exists():
        buttons = InlineKeyboardMarkup(row_width=1)
        for achievement in achievements:
            button = InlineKeyboardButton(f'{achievement.achievement_name} | {achievement.achievement_shortcut}',
                                          callback_data=f'achievement_id_{achievement.id}')
            buttons.add(button)
        buttons.add(InlineKeyboardButton('↩️ Назад', callback_data='achievement_menu'))
        await bot.edit_message_text('Выберите достижение ниже',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
    else:
        await query.answer('Достижений не было найдено')


# show achievement details
async def open_achievement(query: types.CallbackQuery):
    achievement_id = int(query.data.split('_')[-1])
    achievement = Achievement.select().where(Achievement.id == achievement_id)
    if achievement.exists():
        achievement = achievement.get()
        message_text, buttons = achievement_info(achievement)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
        await query.answer()
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=achievement_menu_settings)
        await query.answer('Такого достижения не существует')


# delete the achievement
async def achievement_delete(query: types.CallbackQuery):
    achievement_id = int(query.data.split('_')[-1])
    achievement = MainQuest.select().where(MainQuest.id == achievement_id)
    if achievement.exists():
        achievement = achievement.get()
        achievement.delete_instance(recursive=True)
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=achievement_menu_settings)
        await query.answer('✅ успешно удалено')
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=achievement_menu_settings)
        await query.answer('Такого достижения не существует')


# change the name of specific achievement
async def achievement_name_change(query: types.CallbackQuery):
    await bot.edit_message_text('Введите новое название достижения',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_achievement_menu)
    query_id_container['query'], query_id_container['achiev_id'] = query, int(query.data.split('_')[-1])
    await AchievementNameChanging.achievement_name.set()


# get the new name, and set it to achievement
async def achievement_name_changing(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer('Лимит 100 символов')
        return 0
    query = query_id_container['query']
    achievement_id = query_id_container['achiev_id']
    achievement = Achievement.select().where(Achievement.id == achievement_id).get()
    achievement.achievement_name = message.text
    achievement.save()
    message_text, buttons = achievement_info(achievement)
    await bot.edit_message_text(message_text,
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=buttons)
    query_id_container.clear()
    await state.finish()
    await query.answer()


def register_achievement_commands_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(achievement_menu, Text(equals='achievement_menu'), admin_callback=True, state='*')
    dp.register_callback_query_handler(create_achievement, Text(equals='create_achievement'), admin_callback=True, state='*')
    dp.register_message_handler(getting_achievement_name, regexp=r'.+', admin_message=True, state=AchievementCreating.getting_achievement_name)
    dp.register_message_handler(getting_achievement_shortcut, regexp=r'\w{6}', admin_message=True, state=AchievementCreating.getting_achievement_shortcut)
    dp.register_callback_query_handler(show_achievement_list, Text(equals='achievement_list'), admin_callback=True, state='*')
    dp.register_callback_query_handler(open_achievement, Text(startswith='achievement_id_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(achievement_delete, Text(startswith='achiev_delete_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(achievement_name_change, Text(startswith='achiev_name_change_'), admin_callback=True, state='*')
    dp.register_message_handler(achievement_name_changing, admin_message=True, regexp=r'.+', state=AchievementNameChanging.achievement_name)
