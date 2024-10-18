import os
import json
from datetime import datetime

import traceback, sys

import re
from pprint import pprint


from nltk import sent_tokenize
from nltk import word_tokenize




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

        with open(fn, encoding="utf-8") as inFile:
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



def flagSpecial(s):
    np = {}
    for char in s:
        if ord(char) not in range(16,127):
            if char in np:
                np[char] += 1
            else:
                np[char] = 1

    if len(np) > 0:
        pprint(np)

    return np




RE_CONDENSE_SP = re.compile(r' +')   # condense spaces
RE_CONDENSE_NL = re.compile(r"\s+")  # also newlines and tabs

# menu labels from PDF extractions - from the economist...
RE_GESPERRT    = re.compile(r"( \w){8,}")  # gesperrte Worte "O t t o v o n B i s m a r c k"


# RE_ONLY_ASCII = re.compile(r'[^\x00-\x7F]')
RE_PRINTABLE = re.compile(r'[^\x20-\x7F]')

# RE_URLs = re.compile(r'http\S+')
# RE_URLs = re.compile(r'^https?:\/\/.*[\r\n]*')
RE_URLs = re.compile(r'(http[s]?://\S+)')

# [34]
RE_BRACK1 = re.compile(r'\[\d+\]')
# (2020)  189-222
RE_BRACK2 = re.compile(r'\(\d+\)')
# 189-222


def cleanBodyText(s, compare=False):


    s = s.replace("\x00",  " ") # replace CTRL
    s = s.replace("£",  " Pound ")
    s = s.replace("€",  " Euro ")
    s = s.replace("©",  "  (C) ")
    s = s.replace("→",  "  => ")

    s = s.replace('’',  "'")
    s = s.replace('“',  '"')
    s = s.replace('”',  '"')
    s = s.replace('—',  " - ")
    s = s.replace('–',  " - ")

    # ligatures

    # https://www.compart.com/en/unicode/U+FB00
    s = s.replace('ﬀ',  "ff")

    # https://www.compart.com/en/unicode/U+FB02
    s = s.replace('ﬂ',  "fl")

    s = RE_URLs.sub(" ", s)

    s = RE_CONDENSE_NL.sub(" ", s)
    
    s = RE_BRACK1.sub(" ", s)
    s = RE_BRACK2.sub(" ", s)

    # s = RE_PRINTABLE.sub(' __ ', s)
    flagSpecial(s)

    s = RE_GESPERRT.sub(' ', s)

    s = RE_CONDENSE_SP.sub(' ', s)

    s = s.strip()

    return s





# we use the nltk tokenizer,
# because it should ignore the first dot in "Mr. Smith goes to Washington."
debugLines=4

def sentences(txt):
    sntcs = sent_tokenize(txt, language="english")
    print( f"  { len(sntcs)} sentences found")
    for idx, sntc in enumerate(sntcs):
        if idx < debugLines or idx >= len(sntcs) - debugLines:
            # print( f"    {idx+1:3}  {len(sntc):3}  {ell(sntc, x=48)}")
            print( f"    {idx+1:3}  {len(sntc):3}  {sntc[:124]}")
    return sntcs


def longWords(s, greaterThan=7, maxLen=64):

    s = s.strip()
    words = word_tokenize(s)
    lng = []
    for w in words:
        if len(w) > greaterThan:
            if not lng.count(w) > 0:  # dont add twice
                lng.append(w)
   

    lng.sort(key=len)
    lng.reverse()



    # cut off after maxLen
    sz = 0
    idxCutoff = 2
    for idx, w in enumerate(lng):
        sz += len(w)
        if sz > maxLen:
            idxCutoff = idx
            break

    lng = lng[:idxCutoff]

    return " ".join(lng)

def txtsIntoSample(txts, numSntc=5 ):

    smpls = []  # newly created samples

    for i1, row in enumerate(txts):

        smpl = {}
        smpl["descr"] = txts[i1][0].strip()
        smpl["statements"] = []

        body =  txts[i1][1]

        sntcs = sentences(body)

        numBatches = int(len(sntcs) / numSntc)

        for i2 in range(numBatches):
            i3 = numSntc*i2
            btch = " ".join(sntcs[i3:i3+numSntc]) # ||
            shrt = longWords(btch) 
            stmt = {}
            stmt["short"] = shrt
            stmt["long"]  = btch.strip()
            smpl["statements"].append(stmt)


        smpls.append(smpl)

    return smpls


