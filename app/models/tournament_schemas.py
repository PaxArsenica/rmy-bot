import discord.utils as discord_utils
import utils.config as config
import services.tournament_service as tournament_service
from boto3.dynamodb.conditions import Key
from db.dynamodb import DynamoDb
from discord.ext.commands import Context
from enum import auto, StrEnum
from typing import Any, Self
from utils.errors import TournamentNotFound

db = DynamoDb(config.TOURNAMENTS_TABLE).table

class Participant:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, participant_dict: dict) -> Self:
        return cls(participant_dict['id'], participant_dict['name'])
  
    @classmethod
    def to_dict(cls, participant: Self) -> dict[str, Any]:
        participant_dict = {
            'id': str(participant.id),
            'name': str(participant.name)
        }

        return participant_dict

    @staticmethod
    def participant_decoder(obj: dict) -> Self:
        participant: dict = obj.get("participant")
        if participant:
            return Participant(str(participant['id']), str(participant['name']))
        return obj

class Match:
    def __init__(self, id: str, 
                       round: str, 
                       state: str, 
                       participant1: Participant = {}, 
                       participant2: Participant = {}, 
                       winner: Participant = {}, 
                       loser: Participant = {}, 
                       participant1_score: str = '', 
                       participant2_score: str = '',
                       message_id: str = '',
                       round_part: str = '1') -> None:
        self.id = id
        self.round = round
        self.state = state
        self.participant1 = participant1
        self.participant2 = participant2
        self.winner = winner
        self.loser = loser
        self.participant1_score = participant1_score
        self.participant2_score = participant2_score
        self.message_id = message_id
        self.round_part = round_part

    @classmethod
    def from_dict(cls, match_dict: dict) -> Self:
        participant1 = Participant.from_dict(match_dict['participant1']) if match_dict['participant1'] else {}
        participant2 = Participant.from_dict(match_dict['participant2']) if match_dict['participant2'] else {}
        winner = Participant.from_dict(match_dict['winner']) if match_dict['winner'] else {}
        loser = Participant.from_dict(match_dict['loser']) if match_dict['loser'] else {}
        return cls(match_dict['id'], match_dict['round'], match_dict['state'], participant1, participant2, winner, loser, match_dict['participant1_score'], match_dict['participant2_score'], match_dict['message_id'], match_dict['round_part'])

    @classmethod
    def get_loser(cls, match: Self) -> Participant:
        if match.loser:
            return match.loser
        elif match.winner:
            return match.participant1 if match.winner.id == match.participant1.id else match.participant2
        else:
            if int(match.participant1_score) < int(match.participant2_score):
                return match.participant1
            else:
                return match.participant2

    @classmethod
    def get_winner(cls, match: Self) -> Participant:
        if match.winner:
            return match.winner
        elif match.loser:
            return match.participant1 if match.loser.id == match.participant1.id else match.participant2
        else:
            if int(match.participant1_score) > int(match.participant2_score):
                return match.participant1
            else:
                return match.participant2
    
    @classmethod
    def to_dict(cls, match: Self) -> dict[str, Any]:
        match_dict = {
            'id': str(match.id),
            'round': str(match.round),
            'state': str(match.state),
            'participant1': Participant.to_dict(match.participant1) if match.participant1 else {},
            'participant2': Participant.to_dict(match.participant2) if match.participant2 else {},
            'winner': Participant.to_dict(match.winner) if match.winner else {},
            'loser': Participant.to_dict(match.loser) if match.loser else {},
            'participant1_score': str(match.participant1_score),
            'participant2_score': str(match.participant2_score),
            'message_id': str(match.message_id),
            'round_part': str(match.round_part)
        }

        return match_dict
    
    @classmethod
    async def update_match_scores(cls, ctx: Context, tournament_name: str, match: Self) -> Self:
        if match.message_id:
            msg = await ctx.fetch_message(match.message_id)
            reaction1 = discord_utils.get(msg.reactions, emoji="1️⃣")
            reaction2 = discord_utils.get(msg.reactions, emoji="2️⃣")
            match.participant1_score = str(reaction1.count-1)
            match.participant2_score = str(reaction2.count-1)
            match.winner = match.get_winner(match)
            match.loser = match.get_loser(match)
        return match

    @staticmethod
    def match_decoder(obj: dict, participants: list[Participant]) -> Self:
        match: dict = obj.get("match")
        if match:
            participant1: Participant = next(participant for participant in participants if str(participant.id) == str(match['player1_id'])) if match.get('player1_id') else {}
            participant2: Participant = next(participant for participant in participants if str(participant.id) == str(match['player2_id'])) if match.get('player2_id') else {}
            winner: Participant = {}
            loser: Participant = {}

            if participant1 and participant2:
                match str(match['winner_id']):
                    case participant1.id:
                        winner = participant1
                    case participant2.id:
                        winner = participant2

                match str(match['loser_id']):
                    case participant1.id:
                        loser = participant1
                    case participant2.id:
                        loser = participant2

            participant1_score = match['player1_votes'] if match.get('player1_votes') else ''
            participant2_score = match['player2_votes'] if match.get('player2_votes') else ''
            scores: str = match['scores_csv']
            if scores:
                scores_list: list[str] = scores.split('-')
                participant1_score = scores_list[0]
                participant2_score = scores_list[1]
            return Match(str(match['id']), str(match['round']), str(match['state']), participant1, participant2, winner, loser, participant1_score, participant2_score)
        return obj


