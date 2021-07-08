import datetime

from peewee import *


# The database may look not good functional, but we will try to improve it. Peewee version is bad, better use SQLAlchemy


# change the db name to whatever you want
db = SqliteDatabase('quest_bot.db', pragmas={'foreign_keys': 1, 'ignore_check_constraints': 0})


class BaseModel(Model):
    class Meta:
        database = db


class Player(BaseModel):
    # ----Personal information----
    id = AutoField(primary_key=True)
    player_telegram_id = CharField(max_length=20, unique=True, null=False)
    player_username = CharField(max_length=90, unique=True, null=True)
    player_full_name = CharField(max_length=90, null=True)
    # ----------------------------

    # ----Other important information----
    player_balance = DecimalField(max_digits=12, decimal_places=2, default=0)
    player_skill_points = IntegerField(default=0)
    player_skill_points_to_next_level = IntegerField(default=20)
    player_skill_level = IntegerField(default=0)
    player_info_note = TextField(null=True, default=None)  # Make some note to user, to not forget about some information
    player_joined_date = DateTimeField(default=datetime.datetime.now())
    player_ban = BooleanField(default=False)

    # -----------------------------------

    def __str__(self):
        return '{} | {}'.format(self.player_telegram_id, self.player_full_name)


class Admin(BaseModel):
    id = AutoField(primary_key=True)
    admin_telegram_id = CharField(max_length=20, unique=True, null=False)
    admin_player_profile = ForeignKeyField(model=Player, on_delete='CASCADE')

    def __str__(self):
        return '{} | {}'.format(self.admin_telegram_id, self.admin_player_profile)


class Achievement(BaseModel):
    id = AutoField(primary_key=True)
    achievement_name = CharField(max_length=100, null=False)
    achievement_shortcut = CharField(max_length=6, null=False, unique=True)

    def __str__(self):
        return '{}. {} | {}'.format(self.id, self.achievement_name, self.achievement_shortcut)


class PlayerAchievement(BaseModel):
    player = ForeignKeyField(model=Player, on_delete='CASCADE')
    achievement = ForeignKeyField(model=Achievement, on_delete='CASCADE')


class MainQuest(BaseModel):
    id = AutoField(primary_key=True)
    quest_name = CharField(max_length=50, null=False)
    quest_text = TextField(null=True, default=None)
    quest_achievement = CharField(max_length=6, null=True, unique=True)
    quest_publish = BooleanField(default=False)

    def __str__(self):
        return f'{self.id} | {self.quest_name}'


class QuestSteps(BaseModel):
    id = AutoField(primary_key=True)
    main_quest = ForeignKeyField(model=MainQuest, on_delete='CASCADE')
    step_number = IntegerField(null=False)
    step_question = TextField(null=True, default=None)
    step_answer = CharField(max_length=512, null=False)
    step_reward_money = DecimalField(max_digits=12, decimal_places=2, default=0)
    step_reward_skill = DecimalField(max_digits=9, decimal_places=3, default=0)
    step_last_status = BooleanField(default=False)

    def __str__(self):
        return f'{self.id} | {self.quiz_step_number} | {self.quiz_step_question}'


class PlayerAnswer(BaseModel):
    player = ForeignKeyField(model=Player, on_delete='CASCADE')
    answered_main_quest = ForeignKeyField(model=MainQuest, on_delete='CASCADE')
    answered_question = ForeignKeyField(model=QuestSteps, on_delete='CASCADE')
    answered_step_number = IntegerField(null=False)
    answer_time = DateTimeField(default=datetime.datetime.now())


if __name__ == '__main__':

    table1 = [
        Player,
        Achievement,
        PlayerAchievement,
        Admin,
        MainQuest,
        QuestSteps,
        PlayerAnswer,
    ]

    db.create_tables(table1)
