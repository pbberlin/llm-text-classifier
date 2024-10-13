import os
import pickle
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

    ret = f"line {lineCntr:3d}  {ret}"

    return ret





# Using readline()

speeches = []

# 
def ecbSpeechesCSV2Pickle():

    try:
        with open(r"./data/ecb_speeches.pickle", "rb") as inpFile:
            speeches = pickle.load(inpFile)
    except Exception as error:
        print(f"loading pickle file 'ecb_speeches' caused error: {str(error)}")

    if len(speeches) > 5:
        print(f"loading pickle file 'ecb_speeches' - {len(speeches)} rows ")
        return
    


    with open('./data/ECB_speeches.csv', mode='r', encoding='UTF8') as file2:
        lineCntr = 0
        idxByCol = {}
        colByIdx = []
        try:
            print(f"\treading ECB speeches start")
            while True:
                lineCntr += 1

                if lineCntr > 10:
                    print(f"\treading ECB speeches - early break")
                    break


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

                print(f"\t    line {lineCntr:3d} - content size {len(raw)} ")

                if raw == "":
                    continue


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


                words = word_tokenize(raw) # words

                speeches.append([metaData,raw,sts,words])

            print(f"\treading ECB speeches stop")

            with open(r"./data/ecb_speeches.pickle", "wb+") as outFile:
                pickle.dump(speeches, outFile)

        except Exception as e:
            file2.close()
            print(f"exception {e}")

