import json
import nltk
import string
import re
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

def getDocContent(filePath):
    file = open(filePath, "r")
    return file.read()

def getDocTokens(filePath):
    return getTokens(getDocContent(filePath))

def getTokens(txt):
    tokens = word_tokenize(txt)
    filtered_tokens = [w.strip('.') for w in tokens if not w in string.punctuation and not w in my_stop_words and is_ascii(w)] 
    preferred_tokens = [w[0] for w in nltk.pos_tag(filtered_tokens) if w[1] in pos_tag_preferred]
    stemmed_tokens = [stemmer.stem(lemmatizer.lemmatize(w)) for w in preferred_tokens]
    return stemmed_tokens

def termFrequency(document, term):
    return len(re.finditer(term, document))

def documentFrequency(corpus_path, term):
    return len([set([term]) & set(getDocTokens(file)) for file in getFilesInDir(corpus_path)])

def corpusFrequency(corpus_path, term):
    return sum([termFrequency(getDocContent(file), term) for file in getFilesInDir(corpus_path)])

def index(fresh = False, dir = './docs/'):
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