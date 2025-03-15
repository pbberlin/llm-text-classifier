'''
streamlit run pdf-extraction-02.py

'''

import os
from   pathlib import Path
import pandas as pd


import streamlit as st


import fitz  # PyMuPDF
import pdfplumber

from collections import defaultdict


sr = {
    "Regulatory capital in EUR million €": "RegCap",
    "Performance indicators":              "PerfInd",
    "Balance sheet in €m":                 "BalSht",
    "Income statement in €m":              "IncStatmt",

}
def replaceMany(s):
    for key, value in sr.items():
        s = s.replace(key, str(value))
    return s





def lastXDirs(pth: str, tailSize: int) -> str:
    p1 = Path(pth).resolve()          # ensure absolute path
    p2 = Path(*p1.parts[-tailSize:])
    return str(p2)



def uniqueCols(cols):
    seen = {}
    newCols = []
    for cl in cols:
        if cl in seen:
            seen[cl] += 1
            newCols.append(f"{cl}_{seen[cl]}")  # append index to duplicate names
        else:
            seen[cl] = 0
            newCols.append(cl)
    return newCols


def showDF(df: pd.DataFrame, pageNum: int, tableNum: int):

    st.write(f"page{pageNum} - table{tableNum}")
    try:
        st.dataframe(df)  # interactive table
    except Exception as exc:
        # print(exc)
        st.write(exc)
        print(exc)


# using pdf plumber
def extractTables1(pg, pageNum=0):

    tables = pg.extract_tables()
    for tableNum, table in enumerate(tables):
        # print(f"\tt{tableNum:3>}  ")

        df = pd.DataFrame(table[1:], columns=table[0])  # to DataFrame
        # unique column names
        df.columns = uniqueCols(df.columns)
        
        showDF(df, pageNum, tableNum)

        if False:
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




def processFile(pth: Path, limitPages=10, limitOther=2222):

    lastX2 = lastXDirs(pth, 2)
    lastX4 = lastXDirs(pth, 4)

    print(f"pth = ..{os.sep}{lastX4}")
    st.write(f"### file ..{os.sep}{lastX2}")

    with pdfplumber.open(pth) as pdf:
        
        for pgNum, pg in enumerate(pdf.pages):
            if pgNum > limitPages:
                break
            extractTables1(pg, pgNum)

        # see pdf-extraction-01.py for more extraction logic - but useless




def MuPdfExtractTables2(pg, pageNum=0):

    txtDict = pg.get_text("dict")  # text with positions

    numBlocks = len(txtDict["blocks"])

    if numBlocks > 0:
        print(f"\t  tables found {numBlocks}")
    else:
        return

    for idx, block in enumerate(txtDict["blocks"]):  # text blocks

        tblData = []

        blockType = "Text" 
        if block["type"] == 0:
            blockType = "Text" 
        else: 
            blockType = "Image"


        print(f"\tblock type: {blockType}")
        # print(f"Content: {' '.join(span['text'] for line in block.get('lines', []) for span in line['spans'])}")

        row = []
        for line in block.get("lines", []):
            row_text = " ".join(span["text"] for span in line["spans"])
            row.append(row_text)
        if row:
            tblData.append(row)

        # extracted data to DataFrame (if structured properly)
        df = pd.DataFrame(tblData)
        showDF(df, pageNum, idx)





def MuPdfProcessFile(pth: Path, limitPages=10, limitOther=2222):

    print(f"pth = ..{os.sep}{lastXDirs(pth, 4) }")

    # pdf = fitz.open(pth)
    with fitz.open(pth) as pdf:  # automatically closes 
 
        vs = {}
        for k in pdf.metadata:
            v = pdf.metadata[k]
            if v is None or v.strip() == "":
                continue
            # if "Creator"  in k:
            #     continue
            if v in vs:
                continue
            vs[v] = True
            print(f"\t{k:12} -{v}-")


        for idx0, pg in enumerate(pdf):

            if idx0 > limitPages:
                print(f"\tp{idx0:3>} ...  p{len(pdf)} - p{pdf.page_count} - skipping ", end="")
                break

            print(f"\tp{idx0:-2}  ", end="")

            txt = pg.get_text()
            # print(type(txt))
            lines = txt.split("\n")
            print(f"  {len(txt):4} chars   {len(lines):4} lines")

            MuPdfExtractTables2(pg)

            continue

            rtf = pg.get_text("rtf")
            pRtf = pth.lower().replace(".pdf",".rtf")
            with open(pRtf, "w", encoding="utf-8") as f:
                f.write(rtf)








files = [
    "AT_Oberbank_AG_2016_cbcr_ar_en-page-146-148.pdf",
    "DE_Berenberg_Bank_-_Joh._Berenberg_Gossler_Co._KG_2015_cbcr_sd_de.pdf",
    "DE_Berenberg_Bank_-_Joh._Berenberg_Gossler_Co._KG_2016_cbcr_sd_de.pdf",
    "AT_Oberbank_AG_2016_cbcr_ar_en.pdf",
]

workDir = Path.cwd() / "cbcr"

for fn in files:
    pth = workDir / fn
    processFile(pth)
    # MuPdfProcessFile(pth)