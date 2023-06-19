
#Get Single \ File Path
temp = "G:\\SteamLibrary\\steamapps\\common\\Titanfall2\\Titanfall2.exe"

temp = temp.replace("\"", '')
temp = temp.replace('\\', chr(92))
print(temp)
