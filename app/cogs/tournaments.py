import discord.ext.commands as commands
import discord.utils as discord_utils
import services.tournament_service as tournament_service
import utils.rmy_utils as utils
import utils.tournament_utils as tournament_utils
from discord import AllowedMentions, Colour, Embed, Message
from discord.ext.commands import Bot, Cog, Context
from models.tournament_schemas import Participant, Tournament

log = utils.setup_logging('tournaments')

class Tournaments(Cog, name='tournaments'):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.hybrid_command(name='add_participants', description='Adds participants to a tournament in the server. Multiple participants must be separated by ,')
    async def add_participants(self, ctx: Context, tournament: Tournament, *, participants: str) -> list[Participant]:
        participant_list = participants.split(",")
        tournament_utils.check_is_pending(tournament)
        tournament_utils.check_duplicate_participants(tournament, participant_list)

        participant_response = tournament_service.add_participants(tournament, participant_list)

        embed = Embed(description=f"Pariticipants {participant_list} successfully added to {tournament.name}.", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return participant_response
    
    @commands.hybrid_command(name='create_tournament', description='Creates a tournament in Challonge.')
    async def create_tournament(self, ctx: Context, name: str) -> Tournament:
        tournament = tournament_service.create_tournament(name)
        embed = Embed(description = f"Tournament: {tournament.name} - {tournament.id} successfully created.", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return tournament
    
    @commands.hybrid_command(name='start_round', description='Starts a tournament round in the server.')
    async def start_round(self, ctx: Context, tournament: Tournament, round: int) -> None:
        reactions = ["1️⃣", "2️⃣"]
        messages: list[Message] = []
        webhook = discord_utils.get(await ctx.channel.webhooks(), name='Round')
        if not webhook:
            webhook = await ctx.channel.create_webhook(name='Round')

        init_msg = await webhook.send(content=f'The Rmy Brackets: {tournament.name}\n{tournament.url}\n\nRound {round}', username=self.bot.user.display_name, avatar_url=self.bot.user.avatar, wait=True)
        messages.append(init_msg)
        match_template = f'1️⃣ Player1\n2️⃣ Player2'
        for match in tournament.matches:
            if str(round) == match.round:
                if match.participant1 and match.participant2:
                    temp_template = match_template
                    temp_template = temp_template.replace('Player1', match.participant1.name)
                    temp_template = temp_template.replace('Player2', match.participant2.name)
                    msg = await webhook.send(content=temp_template, allowed_mentions=AllowedMentions.none(), username=self.bot.user.display_name, avatar_url=self.bot.user.avatar, wait=True)
                    for name in reactions:
                        emoji = discord_utils.get(ctx.guild.emojis, name=name)
                        await msg.add_reaction(emoji or name)
                    messages.append(msg)
                else:
                    for message in messages:
                        await message.delete()
                    embed = Embed(description = f"Round {round} not ready yet in tournament: {tournament.name}.", color=Colour.brand_red())
                    log.info(embed.description)
                    await ctx.send(embed=embed)
        await ctx.reply(f'tournament: {tournament.name}, round: {round} ')

    @commands.hybrid_command(name='start_tournament', description='Starts a tournament in the server.')
    async def start_tournament(self, ctx: Context, tournament: Tournament) -> Tournament:
        tournament_utils.check_is_pending(tournament)
        
        start_response = tournament_service.start_tournament(tournament)

        embed = Embed(description=f"Tournament: {tournament.name} successfully started.", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return start_response
    
    @commands.hybrid_command(name='sync_tournament', description='Syncs a tournament in the server with API.')
    async def sync_tournament(self, ctx: Context, tournament: Tournament) -> Tournament:
        synced_tournament = tournament_service.get_api_tournament(tournament)
        embed = Embed(description=f"Tournament: {tournament.name} successfully updated.", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return synced_tournament

    @commands.hybrid_command(name='tournament', description='Creates a tournament in the server.')
    async def tournament(self, ctx: Context, name: str, *, participants: str) -> None:
        tournament: Tournament = await ctx.invoke(self.bot.get_command('create_tournament'), name=name)
        participant_response: list[Participant] = await ctx.invoke(self.bot.get_command('add_participants'), tournament=tournament, participants=participants)
        tournament.participants = participant_response
        await ctx.invoke(self.bot.get_command('start_tournament'), tournament=tournament)
        synced_tournament = tournament_service.get_api_tournament(tournament)
        await ctx.invoke(self.bot.get_command('start_round'), tournament=synced_tournament, round=1)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tournaments(bot))