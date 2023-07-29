import wmi
import json
import os
from time import sleep
from threading import Thread, Event
import pythoncom
import requests
import pystray
import PIL.Image
import sys
import urllib.request
import subprocess
import logging

#Temp
import dearpygui.dearpygui as dpg

iconImg = PIL.Image.open("logo.png")

refresh = Event()
runbo = Event()
active = Event()
runbo.set()
minimized = False

big_process = ""
big_path = ""

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    filename='logs.txt',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)


#-------------Check for Internet----------------------
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

#-----------------API Stuff-----------------------
def getAPIToken():
    global token
    
    if connect():
        respo = requests.post("https://id.twitch.tv/oauth2/token?client_id=71mpsyy8zm8q94br1qtu3qco7ms9ez&client_secret=2v1cwaj8e39hxgi61fubwbnruji45i&grant_type=client_credentials")

        if not respo.status_code == requests.codes.ok:
            logging.warning("API Request Failed")
            token = ""
            return;

        token = respo.json()['access_token']
        t = Thread(target=getNewToken, args=[respo.json()['expires_in']], daemon=True)
        t.start()
        
def getNewToken(timeUntilExpired):
    global token

    #Funny Sleep Hack
    for i in range(0, 4):
        sleep(timeUntilExpired / 5)
    
    respo = requests.post("https://id.twitch.tv/oauth2/token?client_id=71mpsyy8zm8q94br1qtu3qco7ms9ez&client_secret=2v1cwaj8e39hxgi61fubwbnruji45i&grant_type=client_credentials")
    token = respo.json()['access_token']

    t = Thread(target=getNewToken, args=[respo.json()['expires_in']], daemon=True)
    t.start()

getAPIToken()

def getCoverImage(i):
        if token == "":
            getAPIToken()
            return;
        
        parms = {
                    "Client-ID":"71mpsyy8zm8q94br1qtu3qco7ms9ez",
                    "Authorization": 'Bearer ' + token,
                }
        logging.info("Parms Setup")

        games2 = requests.post("https://api.igdb.com/v4/games",
                                                  headers=parms,
                                                  data='fields name, cover; where version_parent = null & category = 0; search "' + i + '";')

        if not games2.status_code == requests.codes.ok:
            logging.warning("API Request Failure")
            return;
        else:
            logging.info("Game Found")
        
        cover = requests.post("https://api.igdb.com/v4/covers",
                                                  headers=parms,
                                                  data='fields image_id; where id = ' + str(games2.json()[0]['cover']) + ';') #str(games.json()[0]['cover']) < What the fuck

        if not cover.status_code == requests.codes.ok:
            logging.warning("API Request Failure")
            return;
        else:
            logging.info("Cover Found")
        
        r = requests.get('https://images.igdb.com/igdb/image/upload/t_cover_big/' + cover.json()[0]['image_id'] + '.jpg')

        if not r.status_code == requests.codes.ok:
            logging.warning("API Request Failure")
            return;
        else:
            logging.info("Image Downloaded")
        
        img_data = r.content

        
        with open('Cover Images/' + games2.json()[0]['name'] + '.jpg', 'wb') as temp:
                temp.write(img_data)
                logging.info("Wrote Image File")

        width, height, channels, data = dpg.load_image("Cover Images/" + games2.json()[0]['name'] + ".jpg")
        with dpg.texture_registry(show=False):
            dpg.add_static_texture(width=width, height=height, default_value=data, tag=games2.json()[0]['name'])

#-------------Process Detection-------------------
def getProcesses():
    pythoncom.CoInitialize()
    global big_process
    global big_path
    global active

    w = wmi.WMI()
    
    process_watcher = w.Win32_Process.watch_for("creation")
    while not active.is_set():
        sleep(1)
        new_process = process_watcher()
        big_process = new_process.Caption.lower()
        big_path = new_process.CommandLine
    logging.info("Process Watcher Closed")


#-----------------Main Script----------------------
with open('games.json') as t:
    text = t.read()
    if text and text != "{}":
        savedGames = json.loads(text)
        for i in savedGames:
            if not os.path.isfile("Cover Images/" + i + ".jpg"):
               if connect():
                getCoverImage(i)   
    else:
        savedGames = {}

