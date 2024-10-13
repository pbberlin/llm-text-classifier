import json
import re


domainSpecificWords = {}

def loadDomainSpecificWords():
    with open("./data/terms-central-banking.json") as file1:
        contents = file1.read()
        global domainSpecificWords
        domainSpecificWords = json.loads(contents)
        print(f"[lib_loaddata] central banking terms loaded after - type {type(domainSpecificWords)} - len {len(domainSpecificWords) } ", )


englishStopWords = []

def loadEnglishStopwords():
    from nltk.corpus import stopwords
    global englishStopWords
    englishStopWords = stopwords.words("english") # lower case



def cleanFileName(fn):

    fn = fn.replace(' - ',' separator ') #  preserve ' - '

    # Replace all non a-z and 0-9, '.'  characters
    #    we may add   '\-'
    fn = re.sub(r'[^a-z0-9\.]', ' ', fn, flags=re.IGNORECASE)

    fn = fn.replace(' separator ',' - ') # restore ' - '

    # Condense multiple hyphens into a single one
    fn = re.sub(r'\-+' , '-', fn)
    # Condense multiple dots    into a single one
    fn = re.sub(r'\.+' , '.', fn)


    fn = fn.strip()
    fn = fn.strip('-')
    fn = fn.strip()

    fn = fn.lower()

    return fn