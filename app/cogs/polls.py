import common.utils as utils
from discord import Color, CustomActivity, Embed, Status
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import BadBoolArgument

log = utils.setup_logging('Polls')

class Polls(commands.Cog, name='polls'):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.hybrid_command(name='poll', description='Creates a poll in the server.')
    async def poll(self, ctx: Context, poll_info: str) -> None:
        log.info('Creating a poll...')
        embed = Embed(description=f"This command is under development.", color=Color.brand_red())
        await ctx.send(embed=embed)
    

async def setup(bot: Bot) -> None:
    await bot.add_cog(Polls(bot))