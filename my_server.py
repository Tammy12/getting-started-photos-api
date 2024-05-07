from flask import Flask
from flask import request, redirect, session
import requests
from uuid import uuid4

app = Flask(__name__)
app.secret_key = uuid4().bytes

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
CLIENT_ID = "<Your Client Id>"
CLIENT_SECRET = "<Your Client Secret>"
REDIRECT_URI = "http://localhost:8080/code"
TOKEN_ENDPOINT = "https://accounts.google.com/o/oauth2/token"

@app.get("/albums")
def get_albums():
    if "access_token" not in session:
        session["original_request"] = request.url
        # redirecting the user to Google's authorization endpoint
        return redirect(get_authorization_redirect())
    access_token = session["access_token"]
    r = requests.get(
        url="https://photoslibrary.googleapis.com/v1/albums", 
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    return r.json()


def get_authorization_redirect() -> str:
    url = AUTH_ENDPOINT
    url += f"?client_id={CLIENT_ID}"
    url += f"&redirect_uri={REDIRECT_URI}"
    url += "&response_type=code"
    url += "&scope=https://www.googleapis.com/auth/photoslibrary.readonly"
    return url


@app.get("/code")
def receive_code():
    code = request.args.get("code")
    access_token = get_access_token(code)
    session["access_token"] = access_token
    return redirect(session["original_request"])


def get_access_token(code: str) -> str:
    token_response = requests.post(
        url=TOKEN_ENDPOINT, 
        data={
            "grant_type": "authorization_code", 
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    return token_response.json()["access_token"]

app.run(port=8080)
