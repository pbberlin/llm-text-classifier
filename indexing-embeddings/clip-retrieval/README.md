# Clip


<https://github.com/rom1504/clip-retrieval>


<https://github.com/rom1504/clip-retrieval/blob/main/docs/laion5B_back.md>


```bash

python3 -m venv venv1
source venv1/bin/activate
pip install clip-retrieval autokeras==1.0.18 keras==2.8.0 Keras-Preprocessing==1.1.2 tensorflow==2.8.0

# update to newest
pip install  autokeras keras Keras-Preprocessing tensorflow -U



export CUDA_VISIBLE_DEVICES=
clip-retrieval back --provide_violence_detector True --provide_safety_model True  --clip_model="ViT-L/14" --default_backend="http://0.0.0.:1234/" --port 1234 --indices-paths indices.json --use_arrow True --enable_faiss_memory_mapping True --columns_to_return='["url", "caption", "md5"]'


```
