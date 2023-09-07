import asyncio
import boto3
import common.utils as utils
import common.errors as errors
import discord
import os
from apscheduler.schedulers.background import BackgroundScheduler
from discord import Color, Embed, Message
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import BadBoolArgument
from dotenv import load_dotenv
from os import environ as env
from services.pubsub import fetch_sub_of_the_week


load_dotenv()
log = utils.setup_logging('RmyBot')

bot = Bot(command_prefix=commands.when_mentioned_or(env['BOT_PREFIX']), intents=discord.Intents.all())
scheduler = BackgroundScheduler()

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

@bot.event
async def on_message(message: Message) -> None:
    if utils.is_bot(bot, message):
        return
    await bot.process_commands(message)
    await message.channel.send(f"I don't recognize that command. Please type '{env['BOT_PREFIX']} list_commands' to see a list of what I can do!")

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
    if isinstance(err, errors.NotAdmin):
        embed = Embed(description=f"{ctx.author.name} is not an admin.", color=Color.brand_red())
        await ctx.send(embed=embed)
    else:
        raise err

@scheduler.scheduled_job('cron', day_of_week='wed', hour=11)
def get_sub_of_the_week_scheduler():
    fetch_sub_of_the_week()


asyncio.run(init_cogs())
scheduler.start()
bot.run(env['TOKEN'])