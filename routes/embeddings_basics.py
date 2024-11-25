import models.embeds as embeds
import models.contexts as contexts
from pprint import pprint, pformat

import models.benchmarks as benchmarks


async def model(db, request):

    res = ""

    res += f"<h3>Embeddings for concepts - multilingual - sentence structure</h3>\n"

    ctxUI, ctxs  = await contexts.PartialUI(request)
    res += ctxUI

    # bmrks = benchmarks.defaults
    bmrks = benchmarks.update([])

    for bmrk in bmrks:

        res += f"<h4>{bmrk['descr']}</h4>\n"

        # extract short and long
        statementsLong = []
        for s in bmrk["statements"]:
            statementsLong.append(s["long"])

        embds = embeds.getEmbeddings(db, statementsLong, ctxs=ctxs)

        embeds.getEmbeddingsPlot(statementsLong, embds, ctxs)
        print("  -----")

        s = embeds.getEmbeddingsHTML(statementsLong, embds, ctxs, strFormat="extended")
        res += f"{s}"



    # cross
    for bmrk1 in bmrks:
        for bmrk2 in bmrks:
            _ = bmrk1
            _ = bmrk2


    return res




