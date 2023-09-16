

from models.tournament_schemas import Tournament, TournamentState
from utils.errors import DuplicateParticipantError, TournamentStateError


def check_is_pending(tournament: Tournament) -> None:
    if tournament.state != TournamentState.PENDING:
        raise TournamentStateError(tournament.name, f"Cannot add participants. Tournament {tournament.state}.")
    
def check_duplicate_participants(tournament: Tournament, participants: str) -> None:
    duplicate_participants = []
    for participant in tournament.participants:
        if participant.name in participants:
            duplicate_participants.append(participant.name)

    if duplicate_participants:
        raise DuplicateParticipantError(tournament.name, duplicate_participants)