from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


get_to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('📋 Главное меню', callback_data='get_to_main_menu', ), ],
    ],

    row_width=1
)


main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('📊 Показать характеристики', callback_data='show_characteristics',), ],
        [InlineKeyboardButton('🚩 Квесты', callback_data='show_available_quest_list')]
    ],

    row_width=1
)


main_menu_for_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('📊 Показать характеристики', callback_data='show_characteristics',), ],
        [InlineKeyboardButton('🚩 Квесты', callback_data='show_available_quest_list')],
        [InlineKeyboardButton('🔐 Админ-панель', callback_data='admin_menu', ), ],
    ],

    row_width=1
)


admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('🔍 Найти игрока по id', callback_data='search_player_by_id', ), ],
        [InlineKeyboardButton('⚔ Настройки достижений', callback_data='achievement_menu', ), ],
        [InlineKeyboardButton('🚩 Настройки квестов', callback_data='quest_menu', ), ],
        [InlineKeyboardButton('📋 Главное меню', callback_data='get_to_main_menu', ), ],
    ],

    row_width=1
)


return_to_admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('🚫 Отмена', callback_data='admin_menu', ), ],
    ],

    row_width=1
)


quest_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('📜 Список квестов', callback_data='quest_list')],
        [InlineKeyboardButton('🔧 Создать квест', callback_data='create_quest')],
        [InlineKeyboardButton('↩️ Назад', callback_data='admin_menu')],
    ],

    row_width=1
)


return_to_quest_settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('🚫 Отмена', callback_data='quest_menu', ), ],
    ],

    row_width=1
)


skip_achievement_shortcut = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('🚫 Отмена', callback_data='quest_menu', ), ],
        [InlineKeyboardButton('Пропустить', callback_data='skip_achievement_setting', ), ],
    ],

    row_width=1
)


continue_finish_quest_creating = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('▶️ Продолжить', callback_data='continue_create', ), ],
        [InlineKeyboardButton('🏁 Завершить', callback_data='finish_create', ), ],
    ],

    row_width=1
)


continue_finish_cancel_quest_creating = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('▶️ Продолжить', callback_data='continue_create', ), ],
        [InlineKeyboardButton('🏁 Завершить', callback_data='finish_create', ), ],
        [InlineKeyboardButton('🚫 Отмена', callback_data='quest_menu', ), ],
    ],

    row_width=1
)


achievement_menu_settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('📜 Список достижений', callback_data='achievement_list')],
        [InlineKeyboardButton('🔧 Создать достижение', callback_data='create_achievement')],
        [InlineKeyboardButton('↩️ Назад', callback_data='admin_menu')],
    ],

    row_width=1
)

return_to_achievement_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('🚫 Отмена', callback_data='achievement_menu', ), ],
    ],

    row_width=1
)
