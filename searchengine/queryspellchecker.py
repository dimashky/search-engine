from spellchecker import SpellChecker
from searchengine import indexer

spell = SpellChecker()

def getSuggestedQuery(query):
    query_tokens = indexer.tokenize(query)
    misspelled = spell.unknown(query_tokens)
    for word in misspelled:
        query = query.replace(word, spell.correction(word))
    return query
