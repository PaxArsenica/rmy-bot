from discord.ext.commands import CheckFailure


class NotAdmin(CheckFailure):
    def __init__(self, message: str="Not an admin."):
        self.message = message
        super().__init__(self.message)