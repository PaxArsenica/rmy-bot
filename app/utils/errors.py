from discord.ext.commands import CheckFailure, CommandError

class RmyError(CommandError):
    def __init__(self, message: str="An unknown RmyError occurred.") -> None:
        self.message = message
        super().__init__(self.message)

class DuplicateParticipantError(RmyError):
    def __init__(self, tournament: str, participants: list[str], message: str="Cannot add duplicate participants.") -> None:
        self.tournament = tournament
        self.participants = participants
        self.message = f"{self.tournament}: {message} -> {participants}"
        super().__init__(self.message)

class DuplicateTournamentError(RmyError):
    def __init__(self, tournament: str, message: str="Cannot add duplicate tournament") -> None:
        self.tournament = tournament
        self.message = f"{self.tournament}: {message}"
        super().__init__(self.message)

class MatchRetrieveError(RmyError):
    def __init__(self, tournament: str, message: str="Error retrieving API matches") -> None:
        self.tournament = tournament
        self.message = f"{self.tournament}: {message}"
        super().__init__(self.message)

class MatchUpdateError(RmyError):
    def __init__(self, tournament: str, message: str="Error updating API match.") -> None:
        self.tournament = tournament
        self.message = f"{self.tournament}: {message}"
        super().__init__(self.message)

class NoParticipantsError(RmyError):
    def __init__(self, tournament: str, message: str="Does not have any participants") -> None:
        self.tournament = tournament
        self.message = f"{self.tournament}: {message}"
        super().__init__(self.message)

class NotAdmin(CheckFailure):
    def __init__(self, message: str="Not an admin.") -> None:
        self.message = message
        super().__init__(self.message)

class ParticipantError(RmyError):
    def __init__(self, tournament: str, participants: list[str], message: str="A Participant Error occurred.") -> None:
        self.tournament = tournament
        self.participants = participants
        self.message = f"{self.tournament}: {message} -> {participants}"
        super().__init__(self.message)

class TournamentCreateError(RmyError):
    def __init__(self, tournament: str, message: str="Error creating tournament") -> None:
        self.tournament = tournament
        self.message = f"{message}: {self.tournament}."
        super().__init__(self.message)

class TournamentFinishError(RmyError):
    def __init__(self, tournament: str, message: str="Error finalizing tournament") -> None:
        self.tournament = tournament
        self.message = f"{self.tournament}: {message}."
        super().__init__(self.message)

class TournamentMaxRoundsError(RmyError):
    def __init__(self, tournament: str, message: str="Max rounds exceeded") -> None:
        self.tournament = tournament
        self.message = f"{self.tournament}: {message}."
        super().__init__(self.message)

class TournamentNotFound(RmyError):
    def __init__(self, tournament: str, message: str="Tournament not found.") -> None:
        self.tournament = tournament
        self.message = f"{self.tournament}: {message}"
        super().__init__(self.message)

class TournamentStartError(RmyError):
    def __init__(self, tournament: str, message: str="Error starting tournament") -> None:
        self.tournament = tournament
        self.message = f"{message}: {self.tournament}."
        super().__init__(self.message)

class TournamentStateError(RmyError):
    def __init__(self, tournament: str, message: str="Tournament already started.") -> None:
        self.tournament = tournament
        self.message = f"{self.tournament}: {message}"
        super().__init__(self.message)