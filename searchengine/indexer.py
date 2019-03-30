import nltk, re, os, string, json
from nltk.stem import WordNetLemmatizer, LancasterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import OrderedDict
from nltk.tag.stanford import StanfordNERTagger
from searchengine import loader, relevance
## import fuzzy

# JAVA ENV
java_path = "C:/Program Files/Java/jdk1.8.0_181/bin/java.exe"
os.environ['JAVAHOME'] = java_path
tagger = StanfordNERTagger('C:/searchengine/stanford-ner/classifiers/english.muc.7class.distsim.crf.ser.gz',
                           'C:/searchengine/stanford-ner/stanford-ner.jar',
                           encoding='utf-8')

# GLOBAL VARIABLES
index_table_cached = False
lemmatizer = WordNetLemmatizer()
stemmer = LancasterStemmer()
stop_words = set(stopwords.words('english'))
du_stop_words = [w for w in loader.loadFile('./storage/stop_words.txt').split('\n') if w]


def index(fresh=False, dir='./docs/'):
    global index_table_cached

    if not fresh:
        if (index_table_cached):
            return index_table_cached
        index_table_cached = loader.loadJsonFile('./storage/index_table.json')
        if(index_table_cached):
            return index_table_cached

    # index for spelling correction
    # bigram index for isolated tem correction and context sensitive correction
    # soundec index for phonetic correction
    soundex_index = {}
    bigram_index = {}
    index_table = {}

    files = loader.getFilesInDir(dir)
    for file in files:
        print("Indexing File: " + dir + file)
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
    
    index_table_cached = index_table
    loader.saveJsonFile('./storage/index_table.json', index_table)
    loader.saveJsonFile('./storage/bigram_index.json', bigram_index)
    loader.saveJsonFile('./storage/soundex_index.json', soundex_index)
    
    return index_table

def getTokens(txt):
    txt = txt.lower()
    word = ""
    final_tokens = []
    tokens = word_tokenize(txt)

    filtered_tokens = [w.translate(str.maketrans('', '', string.punctuation)) for w in tokens]
    filtered_tokens = [w for w in filtered_tokens if not w in list(string.punctuation) + du_stop_words and is_ascii(w) and len(w)]

    tokens_with_pos = [
        w for w in nltk.pos_tag(filtered_tokens) if w[1][0] in ["V", "N", "J", "R"]
    ]

    for t in tokens_with_pos:
        token = t[0]
        pos = t[1]

# Standford TOKEN TYPE
#        stanford_token_type = tagger.tag(token)[1]
#        if (stanford_token_type in ["PERSON","ORGANIZATION","LOCATION"]):
#            final_tokens.append((token, stanford_token_type))
#            continue

        if (pos[0] == "V"):
            word = (lemmatizer.lemmatize(token, "v"), "verb")
        elif (pos[0] in ["R", "J"]):
            word = (lemmatizer.lemmatize(token, "a"), "noun")
        else:
            word = (stemmer.stem(token), "noun")

        final_tokens.append(word)

    return final_tokens

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def getDocTokens(filePath, with_relevance=True):
    doc_content = loader.loadFile(filePath)

    tokens_with_pos = getTokens(doc_content)
    tokens = []
    if(with_relevance):
        tokens = relevance.calc(tokens_with_pos)
    else:
        tokens = [token[0] for token in tokens_with_pos]

    return tokens

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
    return loader.loadJsonFile('./storage/bigram_index.json')

def soundexIndex():
    return loader.loadJsonFile('./storage/soundex_index.json')

def getPhoneticHash(word):
    # soundex = fuzzy.Soundex(4)
    return word