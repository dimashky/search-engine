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
import fuzzy

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
    return getTokens(file.read())


def getTokens(txt):
    tokens = word_tokenize(txt)
    filtered_tokens = [w.strip(
        '.') for w in tokens if not w in string.punctuation and not w in my_stop_words and is_ascii(w)]
    preferred_tokens = [w[0] for w in nltk.pos_tag(
        filtered_tokens) if w[1] in pos_tag_preferred]
    stemmed_tokens = [stemmer.stem(lemmatizer.lemmatize(w))
                      for w in preferred_tokens]
    return stemmed_tokens


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
    soundex = fuzzy.Soundex(4)
    return soundex(word)


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
                index_table[token] = [file]
                soundex_index[token] = getPhoneticHash(token)
                bigram = getBigramForWord(token)
                for c in bigram:
                    if c not in bigram_index.keys():
                        bigram_index[c] = [token]
                    else:
                        bigram_index[c].append(token)
            elif file not in index_table[token]:
                index_table[token].append(file)

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
