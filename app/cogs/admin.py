import common.utils as utils
import discord.ext.commands as commands
import random
from discord import Colour, CustomActivity, Embed, Status
from discord.ext.commands import Bot, Cog, Context
from discord.ext.commands.errors import BadBoolArgument

log = utils.setup_logging('admin')

class Admin(Cog, name='admin'):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @utils.is_admin()
    @commands.command(name='desync', description='Deyncs all global commands.')
    async def desync(self, ctx: Context, guild: str = "True") -> None:
        log.info("Desyncing commands...")
        try:
            guild_bool = utils.str_to_bool(guild)
        except BadBoolArgument:
            log.error("Invalid bool input... must be 'true' or 'false'.")
            embed = Embed(description=f"Invalid bool input... must be 'true' or 'false'.", color=Colour.brand_red())
            await ctx.send(embed=embed)

        embed = Embed(description="Desyncing commands...", color=Colour.yellow())
        await ctx.send(embed=embed)

        if guild_bool:
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            embed = Embed(description="Commands have been desynced in the server.", color=Colour.brand_green())
            log.info("Commands have been desynced in the server.")
        else:
            self.bot.tree.clear_commands(guild=None)
            await self.bot.tree.sync()
            embed = Embed(description="Commands have been desynced globally.", color=Colour.brand_green())
            log.info("Commands have been desynced globally.")

        await ctx.send(embed=embed)

    @utils.is_admin()
    @commands.command(name='kill', description='Kills the bot.')
    async def kill(self, ctx: Context) -> None:
        embed = Embed(description=f"Oh no! {ctx.author.mention} has killed me!", color=Colour.brand_red())
        await ctx.send(embed=embed)
        await self.bot.close()
        log.info('Bot killed.')

    @utils.is_admin()
    @commands.command(name='status', description='Changes the status of the bot in the server.')
    async def status(self, ctx: Context, *, status: str = None) -> None:
        await ctx.message.delete()
        if not status:
            status = random.choice(utils.statuses)
        status = status.strip('"').strip("'").strip()

        await self.bot.change_presence(status=Status.online, activity=CustomActivity(status))
        log.info(f'Updated bot status to "{status}".')

    @utils.is_admin()
    @commands.command(name='sync', description='Syncs all global commands.')
    async def sync(self, ctx: Context, guild: str = "True") -> None:
        log.info("Syncing commands...")
        try:
            guild_bool = utils.str_to_bool(guild)
        except BadBoolArgument:
            log.error("Invalid bool input... must be 'true' or 'false'.")
            embed = Embed(description=f"Invalid bool input... must be 'true' or 'false'.", color=Colour.brand_red())
            await ctx.send(embed=embed)

        embed = Embed(description="Syncing commands...", color=Colour.yellow())
        await ctx.send(embed=embed)

        if guild_bool:
            self.bot.tree.copy_global_to(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            embed = Embed(description="Commands have been synced to the server.", color=Colour.brand_green())
            log.info("Commands have been synced to the server.")
        else:
            await self.bot.tree.sync()
            embed = Embed(description="Commands have been synced globally.", color=Colour.brand_green())
            log.info("Commands have been synced globally.")

        await ctx.send(embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Admin(bot))