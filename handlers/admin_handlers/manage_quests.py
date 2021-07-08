from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from keyboards.inline import return_to_quest_settings, skip_achievement_shortcut, continue_finish_quest_creating, \
    continue_finish_cancel_quest_creating, quest_menu
from states.states import QuestCreating, QuestStepCreating, RiddleTextChanging, AnswerChanging, RewardChanging, \
    SkillChanging, ChoosingQuestMenu
from utils.quest_utils import getting_main_quest_info, getting_quest_step_info
from db.models import Achievement, MainQuest, QuestSteps
from bot import bot


# creating container for queries
query_id_container = {}  # get rid of this shit


# quest-settings menu
async def quest_settings_menu(query: types.CallbackQuery, state: FSMContext = None):
    if state is not None:
        await state.finish()
    query_id_container.clear()
    await bot.edit_message_text('Выберите один из пунктов меню',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=quest_menu)
    await ChoosingQuestMenu.choosing_button.set()
    await query.answer()


# callback to create quest
async def create_quest(query: types.CallbackQuery, state: FSMContext):
    last_message = query.message
    await bot.edit_message_text('Введите название нового квеста',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_quest_settings)
    await state.update_data(message=last_message)
    await QuestCreating.getting_quest_name.set()
    await query.answer()


# gets name of the quest
async def get_quest_name(message: types.Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer('Название квеста не должно содержать больше 50 символов')
        return 0
    info = await state.get_data()
    last_message = info['message']
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=message.chat.id,
                                          text='Введите текст-приветствие для квеста',
                                          reply_markup=return_to_quest_settings)
    await state.update_data(quest_name=message.text, message=last_message)
    await QuestCreating.next()


# getting main quest's text
async def get_quest_text(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_message = info['message']
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=message.chat.id,
                                          text='Введите шорткат достижения, или выберите соответсвующую кнопку',
                                          reply_markup=skip_achievement_shortcut)
    await state.update_data(quest_text=message.text, message=last_message)
    await QuestCreating.next()


# getting achievement shortcut-code
async def get_achievement_code(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_message = info['message']
    achievement = Achievement.select().where(Achievement.achievement_shortcut == message.text)
    if achievement.exists():
        quest_name = await state.get_data()
        quest_name = quest_name['quest_name']
        quest_info = f'Название квеста:\n{quest_name}\n\nШорткат достижения: {message.text}\n\nНачнём создание стартового этапа квеста. Введите загадку для этапа'
        await bot.delete_message(chat_id=last_message.chat.id,
                                 message_id=last_message.message_id)
        last_message = await bot.send_message(chat_id=message.chat.id,
                                              text=quest_info,
                                              reply_markup=return_to_quest_settings)
        await state.update_data(achievement_shortcut=message.text, step_number=1, message=last_message)
        await QuestStepCreating.getting_step_question.set()
    else:
        await message.answer('Введён неправильный шорткат, такового не существует, попробуйте снова')
        return 0


# or skipping achievement shortcut
async def skip_achievement_code(query: types.CallbackQuery, state: FSMContext):
    info = await state.get_data()
    last_message = info['message']
    quest_name = info['quest_name']
    quest_info = f'Название квеста:\n{quest_name}\n\nШорткат достижения: Пусто\n\nНачнём создание стартового этапа квеста. Введите загадку для этапа'
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=query.message.chat.id,
                                          text=quest_info,
                                          reply_markup=return_to_quest_settings)
    await state.update_data(achievement_shortcut=None, step_number=1, message=last_message)
    await QuestStepCreating.getting_step_question.set()
    await query.answer()


# getting text of riddle to quest's step
async def get_step_question(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_message = info['message']
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=message.chat.id,
                                          text='Введите ответ к загадке',
                                          reply_markup=return_to_quest_settings)
    await state.update_data(step_question=message.text, message=last_message)
    await QuestStepCreating.next()


