import wmi
import json
import os
from time import sleep
from threading import Thread
from google_images_search import GoogleImagesSearch
import pythoncom

#-----------------API Stuff-----------------------
pathz = 'Game Cover Arts'
DK = 'AIzaSyBkwVyCi125GHnCXpqE3p1oTOH59I5zAmM'
CX = '25777af3020ad413b'

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
    with open('games.txt') as t:
        text = t.read()
        if text and text != "{}":
            savedGames = json.loads(text)
        else:
            savedGames = {}
    
    games = {}
    names = open('detectablesV2.txt')
    games = json.load(names)

    def getGameFromList(name):
        for i in games:
            if i == name:
                return i
        return False

    #--------------Main Loop----------------------
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

                #Save
                with open("games.txt", "w") as t:
                    json.dump(savedGames, t)
            else:
                savedFlag = False
    
finally:
    active = False
    
    with open("games.txt", "w") as t:
        json.dump(savedGames, t)
    print("written to file")
    
