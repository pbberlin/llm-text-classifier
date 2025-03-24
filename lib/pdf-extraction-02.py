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
def printPre(s: str):
        st.html(f"<div  style='white-space-collapse: preserve; font-family: monospace'>{s}</div>")


print("\nrun start")

import pdfplumber
import fitz
import pdfminer.high_level

from collections import defaultdict


import functools
import time
def timer(func):
    """print runtime of the decorated function
        @timer
            def funcXXX():
    """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        funcName = f"{func.__name__!r}"
        printPre(f"\tfinished {funcName:24} in {run_time:.4f} secs")
        return value
    return wrapper_timer


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


def metaData(pdf):
    vs = {}
    printPre(f"meta data")
    for k in pdf.metadata:
        v = pdf.metadata[k]
        if v is None or v.strip() == "":
            continue
        # if "Creator"  in k:
        #     continue
        if v in vs:
            continue
        vs[v] = True
        printPre(f"\t{k:12} -{v}-")



def printBoundingBox(bbox):
    #  x1 |  y1   --   x2 |  y2
    #  85 | 114   --  510 | 203
    #  85 | 216   --  510 | 330
    #  85 | 343   --  510 | 432
    bboxStr = ""
    for coord in bbox:
        bboxStr += f"{coord:4.0f} "
    printPre(f"\t{bboxStr}")



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
    printPre(f"page {pageNum:3} - table{tableNum}")
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



# dedupe text inside table bounding boxes
def filterTableContents(pdf, tableBBoxesDoc):

    dedupdDoc = []
    doubleDoc = []

    for pageNum, pg in enumerate(pdf.pages):

        if pageNum > limitPages:
            break

        dedupdPg = []
        doublePg = []

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

            if contains:
                doublePg.append(w["text"])
            else:
                dedupdPg.append(w["text"])


        s = " ".join(doublePg)
        doubleDoc.append(s)

        s = " ".join(dedupdPg)
        dedupdDoc.append(s)

        printPre(f"preproc page {pageNum:2} - words {len(words):4} = {len(dedupdPg):4} + {len(doublePg):4}")



    return (dedupdDoc, doubleDoc)



def containsAnyText(pdf):
    for pgNum, pg in enumerate(pdf.pages):
        if pg.extract_text():
            return True  # is extractable
    return False  # no text detected, likely scanned


tableExtractionOptions = {
    "vertical_strategy":     "lines",  
    "horizontal_strategy":   "lines",  
    # "intersection_tolerance": 5,       # adjusting for minor misalignment
}



tableExtractionOptions = {
    "vertical_strategy":     "lines",  
    "horizontal_strategy":   "lines",  
    # "snap_tolerance":        10,  
    "snap_tolerance":            5,  
    "snap_x_tolerance":         25,  
    "snap_x_tolerance":         45,  
    "text_x_tolerance": 22,
    "text_x_tolerance": 244,
    "text_y_tolerance": 44,
}




@timer
def extractTablesPlumber(pth):

    tables = []  # tables whole doc
    bBoxes = []  # tables whole doc - bounding boxes

    with pdfplumber.open(pth) as pdf:

        if False:
            metaData(pdf)

        if not containsAnyText(pdf):
            st.write(f"only scanned contentss")
            return (tables, bBoxes, [], [])

        if False:
            structuredText = pdfminer.high_level.extract_text(pth)
            st.write(f"{structuredText[:200]}... \n\n")
            print(f"{structuredText[:200]}... \n\n")

        for pageNum, pg in enumerate(pdf.pages):
            # st.write(f" {pageNum=} {pg=}  ")
            if pageNum > limitPages:
                break

            tablesPg = [] # tables per page
            bboxesPg = [] # tables per page - bounding boxes

            #  x1 |  y1   --   x2 |  y2
            
            pageBB = pg.bbox
            lim = 20
            pageBB = (50, 100, pageBB[2]-lim, pageBB[3]-lim)

            pgcr = pg.crop( pageBB )
            # https://pypi.org/project/pdfplumber/#extracting-tables - "Extracting tables"
            ts = pgcr.extract_tables( table_settings=tableExtractionOptions )
            for tableNum, t in enumerate(ts):
                # print(f"\tt{tableNum:3>}  ")
                df = pd.DataFrame(t[1:], columns=t[0])  # to DataFrame
                df.columns = uniqueCols(df.columns)
                tablesPg.append(
                    {
                        "pageNum":  pageNum  + 0,
                        "tableNum": tableNum + 0,
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
                printPre(f"preproc page {pageNum:2} - tables {len(tablesPg):1} - bounding boxes {len(bboxesPg)}")


        # remove table text from extracted text
        dedupdTexts, doubleTexts = filterTableContents(pdf,  bBoxes)

        return (tables, bBoxes, dedupdTexts, doubleTexts)


@timer
def extractTablesFitz(pth):
    tables = []
    with fitz.open(pth) as pdf:
        for pageNum, pg in enumerate(pdf):
            # st.write(f" {pageNum=} {pg=}  ")
            tablesPg = [] # tables per page
            if pageNum > limitPages:
                break
            ts = pg.find_tables()
            for tableNum, t in enumerate(ts.tables):
                tablesPg.append(t)
            tables.append(tablesPg)
    return tables


workDir = Path.cwd() / "cbcr"

limitPages=5
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


    tablesFitz = extractTablesFitz(pth)

    tables, bBoxes, dedupdTexts, doubleTexts = extractTablesPlumber(pth)

    for pg, dedupdTxt in enumerate(dedupdTexts):

        st.write(f'''#### page {pg}''')

        if len(tables[pg]) == 0:
            st.write( f"no tables - skipping content")
            continue

        st.write(
            f"deduped: <br> {dedupdTxt[:11400]}",
            unsafe_allow_html=True,
        )

        for t in tables[pg]:
            showDF( t["df"], t["pageNum"], t["tableNum"], )
            # st.write(t["table"])


        st.write(
            f"doubled: <br> {doubleTexts[pg][:11400]}",
            unsafe_allow_html=True,
        )



print("run stop\n")
