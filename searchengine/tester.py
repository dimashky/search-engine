from os import listdir
from os.path import isfile, join
import json
from searchengine import matcher


def loadQueries():
    file = open('./storage/queries.txt')
    text = file.read()
    return [w for w in text.split('\n') if w]


def loadRelevance():
    file = open('./storage/relevance.txt')
    text = file.read()
    final_relevance = []
    relevances = [r for r in text.split('\n') if r]
    for relevance in relevances:
        final_relevance.append(relevance.split())

    return final_relevance


def createTestCases():
    queries = loadQueries()
    relevances = loadRelevance()
   # return json.loads(open('./storage/test_cases.json', "r").read())

    test_cases = {}
    for query, relevance in zip(queries, relevances):
        results = list(matcher.match(query).keys())
        results = [r.replace(".txt", "") for r in results]
        shared_res = set(relevance) & set(results)

        print(shared_res)
        test_cases[query] = [(doc, results.index(doc) + 1 if doc in results else -1)
                             for doc in shared_res]

    try:
        saveTestCases(test_cases)
    except:
        print("Error while SAVING TEST CASES, continue without saving")
    return test_cases


def saveTestCases(test_cases, path='./storage/test_cases.json'):
    file = open(path, "w")
    file.write(json.dumps(test_cases))


def loadTestCase(path='./storage/test_cases.json'):
    file = open(path, "r")
    return json.loads(file.read())


def testCases():
    return loadTestCase('./storage/test_cases.json')


def runTest():
    test_cases = testCases()
