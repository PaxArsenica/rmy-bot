import common.utils as utils
import discord.ext.commands as commands
from discord import Colour, CustomActivity, Embed, Status
from discord.ext.commands import Bot, Cog, Context
from discord.ext.commands.errors import BadBoolArgument
from typing import Optional

log = utils.setup_logging('Polls')

class Polls(Cog, name='polls'):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.hybrid_command(name='poll', description='Creates a poll in the server.')
    async def poll(self, ctx: Context, name: str, max_participants: int, *, participants: Optional[str] = None) -> None:
        log.info('Creating a poll...')

        log.info(name)
        log.info(max_participants)
        log.info(participants)

        embed = Embed(description=f"This command is under development.", color=Colour.brand_red())
        await ctx.send(embed=embed)
    

async def setup(bot: Bot) -> None:
    await bot.add_cog(Polls(bot))