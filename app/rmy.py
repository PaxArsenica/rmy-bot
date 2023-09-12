import asyncio
import boto3
import common.utils as utils
import discord
import os
import random
from common.errors import NotAdmin
from discord import Color, CustomActivity, Embed, Message, Status
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import BadBoolArgument, CommandNotFound
from dotenv import load_dotenv
from os import environ as env


load_dotenv()
log = utils.setup_logging('rmy')

bot = Bot(command_prefix=commands.when_mentioned_or(env['BOT_PREFIX']), intents=discord.Intents.all(), help_command=None)

async def init_db() -> None:
    dynamodb = boto3.resource('dynamodb', region_name=env['AWS_DEFAULT_REGION'])
    mentionRequestsTable = dynamodb.Table('mention-requests')

async def init_cogs() -> None:
    for file in os.listdir(f"{os.path.dirname(os.path.abspath(__file__))}/cogs"):
        if file.endswith(".py"):
            cog = file[:-3]
            try:
                await bot.load_extension(f"cogs.{cog}")
            except Exception as err:
                log.error(f"Failed to load {cog}. : {err}")

@bot.event
async def on_ready() -> None:
    try:
        if utils.str_to_bool(env['STARTUP_SYNC']):
            log.info("Syncing commands...")
            await bot.tree.sync()
            log.info("Commands have been synced globally.")
    except BadBoolArgument:
        log.error("Invalid Sync value... not syncing.")
    except Exception as err:
        raise err

    log.info(f"{bot.user.name} has connected to Discord!")

    status = random.choice(utils.statuses)
    await bot.change_presence(status=Status.online, activity=CustomActivity(status))

@bot.event
async def on_message(message: Message) -> None:
    if utils.is_bot(bot, message):
        return
    await bot.process_commands(message)

@bot.event
async def on_command_completion(ctx: Context) -> None:
    command = ctx.command.qualified_name.split(" ")[0]
    if ctx.guild:
        command_log_message = f"{ctx.author}-{ctx.author.id} successfully completed '{command}' in {ctx.guild.name}-{ctx.guild.id}."  
    else:
        command_log_message = f"{ctx.author}-{ctx.author.id} successfully completed '{command}' in DMs."
    log.info(command_log_message)

@bot.event
async def on_command_error(ctx: Context, err: Exception) -> None:
    if isinstance(err, NotAdmin):
        embed = Embed(description=f"{ctx.author.name} is not an admin.", color=Color.brand_red())
        await ctx.send(embed=embed)
    elif isinstance(err, CommandNotFound):
        command = ctx.message.content.split(env['BOT_PREFIX'])[1].split(" ")[0]
        log.info(f"{ctx.author}-{ctx.author.id} tried to execute invalid command '{command}' in {ctx.guild.name}-{ctx.guild.id}.")
        await ctx.send(f"Sorry, {ctx.author.mention}! I don't recognize the command '{env['BOT_PREFIX']}{command}'. Please type '{env['BOT_PREFIX']}list_commands' to see a list of what I can do!")
    else:
        raise err

asyncio.run(init_cogs())
bot.run(env['TOKEN'])