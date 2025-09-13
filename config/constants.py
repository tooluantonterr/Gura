"""
Константы для всего проекта
"""

# Custom ID для UI компонентов
CUSTOM_IDS = {
    "ticket_select": "ticket_select",
    "ticket_close": "ticket_close",
    "ticket_manage": "ticket_manage",
    "manage_ticket_select": "manage_ticket_select",
    "move_ticket_select": "move_ticket_select"
}

# Эмодзи для UI
EMOJIS = {
    "ticket": "🎫",
    "close": "❌",
    "manage": "⚙️",
    "assign": "👤",
    "move": "📁",
    "transcript": "📄",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️"
}

# Сообщения об ошибках
ERROR_MESSAGES = {
    "no_permission": "❌ У вас нет прав для выполнения этого действия.",
    "ticket_already_assigned": "❌ Этот тикет уже назначен на кого-то.",
    "ticket_already_taken": "❌ Вы уже взяли этот тикет в работу.",
    "category_not_found": "❌ Категория не найдена.",
    "user_not_found": "❌ Пользователь не найден.",
    "invalid_user_format": "❌ Неверный формат ID пользователя.",
    "ticket_assignment_error": "❌ Ошибка при назначении тикета: {error}",
    "ticket_take_error": "❌ Ошибка при взятии тикета: {error}",
    "embed_update_error": "Ошибка при обновлении embed: {error}"
}

# Сообщения об успехе
SUCCESS_MESSAGES = {
    "ticket_assigned": "✅ Тикет назначен на **{user}**\nНазначил: {assigner}",
    "ticket_taken": "🎯 Тикет взят в работу пользователем **{user}**",
    "ticket_moved": "✅ Тикет перенесён в категорию **{category}**",
    "ticket_closed": "Тикет закрыт пользователем {user}"
}

# Placeholder тексты
PLACEHOLDERS = {
    "select_reason": "Выберите причину",
    "select_action": "Выберите действие",
    "select_category": "Выберите новую категорию",
    "enter_user": "Введите ID пользователя или @упоминание"
}

# Описания для UI элементов
DESCRIPTIONS = {
    "create_ticket": "Создать обращение",
    "move_category": "Переместить тикет в другую категорию",
    "assign_ticket": "Назначить тикет на пользователя (Ст.Админ+)",
    "take_ticket": "Назначить данный тикет на себя",
    "send_transcript": "Отправить историю тикета в ЛС"
}
