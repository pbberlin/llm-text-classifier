import os
import faiss
import numpy as np
import time

idxFn = "./idx-800k-maxq200.index"

idxSz = os.path.getsize(idxFn)
idxSz = idxSz/1024/1024/1024 # GB
idxSz = round(idxSz,2)

print(f"index loading {idxSz} GB ...")
t1 = time.process_time()
indexOfEmbeds = faiss.read_index(idxFn)
t2 = time.process_time() - t1
print(f"index loaded in {t2:6.3f}s")


vectSize = 3078
extractSize = 3
k = 5

print("")
print(f"doing some queries")

# for idx1 in range(100):
for idx1 in range(4):

    t3 = time.process_time()
    query = np.float32(np.random.rand(1, vectSize))
    print(f"{idx1:3} query for {query[0][:extractSize]}...{query[0][-extractSize:]}")

    distances, indices = indexOfEmbeds.search(query, k)

    t4 = time.process_time() - t3
    print(f"  took {t4:6.3f}s - top {k} max inner product search result:  ", end="")
    print(indices)

    for idx2, (dist, indice) in enumerate(zip(distances[0], indices[0])):
      print(f"    {idx2+1:3}: vect {indice:6}  => distance {dist:6.2f}")





