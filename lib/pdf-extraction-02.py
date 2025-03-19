'''
streamlit run pdf-extraction-02.py

'''

import os
from   pathlib import Path
import pandas as pd


import streamlit as st
st.set_page_config(
    page_title=None, 
    page_icon=None, 
    # layout="centered", 
    layout="wide", 
    # initial_sidebar_state="auto", 
    initial_sidebar_state="collapsed", 
    menu_items=None,
)
print("\nrun start")

import fitz  # PyMuPDF
import pdfplumber
import pdfminer.high_level

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
def UnusedextractTables(pg, pageNum=0):

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



# Dedupe text inside table bounding boxes

def filterTableContents(pdf, tableBBoxesDoc):

    filteredDoc = []
    
    for pageNum, pg in enumerate(pdf.pages):

        if pageNum > limitPages:
            break

        filteredPg = []

        words = pg.extract_words()  # with coordinates
        # st.write(f"page {pageNum} - words {len(words)}")
        
        tableBBsPg = tableBBoxesDoc[pageNum]

        for wordNum, w in enumerate(words):
            wbb = (w["x0"], w["top"], w["x1"], w["bottom"]) # word bounding box
        
            # check if word is inside any table's bounding box
            contains = False
            for tbb in tableBBsPg:
                if tbb[0] <= wbb[0] <= tbb[2]   and    tbb[1] <= wbb[1] <= tbb[3]  :
                    contains = True
                    break
            
            if not contains:
                filteredPg.append(w["text"])


        s = " ".join(filteredPg)
        filteredDoc.append(s)

        st.write(f"page {pageNum} - words {len(words)} - filtered {len(filteredPg)}")


    return filteredDoc



def containsAnyText(pdf):
    for pgNum, pg in enumerate(pdf.pages):
        if pg.extract_text():
            return True  # is extractable
    return False  # no text detected, likely scanned


workDir = Path.cwd() / "cbcr"

limitPages=9
limitOther=2222

files = [
    "AT_Oberbank_AG_2016_cbcr_ar_en-page-146-148.pdf",
    "DE_Berenberg_Bank_-_Joh._Berenberg_Gossler_Co._KG_2015_cbcr_sd_de.pdf",
    "DE_Berenberg_Bank_-_Joh._Berenberg_Gossler_Co._KG_2016_cbcr_sd_de.pdf",
    "AT_Oberbank_AG_2016_cbcr_ar_en.pdf",
]


for fn in files:
    pth = workDir / fn

    lastX2 = lastXDirs(pth, 2)
    lastX4 = lastXDirs(pth, 4)

    print(f"pth = ..{os.sep}{lastX4}")
    st.write(f"### file ..{os.sep}{lastX2}")

    with pdfplumber.open(pth) as pdf:        

        if not containsAnyText(pdf):
            st.write(f"only scanned contentss")
            continue


        if False:
            structuredText = pdfminer.high_level.extract_text(pth)
            st.write(f"{structuredText[:200]}... \n\n")
            print(f"{structuredText[:200]}... \n\n")


        tables = []  # tables whole doc
        bBoxes = []  # tables whole doc - bounding boxes 

        for pageNum, pg in enumerate(pdf.pages):
            # st.write(f" {pgNum=} {pg=}  ")
            if pageNum > limitPages:
                break

            tablesPg = [] # tables per page
            bboxesPg = [] # tables per page - bounding boxes 
            ts = pg.extract_tables()
            for tableNum, t in enumerate(ts):
                # print(f"\tt{tableNum:3>}  ")
                df = pd.DataFrame(t[1:], columns=t[0])  # to DataFrame
                # unique column names
                df.columns = uniqueCols(df.columns)
                tablesPg.append(
                    {
                        "pageNum":  pageNum  + 1, 
                        "tableNum": tableNum + 1, 
                        "df":       df,
                        "table":    df.to_dict(orient='records'),
                    },
                )

                # table bounding box to exclude text
                bbox = pg.find_tables()[tableNum].bbox
                bboxesPg.append(bbox)

            tables.append(tablesPg)
            bBoxes.append(bboxesPg)

            if len(tablesPg) > 0:
                st.write(f" page {pageNum}: tables {len(tablesPg)} - bounding boxes {len(bboxesPg)}")
            


            # extractTables(pg, pgNum)


        # remove table text from extracted text
        cleanTexts = filterTableContents(pdf,  bBoxes)

        for pg, cleanText in enumerate(cleanTexts):

            st.write(f'''
                #### cleanText for page {pg+1}
                {cleanText[:400]}...
            ''')


        if False:
            for ti in tables:
                showDF( ti["df"], ti["pageNum"], ti["tableNum"], )


print("run stop\n")
