from base64 import b64encode
from dotenv import load_dotenv
from os import environ as env

load_dotenv()

# Env Configs
ADMINS=env['ADMINS']
AWS_ACCESS_KEY_ID=env['AWS_ACCESS_KEY_ID']
AWS_DEFAULT_REGION=env['AWS_DEFAULT_REGION']
AWS_SECRET_ACCESS_KEY=env['AWS_SECRET_ACCESS_KEY']
BOT_PREFIX=env['BOT_PREFIX']
CHALLONGE_API_KEY=env['CHALLONGE_API_KEY']
CHALLONE_API_USERNAME=env['CHALLONGE_API_USERNAME']
COMPOSE_PROJECT_NAME=env['COMPOSE_PROJECT_NAME']
LOG_FILE=env['LOG_FILE']
LOG_FORMAT=env['LOG_FORMAT']
LOG_LEVEL=env['LOG_LEVEL']
STARTUP_SYNC=env['STARTUP_SYNC']
TOKEN=env['TOKEN']

# Challonge Constants
CHALLONGE_API_HEADERS={"Authorization": f"Basic {b64encode(f'{CHALLONE_API_USERNAME}:{CHALLONGE_API_KEY}'.encode('utf-8')).decode('ascii')}", "User-Agent": "RmyBot-2.0"}
CHALLONGE_API_URL = "https://api.challonge.com/v1/tournaments"
CREATE_PARTICIPANTS_ENDPOINT = "participants/bulk_add.json"
CREATE_TOURNAMENT_ENDPOINT = ".json"
FINALIZE_TOURNAMENT_ENDPOINT = "finalize.json"
GET_MATCHES_ENDPOINT = "matches.json"
START_TOURNAMENT_ENDPOINT = "start.json"
UPDATE_MATCHES_ENDPOINT = "matches"

# DynamoDb Constants
TOURNAMENTS_TABLE='tournaments'

# Misc Constants
RMY_PERSONAL_FINANCE_ID=658400107875532810
ZIP_CODE=30303