# getting answer to the riddle of quest's step
async def get_step_answer(message: types.Message, state: FSMContext):
    if len(message.text) > 512:
        await message.answer('Лимит 512 символов')
        return 0
    info = await state.get_data()
    last_message = info['message']
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=message.chat.id,
                                          text='Введите сумму денежной награды за прохождение данного этапа',
                                          reply_markup=return_to_quest_settings)
    await state.update_data(step_answer=message.text.lower(), message=last_message)
    await QuestStepCreating.next()


# getting amount of reward-money for passing a step
async def get_step_reward_money(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_message = info['message']
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=message.chat.id,
                                          text='Введите количество опыта за прохождение данного этапа',
                                          reply_markup=return_to_quest_settings)
    await state.update_data(step_reward_money=int(message.text), message=last_message)
    await QuestStepCreating.next()


# getting amount of reward skill points for passing a step
async def get_step_reward_skill(message: types.Message, state: FSMContext):
    info = await state.get_data()
    last_message = info['message']
    step_number = info['step_number']
    if step_number > 1:
        keyboard = continue_finish_quest_creating
    else:
        keyboard = continue_finish_cancel_quest_creating
    await bot.delete_message(chat_id=last_message.chat.id,
                             message_id=last_message.message_id)
    last_message = await bot.send_message(chat_id=message.chat.id,
                                          text='Продолжить или завершить создание квеста?',
                                          reply_markup=keyboard)
    await state.update_data(step_reward_skill=int(message.text), message=last_message)
    await QuestStepCreating.next()


# if admin chooses to finish
async def finish_creating_quest(query: types.CallbackQuery, state: FSMContext):
    quest_info = await state.get_data()
    last_message = quest_info['message']
    if quest_info['step_number'] == 1:
        quest_name = quest_info['quest_name']
        quest_text = quest_info['quest_text']
        quest_achievement = quest_info['achievement_shortcut']
        step_question = quest_info['step_question']
        step_answer = quest_info['step_answer']
        step_reward = quest_info['step_reward_money']
        step_skill_points = quest_info['step_reward_skill']
        main_quest = MainQuest.create(quest_name=quest_name, quest_text=quest_text, quest_achievement=quest_achievement)
        QuestSteps.create(main_quest=main_quest, step_number=quest_info['step_number'], step_question=step_question,
                          step_answer=step_answer, step_reward_money=step_reward, step_reward_skill=step_skill_points,
                          step_last_status=True)
        await bot.send_message(query.from_user.id, text='✅ Квест успешно создан')
        await bot.delete_message(chat_id=last_message.chat.id,
                                 message_id=last_message.message_id)
        await bot.send_message(chat_id=query.message.chat.id,
                               text='Выберите один из пунктов меню',
                               reply_markup=quest_menu)
        await state.finish()
        await query.answer()
    else:
        step_question = quest_info['step_question']
        step_answer = quest_info['step_answer']
        step_reward = quest_info['step_reward_money']
        step_skill_points = quest_info['step_reward_skill']
        main_quest = quest_info['main_quest']
        QuestSteps.create(main_quest=main_quest, step_number=quest_info['step_number'], step_question=step_question,
                          step_answer=step_answer, step_reward_money=step_reward, step_reward_skill=step_skill_points,
                          step_last_status=True)
        await bot.send_message(query.from_user.id, text='✅ Квест успешно создан')
        await bot.delete_message(chat_id=last_message.chat.id,
                                 message_id=last_message.message_id)
        await bot.send_message(chat_id=query.message.chat.id,
                               text='Выберите один из пунктов меню',
                               reply_markup=quest_menu)
        await state.finish()
        await query.answer()


