import models.embeddings as embeddings
import models.contexts as contexts
from pprint import pprint, pformat

import models.benchmarks as benchmarks


def model(req,session):

    res = ""

    res += f"<h3>Embeddings for concepts - multilingual - sentence structure</h3>\n"

    ctxUI, ctxs  = contexts.PartialUI(req,session)
    res += ctxUI

    # bmrks = benchmarks.defaults
    bmrks = benchmarks.update([])

    for bmrk in bmrks:

        res += f"<h4>{bmrk['descr']}</h4>\n"

        # extract short and long
        statementsLong = []
        for s in bmrk["statements"]:
            statementsLong.append(s["long"])

        embeds = embeddings.getEmbeddings(statementsLong, ctxs=ctxs)
        embeddings.getEmbeddingsPlot(statementsLong, embeds, ctxs)
        print("  -----")

        s = embeddings.getEmbeddingsHTML(statementsLong, embeds, ctxs, strFormat="extended")
        res += f"{s}"



    # cross
    for bmrk1 in bmrks:
        for bmrk2 in bmrks:
            _ = bmrk1
            _ = bmrk2


    return res




