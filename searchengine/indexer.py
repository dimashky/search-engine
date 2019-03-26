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
#import fuzzy

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

def getDocTokens(filePath, without_relevance = True):
    tokens = getTokens(getDocContent(filePath))
    if(without_relevance):
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

def termFrequency(document, term):
    return len(re.finditer(term, document))

def documentFrequency(corpus_path, term):
    return len([set([term]) & set(getDocTokens(file, False)) for file in getFilesInDir(corpus_path)])

def corpusFrequency(corpus_path, term):
    return sum([termFrequency(getDocContent(file), term) for file in getFilesInDir(corpus_path)])

def getBigramForWord(word):
    bigram = []
    word = list(word)
    # first char
    bigram.append('$' + word[0])
    i = 0
    while i < (len(word)-1):
        bigram.append(word[i]+word[i+1])
        i += 1
    # last char
    bigram.append(word[len(word)-1] + '$')
    return bigram

def bigramIndex():
    return loadIndexTable('./storage/bigram_index.json')

def soundexIndex():
    return loadIndexTable('./storage/soundex_index.json')

def getPhoneticHash(word):
    # soundex = fuzzy.Soundex(4)
    return word


def index(fresh=False, dir='./docs/'):
    if not fresh:
        try:
            return loadIndexTable()
        except:
            print("Error while loading INDEX TABLE, continue with new version")

    files = getFilesInDir(dir)
    # index for spelling correction
    # bigram index for isolated tem correction and context sensitive correction
    # soundec index for phonetic correction
    soundex_index = {}
    bigram_index = {}
    index_table = {}
    for file in files:
        tokens = getDocTokens(dir + file)
        for token in tokens:
            if token not in index_table.keys():

                index_table[token[0]] = [(file, token[1])]
                soundex_index[token[0]] = getPhoneticHash(token[0])
                bigram = getBigramForWord(token[0])
                for c in bigram:
                    if c not in bigram_index.keys():
                        bigram_index[c] = [token[0]]
                    else:
                        bigram_index[c].append(token[0])
            elif file not in index_table[token]:
                index_table[token[0]].append((file, token[1]))

    # sort the dictionary for binary search
    index_table = OrderedDict(sorted(index_table.items(), key=lambda t: t[0]))
    bigram_index = OrderedDict(
        sorted(bigram_index.items(), key=lambda t: t[0]))
    soundex_index = OrderedDict(
        sorted(soundex_index.items(), key=lambda t: t[0]))
    # Saving index table to a file
    try:
        saveIndexTable(index_table)
        saveIndexTable(bigram_index, './storage/bigram_index.json')
        saveIndexTable(soundex_index, './storage/soundex_index.json')
    except:
        print("Error while SAVING INDEX TABLE, continue without saving")
    return index_table


def saveIndexTable(index_table, path='./storage/index_table.json'):
    file = open(path, "w")
    file.write(json.dumps(index_table))


def loadIndexTable(path='./storage/index_table.json'):
    file = open(path, "r")
    return json.loads(file.read())
