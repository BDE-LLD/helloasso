#! /usr/bin/env python3

import sys
import api
from helloasso_api.oauth2 import OAuth2Api
from helloasso_api.apiv5client import ApiV5Client
import dotenv

dotenv.load()
clientId = dotenv.get('CLIENTHELLOASSO_ID')
clientSecret = dotenv.get('CLIENTHELLOASSO_SECRET')


class MyApi:
    def __init__(self, client) -> None:
        self._client = client

    def fetchPayments(self):
        payments = {
            "data": [],
            "total": 0,
        }
        res = self._client.call("organizations/bde-42/forms/event/wed/payments").json()
        total = res["pagination"]["totalCount"]
        payments["total"] = total
        payments["data"].extend(res["data"])
        while total > 0:
            total = res["pagination"]["totalCount"]
            res = self._client.call(
                f"organizations/bde-42/forms/event/wed/payments?continuationToken={res['pagination']['continuationToken']}"
            ).json()
            payments["data"].extend(res["data"])
        return payments

    def fetchItems(self):
        items = {
            "data": [],
            "total": 0,
        }
        res = self._client.call("organizations/bde-42/forms/event/wed/items?withDetails=true").json()
        total = res["pagination"]["totalCount"]
        items["total"] = total
        items["data"].extend(res["data"])
        while total > 0:
            total = res["pagination"]["totalCount"]
            res = self._client.call(
                f"organizations/bde-42/forms/event/wed/items?withDetails=true&continuationToken={res['pagination']['continuationToken']}"
            ).json()
            items["data"].extend(res["data"])
        return items

TOKEN = api.get_token(dotenv.get('CLIENT42_ID'), dotenv.get('CLIENT42_SECRET'))

def checkapi(first_name: str, last_name: str, login: str):
    matching_users = api.get(TOKEN, '/v2/users?filter[login]=' + login)
    return len(matching_users) != 0

def isstud(first_name: str, last_name: str, login: str):
    if checkapi(first_name, last_name, login.lower()):
        return "Stud verif ok " + login
    else:
        return "ALERTE non stud " + login



auth = OAuth2Api(
    "api.helloasso.com", client_id=clientId, client_secret=clientSecret, timeout=99999
)

auth.get_token()

client = ApiV5Client(
    api_base="api.helloasso.com/v5/",
    client_id=clientId,
    client_secret=clientSecret,
    access_token=auth.access_token,
    refresh_token=auth.refresh_token,
)

myApi = MyApi(client)

res = list(filter(lambda x: x["type"] != "Donation", myApi.fetchItems()["data"]))

if len(sys.argv) != 2:
    print("Usage: helloasso.py <total | list>")
    sys.exit(1)

if sys.argv[1] == "total":
    print(len(res))
elif sys.argv[1] == "list":
    for item in res:
        print(item["user"]["firstName"] + " " + item["user"]["lastName"] + " " + isstud(item["user"]["firstName"], item["user"]["lastName"], item["customFields"][0]["answer"]))
else:
    print("Usage: helloasso.py <total | list>")
    sys.exit(1)
