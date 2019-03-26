import json
import nltk
import string
from os import listdir
from os.path import isfile, join
from nltk import ngrams
from nltk.stem import WordNetLemmatizer, LancasterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import OrderedDict

lemmatizer = WordNetLemmatizer()
stemmer = LancasterStemmer()
stop_words = set(stopwords.words('english'))
pos_tag_preferred = ['VB', 'VBG', 'VBD', 'JJ', 'NN', 'NNP', 'NNS']


def loadStopWords():
    file = open('./storage/stop_words.txt')
    text = file.read()
    return [w for w in text.split('\n') if w]


my_stop_words = loadStopWords()


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def getFilesInDir(dir):
    return [f for f in listdir(dir) if isfile(join(dir, f))]


def tokenize(query):
    return word_tokenize(query)


def getDocTokens(filePath):
    file = open(filePath, "r")
    tokens = getTokens(file.read())
    tokens = [(token, tokens.count(token)) for token in set(tokens)]
    return tokens


def getTokens(txt):
    tokens = word_tokenize(txt)
    filtered_tokens = [
        w.strip('.') for w in tokens if not w in string.punctuation and not w in my_stop_words and is_ascii(w)
    ]
    tokens_with_pos = [
        w for w in nltk.pos_tag(filtered_tokens) if w[1][0] in ["V", "N", "J", "R"]
    ]

    final_tokens = []
    for t in tokens_with_pos:
        word = ""
        token = t[0].lower()
        if (t[1][0] == "V"):
            word = lemmatizer.lemmatize(token, "v")
        elif (t[1][0] in ["R", "J"]):
            word = lemmatizer.lemmatize(token, "a")
        else:
            word = stemmer.stem(token)
        final_tokens.append(word)

    return final_tokens


def index(fresh=False, dir='./docs/'):
    if not fresh:
        try:
            return loadIndexTable()
        except:
            print("Error while loading INDEX TABLE, continue with new version")

    files = getFilesInDir(dir)
    index_table = {}
    for file in files:
        tokens = getDocTokens(dir + file)
        for token in tokens:
            if token not in index_table.keys():
                index_table[token[0]] = [(file, token[1])]
            elif file not in index_table[token]:
                index_table[token[0]].append((file, token[1]))
    # sort the dictionary for binary search
    index_table = OrderedDict(sorted(index_table.items(), key=lambda t: t[0]))
    # Saving index table to a file
    try:
        saveIndexTable(index_table)
    except:
        print("Error while SAVING INDEX TABLE, continue without saving")
    return index_table


def saveIndexTable(index_table, path='./storage/index_table.json'):
    file = open(path, "w")
    file.write(json.dumps(index_table))


def loadIndexTable(path='./storage/index_table.json'):
    file = open(path, "r")
    return json.loads(file.read())
