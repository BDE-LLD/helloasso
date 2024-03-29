#! /usr/bin/env python3

from dotenv import load_dotenv
import os
import requests
import json
import csv
import sys

from helloasso_api.oauth2 import OAuth2Api
from helloasso_api.apiv5client import ApiV5Client

load_dotenv()

CLIENT_ID = os.getenv("HELLOASSO_CLIENT_ID")
CLIENT_SECRET = os.getenv("HELLOASSO_CLIENT_SECRET")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


class MyApi:
    _client: ApiV5Client
    organisationSlug: str

    def __init__(self, client, organisationSlug) -> None:
        self._client = client
        self.organisationSlug = organisationSlug

    def fetchItems(self, formsType: str, formSlug: str):
        items = {
            "data": [],
            "total": 0,
        }
        res = self._client.call(
            f"organizations/{self.organisationSlug}/forms/{formsType}/{formSlug}/items"
        ).json()
        total = res["pagination"]["totalCount"]
        items["total"] = total
        items["data"].extend(res["data"])
        while total > 0:
            total = res["pagination"]["totalCount"]
            res = self._client.call(
                f"organizations/{self.organisationSlug}/forms/{formsType}/{formSlug}/items?continuationToken={res['pagination']['continuationToken']}"
            ).json()
            items["data"].extend(res["data"])
        return items


def sendWebhook(data: dict):
    try:
        body = json.dumps(data)
        res = requests.post(
            WEBHOOK_URL,
            json=data,
            headers={"Content-Type": "application/json"},
        )
        if res.status_code != 204:
            print(res.status_code)
            print(res.text)
    except Exception as e:
        print(e)


def saveUsers(users: list):
    filePath = os.path.join(os.path.dirname(__file__), "users.csv")
    with open(filePath, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["firstName", "lastName"])
        writer.writeheader()
        writer.writerows(users)


def loadUsers():
    users = []
    filePath = os.path.join(os.path.dirname(__file__), "users.csv")
    with open(filePath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users


def main():
    auth = OAuth2Api(
        "api.helloasso.com",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        timeout=99999,
    )

    auth.get_token()

    client = ApiV5Client(
        api_base="api.helloasso.com/v5/",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token=auth.access_token,
        refresh_token=auth.refresh_token,
    )

    with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
        config = json.load(f)

    myApi = MyApi(client, config["organisationSlug"])

    res = list(
        filter(
            lambda x: x["type"] != "Donation",
            myApi.fetchItems(config["formType"], config["formSlug"])["data"],
        )
    )

    users = [item["user"] for item in res]

    arg = sys.argv[1]

    if arg == "save":
        saveUsers(users)
    elif arg == "check":
        filePath = os.path.join(os.path.dirname(__file__), "users.csv")
        if not os.path.isfile(filePath):
            saveUsers(users)
            print("initialisation of users.csv")
            return
        savedUsers = loadUsers()
        diff = list(filter(lambda x: x not in savedUsers, users))
        if len(diff) > 0:
            str = ", ".join([u["firstName"] + " " + u["lastName"] for u in diff])
            print(f"{len(diff)} tickets vendus !")
            print(f"Dernier(s) acheteur(s) : {str}")
            if WEBHOOK_URL:
                msg = {
                    "content": f"**{len(users)}** tickets vendus !\nDernier(s) acheteur(s) : **{str}**",
                    "username": "HelloAsso",
                    "avatar_url": "https://www.helloasso.com/blog/wp-content/uploads/2022/02/Circle-logo-ha-150x150.png",
                }
                sendWebhook(msg)
            saveUsers(users)
        else:
            print("No new users")
    elif arg == "list":
        print(f"{len(users)} tickets vendus")
        for user in users:
            print(f"{user['firstName']} {user['lastName']}")
    else:
        print("No args or bad args")


if __name__ == "__main__":
    main()