# if admin chooses to continue creating quest
async def continue_creating_quest(query: types.CallbackQuery, state: FSMContext):
    quest_info = await state.get_data()
    last_message = quest_info['message']
    if quest_info['step_number'] == 1:
        quest_name = quest_info['quest_name']
        quest_text = quest_info['quest_text']
        quest_achievement = quest_info['achievement_shortcut']
        step_number = quest_info['step_number']
        step_question = quest_info['step_question']
        step_answer = quest_info['step_answer']
        step_reward = quest_info['step_reward_money']
        step_skill_points = quest_info['step_reward_skill']
        main_quest = MainQuest.create(quest_name=quest_name, quest_text=quest_text, quest_achievement=quest_achievement)
        QuestSteps.create(main_quest=main_quest, step_number=step_number, step_question=step_question,
                          step_answer=step_answer, step_reward_money=step_reward, step_reward_skill=step_skill_points,
                          step_last_status=False)
        step_number += 1
        await bot.delete_message(chat_id=last_message.chat.id,
                                 message_id=last_message.message_id)
        last_message = await bot.send_message(chat_id=query.message.chat.id,
                                              text='Введите загадку для нового этапа',
                                              reply_markup=return_to_quest_settings)
        await state.update_data(main_quest=main_quest, step_number=step_number, message=last_message)
        await QuestStepCreating.getting_step_question.set()
        await query.answer()
    else:
        step_number = quest_info['step_number']
        step_question = quest_info['step_question']
        step_answer = quest_info['step_answer']
        step_reward = quest_info['step_reward_money']
        step_skill_points = quest_info['step_reward_skill']
        main_quest = quest_info['main_quest']
        QuestSteps.create(main_quest=main_quest, step_number=step_number, step_question=step_question,
                          step_answer=step_answer, step_reward_money=step_reward, step_reward_skill=step_skill_points,
                          step_last_status=False)
        step_number += 1
        await bot.delete_message(chat_id=last_message.chat.id,
                                 message_id=last_message.message_id)
        last_message = await bot.send_message(chat_id=query.message.chat.id,
                                              text='Введите загадку для нового этапа',
                                              reply_markup=return_to_quest_settings)
        await state.update_data(step_number=step_number, message=last_message)
        await QuestStepCreating.getting_step_question.set()
        await query.answer()


# getting the list of quests to manage them
async def open_quests_list(query: types.CallbackQuery):
    quests = MainQuest.select()
    if quests.exists():
        quest_list_buttons = InlineKeyboardMarkup(row_width=1)
        for quest in quests:
            button = InlineKeyboardButton(f'{quest.quest_name}', callback_data=f'open_quest_{quest.id}')
            quest_list_buttons.add(button)
        quest_list_buttons.add(InlineKeyboardButton('↩️ Назад', callback_data='quest_menu'))
        await bot.edit_message_text('Выберите квест из списка ниже',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_list_buttons)
        await query.answer()
    else:
        await query.answer('Квестов не было найдено')


# getting information about specific quest
async def open_quest(query: types.CallbackQuery):
    quest_id = int(query.data.split('_')[-1])
    quest = MainQuest.select().where(MainQuest.id == quest_id)
    if quest.exists():
        quest = quest.get()
        message_text, buttons = getting_main_quest_info(quest)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await query.answer('Такого квеста не было найдено')


# publish hidden quest
async def publish_quest(query: types.CallbackQuery):
    quest_id = int(query.data.split('_')[-1])
    quest = MainQuest.select().where(MainQuest.id == quest_id)
    if quest.exists():
        quest = quest.get()
        quest.quest_publish = True
        quest.save()
        quest = MainQuest.select().where(MainQuest.id == quest_id).get()
        message_text, buttons = getting_main_quest_info(quest)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await query.answer('Такого квеста не было найдено')


async def unpublish_quest(query: types.CallbackQuery):
    quest_id = int(query.data.split('_')[-1])
    quest = MainQuest.select().where(MainQuest.id == quest_id)
    if quest.exists():
        quest = quest.get()
        quest.quest_publish = False
        quest.save()
        quest = MainQuest.select().where(MainQuest.id == quest_id).get()
        message_text, buttons = getting_main_quest_info(quest)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await query.answer('Такого квеста не было найдено')


