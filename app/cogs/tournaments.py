import discord.ext.commands as commands
import discord.utils as discord_utils
import services.tournament_service as tournament_service
import utils.rmy_utils as utils
import utils.tournament_utils as tournament_utils
from discord import Colour, Embed, Message
from discord.ext.commands import Bot, Cog, Context
from models.tournament_schemas import Participant, Tournament, TournamentState

log = utils.setup_logging('tournaments')

class Tournaments(Cog, name='tournaments'):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @commands.hybrid_command(name='add_participants', description='Adds participants to a tournament in the server. Multiple participants must be separated by ,')
    async def add_participants(self, ctx: Context, tournament: Tournament, *, participants: str) -> list[Participant]:
        participant_list = participants.split(",")
        await tournament_utils.check_state(ctx, tournament, TournamentState.PENDING, "Cannot add participants.")
        await ctx.defer()
        tournament_utils.check_duplicate_participants(tournament, participant_list)
        tournament = tournament_service.add_participants(tournament, participant_list)

        if len(tournament.participants) < 2:
            add_participants_mention = await utils.mention_command(ctx.bot, 'add_participants')
            message = f"Please add at least one more participant. {add_participants_mention}"
        else:
            start_tournament_mention = await utils.mention_command(ctx.bot, 'start_tournament')
            message = f"When you are ready to begin the tournament please use {start_tournament_mention}"

        embed = Embed(description=f"Pariticipants {participant_list} successfully added to {tournament.name}.\nTournament -> {tournament.url}\n{message}", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return tournament.participants

    @commands.hybrid_command(name='finish_round', description='Finishes current round in tournament.')
    async def finish_round(self, ctx: Context, tournament: Tournament) -> Tournament:
        await tournament_utils.check_state(ctx, tournament, TournamentState.UNDERWAY, f"Cannot finish round.")
        await ctx.defer()
        tournament = await tournament_service.finish_round(ctx, tournament)
        synced_tournament = tournament_service.get_api_tournament(tournament)
        current_round_message = await ctx.fetch_message(int(tournament.round_message_id))
        if synced_tournament.round == tournament.max_rounds and (tournament.round_part == '0' or tournament.round_part == tournament.max_round_parts[int(tournament.round)-1]):
            finish_tournament_mention = await utils.mention_command(ctx.bot, 'finish_tournament')
            next_message = f'\nThis was the final round {current_round_message.jump_url}.\nWhen you are ready to finish the tournament please use {finish_tournament_mention}'
        else:
            start_round_mention = await utils.mention_command(ctx.bot, 'start_round')
            next_message = f'\nCurrent Round: {current_round_message.jump_url}\nWhen you are ready to begin the next round please use {start_round_mention}'
        embed = Embed(description = f"Tournament: {synced_tournament.name} Round: {Tournament.get_round(synced_tournament)} successfully finished.{next_message}", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return synced_tournament

    @commands.hybrid_command(name='finish_tournament', description='Finishes current round in tournament.')
    async def finish_tournament(self, ctx: Context, tournament: Tournament) -> Tournament:
        await tournament_utils.check_state(ctx, tournament, TournamentState.AWAITING_REVIEW, f"Cannot finish Tournament.")
        await ctx.defer()
        tournament = tournament_service.finish_tournament(tournament)
        synced_tournament = tournament_service.get_api_tournament(tournament)
        embed = Embed(description = f"Tournament: {synced_tournament.name} successfully finished.", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)

        webhook = discord_utils.get(await ctx.channel.webhooks(), name='rmy')
        if not webhook:
            webhook = await ctx.channel.create_webhook(name='rmy')

        await webhook.send(content=f"And the winner of **{tournament.name}** is...\n# {tournament.winner}!\n[LFG!](https://tenor.com/view/lets-go-lets-goo-lest-gooooooooooooooooo-gif-19416648)", username=self.bot.user.display_name, avatar_url=self.bot.user.avatar, wait=True)

        return synced_tournament
    
    @commands.hybrid_command(name='create_tournament', description='Creates a tournament in Challonge.')
    async def create_tournament(self, ctx: Context, name: str) -> Tournament:
        await ctx.defer()
        tournament = tournament_service.create_tournament(name)
        add_participants_mention = await utils.mention_command(ctx.bot, 'add_participants')
        embed = Embed(description = f"Tournament: {tournament.name} - {tournament.id} successfully created.\nTournament -> {tournament.url}\nPlease add at least 2 participants using {add_participants_mention}", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return tournament
    
    @commands.hybrid_command(name='start_round', description='Starts next tournament round in the server.')
    async def start_round(self, ctx: Context, tournament: Tournament) -> None:
        await tournament_utils.check_state(ctx, tournament, TournamentState.UNDERWAY, f"Cannot start round.")
        await ctx.defer()
        finish_round_mention = await utils.mention_command(ctx.bot, 'finish_round')
        round_message_id = tournament.round_message_id if tournament.round_message_id else None
        round_message = None
        if round_message_id:
            round_message_obj = await ctx.fetch_message(int(round_message_id))
            round_message = f'\nRound -> {round_message_obj.jump_url}\nWhen you are ready to finish the round please use {finish_round_mention}'
        round, round_part = tournament_utils.check_max_round_parts(tournament, int(tournament.round), int(tournament.round_part)+1, round_message)
        reply = True
        reactions = ["1️⃣", "2️⃣"]
        messages: list[Message] = []
        webhook = discord_utils.get(await ctx.channel.webhooks(), name='rmy')
        if not webhook:
            webhook = await ctx.channel.create_webhook(name='rmy')

        if tournament.max_round_parts[round-1] == '1':
            init_msg_content = f'The Rmy Brackets: [{tournament.name}]({tournament.url})\n\nRound {round}'
            match int(tournament.max_rounds)-int(tournament.round):
                case 0:
                    init_msg_content = f'{init_msg_content} (Finals)'
                case 1:
                    init_msg_content = f'{init_msg_content} (Semi Finals)'
                case 2:
                    init_msg_content = f'{init_msg_content} (Quarter Finals)'
                case _:
                    init_msg_content = init_msg_content
        else:
            init_msg_content = f'The Rmy Brackets: [{tournament.name}]({tournament.url})\n\nRound {round} (Part {round_part} of {tournament.max_round_parts[round-1]})'

        init_msg = await webhook.send(content=init_msg_content, username=self.bot.user.display_name, avatar_url=self.bot.user.avatar, wait=True)
        messages.append(init_msg)
        match_template = f'1️⃣ Player1\n2️⃣ Player2'

        for match in tournament.matches:
            if str(round) == match.round and str(round_part) == match.round_part:
                if match.message_id:
                    existing_message = await ctx.fetch_message(int(match.message_id))
                    await init_msg.delete()
                    embed = Embed(description = f"Round {round} (Part {round_part} of {tournament.max_round_parts[round-1]}) already started in tournament: {tournament.name}.\n{existing_message.jump_url}", color=Colour.brand_red())
                    log.info(embed.description)
                    await ctx.send(embed=embed)
                    reply = False
                    break
                else:
                    if match.participant1 and match.participant2:
                        temp_template = match_template
                        temp_template = temp_template.replace('Player1', match.participant1.name)
                        temp_template = temp_template.replace('Player2', match.participant2.name)
                        msg = await webhook.send(content=temp_template, username=self.bot.user.display_name, avatar_url=self.bot.user.avatar, wait=True)
                        match.message_id = str(msg.id)
                        for name in reactions:
                            emoji = discord_utils.get(ctx.guild.emojis, name=name)
                            await msg.add_reaction(emoji or name)
                        messages.append(msg)
                    else:
                        for message in messages:
                            await message.delete()
                        round_message = await ctx.fetch_message(int(tournament.round_message_id))
                        embed = Embed(description = f"Round {round} not ready yet in tournament: {tournament.name}.\nRound {tournament.round} is in progress {round_message.jump_url}\nWhen voting is complete for Round {tournament.round} use {finish_round_mention}", color=Colour.brand_red())
                        log.info(embed.description)
                        await ctx.send(embed=embed)
                        reply = False
                        break

        if reply:
            tournament.round = round
            tournament.round_part = round_part
            tournament.round_message_id = init_msg.id
            tournament_service.get_api_tournament(tournament)
            finish_round_mention = await utils.mention_command(ctx.bot, 'finish_round')
            embed = Embed(description=f"Round successfully started.\nWhen you are ready to finish the round please use {finish_round_mention}", color=Colour.brand_green())
            log.info(embed.description)
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='start_tournament', description='Starts a tournament in the server.')
    async def start_tournament(self, ctx: Context, tournament: Tournament) -> Tournament:
        await tournament_utils.check_state(ctx, tournament, TournamentState.PENDING, f"Cannot start tournament.")
        await ctx.defer()
        
        start_response = tournament_service.start_tournament(tournament)

        synced_tournament = tournament_service.get_api_tournament(start_response)
        matches, max_rounds, max_round_part_list = tournament_utils.split_match_rounds(synced_tournament)
        synced_tournament.matches = matches
        synced_tournament.max_rounds = max_rounds
        synced_tournament.max_round_parts = max_round_part_list
        synced_tournament = tournament_service.get_api_tournament(synced_tournament)

        start_round_mention = await utils.mention_command(ctx.bot, 'start_round')
        embed = Embed(description=f"Tournament: {tournament.name} successfully started.\nTournament -> {tournament.url}\nWhen you are ready to begin the first round please use {start_round_mention}", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return synced_tournament
    
    @commands.command(name='sync_tournament', description='Syncs a tournament in the server with API.')
    async def sync_tournament(self, ctx: Context, tournament: Tournament) -> Tournament:
        await ctx.defer()
        synced_tournament = tournament_service.get_api_tournament(tournament)
        embed = Embed(description=f"Tournament: {tournament.name} successfully updated.", color=Colour.brand_green())
        log.info(embed.description)
        await ctx.send(embed=embed)
        return synced_tournament


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tournaments(bot))