import discord.utils as utils
import logging
from common.errors import NotAdmin
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import BadBoolArgument
from discord.ext.commands._types import Check
from logging import Logger
from os import environ as env
from typing import Any


def setup_logging(name: str) -> Logger:
    log = logging.getLogger(name)
    log.setLevel(env['LOG_LEVEL'])

    file_handler = logging.FileHandler(filename=env['LOG_FILE'])
    file_handler.setFormatter(logging.Formatter(env['LOG_FORMAT']))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(utils._ColourFormatter())

    log.addHandler(file_handler)
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

def is_bot(bot: Bot, message: Message) -> bool:
    return message.author == bot.user or message.author.bot

def is_admin() -> Check[Any]:
    async def predicate(ctx: Context) -> bool:
        if str(ctx.author.id) not in env['ADMINS']:
            log.error(f"{ctx.author.name} is not an admin.")
            raise NotAdmin

        return True

    return commands.check(predicate)