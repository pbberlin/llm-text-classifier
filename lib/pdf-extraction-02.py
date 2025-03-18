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
def extractTables(pg, pageNum=0):

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
            extractTables(pg, pgNum)

        # see pdf-extraction-01.py for more extraction logic - but useless










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