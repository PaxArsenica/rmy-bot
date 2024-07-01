import asyncio
import discord
import discord.ext.commands as commands
import os
import random
import utils.config as config
import utils.rmy_utils as utils
from db.dynamodb import DynamoDb
from discord import Colour, CustomActivity, Embed, Message, Status
from discord.ext.commands import Bot, Context, HelpCommand
from discord.ext.commands.errors import BadBoolArgument, CommandNotFound
from utils.errors import NotAdmin, RmyError


log = utils.setup_logging('rmy')

class RmyHelpCommand(HelpCommand):
    def __init__(self):
        super().__init__()

bot = Bot(command_prefix=commands.when_mentioned_or(config.BOT_PREFIX), intents=discord.Intents.all(), help_command = None)

async def init_db() -> None:
    db = DynamoDb()
    log.info(f'Connected to {db.client.meta.service_name}')

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
        if utils.str_to_bool(config.STARTUP_SYNC):
            log.info("Syncing commands...")
            await bot.tree.sync()
            log.info("Commands have been synced globally.")
    except BadBoolArgument:
        log.error("Invalid Sync value... not syncing.")

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
    command_log_location = f"{ctx.guild.name}-{ctx.guild.id}." if ctx.guild else "DMs."
    command_log_message = f"{ctx.author}-{ctx.author.id} successfully completed '{command}' in {command_log_location}"
    log.info(command_log_message)

@bot.event
async def on_command_error(ctx: Context, err: Exception) -> None:
    if ctx.command:
        command = ctx.command.name
    embed = Embed(description='Uh oh! There was an error.', color=Colour.brand_red())

    match err:
        case BadBoolArgument():
            message = "Invalid bool input... must be 'true' or 'false'."
            log.error(message)
            embed.description = message
        case CommandNotFound():
            command = ctx.message.content.split(config.BOT_PREFIX)[1].split(" ")[0]
            log.error(f"{ctx.author}-{ctx.author.id} tried to execute invalid command '{command}' in {ctx.guild.name}-{ctx.guild.id}.")
            list_commands_mention = await utils.mention_command(bot, 'list_commands')
            embed.description = f"Sorry, {ctx.author.mention}! I don't recognize the command '{config.BOT_PREFIX}{command}'. Please use {list_commands_mention} to see a list of what I can do!"
        case NotAdmin():
            log.error(f"{ctx.author}-{ctx.author.id} tried to execute admin command '{command}' in {ctx.guild.name}-{ctx.guild.id}.")
            embed.description = f"{ctx.author.mention}, you are not an admin."
        case RmyError():
            embed.description = err.message
        case _:
            log.error(err)
            raise err

    await ctx.send(embed=embed)

asyncio.run(init_cogs())
asyncio.run(init_db())
bot.run(config.TOKEN)