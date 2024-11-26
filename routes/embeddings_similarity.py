import models.embeds as embeds
from pprint import pprint, pformat

import markdown
import models.samples as samples




# els must be sorted in descending order
def posInSortRank(el, els):
    for idx, e in enumerate(els):
        if el >= e:
            # return f"{(len(els) - idx):02d}"
            return f"{idx+1:02d}"

    return f"{len(els):02d}"

# helper for renderTable
# 1st, 2nd, 3rd, 4th quarter?
# els must be sorted in descending order
def posInSortQuant(el, els, quant=4):
    pos = -1
    for idx, e in enumerate(els):
        if el >= e:
            # return f"{(len(els) - idx):02d}"
            pos = idx
            break

    if pos == -1:
        pos = len(els)

    q = float(pos)/float(len(els))*float(quant)
    q = int(q)+1

    return f"{q:02d}"

def stripSingleQ(s):
    return s.replace("'", " ")

def renderTable(
    request,
    t,
    colHdrsSh, colHdrsLg,
    rowCol1Sh, rowCol1Lg,
    tableOnlyNumber=False,
    onlyNumbers=False,
    numCtxs=1,    # number distinct contexts
):

    s = ""

    nRows = len(t)
    nCols = len(t[0])

    widthCol1 = 0.2
    widthCol1Str = f"{100*widthCol1}%"
    cssNCols = f"width: { (1.0-widthCol1)/float(nCols+1)*100:5.1f}%"

    if tableOnlyNumber:
        s += "<table class='results'>"
        s += "<tr>"
        s += f"<td> &nbsp; </td>"
        for idxCol, cell in enumerate(colHdrsSh):
            s += f"<td> {cell:<3} </td>"
        s += "</tr>\n"
        for idxRow, row in enumerate(t):
            s += "<tr>"
            s += f"<td> {rowCol1Sh[idxRow]} </td>"
            for idxCol, cell in enumerate(row):
                s += f"<td> {cell:<3} </td>"
            s += "</tr>\n"
        s += "</table>"
        s += "\n"



    s += "<table class='results'>"


    # first row
    s += "<tr>"
    # first row - first cell
    s += f"<td style='font-size: 80%; vertical-align:bottom;'>  &nbsp; &nbsp; mouse over => long version </td>"
    for idxCol, cell in enumerate(colHdrsSh):
        stl = cssNCols
        if idxCol == 0:
            stl = widthCol1Str
        s += f"<td  title='{stripSingleQ(colHdrsLg[idxCol])}' style='{stl}'> {cell:<3} </td>"
    s += "</tr>\n"


    # data rows
    for idxRow, row in enumerate(t):

        # first col
        s += "<tr>"
        num = f"<span class='col1-numbering'>{idxRow+1}</span>"
        # num = ""
        s += f"  <td title='{stripSingleQ(rowCol1Lg[idxRow])}' >{num}. {rowCol1Sh[idxRow]} </td>"

        # first *data* cols

        max = -10 # max row value

        rowSorted = row[:] # make a copy
        rowSorted.sort()
        rowSorted.reverse()

        for cell in row:
            f1 = float(cell)
            if f1 > max:
                max = f1



        for idxCol, cell in enumerate(row):

            pos = posInSortQuant(cell, rowSorted)
            # print(f"  c{idxCol+1:02} el {cell} is quart {pos} in  {rowSorted}" )


            f1 = float(cell)

            fGraph = pow(f1,0.5)
            fGraph = f1

            fPct = f"{fGraph*100:10.1f}%"

            neg = ""
            if fGraph < 0:
                neg = "neg-factor-loading"
                fPct = "0.01%"

            maxStyle = ""
            if f1 == max:
                maxStyle = "max-cell"




            frmURL1 = request.url_for("chatCompletionSynchroneousH")

            frm1 = f"""
                <form action='{frmURL1}' target='_chat' method='POST'>
                    <input type=hidden name='belief-statement'  value='{stripSingleQ(colHdrsLg[idxCol])}' />
                    <input type=hidden name='speech'            value='{stripSingleQ(rowCol1Lg[idxRow])}' />
                    <button class='llm-submit'>X</button>
                </form>
            """


            frmURL2 = request.url_for("chatCompletionJsonHPost")
            frm2 = f"""
                <form action='{frmURL2}' target='_chat' method='POST'>
                    <input type=hidden name='belief-statement'  value='{stripSingleQ(colHdrsLg[idxCol])}' />
                    <input type=hidden name='speech'            value='{stripSingleQ(rowCol1Lg[idxRow])}' />
                    <button class='llm-submit'>X</button>
                </form>
            """

            frmURL3 = request.url_for("chatCompletionJSH")
            frm3 = f"""
                <form action='{frmURL3}' target='_chat' method='POST'>
                    <input type=hidden name='belief-statement'  value='{stripSingleQ(colHdrsLg[idxCol])}' />
                    <input type=hidden name='speech'            value='{stripSingleQ(rowCol1Lg[idxRow])}' />
                    <button class='llm-submit'>X</button>
                </form>
            """


            s += f"  <td style='{cssNCols}'>"
            s += f"     <span class='number' >  {f1:10.2f}  </span> "
            s += f"     <div  class='bar {maxStyle} quant{pos} {neg}' style='width:{fPct}'></div> "
            s += f"     {frm1}"
            s += f"     {frm2}"
            s += f"     {frm3}"
            s += f"  </td>"




        s += "</tr>\n"
    s += "</table>"


    if onlyNumbers:
        s += f"<pre>{pformat(t)}</pre> \n"
        s += "\n"

    return s



def model(request, db, ctxs, bmrk, smpl ):


    smplSh = [] # sample short keys
    smplLg = [] # sample long  keys
    for idx, smpl in enumerate(smpl["statements"]):
        smplSh.append( smpl["short"] )
        smplLg.append( smpl["long"] )


    bmrkSh = [] # benchmark short keys
    bmrkLg = [] # benchmark long  keys
    for idx, bm in  enumerate(bmrk["statements"]):
        bmrkSh.append( bm["short"] )
        bmrkLg.append( bm["long"]  )


    # x-axis labels - appending context
    bmShTmp = []
    for idx1, t in enumerate(bmrkSh):
        for idx2, ctx in enumerate(ctxs):
            bmShTmp.append(f"{t} <br> <span class='context2'> {ctx['short']} </span> ")
    bmrkSh = bmShTmp


    embsBm = embeds.getEmbeddings(db, bmrkLg, ctxs=ctxs)
    # res += s

    # NO CONTEXT here
    embsSp = embeds.getEmbeddings(db, smplLg)
    # res += s


    if len(bmrkSh) < 1:
        return " no context or no benchmark selected"

    # compute similarity
    coeffsMatr, s = embeds.correlationsXY(
        bmrkSh, embsBm,
        smplSh, embsSp,
    )

    print(f" coeff matrix row{len(coeffsMatr)} x cols{len(coeffsMatr[0])}")
    print(f" coeff matrix benchmarks {len(bmrkSh)} x samples{len(smplSh[0])}")


    htmlTable = renderTable(
        request,
        coeffsMatr,
        bmrkSh, bmrkLg,
        smplSh, smplLg,
        onlyNumbers=False,
        numCtxs = len(ctxs),
    )

    return htmlTable
