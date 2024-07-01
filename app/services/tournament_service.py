import requests
import utils.config as config
import utils.rmy_utils as utils
from collections import defaultdict
from db.dynamodb import DynamoDb
from discord.ext.commands import Context
from http import HTTPStatus
from models.tournament_schemas import Match, Participant, Tournament
from requests import HTTPError, Response
from utils.errors import DuplicateTournamentError, MatchRetrieveError, MatchUpdateError, NoParticipantsError, ParticipantError, TournamentCreateError, TournamentFinishError, TournamentNotFound, TournamentStartError

log = utils.setup_logging('tournament_service')
db = DynamoDb(table=config.TOURNAMENTS_TABLE).table

def add_participants(tournament: Tournament, participants: list[str]) -> Tournament:
    data_dict = defaultdict(list)
    for participant in participants:
        data_dict["participants[][name]"].append(participant.strip())

    try:
        response = requests.post(f'{config.CHALLONGE_API_URL}/{tournament.id}/{config.CREATE_PARTICIPANTS_ENDPOINT}', headers=config.CHALLONGE_API_HEADERS, data=data_dict)
        response.raise_for_status()
        tournament.participants.extend(response.json(object_hook=Participant.participant_decoder))
        tournament_dict = Tournament.to_dict(tournament)
        db.update_item(Key={'name': str(tournament.name)},
                       UpdateExpression="SET participants = :participants_val", 
                       ExpressionAttributeValues={
                           ":participants_val": tournament_dict["participants"]
                       })
        return tournament
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
    
async def finish_round(ctx: Context, tournament: Tournament) -> Tournament:
    updated_matches: list[Match] = []
    if not int(tournament.round_part) > 0:
        start_round_mention = await utils.mention_command(ctx.bot, 'start_round')
        raise MatchUpdateError(tournament.name, f'Round {tournament.round} has not started yet.\nWhen you are ready to begin the round please use {start_round_mention}')
    for match in tournament.matches:
        updated_match: Match = match
        if match.round == tournament.round:
            match = await Match.update_match_scores(ctx, tournament.name, match)
            if match.participant1_score and match.participant2_score:
                updated_match = update_match(tournament, match)
                updated_match.round_part = match.round_part
                updated_match.message_id = match.message_id
        updated_matches.append(updated_match)

    tournament.matches = updated_matches
    tournament_dict = Tournament.to_dict(tournament)
    try:
        db.update_item(Key={'name': str(tournament.name)},
                        UpdateExpression="SET matches = :matches_val",
                        ExpressionAttributeValues={
                            ":matches_val": tournament_dict["matches"]
                        })
        return tournament
    except Exception as err:
        log.error(f"Error getting tournament: {str(err)}")
        raise MatchUpdateError(tournament.name, f'Error updating matches in db.')

def finish_tournament(tournament: Tournament) -> Tournament:
    params = {'include_participants': 1, 'include_matches': 1}
    try:
        response = requests.post(f'{config.CHALLONGE_API_URL}/{tournament.id}/{config.FINALIZE_TOURNAMENT_ENDPOINT}', headers=config.CHALLONGE_API_HEADERS, params=params)
        response.raise_for_status()
        tournament_response: Tournament = response.json(object_hook=Tournament.tournament_decoder)

        for db_match in tournament.matches:
            for api_match in tournament_response.matches:
                if db_match.id == api_match.id:
                    api_match.message_id = db_match.message_id
                    api_match.round_part = db_match.round_part
                    if api_match.round == tournament.max_rounds and api_match.round_part == tournament.max_round_parts[int(tournament.max_rounds)-1]:
                        tournament_response.winner = api_match.get_winner(api_match).name
        tournament_response.round = tournament.round
        tournament_response.round_part = tournament.round_part
        tournament_response.round_message_id = tournament.round_message_id
        tournament_response.max_rounds = tournament.max_rounds
        tournament_response.max_round_parts = tournament.max_round_parts

        tournament_dict = Tournament.to_dict(tournament_response)
        db.update_item(Key={'name': str(tournament.name)},
                       UpdateExpression="SET #state = :state_val, participants = :participants_val, matches = :matches_val, round = :round_val, round_part = :round_part_val, round_message_id = :round_message_id_val, max_rounds = :max_rounds_val, max_round_parts = :max_round_parts_val, winner = :winner_val",
                       ExpressionAttributeNames={
                           "#state": "state"
                       },
                       ExpressionAttributeValues={
                           ":state_val": tournament_dict["state"],
                           ":participants_val": tournament_dict["participants"],
                           ":matches_val": tournament_dict["matches"],
                           ":round_val": tournament_dict["round"],
                           ":round_part_val": tournament_dict["round_part"],
                           ":round_message_id_val": tournament_dict["round_message_id"],
                           ":max_rounds_val": tournament_dict["max_rounds"],
                           ":max_round_parts_val": tournament_dict["max_round_parts"],
                           ":winner_val": tournament_dict["winner"]
                       })
        return tournament_response
    except Exception as err:
        log.error(f"Error during tournament finalization: {str(err)}")
        raise TournamentFinishError(tournament)

