# pdf plumber for analysis of PDF files
import pdfplumber

sr = {
    "Regulatory capital in EUR million €": "RegCap",
    "Performance indicators":              "PerfInd",
    "Balance sheet in €m":                 "BalSht",
    "Income statement in €m":              "IncStatmt",

}

from collections import defaultdict

def replaceMany(s):
    for key, value in sr.items():
        s = s.replace(key, str(value))
    return s


def processFile(fn: str, limitPages=2222, limitOther=2222):

    print(f"{fn=}")

    with pdfplumber.open(fn) as pdf:

        # print(pdf.metadata)
        for k in pdf.metadata:
            if "Producer" in k:
                continue
            if "Creator" in k:
                continue
            print(f"\t{k:12} {pdf.metadata[k]}")


        for idx0, page in enumerate(pdf.pages):
            if idx0 > limitPages:
                break




            print(f"\tp{idx0:3>}  ", end="")

            txt = page.extract_text()
            # print(type(txt))
            lines = txt.split("\n")
            print(f"  {len(txt):4} chars   {len(lines):4} lines")
            

            if False:
                # rectangles dont contain any text
                keysAll = defaultdict(lambda: 0)
                for idx2, rect in enumerate(page.rects):
                    keys = [*rect] # unpack into a list literal 
                    # print( keys )
                    for k in keys:
                        if k == "tag" or k == "object_type" or k == "path" or k == "pts":
                            if not rect[k] is None:
                                tp = type(rect[k])
                                s = f"{rect[k]}"
                                print(f"\t{k:10}  {tp}  {s[:80]}")
                        else:
                            keysAll[k] += 1
                    pass
                for ka in keysAll:
                    print(f"\t{ka:24} - {keysAll[ka]:4}")
            
            continue

            # text with x-y coordinates
            top = -1
            rowCntr = 0
            lineLen = 0
            xPrev = 0
            lenPrev = 20
            for idx2, word in enumerate(page.extract_words()):
                # word is a dictionary with text, x0, x1, top, bottom, and more.
                if top != word["top"]:
                    top = word["top"]
                    rowCntr += 1
                    lineLen = 0
                    print(f"")
                    print(f"\trow{rowCntr} tp{word["top"]:6.1f} ", end="")
                lineLen += len(word["text"])
                dx = (word["x0"] - xPrev)
                perChar = dx / lenPrev

                # print(f"{word["text"]} {perChar:.1f} ", end="")
                print(f"{word["text"]} ", end="")
                if perChar > 15:
                    print("")
                    print("\t new col? ", end="")
                if lineLen > 95:
                    lineLen = 0
                    print("")
                    print("\t  ", end="")

                xPrev   = word["x0"]
                lenPrev = len(word["text"])
                if rowCntr> 4*limitOther:
                    print()
                    break

            # tables
            tables = page.extract_tables()
            for idx2, table in enumerate(tables):
                print(f"\tt{idx2:3>}  ")
                # print(f"\tt{idx2:3>}  {table}")
                # nested list representing table rows and columns.
                for idx3, row in enumerate(table):
                    # print(f"\tr{idx3:3>} {row} ")
                    print(" ", end="")
                    for idx4, cell in enumerate(row):
                        if cell is None:
                            cell="-"
                        if cell == "":
                            cell="-"
                        cell = replaceMany(cell)
                        cell = cell.strip()
                        print( f"{cell:>10} ", end="" )
                    print("")


                if idx2> limitOther:
                    break




files = [
    "AT_Oberbank_AG_2016_cbcr_ar_en-page-146-148.pdf",
    "DE_Berenberg_Bank_-_Joh._Berenberg_Gossler_Co._KG_2015_cbcr_sd_de.pdf",
    "DE_Berenberg_Bank_-_Joh._Berenberg_Gossler_Co._KG_2016_cbcr_sd_de.pdf",
]

for fn in files:
    processFile(fn)