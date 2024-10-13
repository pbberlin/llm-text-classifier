import os
import pathlib
import re

import pprint
import pickle

from   pypdf import PdfReader
import fitz  # PyMuPDF

import pandas as pd


from nltk import sent_tokenize


# copy from lib_openai
def removeNewlines(txt):
    # flat = re.sub(r'\n+', r' ', txt)
    flat = txt
    flat = flat.replace("\n", ' ')
    flat = flat.replace("  ", ' ')
    flat = flat.replace("  ", ' ')
    return flat

# copy from lib_openai
# ellipsis of a long string
def ell(s, x=16):
    s = removeNewlines(s)
    s.strip()
    if len(s) < 2*x:
        return s
    return f"{s[:x]} … {s[-x:]}"




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

    # ligatures

    # https://www.compart.com/en/unicode/U+FB00
    s = s.replace('ﬀ',  "ff")

    # https://www.compart.com/en/unicode/U+FB02
    s = s.replace('ﬂ',  "fl")

    s = RE_URLs.sub(" ", s)

    s = RE_CONDENSE_NL.sub(" ", s).strip()

    # s = RE_PRINTABLE.sub(' __ ', s)
    flagSpecial(s)

    s = RE_GESPERRT.sub(' ', s)

    s = RE_CONDENSE_SP.sub(' ', s)

    return s

# PDF extraction shortcomings:
#   https://pypdf.readthedocs.io/en/stable/user/extract-text.html#example-1-ignore-header-and-footer
# visitor funcs can be used to include/exclude regions
#
#  func *fails* on the letters "f" or "fi" or "fl" in PDFs of economist articles.
#  also introduces spaces in URLs
def extract1(pth, printProgressUntilPage=-1, mode="plain"):
    rdr = PdfReader(pth)
    cnt = ""
    for idx, key in enumerate(rdr.pages):
        page = rdr.pages[idx]
        cnt += page.extract_text(extraction_mode=mode)  # plain or layout
        cnt += " "
        if idx < printProgressUntilPage:
            print(f"\t   page {idx:3d} complete, {len(cnt):5d} chars")

    return cnt


#  func works better than extract1
def extract2(pth, printProgressUntilPage=-1):
    doc = fitz.open(pth) # pdf document
    cnt = ""
    for idx, key in enumerate(doc):
        page = doc[idx]
        cnt += page.get_text()
        cnt += " "
        if idx < printProgressUntilPage:
            print(f"\t   page {idx:3d} complete, {len(cnt):5d} chars")
    return cnt


def cleanseColOfList(txts1, colIdx=1):

    txts2 = []
    for idx1, row1 in enumerate(txts1):
        row2 = []
        for idx2, val in enumerate(row1):
            if idx2 == colIdx:
                row2.append( cleanBodyText(val) )
            else:
                row2.append(val)
        txts2.append(row2)

    if False:
        pprint.pp(txts2[0])
        pprint.pp(txts2[1])
        pprint.pp(txts2[4])
        pprint.pp(txts2[8])

    return txts2




# iterate files in directory
def iterateLocalDir(dir):

    texts=[]

    dir = os.path.join(".", dir)
    for idx, file in enumerate(os.listdir(dir)):

        filePath = os.path.join(dir, file)

        base = os.path.splitext(file)[0] # no file extension

        # remove hyphens - preserve ' - '
        base = base.replace(' - ','|')
        base = base.replace('-',' ')
        base = base.replace('|',' - ')

        base = base.replace('_', ' ')
        base = base.replace('#update','')
        print(f"  processing #{idx+1:2} \n\t{base}  \n\t{file}")

        if pathlib.Path(file).suffix.lower() == ".pdf":

            # print(f"  found PDF")
            # cnt = extract1(filePath, printProgressUntilPage=-1)
            cnt = extract2(filePath, printProgressUntilPage=-1)

            # if idx < 3 or (idx%9) == 0 or (idx%8) == 0:
            #     print( f"     len {len(text):4d}  start {text[0:33]}  end {text[-33]}" )
            dbgText = RE_CONDENSE_NL.sub(" ", cnt)
            print( f"\t  {len(cnt):4d} chars" )
            print( f"\t  {ell( dbgText, x=64)}" )

            # adding *tuple*
            texts.append((base, cnt))

        elif pathlib.Path(file).suffix.lower() == ".csv":
            print(f"\tskipping CSV file")

        else:
            # non PDF
            with open( filePath, "r", encoding="UTF-8") as f:
                cnt = f.read()
                # adding *tuple*
                texts.append((base, cnt))

    return texts

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


# uploaded file contents into single CSV file
def toCSV(txts, columns= ['fname', 'text'], csvFilePath = os.path.join("data","extracted-pdf-texts.csv")):

    cleansedTxts = cleanseColOfList(txts, colIdx=1)

    df = pd.DataFrame(cleansedTxts)
    df.columns = columns

    # Set the text column to be the raw text with the newlines removed
    # df['text'] = df.fname + ". " + texts2
    df.to_csv(
        csvFilePath,
        sep=";",
        na_rep="<no-data>",
        encoding='utf-8',
        quotechar='"',
        # quoting=csv.QUOTE_NONNUMERIC ,
        quoting=2 ,
    )
    # df.head()

    return cleansedTxts

# uploaded file contents as samples into pickle file
def saveNewSamples(newSamples, append=False):

    smpls = []

    if append:
        try:
            with open(r"./data/samples-newly-imported.pickle", "rb") as inpFile:
                smpls = pickle.load(inpFile)
                print(f"appending 'samples' - loading - size {len(smpls):2}")
        except Exception as error:
            print(f"appending 'samples' - loading - error: {str(error)}")
            smpls = []


    # we could use extend
    for newSpl in newSamples:
        smpls.append(newSpl)

    with open(r"./data/samples-newly-imported.pickle", "wb+") as outFile:
        pickle.dump(smpls, outFile)
        print(f"appending 'samples' - saving  - size {len(smpls):2}")


# takes a list of texts and converts them into samples
#   each element of txts[...][0] should contain title
#   each element of txts[...][1] should contain a longer text
#           txts[...][1] is split into sample statements
#   numSntc - the number of sentences in one statement
def txtsIntoSample(txts, numSntc=5 ):

    smpls = []  # newly created samples

    for i1, row in enumerate(txts):

        smpl = {}
        smpl["descr"] = txts[i1][0] 
        smpl["statements"] = [] 

        body =  txts[i1][1]
        sntcs = sentences(body)
        
        numBatches = int(len(sntcs) / numSntc)

        for i2 in range(numBatches):
            i3 = numSntc*i2
            btch = " ".join(sntcs[i3:i3+numSntc]) # ||
            stmt = {}
            stmt["short"] = sntcs[i3]
            if len(stmt["short"]) > 48:
                stmt["short"] = stmt["short"][:48]
            stmt["long"]  = btch
            smpl["statements"].append(stmt)
            

        smpls.append(smpl)

    return smpls


def uploadedToSamplesInPickleFile():

    textsFromFiles = iterateLocalDir("uploaded-files")
    if len(textsFromFiles) < 1:
        print("no uploaded files found; returning")
        return

    cleansedTexts = cleanseColOfList(textsFromFiles, colIdx=1)

    toCSV(cleansedTexts)

    newSamples = txtsIntoSample(cleansedTexts)


    return newSamples


if __name__ == '__main__':
    newSamples = uploadedToSamplesInPickleFile()
    saveNewSamples(newSamples)