def get_api_tournament(tournament: Tournament) -> Tournament:
    params = {'include_participants': 1, 'include_matches': 1}
    try:
        response = requests.get(f'{config.CHALLONGE_API_URL}/{tournament.id}{config.CREATE_TOURNAMENT_ENDPOINT}', headers=config.CHALLONGE_API_HEADERS, params=params)
        response.raise_for_status()
        tournament_response: Tournament = response.json(object_hook=Tournament.tournament_decoder)

        for db_match in tournament.matches:
            for api_match in tournament_response.matches:
                if db_match.id == api_match.id:
                    api_match.message_id = db_match.message_id
                    api_match.round_part = db_match.round_part
        tournament_response.round = tournament.round
        tournament_response.round_part = tournament.round_part
        tournament_response.round_message_id = tournament.round_message_id
        tournament_response.max_rounds = tournament.max_rounds
        tournament_response.max_round_parts = tournament.max_round_parts
        tournament_response.winner = tournament.winner

        tournament_dict = Tournament.to_dict(tournament_response)
        db.update_item(Key={'name': str(tournament.name)},
                       UpdateExpression="SET #state = :state_val, participants = :participants_val, matches = :matches_val, round = :round_val, round_part = :round_part_val, round_message_id = :round_message_id_val, max_rounds = :max_rounds_val, max_round_parts = :max_round_parts_val, winner = :winner_val",
                       ExpressionAttributeNames={
                           "#state": "state"
                       },
                       ExpressionAttributeValues={
                           ":state_val": tournament_dict["state"],
                           ":participants_val": tournament_dict["participants"],
                           ":matches_val": tournament_dict["matches"],
                           ":round_val": tournament_dict["round"],
                           ":round_part_val": tournament_dict["round_part"],
                           ":round_message_id_val": tournament_dict["round_message_id"],
                           ":max_rounds_val": tournament_dict["max_rounds"],
                           ":max_round_parts_val": tournament_dict["max_round_parts"],
                           ":winner_val": tournament_dict["winner"]
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
                       UpdateExpression="SET #state = :state_val, matches = :matches_val, max_rounds = :max_rounds_val, max_round_parts = :max_round_parts_val",
                       ExpressionAttributeNames={
                           "#state": "state"
                       },
                       ExpressionAttributeValues={
                           ":state_val": tournament_dict["state"],
                           ":matches_val": tournament_dict["matches"],
                           ":max_rounds_val": tournament_dict["max_rounds"],
                           ":max_round_parts_val": tournament_dict["max_round_parts"]
                       })
        return tournament_response
    except HTTPError as http_err:
        response: Response = http_err.response
        if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            response_json: dict = response.json()
            errors: list = response_json.get('errors')
            if errors:
                err = next(iter(errors))
                log.error(err)
                raise TournamentStartError(tournament.name, err)
    except Exception as err:
        log.error(f"Error starting tournament: {str(err)}")
        raise TournamentStartError(tournament.name)

def update_match(tournament: Tournament, match: Match) -> Match:
    payload = {}
    payload['match[scores_csv]'] = f"{match.participant1_score}-{match.participant2_score}"
    payload['match[winner_id]'] = Match.get_winner(match).id
    payload['match[player1_votes]'] = match.participant1_score
    payload['match[player2_votes]'] = match.participant2_score

    try:
        response = requests.put(f'{config.CHALLONGE_API_URL}/{tournament.id}/{config.UPDATE_MATCHES_ENDPOINT}/{match.id}.json', headers=config.CHALLONGE_API_HEADERS, data=payload)
        response.raise_for_status()
        return next(iter([Match.match_decoder(match, tournament.participants) for match in [response.json()]]))
    except HTTPError as http_err:
        response: Response = http_err.response
        if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            response_json: dict = response.json()
            errors: list = response_json.get('errors')
            if errors:
                err = next(iter(errors))
                log.error(err)
                raise MatchUpdateError(tournament.name, err)
    except Exception as err:
        log.error(f"Error during match update: {str(err)}")
        raise MatchUpdateError(tournament.name, f'Error updating match {match.id}: {match.participant1.name}-{match.participant2.name}')
