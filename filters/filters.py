from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


from db.models import Admin, Player


def check_for_admin(admin_id):
    admin = Admin.select().where(Admin.admin_telegram_id == admin_id)
    if admin.exists():
        return True
    return False


class IsDirectStart(BoundFilter):
    key = 'is_direct_start'

    def __init__(self, is_direct_start):
        self.is_direct_start = is_direct_start

    async def check(self, message: types.Message):
        if message.chat.id == message.from_user.id:
            return True
        return False


class IsDirectM(BoundFilter):
    key = 'is_direct_message'

    def __init__(self, is_direct_message):
        self.is_direct_message = is_direct_message

    async def check(self, message: types.Message):
        if message.chat.id == message.from_user.id:
            player = Player.select().where(Player.player_telegram_id == message.from_user.id).get()
            if player.player_ban is False:
                return True
        return False


class IsDirectC(BoundFilter):
    key = 'is_direct_callback'

    def __init__(self, is_direct_callback):
        self.is_direct_callback = is_direct_callback

    async def check(self, query: types.CallbackQuery):
        if query.message.chat.id == query.from_user.id:
            player = Player.select().where(Player.player_telegram_id == query.from_user.id).get()
            if player.player_ban is False:
                return True
        return False


class IsDirectAdminM(BoundFilter):
    key = 'admin_message'

    def __init__(self, admin_message):
        self.admin_message = admin_message

    async def check(self, message: types.Message):
        admin = Admin.select().where(Admin.admin_telegram_id == message.from_user.id)
        if admin.exists():
            if message.chat.id == message.from_user.id:
                return True
            return False
        return False


class IsDirectAdminC(BoundFilter):
    key = 'admin_callback'

    def __init__(self, admin_callback):
        self.admin_callback = admin_callback

    async def check(self, query: types.CallbackQuery):
        admin = Admin.select().where(Admin.admin_telegram_id == query.from_user.id)
        if admin.exists():
            if query.message.chat.id == query.from_user.id:
                return True
            return False
        return False