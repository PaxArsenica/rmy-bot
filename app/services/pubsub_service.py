import html
import requests
import utils.config as config
import utils.rmy_utils as utils
from db.dynamodb import DynamoDb
from models.pubsub_schemas import Store, Sub

log = utils.setup_logging('pubsub_service')
default_store = Store("00776", "Publix at Piedmont")

def fetch_sub_of_the_week(zip_code: str = "") -> tuple[list[Sub], Store]:
    #Sub of the Week
    sotw: list[Sub] = []
    store = get_store(config.ZIP_CODE) if not zip_code else get_store(zip_code)

    try:
        response = requests.get(f"https://services.publix.com/api/v3/product/SearchMultiCategory?storeNumber={store.id}&sort=popularityrank+asc,+titlecopy+asc&rowCount=60&orderAheadOnly=true&facet=onsalemsg::On+Sale&categoryIdList=d3a5f2da-3002-4c6d-949c-db5304577efb", data="", headers={}, params={})
        response.raise_for_status()
        response_json = response.json()
        if len(response_json) == 0:
            log.error(f"No subs were returned.")
            return sotw
    except Exception as err:
        log.error(f"Error during fetch_sub_of_the_week request: {err}")
        return sotw

    for product in response_json[0]:
        sub: str = html.unescape(product["title"])
        description: str = html.unescape(product["shortdescription1"]) if product["shortdescription1"] else ""
        image: str = html.unescape(product["productimages"]) if product["productimages"] else ""
        if "sub" in sub.lower():
            sotw.append(Sub(sub, description, image))
    return sotw, store

def get_store(zip_code: str) -> Store:
    try:
        response = requests.get("https://services.publix.com/api/v1/storelocation", data="", headers={}, params={"types": "R,G,H,N,S", "option": "", "count": "15", "includeOpenAndCloseDates": "true"," isWebsite": "true", "zipCode": zip_code})
        response.raise_for_status()
        response_json = response.json()
        if len(response_json["Stores"]) == 0:
            log.warning(f"No stores nearby... default store is returned.")
            return default_store
    except Exception as err:
        log.error(f"Error during get_store request: {err}")
        return default_store

    id = response_json["Stores"][0]["KEY"]
    name = response_json["Stores"][0]["NAME"]
    return Store(id, name)
