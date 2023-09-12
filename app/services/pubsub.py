import common.utils as utils
import html
import requests
from models.pubsub_schemas import Store, Sub
from os import environ as env
from typing import Tuple

log = utils.setup_logging('pubsub')
defaultStore = Store("00776", "Publix at Piedmont")

def fetch_sub_of_the_week(zip_code: str = "") -> Tuple[list[Sub], Store]:
    #Sub of the Week
    sotw: list[Sub] = []
    store = get_store(env['ZIP_CODE']) if not zip_code else get_store(zip_code)

    try:
        response = requests.request("GET", f"https://services.publix.com/api/v3/product/SearchMultiCategory?storeNumber={store.id}&sort=popularityrank+asc,+titlecopy+asc&rowCount=60&orderAheadOnly=true&facet=onsalemsg::On+Sale&categoryIdList=d3a5f2da-3002-4c6d-949c-db5304577efb", data="", headers={}, params={})
        response.raise_for_status()
        if len(response.json()) == 0:
            log.error(f"No subs were returned.")
            return sotw
    except Exception as err:
        log.error(f"Error during fetch_sub_of_the_week request: {err}")
        return sotw

    for product in response.json()[0]:
        sub: str = html.unescape(product["title"])
        description: str = html.unescape(product["shortdescription1"]) if product["shortdescription1"] else ""
        image: str = html.unescape(product["productimages"]) if product["productimages"] else ""
        if "sub" in sub.lower():
            sotw.append(Sub(sub, description, image))
    return sotw, store

def get_store(zip_code: str) -> Store:
    try:
        response = requests.request("GET", "https://services.publix.com/api/v1/storelocation", data="", headers={}, params={"types": "R,G,H,N,S", "option": "", "count": "15", "includeOpenAndCloseDates": "true"," isWebsite": "true", "zipCode": zip_code})
        response.raise_for_status()
        if len(response.json()["Stores"]) == 0:
            log.warning(f"No stores nearby... default store is returned.")
            return defaultStore
    except Exception as err:
        log.error(f"Error during get_store request: {err}")
        return defaultStore

    id = response.json()["Stores"][0]["KEY"]
    name = response.json()["Stores"][0]["NAME"]
    return Store(id, name)
