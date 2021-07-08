from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from db.models import Player, MainQuest, PlayerAnswer, QuestSteps, Achievement, PlayerAchievement
from keyboards.inline import main_menu, main_menu_for_admin
from utils.player_utils import skill_level_calculator
from filters.filters import check_for_admin
from states.states import SolvingQuest
from bot import bot

# creating container for queries
query_id_container = {}  # get rid of this shit


#  open list of all available quests
async def show_available_quests(query: types.CallbackQuery):
    quests = MainQuest.select().where(MainQuest.quest_publish==True)
    if quests.exists():
        buttons = InlineKeyboardMarkup(row_width=1)
        for quest in quests:
            button = InlineKeyboardButton(f'{quest.quest_name}', callback_data=f'start_solve_quest_{quest.id}')
            buttons.add(button)
        buttons.add(InlineKeyboardButton('📋 Главное меню', callback_data='get_to_main_menu'))
        await bot.edit_message_text('Для старта, выберите квест ниже',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
        await SolvingQuest.choosing_quest.set()
        await query.answer()
    else:
        await query.answer('Квестов не было найдено')


#  handler for starting to solve quest
async def start_solving_quest(query: types.CallbackQuery, state: FSMContext):
    quest_id = int(query.data.split('_')[-1])
    quest = MainQuest.select().where(MainQuest.id == quest_id)
    if quest.exists():
        quest = quest.get()
        player = Player.select().where(Player.player_telegram_id == query.from_user.id).get()
        player_answers = PlayerAnswer.select().where((PlayerAnswer.player == player) & (PlayerAnswer.answered_main_quest == quest)).order_by(PlayerAnswer.answered_step_number)
        if player_answers.exists():
            last_answer = player_answers[-1]
            last_solved_step = last_answer.answered_question
            if last_solved_step.step_last_status:
                await state.finish()
                mm = main_menu
                if check_for_admin(admin_id=query.from_user.id):
                    mm = main_menu_for_admin
                await bot.edit_message_text('Выберите один из пунктов меню:',
                                            chat_id=query.message.chat.id,
                                            message_id=query.message.message_id,
                                            reply_markup=mm)
                await query.answer('👑 вы уже прошли данный квест!')
            else:
                next_step_number = last_solved_step.step_number + 1
                quest_step = QuestSteps.select().where((QuestSteps.main_quest == quest) & (QuestSteps.step_number == next_step_number)).get()
                await state.update_data(quest_step_id=quest_step.id, message=query.message)
                message_text = f'Этап {quest_step.step_number}\n\n{quest_step.step_question}'
                buttons = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('↩️ Назад', callback_data='get_to_main_menu'))
                await bot.edit_message_text(message_text,
                                            chat_id=query.message.chat.id,
                                            message_id=query.message.message_id,
                                            reply_markup=buttons)
                await SolvingQuest.solving_step.set()
                await query.answer()
        else:
            quest_step = QuestSteps.select().where((QuestSteps.main_quest == quest) & (QuestSteps.step_number == 1)).get()
            await state.update_data(quest_step_id=quest_step.id, message=query.message)
            message_text = f'{quest.quest_text}\n\nЭтап {quest_step.step_number}\n\n{quest_step.step_question}'
            buttons = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('↩️ Назад', callback_data='get_to_main_menu'))
            await bot.edit_message_text(message_text,
                                        chat_id=query.message.chat.id,
                                        message_id=query.message.message_id,
                                        reply_markup=buttons)
            await SolvingQuest.solving_step.set()
            await query.answer()
    else:
        await state.finish()
        mm = main_menu
        if check_for_admin(admin_id=query.from_user.id):
            mm = main_menu_for_admin
        await bot.edit_message_text('Выберите один из пунктов меню:',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=mm)
        await query.answer('Квест не был найден')


# getting the answer to quest step
async def getting_answer_to_quest_step(message: types.Message, state: FSMContext):
    info = await state.get_data()
    quest_step_id = info['quest_step_id']
    last_message = info['message']
    step = QuestSteps.select().where(QuestSteps.id == quest_step_id)
    if step.exists():
        step = step.get()
        main_quest = step.main_quest
        if step.step_answer == message.text.lower():
            player = Player.select().where(Player.player_telegram_id == message.from_user.id).get()
            PlayerAnswer.create(player=player, answered_main_quest=main_quest, answered_question=step, answered_step_number=step.step_number)
            player.player_balance += step.step_reward_money
            player.player_skill_points += step.step_reward_skill
            if player.player_skill_points > player.player_skill_points_to_next_level:
                level, points_to_next_level = skill_level_calculator(player.player_skill_points)
                player.player_skill_level = level
                player.player_skill_points_to_next_level = points_to_next_level
            player.save()
            await message.answer(f'🎉 правильный ответ! Вы прошли данный этап квеста!\n\nПолучено:\n{step.step_reward_money} опыта 🔑\n{step.step_reward_skill} очков навыка ⚔')
            if step.step_last_status:
                await message.answer('👑 Поздравляем! Вы прошли все этапы квеста!')
                if main_quest.quest_achievement:
                    achievement = Achievement.select().where(Achievement.achievement_shortcut == main_quest.quest_achievement)
                    if achievement.exists():
                        achievement = achievement.get()
                        PlayerAchievement.create(player=player, achievement=achievement)
                        await message.answer(f'Получено достижение "{achievement.achievement_name}"')
                await state.finish()
                mm = main_menu
                if check_for_admin(admin_id=message.from_user.id):
                    mm = main_menu_for_admin
                await bot.delete_message(chat_id=last_message.chat.id,
                                         message_id=last_message.message_id)
                await bot.send_message(chat_id=message.chat.id,
                                       text='Выберите один из пунктов меню:',
                                       reply_markup=mm)
            else:
                next_step_number = step.step_number + 1
                next_step = QuestSteps.select().where((QuestSteps.main_quest == main_quest) & (QuestSteps.step_number == next_step_number)).get()
                message_text = f'Этап {next_step.step_number}\n\n{next_step.step_question}'
                buttons = InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton('↩️ Назад', callback_data='get_to_main_menu'))
                await bot.delete_message(chat_id=last_message.chat.id,
                                         message_id=last_message.message_id)
                last_message = await bot.send_message(chat_id=message.chat.id,
                                                      text=message_text,
                                                      reply_markup=buttons)
                await state.update_data(quest_step_id=next_step.id, message=last_message)
                await SolvingQuest.solving_step.set()
        else:
            await message.answer('Ответ неверный, подумайте лучше')
            await SolvingQuest.solving_step.set()
    else:
        await state.finish()
        mm = main_menu
        if check_for_admin(admin_id=message.from_user.id):
            mm = main_menu_for_admin
        await bot.delete_message(chat_id=last_message.chat.id,
                                 message_id=last_message.message_id)
        await bot.send_message(chat_id=message.chat.id,
                               text='Выберите один из пунктов меню:',
                               reply_markup=mm)
        await message.answer('Квест не был найден')


def register_user_quest_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(show_available_quests, Text(equals='show_available_quest_list'), is_direct_callback=True)
    dp.register_callback_query_handler(start_solving_quest, Text(startswith='start_solve_quest_'), is_direct_callback=True, state=SolvingQuest.choosing_quest)
    dp.register_callback_query_handler(getting_answer_to_quest_step, is_direct_message=True, regexp=r'.+', state=SolvingQuest.solving_step)
