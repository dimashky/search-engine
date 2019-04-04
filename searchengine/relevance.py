import re, math
from searchengine import loader, indexer

def tf(tokens_with_pos, corpus_path = "./docs/"):
    tokens_tf = []
    tokens = [t[0] for t in tokens_with_pos]
    tokens_count = len(tokens)
    for token_with_pos in set(tokens_with_pos):
        token = token_with_pos[0]
        pos = token_with_pos[1]

        term_count = tokens.count((token))
        tf = term_count
        tf = 1 + math.log10(tf)

        if(pos in ["PERSON","ORGANIZATION","LOCATION"]):
            tf += (tf / 10) # add some weight
        if(token.count(" ") > 0):
            tf += 0 #term_count * 0.05 # add some weight
        
        tokens_tf.append((token, tf, pos))
    return tokens_tf

def relevance(tf, idf):
    return tf*idf

def getIndexTableWithIDF(tokens_frequency, corpus_docs_cnt):
    index_table = {}
    for token, docs in tokens_frequency.items():
        df = len(docs)
        idf = math.log10(corpus_docs_cnt/df)
        index_table[token] = [(d[0], relevance(d[1], idf)) for d in docs]
    return index_table



