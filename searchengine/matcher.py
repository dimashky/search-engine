from searchengine import indexer

def match(query):
    index_table = indexer.index()
    query_tokens = indexer.getTokens(query)
    common_tokens = set(index_table.keys()) & set(query_tokens)
    return set([doc for t in common_tokens for doc in index_table[t]])