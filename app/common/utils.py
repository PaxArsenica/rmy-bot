import discord.utils as utils
import logging
import sys
from common.errors import NotAdmin
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import BadBoolArgument
from discord.ext.commands._types import Check
from logging import Logger
from os import environ as env
from typing import Any, Union

def debugger_is_active() -> bool:
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None

def setup_logging(name: str) -> Logger:
    log = logging.getLogger(name)
    log.setLevel(env['LOG_LEVEL'])

    if debugger_is_active():
        file_handler = logging.FileHandler(filename=env['LOG_FILE'])
        file_handler.setFormatter(logging.Formatter(env['LOG_FORMAT']))
        log.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(utils._ColourFormatter())
    log.addHandler(console_handler)
    
    return log

log = setup_logging('utils')

def str_to_bool(s: str) -> bool:
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    else:
        raise BadBoolArgument("Invalid bool.")

def is_admin(author_id: str = None) -> Union[Check[Any], bool]:
    async def predicate(ctx: Context) -> bool:
        if str(ctx.author.id) not in env['ADMINS']:
            log.error(f"{ctx.author.name} is not an admin.")
            raise NotAdmin

        return True
    if not author_id:
        return commands.check(predicate)
    else:
        return False if str(author_id) not in env['ADMINS'] else True

def is_bot(bot: Bot, message: Message) -> bool:
    return message.author == bot.user or message.author.bot