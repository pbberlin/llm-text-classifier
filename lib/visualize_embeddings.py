# pip install numpy scikit-learn matplotlib

import os
import openai
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None or  len(OPENAI_API_KEY) < 2:
    print("set Open AI key via 'OPENAI_API_KEY'")
    os._exit(0)

import openai
client = openai.OpenAI()
# https://platform.openai.com/docs/models/embeddings
modelName = "text-embedding-3-large"



def get_embeddings(statements):

    # return [openai.Embedding.create(input=statement)['data'][0]['embedding'] for statement in statements]

    arr = []

    response = client.embeddings.create(
        input=statements, 
        model=modelName,
    )

    for idx, record in enumerate(response.data):
        # arr.append(record.embedding)
        arr.append( np.array(record.embedding) )

    # return np.array(record.embedding)
    return arr

def plot_embeddings(embeddings, labels, title):
    plt.figure(figsize=(8, 8))
    for i, label in enumerate(labels):
        plt.scatter(embeddings[i, 0], embeddings[i, 1])
        plt.annotate(label, (embeddings[i, 0], embeddings[i, 1]), textcoords="offset points", xytext=(0, 10), ha='center')
    plt.title(title)
    plt.show()


# Reduce the dimensionality of the embeddings to 2D using PCA and plot them:
def visualize_pca(embeddings, labels):

    sz1 = len(embeddings)
    sz2 = len(labels)
    print(f" {sz1} / {sz2} dimensions")

    pca = PCA(n_components=sz1)


    reduced_embeddings = pca.fit_transform(embeddings)
    plot_embeddings(reduced_embeddings, labels, 'PCA of Embeddings')

'''
    # Example usage:
    embeddings = np.array([
        [0.1, 0.3, 0.4, ...],  # embedding 1
        [0.2, 0.1, 0.5, ...]   # embedding 2
    ])
    labels = ['Context 1', 'Context 2']

    visualize_with_pca(embeddings, labels)
'''


# Compute and Visualize t-SNE
# Reduce the dimensionality of the embeddings to 2D using t-SNE and plot them:
# 
#   Example usage:
#   visualize_with_tsne(embeddings, labels)
def visualize_tsne(embeddings, labels, perplexity=30, n_iter=300):

    sz1 = len(embeddings)
    sz2 = len(labels)
    print(f" tsne 1:  {sz1} / {sz2} dimensions")

    # perplexity must be less than the number of samples.
    perplexity = 2
    perplexity = sz1 - 1

    tsne = TSNE(n_components=sz1, 
        perplexity=perplexity, 
        n_iter=n_iter, 
        random_state=42,
    )
    print(f" tsne 2:  {tsne}")

    reduced_embeddings = tsne.fit_transform(embeddings)
    print(f" tsne 3:  {reduced_embeddings} ")

    plot_embeddings(reduced_embeddings, labels, 't-SNE of Embeddings')




# Example usage:
statements = [
    "In the context of fiscal policy, growth is good.",
    "In the context of botanical studies, growth is good.",
    "In the context of cancer research or oncology, growth is good.",
    # "pollution has vitamins.",
]
labels = [
    'Fiscal Context', 
    'Botanical Context',
    'Oncology',
    # 'Pollution vits',
]
embeddings = get_embeddings(statements)

if False:
    pass

visualize_pca(embeddings, labels)


visualize_tsne(  np.array(embeddings)  , labels)

