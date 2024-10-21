import os
from pprint import pprint

# pip install nltk
import nltk
from   nltk import sent_tokenize, word_tokenize


from lib.util import cleanBodyText, txtsIntoSample
from lib.util import loadJson, saveJson
from lib.util import stackTrace



def headerCols(lineCntr, colByIdx, cols):
    ret = ""
    # print(f"\t  cols {len(cols)}")
    for idx, val in enumerate(cols):
        val = val.strip()
        if len(val) == 0:
            val = "[empty]"
        # print(f"\t  key {colByIdx[idx]:10s} - {val}")
        # if colByIdx[idx] != "contents" and colByIdx[idx] != "subtitle" :
        if colByIdx[idx] != "contents" :
            # ret += f"{colByIdx[idx]:10s} - {val}   "
            if   colByIdx[idx] == "title" :
                # dont shorten
                pass
            elif colByIdx[idx] == "subtitle" :
                val = val.replace("Speech by ", " ")
                val = val.replace("Member of the Executive Board of the ", " ")
                val = val[:32]
                pass
            elif colByIdx[idx] == "date":
                val = val[2:]
            elif colByIdx[idx] == "speakers":
                val = val[:16]
                val = f"{val:16s}"
            else:
                val = val[:32]

            ret += f"{colByIdx[idx]}: {val}   "

    ret = ret.strip()

    ret = ret.replace("speakers:", "sp:")
    ret = ret.replace("title:"   , "ti:")

    ret = f"{ret}  csv-line {lineCntr:3d}  "

    return ret





# Using readline()

speeches = []

#
def ecbSpeechesCSV2Json(numSntcs,  filterBy="", earlyBreakAt=10,  tokenizeWords=False):

    speeches = []

    with open('./data/ECB_speeches.csv', mode='r', encoding='UTF8') as file2:
        lineCntr = 0
        impoCntr = 0   # not filtered
        idxByCol = {}
        colByIdx = []
        try:
            print(f"reading ECB speeches start - filter by {filterBy}")
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
                metaDataTwoLines = metaData.split(" ti: ")

                raw = cols[ idxByCol["contents"] ]
                raw.strip()

                if raw == "":
                    continue

                if filterBy != "":
                    contains1 = (filterBy in raw)
                    contains2 = (filterBy.title() in raw)
                    contains3 = (filterBy.lower() in raw)

                    if contains1 or contains2 or contains3:
                        print(f"\tline {lineCntr:3d} - content size {len(raw)} ")
                    else:
                        print(f"\tline {lineCntr:3d} - does not contain '{filterBy}' - continue")
                        continue

                impoCntr += 1


                print(f"\t    {metaDataTwoLines[0]}")
                print(f"\t    {metaDataTwoLines[1][:60]}")

                # cut off reference part
                # before cleanBodyText
                delimiters = [
                    "hank you for your attention.",
                    "orward to your questions.",
                    "ielen dank für Ihre Aufmerksamkeit.",
                    "hank you.",
                    "your questions.      See ",
                    "your questions.       See ",
                    ".      See ",
                    ".       See ",
                ]
                anyFound = False
                for delimiter in delimiters:
                    if delimiter in raw:
                        print(f"\t\t'{delimiter}'s found")
                        cutoff = raw.index(delimiter)
                        fourFifths = int(len(raw)*0.65)
                        if cutoff > fourFifths:
                            raw = raw[:cutoff]
                            print(f"\t\t cutoff at {cutoff} - {fourFifths}")
                            anyFound = True
                            break
                    else:
                        pass
                        # print(f"\t\t'{delimiter}' not found")

                print(f"\t\tany delimiter found: {anyFound}")




                raw = cleanBodyText(raw)

                sts = sent_tokenize(raw)
                # debug only
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


            saveJson(speeches,   f"ecb-speeches-{filterBy}"      , "tmp-import")
            # print(f"reading ECB speeches stop")

            longwords = {}
            longwords = loadJson(f"longwords", "tmp-import", onEmpty="dict")
            newSamples, longwords = txtsIntoSample(speeches, longwords, numSntcs)
            saveJson(longwords,  f"longwords", "tmp-import")

            numSStr = "-".join(  map(str, numSntcs) )
            saveJson(newSamples, f"ecb-speeches-smpls-{filterBy}-{numSStr}stcs", "tmp-import")


            return newSamples


        except Exception as exc:
            file2.close()
            print(f"ecbSpeechesCSV2Json(): exception {exc}")
            print(stackTrace(exc))
            return []


if __name__ == '__main__':
    # does not work from this directory and upper directory
    #   due to import paths (lib.util or just utils)
    ecbSpeechesCSV2Json(earlyBreakAt=10, filterBy="Asset purchase")
