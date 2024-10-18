import os
from pprint import pprint

# pip install nltk
import nltk

if False:
    nltk.download('punkt')  # for tokenization
    nltk.download("averaged_perceptron_tagger") # for parts of speech tagging

from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.probability import FreqDist

from nltk.text import Text # for concordance


from nltk.stem import WordNetLemmatizer
wnLem = WordNetLemmatizer()

from lib.util import cleanBodyText, txtsIntoSample
from lib.util import loadJson, saveJson



def headerCols(lineCntr, colByIdx, cols):
    ret = ""
    # print(f"\t  cols {len(cols)}")
    for idx, val in enumerate(cols):
        val = val.strip()
        if len(val) > 32:
            val = val[0:32]
        if len(val) == 0:
            val = "[empty]"
        # print(f"\t  key {colByIdx[idx]:10s} - {val}")
        # if colByIdx[idx] != "contents" and colByIdx[idx] != "subtitle" :
        if colByIdx[idx] != "contents" :
            # ret += f"{colByIdx[idx]:10s} - {val}   "
            val = val[:32]
            if colByIdx[idx] == "date":
                val = val[2:]
            if colByIdx[idx] == "speakers":
                val = val[:16]
                val = f"{val:16s}"
            ret += f"{colByIdx[idx]}: {val}   "
    ret = ret.strip()

    ret = ret.replace("speakers:", "sp:")
    ret = ret.replace("title:"   , "ti:")

    ret = f"{ret}  csv-line {lineCntr:3d}  "

    return ret





# Using readline()

speeches = []

# 
def ecbSpeechesCSV2Json(filterBy="", earlyBreakAt=10, tokenizeWords=False):

    speeches = []

    with open('./data/ECB_speeches.csv', mode='r', encoding='UTF8') as file2:
        lineCntr = 0
        impoCntr = 0   # not filtered
        idxByCol = {}
        colByIdx = []
        try:
            print(f"\treading ECB speeches start - filter by {filterBy}")
            while True:

                if impoCntr > earlyBreakAt:
                    print(f"\treading ECB speeches - early break at {earlyBreakAt}")
                    break

                lineCntr += 1

                line = file2.readline()

                if not line:
                    print(f"\tno more lines at {lineCntr}")
                    break

                # header data preparation
                if lineCntr == 1:
                    cols = line.split("|")
                    print(f"\t  line {lineCntr: 3d}")

                    print(f"\t  cols {len(cols)}")
                    for idx, val in enumerate(cols):
                        val = val.strip()
                        if len(val) > 32:
                            val = val[0:32]
                        idxByCol[val] = idx
                        colByIdx.append(val)
                    print(f"\t  cols {idxByCol}")
                    print(f"\t  cols {colByIdx}")
                    continue

                # print(f"Line{count}: {line.strip()}")


                # 
                # 
                # body data processing
                cols = line.split("|")
                metaData = headerCols(lineCntr, colByIdx , cols)
                print(f"\t    {metaData}")

                raw = cols[ idxByCol["contents"] ]
                raw.strip()

                raw = cleanBodyText(raw)


                print(f"\t    line {lineCntr:3d} - content size {len(raw)} ")

                if raw == "":
                    continue

                if filterBy != "":
                    contains1 = (filterBy in raw)
                    contains2 = (filterBy.title() in raw)
                    contains3 = (filterBy.lower() in raw)

                    if contains1 or contains2 or contains3:
                        pass
                    else:
                        print(f"\t  filtered out '{filterBy}' - ")
                        continue


                impoCntr += 1


                sts = sent_tokenize(raw) 
                for idx, st in enumerate(sts):
                    if idx < 7:
                        break
                    if idx > 13:
                        break
                    if (idx % 2) == 0:
                        continue
                    st = st.strip()
                    print(f"\t  \tst {idx:2d} - {st[:53]} ...  {st[len(st)-53:]}")


                if tokenizeWords:
                    words = word_tokenize(raw) # words
                    speeches.append([metaData,raw,sts,words])

                else:
                    speeches.append([metaData,raw,sts])


            print(f"\treading ECB speeches stop")

            newSamples = txtsIntoSample(speeches)
            # saveJson(newSamples, f"ecb-speeches-{filterBy}-smpls", "tmp-import")

            saveJson(speeches,   f"ecb-speeches-{filterBy}", "tmp-import")
            saveJson(newSamples, f"ecb-speeches-smpls-{filterBy}", "tmp-import")


            return newSamples


        except Exception as e:
            file2.close()
            print(f"exception {e}")
            return []


if __name__ == '__main__':
    # does not work from this directory and upper directory
    #   due to import paths (lib.util or just utils)
    ecbSpeechesCSV2Json(earlyBreakAt=10, filterBy="Asset purchase")
