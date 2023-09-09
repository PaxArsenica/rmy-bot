import html
import requests
from os import environ as env
from typing import List

class Sub:
    def __init__(self, name: str, description: str = "", image: str = "") -> None:
        self.name = name
        self.description = description
        self.image = image

class Store:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

#Sub of the Week
sotw: List[Sub] = []

def fetch_sub_of_the_week(zip_code: str = "") -> List[Sub]:
    sotw.clear()
    store = get_store(env['ZIP_CODE']) if not zip_code else get_store(zip_code)
    response = requests.request("GET", f"https://services.publix.com/api/v3/product/SearchMultiCategory?storeNumber={store.id}&sort=popularityrank+asc,+titlecopy+asc&rowCount=60&orderAheadOnly=true&facet=onsalemsg::On+Sale&categoryIdList=d3a5f2da-3002-4c6d-949c-db5304577efb", data="", headers={}, params={})

    for product in response.json()[0]:
        sub: str = html.unescape(product["title"])
        description: str = html.unescape(product["shortdescription1"]) if product["shortdescription1"] else ""
        image: str = html.unescape(product["productimages"]) if product["productimages"] else ""
        if "sub" in sub.lower():
            sotw.append(Sub(sub, description, image))
    return sotw

def get_store(zip_code: str) -> Store:
    response = requests.request("GET", "https://services.publix.com/api/v1/storelocation", data="", headers={}, params={"types": "R,G,H,N,S", "option": "", "count": "15", "includeOpenAndCloseDates": "true"," isWebsite": "true", "zipCode": zip_code})

    if response.status_code != 200 or len(response.json()["Stores"]) == 0:
        return Store("00776", "Publix at Piedmont")

    id = response.json()["Stores"][0]["KEY"]
    name = response.json()["Stores"][0]["NAME"]
    return Store(id, name)
