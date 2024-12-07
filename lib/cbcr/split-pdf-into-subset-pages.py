import os
from PyPDF2 import PdfReader, PdfWriter

contains = [
    "§ 64 (1) no. 18 Banking Act",
    "Net interest income",
    "Operating profit",
    "Number of employees",
    "Profit for the year before tax",
    "Income taxes",
]

def subsets(fPath, subsetSize=3, overlap=1):

    if overlap >= subsetSize:
        raise ValueError("Overlap must be less than the number of pages per subset.")

    # Read the input PDF
    reader = PdfReader(fPath)
    totalPages = len(reader.pages)

    if subsetSize >= totalPages :
        print(f"skipping : {fPath} - only {totalPages} len")
        return


    baseName = os.path.splitext(os.path.basename(fPath))[0]
    dir = os.path.dirname(fPath)

    start  = 0
    subsetNum = 1
    
    while start < totalPages:
        end = min(start + subsetSize, totalPages)
        
        writer = PdfWriter()
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        
        outF = os.path.join(dir, f"{baseName}-page-{start + 1:03d}-{end:03d}.pdf")
        with open(outF, 'wb') as f:
            writer.write(f)
        
        print(f"created {outF}")
        
        start += subsetSize - overlap
        subsetNum += 1


files = [
    "AT_Oberbank_AG_2016_cbcr_ar_en.pdf",
    "DE_Berenberg_Bank_-_Joh._Berenberg_Gossler_Co._KG_2015_cbcr_sd_de.pdf",
    "DE_Berenberg_Bank_-_Joh._Berenberg_Gossler_Co._KG_2016_cbcr_sd_de.pdf",
]


for fn in files:
    subsets(fn, subsetSize=3, overlap=2)

