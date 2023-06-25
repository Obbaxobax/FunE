import wmi
import json
import os
from time import sleep
from threading import Thread
from google_images_search import GoogleImagesSearch
import pythoncom

pathz = 'Game Cover Arts'
DK = 'AIzaSyBkwVyCi125GHnCXpqE3p1oTOH59I5zAmM'
CX = '25777af3020ad413b'

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

try:
    with open('games.txt') as t:
        text = t.read()
        if text and text != "{}":
            savedGames = json.loads(text)
            print(savedGames)
        else:
            savedGames = {}
    
    games = {}
    names = open('detectable.json')
    data = json.load(names)

    def getGameFromList(name):
        for i in games:
            if i == name:
                return i
        return False

    for i in data:
        listify = list(i)
        if any("executables" in word for word in listify) == False:
            continue
        
        for g in i['executables']:
            if g['os'] != 'win32':
                continue

            splited = g['name'].split("/") 
            games[splited[len(splited)-1].lower()] = i['name']

    #Funny library
    flag = False

    x = Thread(target=getProcesses)
    x.start()

    while True:
        sleep(1)

        
        
        funny = getGameFromList(big_process)
        if funny:
            print(funny + " has been found!")
            for i in savedGames:
                if i == funny:
                    flag = True
                    break

            if not flag:
                #temp = new_process.CommandLine.replace("\"", '')
                temp = (big_path.split('"')[1])
                print(temp)
                savedGames[games[funny]] = [funny, temp]
                with open("games.txt", "w") as t:
                    json.dump(savedGames, t)
            else:
                flag = False
    
finally:
    active = False
    
    with open("games.txt", "w") as t:
        json.dump(savedGames, t)
    print("written to file")
    
