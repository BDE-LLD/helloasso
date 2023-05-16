import requests as rq
import json
from datetime import datetime

def get_token(client_id: str, client_secret: str):
    payload = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
    r = rq.post("https://api.intra.42.fr/oauth/token", data=payload)
    r_json = json.loads(r.text)
    try:
        return r_json['access_token']
    except KeyError:
        return "An error occured while getting the token !"

def get_token_from_env():
    with open('.env') as env_file:
        data = json.load(env_file)
        token = get_token(data['CLIENT_ID'], data['CLIENT_SECRET'])
    return token

def get(token: str, path: str):
    headers = {'Authorization': 'Bearer ' + token}
    r = rq.get("https://api.intra.42.fr/" + path, headers=headers)
    return json.loads(r.text)

##############################################

def get_events_ids(token: str, name: str):
    return [event['id'] for event in get(token, "/v2/events?campus_id=1&filter[name]=" + name)]

def get_blackhole(token: str, uid: str):
    print(uid)
    blackhole_str = get(token, "/v2/cursus_users?filter[user_id]=" + str(uid) + "&filter[cursus_id]=21")[0]['blackholed_at']
    blackhole = datetime.strptime(blackhole_str, "%Y-%m-%dT%H:%M:%S.000Z")
    return blackhole