names = open('detectablesV2.json')
games = json.load(names)

def on_clicked(icon, item):
    runbo.clear()

def iconFunc():
    icon.run()

def on_activate(icon, item):
    global minimized
    minimized = False
    #updateUI()
    T = Thread(target=dpgLoop, daemon=True)
    T.start()

icon = pystray.Icon("FunE", iconImg, menu=pystray.Menu(
    pystray.MenuItem("Exit", on_clicked),
    pystray.MenuItem("Open", on_activate, default=True, visible=False)
))

f = Thread(target=iconFunc, daemon=True)
f.start()

def openGame(sender, app_data, user_data):
    logging.info("Launching")
    if '"' in str(savedGames[user_data][1]):
        temp = savedGames[user_data][1].split('"')
        subprocess.call([temp[1], temp[2]])
    else:
        temp = savedGames[user_data][1]
        subprocess.call(temp)

def dpgLoop():
    dpg.create_context()
    dpg.create_viewport(title="You're playing minecraft in a cave looking for diamonds. Thats FunE...", width=600, height=600)
    dpg.setup_dearpygui()

    with dpg.window(label="Example Window", tag="Main"):
        for i in savedGames:
            if os.path.isfile("Cover Images/" + i + ".jpg"):
                width, height, channels, data = dpg.load_image("Cover Images/" + i + ".jpg")
            else:
                width, height, channels, data = dpg.load_image("Cover Images/placeholder_.png")
                
            with dpg.texture_registry(show=False):
                dpg.add_static_texture(width=width, height=height, default_value=data, tag=i)

            dpg.add_image_button(texture_tag=i, width=100, height=150, label=i, callback=openGame, user_data=i)
        dpg.add_button(label="Reset", width=110, height=20, callback=updateUI)

    dpg.show_viewport()
    dpg.set_primary_window("Main", True)
    dpg.set_exit_callback(minimizeCallback)
    
    while not refresh.is_set():
        sleep(0.1)
        dpg.render_dearpygui_frame()
        if not dpg.is_dearpygui_running():
            break;
        
    dpg.destroy_context()

def updateUI():
    dpg.delete_item(item="Main", children_only=True)
    dpg.delete_item(item="Main")
    
    with dpg.window(label="Example Window", tag="Main"):
        for i in savedGames:
            dpg.add_image_button(texture_tag=i, width=100, height=150, label=i, callback=openGame, user_data=i)
        dpg.add_button(label="Reset", width=110, height=20, callback=updateUI)
    dpg.set_primary_window("Main", True)

def minimizeCallback():
    global minimized
    minimized = True
    
    refresh.set()
    sleep(0.5)
    refresh.clear()

def getGameFromList(name):
    for i in games:
        if i == name:
            return i
    return False


#-----------------Main Loop----------------------
savedFlag = False

x = Thread(target=getProcesses, daemon=True)
x.start()
dpgT = Thread(target=dpgLoop, daemon=True)
dpgT.start()

while runbo.is_set():
    sleep(1)
    checkedGame = getGameFromList(big_process)
    
    if checkedGame:
        logging.info(checkedGame + " has been found!")
        
        for i in savedGames:
            if savedGames[i][0] == checkedGame:
                savedFlag = True
                logging.info("Game Already Saved")
                sleep(5)
                break

        if not savedFlag:
            logging.info("Saving")
            if big_path:
                temp = big_path
                savedGames[games[checkedGame]] = [checkedGame, temp]

                #Get Api Images
                if connect():
                    logging.info("Grabbing image")
                    getCoverImage(games[checkedGame])
                    logging.info("Image Grab Success")
                else:
                    logging.warning("Image Request Failed. No Connection to Internet.")

                if not minimized:
                    logging.info("Updating UI")
                    updateUI()
                
                #Save
                with open("games.json", "w") as t:
                    logging.info("Saving")
                    json.dump(savedGames, t)
            else:
                logging.warning("No Valid Path")
        else:
            savedFlag = False
logging.info("Done")
icon.stop()
dpg.destroy_context()
active.set()

with open("games.json", "w") as t:
    json.dump(savedGames, t)
logging.info("written to file")
sys.stdout.close()
sleep(1)
sys.exit()


