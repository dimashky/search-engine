from spellchecker import SpellChecker
from searchengine import indexer
from nltk.tokenize import word_tokenize

spell = SpellChecker()

def getSuggestedQuery(query):
    query_tokens = word_tokenize(query)
    misspelled = spell.unknown(query_tokens)
    for word in misspelled:
        query = query.replace(word, spell.correction(word))
    return query
