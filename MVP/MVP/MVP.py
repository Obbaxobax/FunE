import wmi
import json
import os
from time import sleep
from threading import Thread
import pythoncom
import requests

#-----------------API Stuff-----------------------
respo = requests.post("https://id.twitch.tv/oauth2/token?client_id=71mpsyy8zm8q94br1qtu3qco7ms9ez&client_secret=2v1cwaj8e39hxgi61fubwbnruji45i&grant_type=client_credentials")
token = respo.json()['access_token']

def getNewToken(timeUntilExpired):
    global token

    #Funny Sleep Hack
    for i in range(0, 4):
        sleep(timeUntilExpired / 5)
    
    respo = requests.post("https://id.twitch.tv/oauth2/token?client_id=71mpsyy8zm8q94br1qtu3qco7ms9ez&client_secret=2v1cwaj8e39hxgi61fubwbnruji45i&grant_type=client_credentials")
    token = respo.json()['access_token']

    t = Thread(target=getNewToken, args=[respo.json()['expires_in']])
    t.start()

t = Thread(target=getNewToken, args=[respo.json()['expires_in']])
t.start()


#-------------Process Detection-------------------
active = True

def getProcesses():
    pythoncom.CoInitialize()
    global big_process
    global big_path
    global active

    w = wmi.WMI()
    
    process_watcher = w.Win32_Process.watch_for("creation")
    while active:
        sleep(1)
        new_process = process_watcher()
        big_process = new_process.Caption.lower()
        big_path = new_process.CommandLine

big_process = ""
big_path = ""


#-----------------Main Script----------------------
try:
    with open('games.json') as t:
        text = t.read()
        if text and text != "{}":
            savedGames = json.loads(text)
        else:
            savedGames = {}
    
    names = open('detectablesV2.json')
    games = json.load(names)

    def getGameFromList(name):
        for i in games:
            if i == name:
                return i
        return False

#-----------------Main Loop----------------------
    savedFlag = False

    x = Thread(target=getProcesses)
    x.start()

    while True:
        sleep(1)
        checkedGame = getGameFromList(big_process)
        
        if checkedGame:
            print(checkedGame + " has been found!")
            
            for i in savedGames:
                if i == checkedGame:
                    savedFlag = True
                    break

            if not savedFlag:
                temp = (big_path.split('"')[1])
                savedGames[games[checkedGame]] = [checkedGame, temp]

                #Get Api Images
                parms = {
                    "Client-ID":"71mpsyy8zm8q94br1qtu3qco7ms9ez",
                    "Authorization": 'Bearer ' + token,
                }

                games = requests.post("https://api.igdb.com/v4/games",
                                                          headers=parms,
                                                          data='fields name, cover; where version_parent = null & category = 0; search "' + 'Titanfall 2' + '";')


                cover = requests.post("https://api.igdb.com/v4/covers",
                                                          headers=parms,
                                                          data='fields image_id; where id = ' + str(games.json()[0]['cover']) + ';') #str(games.json()[0]['cover']) < What the fuck

                img_data = requests.get('https://images.igdb.com/igdb/image/upload/t_cover_big/' + cover.json()[0]['image_id'] + '.jpg').content
                with open('Cover Images/' + games.json()[0]['name'] + '.jpg', 'wb') as temp:
                        temp.write(img_data)                

                #Save
                with open("games.json", "w") as t:
                    json.dump(savedGames, t)
            else:
                savedFlag = False
    
finally:
    active = False
    
    with open("games.json", "w") as t:
        json.dump(savedGames, t)
    print("written to file")
    