# delete existing quest
async def delete_quest(query: types.CallbackQuery):
    quest_id = int(query.data.split('_')[-1])
    quest = MainQuest.select().where(MainQuest.id == quest_id)
    if quest.exists():
        quest = quest.get()
        quest.delete_instance(recursive=True)
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await query.answer('✅ успешно удалено')


# get info about specific step of the quest
async def open_quest_step(query: types.CallbackQuery):
    step_id = int(query.data.split('_')[-1])
    step = QuestSteps.select().where(QuestSteps.id == step_id)
    if step.exists():
        step = step.get()
        message_text, buttons = getting_quest_step_info(step)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
        await query.answer()
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await query.answer('Такого этапа не было найдено')


# if you decided to change riddle of the quest's step
async def riddle_change(query: types.CallbackQuery):
    await bot.edit_message_text('Введите новую загадку для этапа',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_quest_settings)
    query_id_container['step_id'], query_id_container['query'] = int(query.data.split('_')[-1]), query
    await RiddleTextChanging.getting_riddle_text.set()


# getting new text of the riddle and setting it to quest's step
async def riddle_text_changing(message: types.Message, state: FSMContext):
    query = query_id_container['query']
    step_id = query_id_container['step_id']
    step = QuestSteps.select().where(QuestSteps.id == step_id)
    if step.exists():
        step = step.get()
        step.step_question = message.text
        step.save()
        step = QuestSteps.select().where(QuestSteps.id == step_id).get()
        message_text, buttons = getting_quest_step_info(step)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
        await state.finish()
        query_id_container.clear()
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await state.finish()
        query_id_container.clear()
        await query.answer('Такого этапа не было найдено')


# if you decided to change the answer to the quest's step
async def answer_change(query: types.CallbackQuery):
    await bot.edit_message_text('Введите новый ответ к загадке',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_quest_settings)
    query_id_container['step_id'], query_id_container['query'] = int(query.data.split('_')[-1]), query
    await AnswerChanging.getting_answer.set()


# getting new answer and setting it to quest's step
async def answer_changing(message: types.Message, state: FSMContext):
    if len(message.text) > 512:
        await message.answer('Лимит 512 символов')
        return 0
    query = query_id_container['query']
    step_id = query_id_container['step_id']
    step = QuestSteps.select().where(QuestSteps.id == step_id)
    if step.exists():
        step = step.get()
        step.step_answer = message.text.lower()
        step.save()
        step = QuestSteps.select().where(QuestSteps.id == step_id).get()
        message_text, buttons = getting_quest_step_info(step)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
        await state.finish()
        query_id_container.clear()
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await state.finish()
        query_id_container.clear()
        await message.answer('Такого этапа не было найдено')


# if you decided to change reward-money of the quest's step
async def reward_change(query: types.CallbackQuery):
    await bot.edit_message_text('Введите новую денежную награду',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_quest_settings)
    query_id_container['step_id'], query_id_container['query'] = int(query.data.split('_')[-1]), query
    await RewardChanging.getting_reward.set()


# getting amount of reward and setting it to quest's step
async def reward_changing(message: types.Message, state: FSMContext):
    query = query_id_container['query']
    step_id = query_id_container['step_id']
    step = QuestSteps.select().where(QuestSteps.id == step_id)
    if step.exists():
        step = step.get()
        step.step_reward_money = int(message.text)
        step.save()
        step = QuestSteps.select().where(QuestSteps.id == step_id).get()
        message_text, buttons = getting_quest_step_info(step)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
        await state.finish()
        query_id_container.clear()
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await state.finish()
        query_id_container.clear()
        await message.answer('Такого этапа не было найдено')


# if you decided to change reward skill points of the quest's step
async def skill_change(query: types.CallbackQuery):
    await bot.edit_message_text('Введите новое кол-во очков навыка',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=return_to_quest_settings)
    query_id_container['step_id'], query_id_container['query'] = int(query.data.split('_')[-1]), query
    await SkillChanging.getting_skill.set()


