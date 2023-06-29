import requests
import json

respo = requests.post("https://id.twitch.tv/oauth2/token?client_id=71mpsyy8zm8q94br1qtu3qco7ms9ez&client_secret=2v1cwaj8e39hxgi61fubwbnruji45i&grant_type=client_credentials")

token = respo.json()['access_token']
print(respo.json())
print(token)

parms = {
    "Client-ID":"71mpsyy8zm8q94br1qtu3qco7ms9ez",
    "Authorization": 'Bearer ' + token,
}

games = requests.post("https://api.igdb.com/v4/games", headers=parms, data="fields name; limit 2;")
print(games.json())
