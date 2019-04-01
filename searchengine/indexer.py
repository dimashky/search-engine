import nltk, re, os, string, json
from nltk.stem import WordNetLemmatizer, LancasterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import OrderedDict
from nltk.tag.stanford import StanfordNERTagger
from searchengine import loader, relevance, abbreviation
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
du_stop_words = [w.lower() for w in loader.loadFile('./storage/stop_words.txt').split('\n') if w]
abbreviationResolver = abbreviation.AbbreviationResolver()

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

    quantity_pattern = "((\d{1,3},\d{3})|(\d{1,3}))(-\w*)*"

    filtered_tokens = [w.strip(string.punctuation) for w in tokens if not re.search(quantity_pattern, w)]
    filtered_tokens = [w for w in filtered_tokens if not w in list(string.punctuation) + du_stop_words and is_ascii(w) and len(w) > 1]

    multi_terms = nGramsHandler(filtered_tokens)

    tokens_with_pos = [
        w for w in nltk.pos_tag(filtered_tokens) if w[1][0] in ["V", "N", "J", "R"]
    ] + [
        (w, "Noun") for w in multi_terms
    ]

#Standford TOKEN TYPE
#    stanford_tokens_pos = tagger.tag(tokens)

    for idx,(token,pos) in enumerate(tokens_with_pos):

#        if (stanford_tokens_pos[idx][1] in ["PERSON","ORGANIZATION","LOCATION"]):
#            final_tokens.append((token, stanford_tokens_pos[idx]))
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
    content_replaced_abbreviation = abbreviationResolver.replaceTextAbbreviation(doc_content)
    tokens_with_pos = getTokens(content_replaced_abbreviation)
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

def nGramsHandler(terms, min_occurance = 3):
    global abbreviationResolver

    gram2 = list(nltk.ngrams(terms, 2))
    gram2 = [g[0]+" "+g[1] for g in gram2 if not g[0] in du_stop_words and not g[1] in du_stop_words]

    gram3 = list(nltk.ngrams(terms, 3))
    gram3 = [g[0]+" "+g[1]+" "+g[2] for g in gram3 if not g[0] in du_stop_words and not g[2] in du_stop_words]
    
    gram4 = list(nltk.ngrams(terms, 4))
    gram4 = [g[0]+" "+g[1]+" "+g[2]+" "+g[3] for g in gram4 if not g[0] in du_stop_words and not g[3] in du_stop_words]

    grams = gram2 + gram3 + gram4
    grams = [g for g in grams if grams.count(g) >= min_occurance or abbreviationResolver.isTerm(g)]

    return grams
