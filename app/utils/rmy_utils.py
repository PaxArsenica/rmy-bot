import discord.ext.commands as commands
import discord.utils as utils
import logging
import sys
import utils.config as config
from discord import Message
from discord.app_commands import AppCommand
from discord.ext.commands import Bot, Command, Context
from discord.ext.commands.errors import BadBoolArgument
from discord.ext.commands._types import Check
from logging import Logger
from typing import Any
from utils.errors import NotAdmin

def debugger_is_active() -> bool:
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None

def setup_logging(name: str) -> Logger:
    log = logging.getLogger(name)
    log.setLevel(config.LOG_LEVEL)

    if debugger_is_active():
        file_handler = logging.FileHandler(filename=config.LOG_FILE)
        file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
        log.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(utils._ColourFormatter())
    log.addHandler(console_handler)
    
    return log

log = setup_logging('utils')
statuses = ["Tickling Arsène!", "Praying on R's downfall.", "Gaming with Trevor!"]

def str_to_bool(s: str) -> bool:
    match s.lower():
        case "true":
            return True
        case "false":
            return False
        case _:
            raise BadBoolArgument("Invalid bool.")

async def mention_command(bot: Bot, name: str) -> Command:
    commands: list[AppCommand] = await bot.tree.fetch_commands()
    for command in commands:
        if command.name == name:
            return f'</{command.name}:{command.id}>'

def is_admin(author_id: str='') -> Check[Any] | bool:
    async def predicate(ctx: Context) -> bool:
        if str(ctx.author.id) not in config.ADMINS:
            log.error(f"{ctx.author.name} is not an admin.")
            raise NotAdmin

        return True

    if not author_id:
        return commands.check(predicate)
    else:
        return False if str(author_id) not in config.ADMINS else True

def is_bot(bot: Bot, message: Message) -> bool:
    return message.author == bot.user or message.author.bot

def is_me(bot: Bot, message: Message) -> bool:
    return message.author == bot.user