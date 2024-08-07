import discord.ext.commands as commands
import os
import services.pubsub_service as pubsub_service
import utils.config as config
import utils.rmy_utils as utils
from collections import namedtuple
from discord import Colour, Embed, File, Member
from discord.ext.commands import Bot, Cog, Context

log = utils.setup_logging('Messages')

class Messages(Cog, name='messages'):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.hybrid_command(name='about', description='Posts details about RmyBot.')
    async def about(self, ctx: Context) -> None:
        img_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "rmybot.png"))

        rmy_bot_logo = File(img_path, filename="rmybot.png")
        about_embed = Embed(title='RMY Bot', color=Colour.red(), description=f"My name is RMY Bot 2.0. My purpose is to entertain the members of RMY with fun and useful commands. Type '{config.BOT_PREFIX}list_commands' to learn more about what I can do.")
        about_embed.set_image(url='attachment://rmybot.png')
        await ctx.send(file=rmy_bot_logo, embed=about_embed)

    @commands.hybrid_command(name='balagadoo', description='Posts a balagadoo gif.')
    async def balagadoo(self, ctx: Context) -> None:
        await ctx.send("https://www.youtube.com/watch?v=y7Phst7PoN0")
    
    @commands.hybrid_command(name='bot', description='Posts a bot gif.')
    async def bot(self, ctx: Context) -> None:
        await ctx.send("https://tenor.com/view/you-are-bot-noob-bot-you-are-noob-ur-noob-gif-22801538")

    @commands.hybrid_command(name='flaccid', description='Posts a flaccid gif.')
    async def flaccid(self, ctx: Context) -> None:
        await ctx.send("https://tenor.com/view/meryl-streep-flacid-gif-10066576")

    @commands.hybrid_command(name='list_commands', description='Returns all commands available.')
    async def list_commands(self, ctx: Context) -> None:
        Command = namedtuple('Command', ['name', 'description'])
        command_list: list[Command] = []
        admin_command_list: list[Command] = []
        embed = Embed(title="RMY Bot Commands", color=Colour.green(), description="Here's a list of my commands:")

        for command in self.bot.commands:
            rmy_command = Command(command.name, command.description)
            if command.cog_name == 'admin':
                if utils.is_admin(ctx.author.id):
                    admin_command_list.append(rmy_command)
            else:
                command_list.append(rmy_command)
                
        if admin_command_list:
            admin_embed = Embed(title="RMY Bot Commands", color=Colour.red(), description="Here's a list of my admin commands:")
            admin_command_list.sort()
            for command in admin_command_list:
                admin_embed.add_field(name=command.name, value=command.description, inline=False)
            await ctx.author.send(embed=admin_embed)

        command_list.sort()
        for command in command_list:
            embed.add_field(name=command.name, value=command.description, inline=False)
            
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='loot', description='Posts the loot message.')
    async def loot(self, ctx: Context) -> None:
        await ctx.send(f"It wouldn't be me if I didn't loot.")

    @commands.hybrid_command(name='pubsub', description='Posts the pubsub of the week.')
    async def pubsub(self, ctx: Context, zip_code: str='') -> None:
        subs, store = pubsub_service.fetch_sub_of_the_week(zip_code)

        embeds: list[Embed] = []
        tender = False

        if subs:
            for sub in subs:
                embed = Embed(color=Colour.green())
                embed.add_field(name=sub.name, value=sub.description, inline=False)
                embed.set_image(url=sub.image)
                embeds.append(embed)
                if sub.name.lower().find('tender') != -1:
                    tender = True
            await ctx.send(content=f"This week's Publix Subs at {store.name} are", embeds=embeds)

            if tender:
                await ctx.send("https://tenor.com/view/lets-go-lets-goo-lest-gooooooooooooooooo-gif-19416648")
        else:
            embed = Embed(description='There was an error while retrieving the Sub of the Week. Please try again later.', color=Colour.brand_red())
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='roth', description='Posts the personal finance guide.')
    async def roth(self, ctx: Context) -> None:
        personal_finance_channel = self.bot.get_channel(int(config.RMY_PERSONAL_FINANCE_ID))
        await ctx.send(f"You telling me you don't have a Roth IRA? You better open one up right mf now! And while you're at it, check out my guide to personal finance (see the pinned post in the #{personal_finance_channel.mention} channel)!")

    @commands.hybrid_command(name='slap', description='Slaps someone in the discord.')
    async def slap(self, ctx: Context, member: Member, reason: str = '') -> None:
        await ctx.send(f'{ctx.author.mention} slapped {member.mention} because {reason}') if reason else await ctx.send(f'{ctx.author.mention} slapped {member.mention}')

    @commands.hybrid_command(name='ydr', description="Y'ALL DON'T READ!")
    async def ydr(self, ctx: Context, member: Member = None) -> None:
        await ctx.invoke(self.bot.get_command('slap'), member=member, reason="THEY **DON'T READ!**") if member else await ctx.send(f"# **Y'ALL DON'T READ!**")
    

async def setup(bot: Bot) -> None:
    await bot.add_cog(Messages(bot))