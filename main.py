import base64
import json
import os
import pprint
import random

import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
CLIENT_ID = "803535d30a9f4eeb9f97277709488bfd"
CLIENT_SECRET = "c33e3530c37741629d51bb21c3447598"


def get_token():
    auth_str = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    res = requests.post(url, headers=headers, data=data)
    json_res = json.loads(res.content)
    token = json_res["access_token"]
    return token


TOKEN = get_token()
headers = {
    "Authorization": "Bearer " + TOKEN,
    "Content-Type": "application/json", }

query = "NFS Underground ost"
type = "playlist"
req = requests.get(f"https://api.spotify.com/v1/search?q={query}&type={type}", headers=headers)
playlist = req.json()["playlists"]["items"][0]["tracks"]["href"]
req2 = requests.get(playlist, headers=headers)


def prepare_round():
    preview_url = random.choices(req2.json()['items'], k=4)
    round_data = {}
    answer = ''
    link = ''
    for i in preview_url:
        round_data[i['track']["name"]] = i['track']['preview_url']
    for i in round_data:
        if round_data[i] is not None:
            answer = i
            link = round_data[i]
            break
    if link == '':
        return None
    a = list(round_data.keys())
    random.shuffle((a))
    return {"answer": answer, "link": link, "options": a}


@app.route('/_new_sound')
def add_numbers():
    data = prepare_round()
    while data is None:
        data = prepare_round()
    print(json.dumps(data, indent=3))
    return json.dumps(data, indent=3)


@app.route('/index')
@app.route('/')
def index():
    data = prepare_round()
    while data is None:
        data = prepare_round()
    return render_template("index.html", data=data)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