class Tournament:
    def __init__(self, id: str, name: str, state: str, url: str, participants: list[Participant] = [], matches: list[Match] = [], round: str = '1', round_part: str = '0', round_message_id: str = '', max_rounds: str = '1', max_round_parts: list[str] = [], winner: str = '') -> None:
        self.id = id
        self.name = name
        self.state = state
        self.url = url
        self.participants = participants
        self.matches = matches
        self.round = round
        self.round_part = round_part
        self.round_message_id = round_message_id
        self.max_rounds = max_rounds
        self.max_round_parts = max_round_parts
        self.winner = winner

    @classmethod
    async def convert(cls, ctx, tournament: str) -> Self:
        db_tournament = cls.get_db_tournament(tournament)
        return tournament_service.get_api_tournament(db_tournament)
    
    @classmethod
    def from_dict(cls, tournament_dict: dict) -> Self:
        participants = list(map(Participant.from_dict, tournament_dict['participants']))
        matches = list(map(Match.from_dict, tournament_dict['matches']))
        return cls(str(tournament_dict['id']), str(tournament_dict['name']), str(tournament_dict['state']), tournament_dict['url'], participants, matches, str(tournament_dict['round']), str(tournament_dict['round_part']), str(tournament_dict['round_message_id']), str(tournament_dict['max_rounds']), tournament_dict['max_round_parts'], tournament_dict['winner'])
    
    @classmethod
    def get_db_tournament(cls, tournament: str) -> Self:
        data: dict = db.get_item(Key={'name': tournament})
        if data.get('Item'):
            return cls.from_dict(data['Item'])
        else:
            data = db.query(IndexName='id-index', KeyConditionExpression=Key('id').eq(tournament))
            if data.get('Items'):
                return cls.from_dict(data['Items'][0])
        
        raise TournamentNotFound(tournament, "Tournament not found from DB.")
    
    @classmethod
    def get_round(cls, tournament: Self) -> str:
        return f'{tournament.round} Part {tournament.round_part}' if int(tournament.round_part) > 1 else tournament.round

    @classmethod
    def to_dict(cls, tournament: Self) -> dict[str, Any]:
        tournament_dict = {
            'id': str(tournament.id),
            'name': tournament.name,
            'state': tournament.state,
            'url': tournament.url,
            'round': tournament.round,
            'round_part': tournament.round_part,
            'round_message_id': tournament.round_message_id,
            'max_rounds': tournament.max_rounds,
            'max_round_parts': tournament.max_round_parts,
            'winner': tournament.winner
        }

        participants_dict = []
        for participant in tournament.participants:
            participants_dict.append(Participant.to_dict(participant))

        matches_dict = []
        for match in tournament.matches:
            matches_dict.append(Match.to_dict(match))
            
        tournament_dict['participants'] = participants_dict
        tournament_dict['matches'] = matches_dict

        return tournament_dict

    @staticmethod
    def tournament_decoder(obj: dict) -> Self:
        tournament: dict = obj.get("tournament")
        participants = []
        matches = []
        if tournament:
            if tournament.get("participants"):
                participants: list[Participant] = list(map(Participant.participant_decoder, tournament['participants']))
                if tournament.get("matches"):
                    matches: list[Match] = [Match.match_decoder(match, participants) for match in tournament['matches']]
            return Tournament(str(tournament['id']), tournament['name'], tournament['state'], f"https://challonge.com/{str(tournament['url'])}", participants, matches)
        return obj

class TournamentState(StrEnum):
    AWAITING_REVIEW = auto()
    COMPLETE = auto()
    PENDING = auto()
    UNDERWAY = auto()