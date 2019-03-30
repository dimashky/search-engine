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
from nltk.tag.stanford import StanfordNERTagger
import os
# import fuzzy

java_path = "C:/Program Files/Java/jdk1.8.0_181/bin/java.exe"
os.environ['JAVAHOME'] = java_path

def formatted_entities(classified_tokens, with_tag=False):
    entities = {'persons': list(), 'organizations': list(),
                'locations': list(), 'date': list()}

    for entry in classified_tokens:
        entry_value = entry[0]
        entry_type = entry[1]

        if entry_type == 'PERSON':
            entities['persons'].append(entry_value)

        elif entry_type == 'ORGANIZATION':
            entities['organizations'].append(entry_value)

        elif entry_type == 'LOCATION':
            entities['locations'].append(entry_value)

        elif entry_type == 'DATE':
            entities['date'].append(entry_value)

    if (with_tag):
        return entities

    output = entities['persons'] + entities['locations']

    return output


tagger = StanfordNERTagger('C:/searchengine/stanford-ner/classifiers/english.muc.7class.distsim.crf.ser.gz',
                           'C:/searchengine/stanford-ner/stanford-ner.jar',
                           encoding='utf-8')

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


def getDocTokens(filePath, with_relevance=True):
    tokens_with_pos = getTokens(getDocContent(filePath))
    tokens = []
    if(with_relevance):
        tokens = [(token[0], tokens_with_pos.count(token) + (5 if token[1] in ["persons", "locations"] else 0), token[1])
                  for token in set(tokens_with_pos)]
    else:
        tokens = [token[0] for token in tokens_with_pos]
    return tokens


def getTokens(txt):
    tokens = word_tokenize(txt)
    filtered_tokens = [
        w.strip('.') for w in tokens if not w in string.punctuation and not w in my_stop_words and is_ascii(w)
    ]
    classified_tokens_list = tagger.tag(filtered_tokens)
    formatted_result = formatted_entities(classified_tokens_list, True)
    entities = formatted_result['persons'] + formatted_result['locations']

    tokens_with_pos = [
        w for w in nltk.pos_tag(filtered_tokens) if w[1][0] in ["V", "N", "J", "R"]
    ]

    final_tokens = []
    for t in tokens_with_pos:
        if (t[0] in entities):
            key = [key for key in formatted_result if t[0]
                   in formatted_result[key]][0]
            final_tokens.append((t[0].lower(), key))
            continue

        word = ""
        token = t[0].lower()

        if (t[1][0] == "V"):
            word = (lemmatizer.lemmatize(token, "v"), "verb")
        elif (t[1][0] in ["R", "J"]):
            word = (lemmatizer.lemmatize(token, "a"), "noun")
        else:
            word = (stemmer.stem(token), "noun")
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
        print(dir + file)
        tokens = getDocTokens(dir + file)
        for token in tokens:

            if token[0] in index_table.keys():
                index_table[token[0]].append((file, token[1]))
                continue

            index_table[token[0]] = [(file, token[1])]
            soundex_index[token[0]] = getPhoneticHash(token[0])
            bigram = getBigramForWord(token[0])
            for c in bigram:
                if c not in bigram_index.keys():
                    bigram_index[c] = [token[0]]
                else:
                    bigram_index[c].append(token[0])

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
