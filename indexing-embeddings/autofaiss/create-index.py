'''
    demo of 
    https://github.com/criteo/autofaiss
'''
print("imports - start")
import time
from autofaiss import build_index
import numpy as np
print("imports - stop")
print("")

vectSize = 3078
numEmbeddings =  10*1000
numEmbeddings =      900     # max on notebook with 8 GB RAM
numEmbeddings =   2*1000
numEmbeddings =   4*1000     #     7 secs on osm.zew.local
numEmbeddings =  20*1000     #   200 sec
numEmbeddings = 100*1000     #  1400 sec
numEmbeddings = 500*1000-1   #  6000 sec  16GB RAM
numEmbeddings = 800*1000     # 11000 sec

print("creating random embeds - start")
# embeddings = np.float32(np.random.rand(100, vectSize))
embeddings = np.float32(np.random.rand(numEmbeddings, vectSize))
print("creating random embeds - stop")
print("")


index, index_infos = build_index(
    embeddings,

    save_on_disk=True,
    index_path="./idx-800k-maxq040.index",
    index_infos_path="./idx-800k-maxq040-info.json",
    # index_key="--",

    max_index_query_time_ms=40,

    max_index_memory_usage="12G",
    current_memory_available="18G",

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


