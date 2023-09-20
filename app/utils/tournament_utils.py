import utils.rmy_utils as utils
from discord.ext.commands import Context
from models.tournament_schemas import Match, Tournament, TournamentState
from utils.errors import DuplicateParticipantError, TournamentMaxRoundsError, TournamentStateError

async def check_state(ctx: Context, tournament: Tournament, tournament_state: str, message: str = '') -> None:
    if tournament.state == TournamentState.AWAITING_REVIEW:
        finish_tournament_mention = await utils.mention_command(ctx.bot, 'finish_tournament')
        current_round_message = await ctx.fetch_message(int(tournament.round_message_id))
        err_message = f"{message} {tournament.name} is awaiting review.\nRound -> {current_round_message.jump_url}\nWhen you are ready to finish the tournament please use {finish_tournament_mention}."

    elif tournament.state == TournamentState.COMPLETE:
        current_round_message = await ctx.fetch_message(int(tournament.round_message_id))
        err_message = f"{message} {tournament.name} is {tournament.state}.\nTournament Finals -> {current_round_message.jump_url}"

    elif tournament.state == TournamentState.PENDING:
        err_message = f"{message} {tournament.name} is {tournament.state}."
        if len(tournament.participants) < 2:
            err_message = f"{err_message}\nPlease add at least 2 participants before you begin the tournament."
        start_tournament_mention = await utils.mention_command(ctx.bot, 'start_tournament')
        err_message = f"{err_message}\nWhen you are ready to begin the tournament please use {start_tournament_mention}."

    elif tournament.state == TournamentState.UNDERWAY:
        if int(tournament.max_round_parts[int(tournament.round)-1]) <= 1:
            err_message = f"{message} {tournament.name} is {tournament.state} in Round {tournament.round} of {tournament.max_rounds}."
        else:
            err_message = f"{message} {tournament.name} is {tournament.state} in Round {tournament.round} (Part {tournament.round_part} of {tournament.max_round_parts[int(tournament.round)-1]}) of {tournament.max_rounds}."

        if tournament.round_message_id:
            current_round_message = await ctx.fetch_message(int(tournament.round_message_id))
            err_message = f'{err_message}\nRound -> {current_round_message.jump_url}'
        else:
            start_round_mention = await utils.mention_command(ctx.bot, 'start_round')
            err_message = f'{err_message}\nWhen you are ready to start the first round please use {start_round_mention}'

    else:
        err_message = f"{message} {tournament.name} is {tournament.state}."

    if tournament.state != tournament_state:
        raise TournamentStateError(tournament.name, err_message)

def check_max_rounds(tournament: Tournament, round: int, msg: str = '') -> None:
    if round > int(tournament.max_rounds):
        raise TournamentMaxRoundsError(tournament.name, f"Round {tournament.max_rounds} was the final round.{msg}")

def check_max_round_parts(tournament: Tournament, round: int, round_part: int, msg: str = '') -> tuple[int, int]:
    check_max_rounds(tournament, round, msg)
    if round_part > int(tournament.max_round_parts[round-1]):
        round += 1
        round_part = 1
        check_max_rounds(tournament, round, msg)
    return round, round_part

    
def check_duplicate_participants(tournament: Tournament, participants: str) -> None:
    duplicate_participants = []
    for participant in tournament.participants:
        if participant.name in participants:
            duplicate_participants.append(participant.name)

    if duplicate_participants:
        raise DuplicateParticipantError(tournament.name, duplicate_participants)

def split_match_rounds(tournament: Tournament) -> tuple[list[Match], str, list[str]]:
    round_part_count = 0
    round_part = 1
    max_rounds = 1
    match_list: list[Match] = []

    for match in tournament.matches:
        max_rounds = int(match.round) if int(match.round) > max_rounds else max_rounds


    max_round_part_list: list[str] = ['1']*max_rounds
    for round in range(1, max_rounds+1):
        round_part_count = 0
        round_part = 1
        for match in tournament.matches:
            if round_part_count >= 8:
                round_part_count = 0
                round_part += 1
            if int(match.round) == round:
                match.round_part = str(round_part)
                round_part_count += 1
                match_list.append(match)
                max_round_part_list[round-1]=str(round_part)

    return match_list, str(max_rounds), max_round_part_list