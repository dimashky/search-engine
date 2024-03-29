from searchengine import indexer, abbreviation, loader
from collections import OrderedDict
from similarity.levenshtein import Levenshtein
from operator import itemgetter
from scipy import spatial
import numpy as np
import traceback

abbreviationResolver = abbreviation.AbbreviationResolver()

def makeVector(document, dimensions, date_dimenstions):
    index_table = indexer.index()
    dates_index = loader.loadJsonFile('./storage/dates_index.json')
    if not dates_index: dates_index = {}
    dates_index_keys = dates_index.keys()
    vector = []
    for dim in dimensions:
        docs = [doc[0] for doc in index_table[dim]]
        if (document in docs):
            vector.append(
                [doc[1] for doc in index_table[dim] if doc[0] == document][0])
        else:
            vector.append(0)
    for dim in date_dimenstions:
        if(dim in dates_index_keys and document in dates_index[dim]):
            vector.append(1)
        else:
            vector.append(0)
    return vector


def getDocuments(dimensions, date_dimenstions):
    index_table = indexer.index()
    dates_index = loader.loadJsonFile('./storage/dates_index.json')
    if not dates_index: dates_index = {}
    dates_index_keys = dates_index.keys()
    documents = {}
    try:
        for dim in dimensions:
            docs = [doc[0] for doc in index_table[dim]]
            for doc in docs:
                if (doc not in documents):
                    v = makeVector(
                        doc, dimensions, date_dimenstions)
                    documents[doc] = v / np.linalg.norm(v)
        for dim in date_dimenstions:
            if not dim in dates_index_keys:
                continue
            for doc in dates_index[dim]:
                if (doc not in documents):
                    v = makeVector(
                        doc, dimensions, date_dimenstions)
                    documents[doc] = v / np.linalg.norm(v)
    except Exception as e:
        print("Exception in get Docs\n"+str(e))
        traceback.print_exc()

    return documents


def getCorrectQuery(query_tokens):
    index_table = indexer.index()
    correct_query_token = []
    for t in query_tokens:
        if(t in index_table.keys()):
            correct_query_token.append(t)
        # else correct it with any algo
        # else:
            # correct_query_token.append(getCorrectWordUsingBigramIndex(t))
    return correct_query_token


def getCorrectWordUsingBigramIndex(word):
    bigram_index = indexer.bigramIndex()
    possible_words = {}
    levenshtein = Levenshtein()
    bigram = indexer.getBigramForWord(word)
    for b in bigram:
        if b in bigram_index.keys():
            for term in bigram_index[b]:
                possible_words[term] = 0
    for p_word in possible_words:
        possible_words[p_word] = levenshtein.distance(word, p_word)
    possible_words = OrderedDict(
        sorted(possible_words.items(), key=lambda kv: kv[1]))
    return list(possible_words.keys())[0]


def getCorrectDate(date_tokens):
    dates_index = loader.loadJsonFile('./storage/dates_index.json')
    # for d in date_tokens:
    #  if(d not in dates_index.keys()):
    #     date_tokens.remove(d)
    return date_tokens


def getCorrectWordUsingSoundexIndex(word):
    soundex_index = indexer.soundexIndex()
    phonetic_hash = indexer.getPhoneticHash(word)
    for term, hash in soundex_index:
        if(hash == phonetic_hash):
            return term
    return 0


def match(query):
    global abbreviationResolver
    query = abbreviationResolver.replaceTextAbbreviation(query)
    query = query.lower()
    query_tokens = [token[0] for token in indexer.getTokens(query)]
    query_tokens += indexer.nGramsHandler(query_tokens, 1)
    query_tokens = getCorrectQuery(query_tokens)
    query_date_tokens = indexer.extractDates(query)
    query_date_tokens = getCorrectDate(query_date_tokens)

    query_vector = [1] * (len(query_tokens) + len(query_date_tokens))
    documents = getDocuments(query_tokens, query_date_tokens)
    relevance_document = {}

    for doc in documents:
        relevance_document[doc] = cos_similarity = 1 - spatial.distance.cosine(query_vector, documents[doc])
        if(cos_similarity == 1):
            relevance_document[doc] = sum(documents[doc])/len(documents[doc])

    relevance_document = OrderedDict(
        sorted(relevance_document.items(), key=itemgetter(1), reverse=True))
    return relevance_document
