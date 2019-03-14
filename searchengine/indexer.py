import string
from os import listdir
from os.path import isfile, join
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from collections import OrderedDict
import json
import nltk

stop_words = set(stopwords.words('english')) 
pos_tag_preferred = ['VB', 'VBG', 'VBD', 'JJ', 'NN', 'NNP', 'NNS']

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def getFilesInDir(dir):
    return [f for f in listdir(dir) if isfile(join(dir, f))]

def getDocTokens(filePath):
    file = open(filePath, "r")
    # tokenizing the doc content
    doc_tokens = word_tokenize(file.read())
    # filtered mean without stop words and punctuation
    filtered_doc_tokens = [w for w in doc_tokens if not w in stop_words and not w in string.punctuation and is_ascii(w)] 
    # preferred mean take only specific Parts Of Speach (pos) tags 
    preferred_doc_tokens = [w[0] for w in nltk.pos_tag(filtered_doc_tokens) if w[1] in pos_tag_preferred]
    # stemming
    stemmed_doc_tokens = [PorterStemmer().stem(w) for w in preferred_doc_tokens]
    return stemmed_doc_tokens

def index(fresh = False, dir = './docs/'):
    # fresh mean create new index table.
    if not fresh:
        try:
            return loadIndexTable()
        except:
            print("Error while loading INDEX TABLE, continue with new version")

    files = getFilesInDir(dir)
    index_table = {}
    for file in files:
        tokens = getDocTokens(dir + file)
        # update or create index table with recently fetched tokens
        for token in tokens:
            if token not in index_table.keys():
                index_table[token] = [file]
            elif file not in index_table[token]:
                index_table[token].append(file)
    # sort the dictionary for binary search
    index_table = OrderedDict(sorted(index_table.items(), key=lambda t: t[0]))
    # Saving index table to a file
    try:
        saveIndexTable(index_table)
    except:
        print("Error while SAVING INDEX TABLE, continue without saving")
    return index_table

def saveIndexTable(index_table, path = './storage/index_table.json'):
    file = open(path, "w")
    file.write(json.dumps(index_table))

def loadIndexTable(path = './storage/index_table.json'):
    file = open(path, "r")
    return json.loads(file.read())