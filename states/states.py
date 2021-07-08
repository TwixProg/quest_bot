from aiogram.dispatcher.filters.state import State, StatesGroup


# States for FSM
class FindingPlayer(StatesGroup):
    getting_player_id = State()
    getting_player_change = State()


class ChangingSkillPoints(StatesGroup):
    getting_skill_points = State()


class ChangingBalance(StatesGroup):
    getting_balance = State()


class ChoosingQuestMenu(StatesGroup):
    choosing_button = State()


# fsm for quest creating
class QuestCreating(StatesGroup):
    getting_quest_name = State()
    getting_quest_text = State()
    getting_quest_achievement_code = State()


# fsm for creating quest's steps
class QuestStepCreating(StatesGroup):
    getting_step_question = State()
    getting_step_answer = State()
    getting_step_reward_money = State()
    getting_step_reward_skill = State()
    asking_to_create_next_step = State()


class RiddleTextChanging(StatesGroup):
    getting_riddle_text = State()


class AnswerChanging(StatesGroup):
    getting_answer = State()


class RewardChanging(StatesGroup):
    getting_reward = State()


class SkillChanging(StatesGroup):
    getting_skill = State()


class AchievementCreating(StatesGroup):
    getting_achievement_name = State()
    getting_achievement_shortcut = State()


class AchievementNameChanging(StatesGroup):
    achievement_name = State()


class SolvingQuest(StatesGroup):
    choosing_quest = State()
    solving_step = State()