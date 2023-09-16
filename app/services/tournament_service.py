import requests
import utils.config as config
import utils.rmy_utils as utils
from collections import defaultdict
from db.dynamodb import DynamoDb
from http import HTTPStatus
from models.tournament_schemas import Match, Participant, Tournament
from utils.errors import DuplicateTournamentError, MatchRetrieveError, NoParticipantsError, ParticipantError, TournamentCreateError, TournamentNotFound, TournamentStartError
from requests import HTTPError, Response
from typing import Any

log = utils.setup_logging('tournament_service')
db = DynamoDb(table=config.TOURNAMENTS_TABLE).table

def add_participants(tournament: Tournament, participants: list[str]) -> list[Participant]:
    data_dict = defaultdict(list)
    for participant in participants:
        data_dict["participants[][name]"].append(participant.strip())

    try:
        response = requests.post(f'{config.CHALLONGE_API_URL}/{tournament.id}/{config.CREATE_PARTICIPANTS_ENDPOINT}', headers=config.CHALLONGE_API_HEADERS, data=data_dict)
        response.raise_for_status()
        response.json(object_hook=Participant.participant_decoder)
        tournament.participants.extend(response.json(object_hook=Participant.participant_decoder))
        tournament_dict = Tournament.to_dict(tournament)
        db.update_item(Key={'name': str(tournament.name)},
                       UpdateExpression="SET participants = :participants_val", 
                       ExpressionAttributeValues={
                           ":participants_val": tournament_dict["participants"]
                       })
        return tournament.participants
    except Exception as err:
        log.error(f"Error adding participants {participants}: {str(err)}")
        raise ParticipantError(tournament.name, participants, f"Error adding participants")

def create_tournament(name: str) -> Tournament:
    try:
        Tournament.get_db_tournament(name)
        raise DuplicateTournamentError(name)
    except TournamentNotFound:
        pass

    payload = {}
    payload['tournament[name]'] = name
    try:
        response = requests.post(f'{config.CHALLONGE_API_URL}{config.CREATE_TOURNAMENT_ENDPOINT}', headers=config.CHALLONGE_API_HEADERS, data=payload)
        response.raise_for_status()
        tournament: Tournament = response.json(object_hook=Tournament.tournament_decoder)
        tournament_dict = Tournament.to_dict(tournament)
        db.put_item(Item=tournament_dict)
        return tournament
    except Exception as err:
        log.error(f"Error during tournament creation: {str(err)}")
        raise TournamentCreateError(name)
    
def get_api_tournament(tournament: Tournament) -> Tournament:
    params = {'include_participants': 1, 'include_matches': 1}
    try:
        response = requests.get(f'{config.CHALLONGE_API_URL}/{tournament.id}{config.CREATE_TOURNAMENT_ENDPOINT}', headers=config.CHALLONGE_API_HEADERS, params=params)
        response.raise_for_status()
        tournament_response: Tournament = response.json(object_hook=Tournament.tournament_decoder)
        tournament_dict = Tournament.to_dict(tournament_response)
        db.update_item(Key={'name': str(tournament.name)},
                       UpdateExpression="SET #state = :state_val, participants = :participants_val, matches = :matches_val", 
                       ExpressionAttributeNames={
                           "#state": "state"
                       },
                       ExpressionAttributeValues={
                           ":state_val": tournament_dict["state"],
                           ":participants_val": tournament_dict["participants"],
                           ":matches_val": tournament_dict["matches"]
                       })
        return tournament_response
    except Exception as err:
        log.error(f"Error getting tournament: {str(err)}")
        raise TournamentNotFound(tournament, "Tournament not found from API.")

def get_matches(tournament: Tournament) -> list[Match]:
    payload = {}
    payload['state'] = 'open'

    if tournament.participants:
        try:
            response = requests.get(f'{config.CHALLONGE_API_URL}/{tournament.id}/{config.GET_MATCHES_ENDPOINT}', headers=config.CHALLONGE_API_HEADERS, data=payload)
            response.raise_for_status()
            return [Match.match_decoder(match, tournament.participants) for match in response.json()]
        except Exception as err:
            log.error(f"Error getting matches: {str(err)}")
            raise MatchRetrieveError(tournament.name)
    else:
        raise NoParticipantsError(tournament.name, "Cannot retrieve matches that have no participants")

def start_tournament(tournament: Tournament) -> Tournament:
    try:
        response = requests.post(f'{config.CHALLONGE_API_URL}/{tournament.id}/{config.START_TOURNAMENT_ENDPOINT}', headers=config.CHALLONGE_API_HEADERS)
        response.raise_for_status()
        tournament_response: Tournament = response.json(object_hook=Tournament.tournament_decoder)
        tournament_dict = Tournament.to_dict(tournament_response)
        db.update_item(Key={'name': str(tournament.name)},
                       UpdateExpression="SET #state = :state_val",
                       ExpressionAttributeNames={
                           "#state": "state"
                       },
                       ExpressionAttributeValues={
                           ":state_val": tournament_dict["state"]
                       })
        return tournament_response
    except HTTPError as http_err:
        response: Response = http_err.response
        if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            response_json: dict = response.json()
            errors: list = response_json.get('errors')
            if errors:
                log.error(errors[0])
                raise TournamentStartError(tournament.name, errors[0])
    except Exception as err:
        log.error(f"Error starting tournament: {str(err)}")
        raise TournamentStartError(tournament.name)
