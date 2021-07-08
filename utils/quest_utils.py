from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.models import QuestSteps, Achievement


def getting_main_quest_info(quest):
    main_quest_name = quest.quest_name
    main_quest_text = quest.quest_text
    if quest.quest_achievement:
        achievement = Achievement.select().where(Achievement.achievement_shortcut == quest.quest_achievement)
        if achievement.exists:
            achievement = achievement.get()
            main_quest_achievement = f'{achievement.achievement_name} | {achievement.achievement_shortcut}'
        else:
            main_quest_achievement = 'Пусто'
    else:
        main_quest_achievement = 'Пусто'
    if quest.quest_publish:
        publish_status = '✅ опубликовано'
        publish_hide_button = InlineKeyboardButton('🔘 Скрыть', callback_data=f'unpublish_{quest.id}')
    else:
        publish_status = '♻️ ожидает публикации'
        publish_hide_button = InlineKeyboardButton('✅ опубликовать', callback_data=f'publish_{quest.id}')
    quest_steps = QuestSteps.select().where(QuestSteps.main_quest == quest).order_by(QuestSteps.step_number)
    buttons = InlineKeyboardMarkup(row_width=1)
    for step in quest_steps:
        if step.step_last_status:
            button = InlineKeyboardButton(f'⚫️ этап {step.step_number}', callback_data=f'step_id_{step.id}')
        else:
            button = InlineKeyboardButton(f'⚪️ этап {step.step_number}', callback_data=f'step_id_{step.id}')
        buttons.add(button)
    buttons.add(publish_hide_button)
    buttons.add(InlineKeyboardButton('🗑 Удалить', callback_data=f'quest_delete_{quest.id}'), InlineKeyboardButton('↩️ Назад', callback_data='quest_list'))
    message_text = f'Название:\n{main_quest_name}\n\nОписание:\n{main_quest_text}\n\nДостижение: {main_quest_achievement}\n\nСтатус публикации: {publish_status}'
    return message_text, buttons


def getting_quest_step_info(step):
    step_main_quest = step.main_quest
    step_number = step.step_number
    step_question = step.step_question
    step_answer = step.step_answer
    step_reward = step.step_reward_money
    step_skill = step.step_reward_skill
    step_status = step.step_last_status
    if step_status:
        step_status = '🏁 финальный этап'
    else:
        step_status = '🏳️ обычный этап'
    message_text = f'Название квеста: {step_main_quest.quest_name}\n\nНомер этапа: {step_number}\n\nЗагадка этапа:\n{step_question}\n\nОтвет:\n{step_answer}\n\nНаграда:\n{step_reward} опыта 🔑\n{step_skill} очков навыка ⚔\n\nСтатус: {step_status}'
    buttons = InlineKeyboardMarkup(row_width=2)
    question_change_btn = InlineKeyboardButton('Изменить загадку', callback_data=f'riddle_text_change_{step.id}')
    answer_change_btn = InlineKeyboardButton('Изменить ответ', callback_data=f'answer_change_{step.id}')
    reward_change_btn = InlineKeyboardButton('Изменить награду', callback_data=f'reward_change_{step.id}')
    skill_change_btn = InlineKeyboardButton('Изменить очки навыка', callback_data=f'skill_change_{step.id}')
    return_btn = InlineKeyboardButton('↩️ Назад', callback_data='quest_menu')
    buttons.add(question_change_btn, answer_change_btn, reward_change_btn, skill_change_btn, return_btn)
    return message_text, buttons


def achievement_info(achievement):
    message_text = f'{achievement.achievement_name} | {achievement.achievement_shortcut}'
    buttons = InlineKeyboardMarkup(row_width=1)
    achievement_name_change_btn = InlineKeyboardButton('📝 Сменить название',
                                                       callback_data=f'achiev_name_change_{achievement.id}')
    achievement_delete_btn = InlineKeyboardButton('🗑 Удалить', callback_data=f'achiev_delete_{achievement.id}')
    return_back_btn = InlineKeyboardButton('↩️ Назад', callback_data='achievement_menu')
    buttons.add(achievement_name_change_btn, achievement_delete_btn, return_back_btn)
    return message_text, buttons