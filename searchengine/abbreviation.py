import json, string, re
from searchengine import loader

class AbbreviationResolver:
    def __init__(self):
        self.abbrev = loader.loadJsonFile("./storage/abbreviations.json")
        
        if(self.abbrev == False):
            print("no abbrevs get, reset dict")
            self.abbrev = {}
        
        self.pattern = "((\w\.)+\w)"
        self.abbrev_keys = self.abbrev.keys()
    
    def isAbbreviation(self, term):
        return not re.search(self.pattern, term) is None

    def getAbbreviation(self, term):
        if not term in self.abbrev_keys:
            return term

        return self.abbrev[term].lower()
    
    def replaceTextAbbreviation(self, text):
        abbrev_matches = re.findall(self.pattern, text)
        abbrev_matches = set([abbrev[0] for abbrev in abbrev_matches if abbrev[0].upper() in self.abbrev_keys])
        for abbrev in abbrev_matches:
            text = text.replace(abbrev, self.abbrev[abbrev.upper()])
        for abbrev in [k for k in self.abbrev_keys if not re.search(self.pattern, k)]:
            text = text.replace(abbrev, self.abbrev[abbrev.upper()])
        return text
    
    def isTerm(self, term_with_spaces):
        return len([t for t in self.abbrev_keys if self.abbrev[t].lower() == term_with_spaces.lower()]) > 0