import re, math
from searchengine import loader, indexer

def calc(tokens_with_pos, corpus_path = "./docs/"):
    tokens_with_relevance = []
    tokens = [t[0] for t in tokens_with_pos]
    for token_with_pos in set(tokens_with_pos):
        token = token_with_pos[0]
        pos = token_with_pos[1]
        relevance = 0

        tf = 1 + math.log10(tokens.count((token)))
        idf = 1

        relevance = tf * idf

        if(pos in ["PERSON","ORGANIZATION","LOCATION"]):
            relevance += (relevance / 10) # add some weight
        
        tokens_with_relevance.append((token, relevance, pos))
    return tokens_with_relevance
