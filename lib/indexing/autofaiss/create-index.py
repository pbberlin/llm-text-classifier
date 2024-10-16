'''
    embeddings indexing
    https://github.com/criteo/autofaiss
'''
print("imports - start")
import time
from autofaiss import build_index
import numpy as np
print("imports - stop")
print("")

vectSize = 3078

numK = 0.9     # max on notebook with 8 GB RAM
numK =   2
numK =   4     #     7 secs on osm.zew.local
numK =  20     #   200 sec
numK = 100     #  1400 sec
numK = 500     #  6000 sec  16GB RAM
numK = 800     # 11000 sec


numK = 0.5
numK = 0.1
numEmbeddings = int(numK*1000)
maxQueryTime =  20
maxQueryTime = 500

fnIdx = f"idx-{numK}k-maxq{maxQueryTime}.index"
fnIfo = f"idx-{numK}k-maxq{maxQueryTime}-info.json"


embds = np.float32(np.random.rand(numEmbeddings, vectSize))
print(f"created {numK}k random embedings")
print("")



index, index_infos = build_index(
    embds,
    save_on_disk=True,
    index_path=fnIdx,
    index_infos_path=fnIfo,

    # index_key="--",

    max_index_query_time_ms=maxQueryTime,

    max_index_memory_usage=   "2G",
    current_memory_available= "4G",

    make_direct_map=True,
    should_be_memory_mappable=True,
)


print("creating index - stop")
print("")
print("")

extractSize = 3

for idx in range(2):

    t1 = time.process_time()
    query = np.float32(np.random.rand(1, vectSize))
    print(f"{idx:3} query {query[0][:extractSize]}...{query[0][-extractSize:]}")

    _, I = index.search(query, 1)

    t2 = time.process_time() - t1
    print(f"    {t2}s  search result ", end="")
    print(I)


