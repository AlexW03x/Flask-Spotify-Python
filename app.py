from flask import Flask, render_template, url_for, redirect, request
from urllib.request import urlopen
import spotipy
import requests
import os
import re

from pytube import YouTube
from moviepy.editor import *
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

app = Flask(__name__)
myclientID = 'CLIENT_ID_HERE'
myclientSecret = 'CLIENT_SECRET_HERE'
userid = 'YOUR SPOTIFY USER ID HERE'

#spotify API grab
auth = spotipy.SpotifyClientCredentials(client_id=myclientID, client_secret=myclientSecret)
sp = spotipy.Spotify(auth_manager=auth, client_credentials_manager=auth)

##variables for us##
playlists = sp.user_playlists(userid)

global count
count = 0 #to begin the list for transferring data to the website
options = []
playlistimgs = []
tracks = []
links = []
totalopts = playlists["total"]
for i in range(playlists["total"]):
    options.append(playlists["items"][i]["name"])
    playlistimgs.append(playlists["items"][i]["images"][0]["url"])
    tracks.append(playlists["items"][i]["tracks"]["total"])
    links.append(playlists["items"][i]["external_urls"]["spotify"])

global finaloutput
finaloutput = ""

@app.route("/")
def index():
    return render_template("index.html", 
                           options=options[count], 
                           images=playlistimgs[count], 
                           tracks=tracks[count], 
                           links=links[count],
                           optionss=options,
                           totalopts=totalopts)

@app.route("/", methods=["GET", "POST"])
def new_index():
    global count
    ni = request.form.get("plopt")
    count = int(ni)
    print(count)
    finaloutput = ""
    for i in range(len(options[count])):
        if options[count][i].isascii():
            finaloutput += options[count][i]
    print(finaloutput)
    return render_template("index.html",
                           options=options[count],
                           images=playlistimgs[count],
                           tracks=tracks[count],
                           links=links[count],
                           optionss=options,
                           totalopts=totalopts)

@app.route("/download", methods=["POST"])
def download():
    begindownload()
    return render_template("index.html",
                           options=options[count],
                           images=playlistimgs[count],
                           tracks=tracks[count],
                           links=links[count],
                           optionss=options,
                           totalopts=totalopts)    

def requestYoutube(x):
    youtubelink = "https://www.youtube.com/results?search_query=" + x.replace(" ", "+")
    reattempts = 5
    while reattempts > 0:
        try:
            link = urlopen(youtubelink)
            break
        except:
            reattempts -=1
    else:
        print("Skipped!")
    if reattempts > 0:
        finallink = "https://www.youtube.com/watch?v=" + re.findall(r"watch\?v=(\S{11})", link.read().decode())[0]
        return finallink
    else: #prevents download function from downloading causing an error
        return False     

def download_song(x):
    link = YouTube(x)
    link.title = "".join([char for char in link.title if char not in ["/", "\\", "|", "?", "*", ":", ">", "<", "'"]])   
    if os.path.exists(finaloutput + f"/{link.title}.mp3"):
        return False #skip file if exists
    
    file_ = link.streams.filter(only_audio=True).first()
    thefile = file_.download(output_path=finaloutput + "/")
    mp3 = os.path.splitext(thefile)[0]
    finalfile = mp3 + ".mp3"
    mp4tomp3 = AudioFileClip(thefile)
    mp4tomp3.write_audiofile(finalfile, logger=None)
    mp4tomp3.close()
    os.remove(thefile)
    os.replace(finalfile, finaloutput + f"/{link.title}.mp3")
    finalfile = finaloutput + f"/{link.title}.mp3"
    return finalfile    

def begindownload():
    global count
    global finaloutput
    if finaloutput == "":
        finaloutput = options[count]
    ez = playlists["items"][count]["uri"]
    curplay = sp.playlist_tracks(ez)
    for i, track in enumerate(curplay["items"], start=1):
        tname = track["track"]["name"]
        aname = track["track"]["artists"][0]["name"]
        links = track["track"]["external_urls"]["spotify"]

        getlink = requestYoutube(aname + " - " + tname + " audio")
        if getlink != False:
            song = download_song(getlink)
            if song:
                os.replace(song, finaloutput + f"/{os.path.basename(song)}")
            

if __name__ == "__main__":
    app.run(debug=True)