import wmi
import json
import os

try:
    with open('games.txt') as t:
        text = t.read()
        if text:
            savedGames = json.load(t)
        else:
            savedGames = {}
    
    games = []
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
            games.append(splited[len(splited)-1].lower())


    #Funny library
    w = wmi.WMI()

    process_watcher = w.Win32_Process.watch_for("creation")
    while True:
        new_process = process_watcher()
        funny = getGameFromList(new_process.Caption.lower())
        if funny:
            print(funny + " has been found!")
            for i in savedGames:
                if i == funny:
                    break
            savedGames[funny] = new_process.CommandLine
            with open("games.txt", "w") as t:
                json.dump(savedGames, t)

finally:
    with open("games.txt", "w") as t:
        json.dump(savedGames, t)
    print("written to file")
    
