import discord.ext.commands as commands
import services.tournament_service as tournament_service
import utils.rmy_utils as utils
import utils.tournament_utils as tournament_utils
from discord import Colour, Embed
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
        final_tournament = tournament_service.get_api_tournament(tournament)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tournaments(bot))