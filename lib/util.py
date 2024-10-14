import os
import json
from datetime import datetime

import traceback, sys

import re

def stackTrace(e):

    cwd = os.getcwd()

    l = []

    fls = traceback.format_exc().splitlines()
    fls = fls[1:] # remove constant Traceback (most recent call last):

    for idx, line in enumerate(fls):
        # line = line.replace("\"C:\python3\lib", "...")
        line = line.replace("File \"", "")
        line = line.replace("\",", "\t\t")
        line = line.replace( cwd , "...")

        l.extend( f"{idx:2d} {line} \n")

    l.extend( "---\n")

    l.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]) )

    s = ""
    s += "".join(l)
    s.strip()

    return s


domainSpecificWords = {}

def loadDomainSpecificWords():
    with open("./data/init/terms-central-banking.json") as file1:
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
'''
generic save as JSON.

    :param dta        :       any list or dict
    :param str name   :       name part of file
    :param str subset :       subdir under data
    :param [0,1,2,3] tsGran: timestamp granularity

    :rtype: None
'''
def saveJson(dta, name, subset="misc", tsGran=0):

    try:

        dr = os.path.join(".", "data", subset)
        os.makedirs(dr, exist_ok=True )

        ts = ""
        if   tsGran == 1:
            ts = f"-{datetime.now():%Y-%m-%d-%H}"
        elif tsGran == 2:
            ts = f"-{datetime.now():%Y-%m-%d-%H-%M}"
        elif tsGran == 3:
            ts = f"-{datetime.now():%Y-%m-%d-%H-%M-%S}"

        fn = os.path.join(dr, f"{name}{ts}.json" )

        with open(fn, "w", encoding='utf-8') as outFile:
            json.dump(dta, outFile, ensure_ascii=False, indent=4)
            print(f"saving '{name:12}' as json - {len(dta):3} entries - {dr}")

    except Exception as exc:
        print(str(exc))
        # print( stackTrace(exc) )




'''
generic loading from JSON.

    :param str name   :       name part of file
    :param str subset :       subdir under data
    :rtype: []
'''
def loadJson(name, subset="misc", onEmpty="list"):

    try:
        dr = os.path.join(".", "data", subset)
        fn = os.path.join(dr, f"{name}.json" )

        with open(fn) as inFile:
            strContents = inFile.read()
            dta = json.loads(strContents)
            print(f"loaded  '{name:12}' as json {type(dta)} - {len(dta):3} entries - {dr}")
            return dta


    except Exception as exc:
        print(str(exc))
        # print( stackTrace(exc) )
        if onEmpty=="dict":
            return {}
        return []



