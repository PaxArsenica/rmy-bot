import common.utils as utils
from discord import Color, Embed, File
from discord.ext import commands
from discord.ext.commands import Bot, Context
from os import environ as env
from services.pubsub import fetch_sub_of_the_week, get_store
from typing import List

log = utils.setup_logging('Messages')

class Messages(commands.Cog, name='messages'):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.hybrid_command(name='about', description='Posts details about RmyBot.')
    async def about(self, ctx: Context) -> None:
        rmy_bot_logo = File("./img/rmybot.png", filename="rmybot.png")
        about_embed = Embed(title='RMY Bot', color=Color.red(), description=f"My name is RMY Bot v0.1. My purpose is to entertain the members of RMY with fun and useful commands. Type '{env['BOT_PREFIX']} list_commands' to learn more about what I can do.")
        about_embed.set_image(url='attachment://rmybot.png')
        await ctx.send(file=rmy_bot_logo, embed=about_embed)

    @commands.hybrid_command(name='balagadoo', description='Posts a balagadoo gif.')
    async def balagadoo(self, ctx: Context) -> None:
        await ctx.send("https://www.youtube.com/watch?v=y7Phst7PoN0")
    
    @commands.hybrid_command(name='bot', description='Posts a bot gif.')
    async def bot(self, ctx: Context) -> None:
        await ctx.send("https://tenor.com/view/you-are-bot-noob-bot-you-are-noob-ur-noob-gif-22801538")

    @commands.hybrid_command(name='flaccid', description='Rosts a flaccid gif.')
    async def flaccid(self, ctx: Context) -> None:
        await ctx.send("https://tenor.com/view/meryl-streep-flacid-gif-10066576")

    @commands.hybrid_command(name='list_commands', description='Returns all commands available.')
    async def list_commands(self, ctx: Context) -> None:
        command_list = []
        embed = Embed(title="RMY Bot Commands", color=Color.red(), description="Here's a list of my commands:")
        for command in self.bot.commands:
            command_list.append((command.name, command.description))

        command_list.sort()
        for command in command_list:
            embed.add_field(name=command[0], value=command[1], inline=False)
            
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='loot', description='Posts the loot message.')
    async def loot(self, ctx: Context) -> None:
        await ctx.send(f"It wouldn't be me if I didn't loot.")

    @commands.hybrid_command(name='pubsub', description='Posts the pubsub of the week.')
    async def pubsub(self, ctx: Context, zip_code: str = None) -> None:
        sub_response = fetch_sub_of_the_week(zip_code)
        store_response = get_store(env['ZIP_CODE']) if not zip_code else get_store(zip_code)

        embeds: List[Embed] = []
        tender = False

        if sub_response:
            for sub in sub_response:
                embed = Embed(color=Color.green())
                embed.add_field(name=sub.name, value=sub.description, inline=False)
                embed.set_image(url=sub.image)
                embeds.append(embed)
                if sub.name.lower().find('tender') != -1:
                    tender = True
            await ctx.send(content=f"This week's Publix Subs at {store_response.name} are", embeds=embeds)

            if tender:
                await ctx.send("https://tenor.com/view/lets-go-lets-goo-lest-gooooooooooooooooo-gif-19416648")
        else:
            await ctx.send("There was an error while retrieving the Sub of the Week. Please try again later.")

    @commands.hybrid_command(name='roth', description='Posts the personal finance guide.')
    async def roth(self, ctx: Context) -> None:
        personal_finance_channel = self.bot.get_channel(int(env['RMY_PERSONAL_FINANCE_ID']))
        await ctx.send(f"You telling me you don't have a Roth IRA? You better open one up right mf now! And while you're at it, check out my guide to personal finance (see the pinned post in the #{personal_finance_channel.mention} channel)!")
    

async def setup(bot: Bot) -> None:
    await bot.add_cog(Messages(bot))