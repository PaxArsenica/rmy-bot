import requests
import os
from dotenv import load_dotenv

load_dotenv()
request_headers = {
    'Content-Type': 'application/json',
    'X-RapidAPI-Key': os.environ.get("RAPID_API_KEY"),
    'X-RapidAPI-Host': 'call-of-duty-modern-warfare.p.rapidapi.com',
}

async def get_cod_stats(username, platform):
    cod_stats = requests.get(url=f'https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/{username}/{platform}', headers=request_headers)
    print(cod_stats.text)