import json
import string

class AbbreviationResolver:
    def __init__(self):
        try:
            file = open("./storage/abbreviations.json")
            self.abbrev = json.loads(file.read())
            self.abbrev_keys = self.abbrev.keys()
        except FileNotFoundError:
            self.abbrev = {}
    
    def synonym(self, item):
        if(len(punc for punc in string.punctuation if punc != "." and item.find(punc)) != 0):
            return item
        
        item = item.replace(".","")

        if(item in self.abbrev_keys):
            return self.abbrev[item]
            
        return item