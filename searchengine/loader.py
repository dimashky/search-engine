import json
from os import listdir
from os.path import isfile, join

def loadFile(path):
    try:
        file = open(path, "r")
        data = file.read()
        file.close()
        return data
    except:
        print("EXCEPTION: while load file: "+path)
        return False

def loadJsonFile(path):
    try:
        file = open(path, "r")
        data = json.loads(file.read())
        file.close()
        return data
    except:
        print("EXCEPTION: while load JSON file: "+path)
        return False

def saveFile(path, data):
    try:
        file = open(path, "w")
        file.write(data)
        file.close()
        return True
    except:
        print("EXCEPTION: while save file: "+path)
        return False

def saveJsonFile(path, data):
    try:
        file = open(path, "w")
        file.write(json.dumps(data))
        file.close()
        return True
    except:
        print("EXCEPTION: while save JSON file: "+path)
        return False

def getFilesInDir(dir):
    return [f for f in listdir(dir) if isfile(join(dir, f))]