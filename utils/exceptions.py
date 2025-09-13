class TicketBotException(Exception):
    pass

class PermissionError(TicketBotException):
    def __init__(self, message: str = "Недостаточно прав"):
        self.message = message
        super().__init__(self.message)

class TicketError(TicketBotException):
    def __init__(self, message: str = "Ошибка работы с тикетом"):
        self.message = message
        super().__init__(self.message)

class ConfigurationError(TicketBotException):
    def __init__(self, message: str = "Ошибка конфигурации"):
        self.message = message
        super().__init__(self.message)

class DataError(TicketBotException):
    def __init__(self, message: str = "Ошибка работы с данными"):
        self.message = message
        super().__init__(self.message)
