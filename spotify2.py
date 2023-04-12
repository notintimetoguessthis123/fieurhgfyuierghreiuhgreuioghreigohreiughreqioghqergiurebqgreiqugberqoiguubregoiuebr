from flask import Flask, request, redirect
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import requests
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap, json
import ctypes
import time


app = Flask(__name__)

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
REDIRECT_URI = 'http://localhost:3000/callback'
CLIENT_ID = "854334c94c4d4bfd9d052ed81d6d2d96"
CLIENT_SECRET = "424d820dd0f14fdaa80b93ca61433379"
SCOPE = [
    "user-read-email",
    "playlist-read-collaborative",
    "user-read-currently-playing"
]
token = ''

def GrabSpotifyCurSong(curSongJson):
    return curSongJson['item']['name']
def GrabSpotifyCurArtist(curSongJson):
    return curSongJson['item']['artists'][0]['name']
def GrabCurrentSongImage(curSongJson):
    return curSongJson['item']['album']['images'][0]['url']
def GrabCurrentSongTimestamp(curSongJson):
    return curSongJson['progress_ms']
def GrabTotalSongTimestamp(curSongJson):
    return curSongJson['item']['duration_ms']

@app.route("/login")
def login():
    spotify = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    authorization_url, state = spotify.authorization_url(AUTH_URL)
    return redirect(authorization_url)

@app.route("/callback", methods=['GET'])
def callback():
    global token
    code = request.args.get('code')
    res = requests.post(TOKEN_URL,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI
        })
    token = str(res.json()['access_token']).replace('"','')
    print(token)
    endpoint = "https://api.spotify.com/v1/me/player/currently-playing"
    spotifyHeaders = {'Authorization':'Bearer ' + token}
    try:
        while True:
            curSong = requests.get(endpoint, headers=spotifyHeaders)
            print(curSong.text)
            print(curSong.status_code)
            curSongJson = curSong.json()

            curSong = requests.get(endpoint, headers=spotifyHeaders)

            currentSong = GrabSpotifyCurSong(curSongJson)
            currentArtist = GrabSpotifyCurArtist(curSongJson)
            img = GrabCurrentSongImage(curSongJson)
            current_time = GrabCurrentSongTimestamp(curSongJson)
            total_time = GrabTotalSongTimestamp(curSongJson)

            print(currentSong)
            print(currentArtist)
            print(img)
            print(current_time)
            print(total_time)
                
            img_data = requests.get(img).content
            with open('C:\\temp.jpg', 'wb') as handler:
                handler.write(img_data)
                
            image = Image.open("C:\\temp.jpg")
            image2 = image.resize((2560, 1440))
            blurred_image = image2.filter(ImageFilter.GaussianBlur(radius=40))
            enhancer = ImageEnhance.Brightness(blurred_image)
            blurred_image = enhancer.enhance(.3)
            blurred_image.paste(image, (960, 400))
            myFont = ImageFont.truetype('C:\\Windows\\Fonts\\Verdana.ttf', 40)
            d1 = ImageDraw.Draw(blurred_image)
            try:
                d1.text(((2560 / 2) - (d1.textlength(currentSong.lower(),font=myFont) / 2), 10), currentSong.lower(), font=myFont, fill =(255, 255, 255))  
                d1.text(((2560 / 2) - (d1.textlength(currentArtist.lower(),font=myFont) / 2), 55), currentArtist.lower(), font=myFont, fill =(255, 255, 255))  
            except:
                d1.text(((2560 / 2) - (d1.textlength(currentSong.lower(),font=myFont) / 2), 10), currentSong.lower(), font=myFont, stroke_fill=(255,255,255), fill=255)  
                d1.text(((2560 / 2) - (d1.textlength(currentArtist.lower(),font=myFont) / 2), 55), currentArtist.lower(), font=myFont, stroke_fill=(255,255,255), fill=255)  
                
            blurred_image.save("C:\\Temp\\temp2.jpg",quality=100)
                
            SPI_SETDESKWALLPAPER = 20 
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, "C:\\temp2.jpg" , 3)
            time.sleep(5)    
    except:
        return redirect("http://localhost:3000/login", code=302)


if __name__ == '__main__':
    app.run(port=3000,debug=True)
