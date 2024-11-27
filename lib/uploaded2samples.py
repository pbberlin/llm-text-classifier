import os
import pathlib
import re

import pprint
import pickle

from   pypdf import PdfReader
import fitz  # PyMuPDF

import pandas as pd


from lib.util import cleanBodyText, txtsIntoSample
import  lib.config as cfg


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
def iterateLocalDir():

    ds  = cfg.get("dataset")
    dir = os.path.join(".", "data", ds, "uploaded-files")

    texts=[]

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


# takes a list of texts and converts them into samples
#   each element of txts[...][0] should contain title
#   each element of txts[...][1] should contain a longer text
#           txts[...][1] is split into sample statements
#   numSntc - the number of sentences in one statement
def uploadedToSamples():


    textsFromFiles = iterateLocalDir()
    if len(textsFromFiles) < 1:
        print("no uploaded files found; returning")
        return

    cleansedTexts = cleanseColOfList(textsFromFiles, colIdx=1)

    toCSV(cleansedTexts)

    newSamples = txtsIntoSample(cleansedTexts)


    return newSamples



if __name__ == '__main__':
    # does not work from this directory and upper directory
    #   due to import paths (lib.util or just utils)
    newSamples = uploadedToSamples()