# getting amount of skill points and setting it to quest's step
async def skill_changing(message: types.Message, state: FSMContext):
    query = query_id_container['query']
    step_id = query_id_container['step_id']
    step = QuestSteps.select().where(QuestSteps.id == step_id)
    if step.exists():
        step = step.get()
        step.step_reward_skill = int(message.text)
        step.save()
        step = QuestSteps.select().where(QuestSteps.id == step_id).get()
        message_text, buttons = getting_quest_step_info(step)
        await bot.edit_message_text(message_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=buttons)
        await state.finish()
        query_id_container.clear()
    else:
        await bot.edit_message_text('Выберите один из пунктов меню',
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=quest_menu)
        await state.finish()
        query_id_container.clear()
        await message.answer('Такого этапа не было найдено')


def register_quest_commands_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(quest_settings_menu, Text(equals='quest_menu'), state='*', admin_callback=True)
    dp.register_callback_query_handler(create_quest, Text(equals='create_quest'), admin_callback=True, state=ChoosingQuestMenu.choosing_button)
    dp.register_message_handler(get_quest_name, admin_message=True, regexp=r'.+', state=QuestCreating.getting_quest_name)
    dp.register_message_handler(get_quest_text, admin_message=True, regexp=r'(?:.\s?)+', state=QuestCreating.getting_quest_text)
    dp.register_message_handler(get_achievement_code, admin_message=True, regexp=r'\w{6}', state=QuestCreating.getting_quest_achievement_code)
    dp.register_callback_query_handler(skip_achievement_code, Text(startswith='skip_achievement_setting'), admin_callback=True, state=QuestCreating.getting_quest_achievement_code)
    dp.register_message_handler(get_step_question, admin_message=True, regexp=r'(?:.\s?)+', state=QuestStepCreating.getting_step_question)
    dp.register_message_handler(get_step_answer, admin_message=True, regexp='.+', state=QuestStepCreating.getting_step_answer)
    dp.register_message_handler(get_step_reward_money, admin_message=True, regexp=r'\b[-+]?\d+$', state=QuestStepCreating.getting_step_reward_money)
    dp.register_message_handler(get_step_reward_skill, admin_message=True, regexp=r'\b[-+]?\d+$', state=QuestStepCreating.getting_step_reward_skill)
    dp.register_callback_query_handler(finish_creating_quest, Text(equals='finish_create'), admin_callback=True, state=QuestStepCreating.asking_to_create_next_step)
    dp.register_callback_query_handler(continue_creating_quest, Text(equals='continue_create'), admin_callback=True, state=QuestStepCreating.asking_to_create_next_step)
    dp.register_callback_query_handler(open_quests_list, Text(equals='quest_list'), admin_callback=True, state='*')
    dp.register_callback_query_handler(open_quest, Text(startswith='open_quest_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(publish_quest, Text(startswith='publish_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(unpublish_quest, Text(startswith='unpublish_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(delete_quest, Text(startswith='quest_delete_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(open_quest_step, Text(startswith='step_id_'), admin_callback=True, state='*')
    dp.register_callback_query_handler(riddle_change, Text(startswith='riddle_text_change_'), admin_callback=True, state='*')
    dp.register_message_handler(riddle_text_changing, admin_message=True, regexp=r'(?:.\s?)+', state=RiddleTextChanging.getting_riddle_text)
    dp.register_callback_query_handler(answer_change, Text(startswith='answer_change_'), admin_callback=True, state='*')
    dp.register_message_handler(answer_changing, admin_message=True, regexp=r'.+', state=AnswerChanging.getting_answer)
    dp.register_callback_query_handler(reward_change, Text(startswith='reward_change_'), admin_callback=True, state='*')
    dp.register_message_handler(reward_changing, admin_message=True, regexp=r'\b[-+]?\d+$', state=RewardChanging.getting_reward)
    dp.register_callback_query_handler(skill_change, Text(startswith='skill_change_'), admin_callback=True, state='*')
    dp.register_message_handler(skill_changing, admin_message=True, regexp=r'\b[-+]?\d+$', state=SkillChanging.getting_skill)
