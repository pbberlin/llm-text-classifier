# Text classification using LLMs

## Overview

* High level overview
* Provide intuition
* Provide inspiration
{: #an_id .a_class somekey='some value' }


### Summary 1

* Use cheap `embeddings` for coarse pre-selection of text by relevance
* Use `embeddings` to measure basic concepts
* Use expensive `LLM chat-completion` to _measure_ advanced concepts
* Find the cutoff, where LLMs can still "reason" reliably
* The rest is human work

#### Summary 1 cont'd

Cutoff will depend on your research area; for example:

* All things inflation - "How inflationary is statement `x`"?
    * Will work well.
* Effects of inflation going into an ISLM model economy - <br> all the channels and effects.
    * Will work somewhat - <br> if the corpus is thick on "ISLM model"
* More than two degrees of freedom => Confusion
* Improvement on existing methods <br> such as [bag of words](https://en.wikipedia.org/wiki/Bag-of-words_model)?
{: .small }



### Summary 2

If extracting numbers and measuring content was largely successful: 

* Restructure the remaining work, so that humans can do it as easy as possible
* Validation
* Robustness, fireproofing, scientific documentation 
* Reproducibility

<!-- I built some piece of software for quick testing and prototyping -->







### Projects with potential use for LLMs

1.  GuW project<br>
    mining speeches on central bank policies 
1.  CbCR projects  - extracting   
taxation parameters from weakly structured texts 
2.  Municipal taxation - council minutes - <br>
  extracting
    * Business tax rates
    * Period in time
    * Own municipality vs. other municipalities

#### Municipal taxation cont'd

* Mining text for  _concepts_
* Perceived `competitive networks`
* Tax multipliers 
* Various `narratives`
* ...

<!-- additional page break -->
<!--psagebreak-->

#### Projects with potential cont'd 

<!-- : value='4'  -->
Financial markets dept

* Pension policy research  -  <br>
  classify text against concepts
* Financial literacy research - <br>
  capturing `financial calculus` with LLMs


=> Time to establish some foundations


## Cross sectional solution

<table>
    <tr>
        <td style="width:33%" >GuW</td>
        <td style="width:33%" >CbCR</td>
        <td style="width:33%" >Business tax</td>
    </tr><tr><td colspan="3" style="text-align: center">crawling</td>
    </tr><tr><td colspan="3" style="text-align: center">PDF extraction, cleansing</td>
    </tr><tr><td colspan="3" style="text-align: center">number extraction</td>
    </tr><tr><td colspan="3" style="text-align: center">concept extraction</td>
    </tr>
</table>


### Finding the cutoff

* LLMs are formidable at _sentiment analysis_ <br>
  categorization as `positive` and `negative` is excellent  
* Even if evaluated _concepts_ are not in the corpus
    * "Apfeldachschlüssel wäre für uns alle ein großer Gewinn, <br> 
      wenn er die Chromodysterose absolviert hat. <br>
      Davon kann man nur träumen."
    * Deliberately non-existent concepts: <br> `Apfeldachschlüssel` and `Chromodysterose`.
    {: .small }
    * Deliberately ambiguous and not in English.
    {: .small }



#### Sentiment for unknown concepts cont'd

![sentiment for unknown things 1](./img/prompt-1.jpg){: style="width:80%"}

#### Sentiment for unknown concepts cont'd

![sentiment for unknown things 2](./img/prompt-2.jpg){: style="width:90%"}

Every nuance and ambiguity is precisely captured


### Corpus

Consider following two realms

* Reality 
* The language corpus of the entire Internet

There are all kinds of differences between  
reality and the language corpus  

Linguistics researches this

Also [philosophy](https://en.wikipedia.org/wiki/Ludwig_Wittgenstein)

### Corpus biases

* We _cannot_ derive any statement about the relationship  
   between the LLM corpus and actual reality 
* LLMs can only make claims about the corpus
* Results reflect the preferences and biases of the corpus

#### Corpus cont'd

* Consider controversial concepts, <br>
for instance [Supply-side economics](https://en.wikipedia.org/wiki/Supply-side_economics)
* Supply-side economics contains some more realistic assumptions<br> 
  such as `cheaper factors increase supply`
* Other assumptions are more debatable:
    *  An increase in supply _might_ pay for lost revenue, <br> under certain  conditions
    {: style="margin-left:3rem" .myclass }

### Thin corpus 1

* Huge amounts of material about [Hamlet](https://en.wikipedia.org/wiki/Hamlet) 
* Little material on the German novel [Effi Briest](https://en.wikipedia.org/wiki/Effi_Briest)

=> Questions about _details_ about the romantic relationship <br> between protagonists Hamlet and Ophelia  
   are answered with enormous breadth 

=> Similar questios about "Effi and Crampas" are answered  <br>
    with _hallucinations_  drawn from U.S. movies (the next best thing)

### Thin corpus 2

Huge productivity gains for _standard_ programming task

Prolonged detours for peripheral tasks

* Svelte version 5 
* Streaming a HTML response using flask
* Coding template with more than <br> three functional dimensions




### Generic solution - detailed questions

1. Extract numbers with _conditions_  
    * Business tax rate for Hintertupfingen for 2023
    * Previous tax rates  - for 2023, 2022
    * Tax rate of adjacent municipality
2. Validation
    * Outsource validation of extracted data  
      to platforms like Mechanical Turk
    * Cost?



#### Detailed questions cont'd

3. Can we use LLM embeddings to quantify text <br>
 against more advanced concepts? 
    * Not just `favorable`  vs `unfavorable`.
    * How much `alignment` between a benchmark <br> and some piece of text





## Tokenization

* Limited granularity<br>
  ![Granularity](./img/embeddings-granularity.jpg)
* `2023` is not encoded as a singular entity


## On Embeddings

* Each embeddings consists of 3078 numbers  -   
each in the range of one trillon.
* Embeddings for the word [`price`](./img/embeddings-price-compr.json) -  
    <small> 20 sheets of pages. </small><br>

#### On Embeddings cont'd

* Embeddings capture `meaning` 
* Vector distance measures similarity
* ![embeddings](./img/embeddings-text.jpg){: style="width:90%" }
{: .nobullet  }


#### On Embeddings cont'd

* Vector dimensions can be seen as "[principal components](https://en.wikipedia.org/wiki/Principal_component_analysis)" of  the language corpus
* As of October 2024, LLM models express the meaning of language in vectors of 3078 dimensions
* These dimensions (think `principal components`) are derived by expensive AI training
* For a given LLM, embeddings are _deterministic_. No variation. No hallucination.
* Building block for the `generative` AI components

#### On Embeddings cont'd

* Most dimensions cannot be associated with words or concepts.
* They rather represent `shades` of language - <br>
such as "positivity" or "short term future", "long term future"
* No common sense meaning <br> for many `principal components`

---

* Local clusters of LLM cells <br> might be [associated](https://www.economist.com/science-and-technology/2024/07/11/researchers-are-figuring-out-how-large-language-models-work) with some language concepts
* Correct classification _may_ be indicated  <br> by loadings on localized clusters

<!-- * Failed classification may be indicated <br> by small loadings all over the vector space. -->
<!-- * Resulting in a weak and diffuse classification.  -->


#### On Embeddings cont'd

* Two statements containing identical words - difference is only in punctuation
    * I am giving up  drinking until this is over.
    {: .small-2}
    * I am giving up. Drinking until this is over.
    {: .small-2}
* ![considerably different](./img/embeddings-drinking-until.jpg) <br>
 Chart: "Significant" positive and negative [embedding] values - 32 values of biggest magnitude.<br>
 Short grey bars indicate identical dimensions (48%) - 52% are _distinct_.<br>
 Even identical dimensions have different values. <br>
 Data points of  _second_ series are shifted right by two pixels, in order to make the almost perfect overlap visible.  
{: .small-2 .nobullet }

 
#### On Embeddings cont'd

* LLMs put heavy weights on punctuation tokens
* _Preceding_ words heavily influence the weighting of a word



#### On Embeddings cont'd

* Variations and translations of the word `price` <br>
* ![Example price](./img/embeddings-price.jpg)
{: .nobullet }
* All load highly negative on dimension 87, <br>
and highly positive on dimensions 528 and 57
* Maybe, these is the cluster for the concept of a price in the context of economics?  




### Similarity of advanced concepts - using embeddings only

How well can LLMs capture  _advanced concepts of research_ . 

Example: Purchase of government bonds by the EU

Take two statements around the concept of `central bank`, `central bank intervention`, the `market for government bonds` and important macro variables:

<!--pagebreak-->

* The European Central Bank (ECB) did take a strongly active position in recent years by purchasing sovereign bonds of euro countries. This strongly active position of the ECB should continue.
* The European Central Bank (ECB) purchase programmes for sovereign bonds of euro countries will increase money supply and eventually increase expectations of the price level.
* ![strong similarity](./img/embeddings-ecb-gvt-bond-purchase.jpg)
{: .nobullet}

<!--pagebreak-->

* The embeddings of the two statements from a relatively specific scientific domain show strong similarities.
* Despite very different wording
* Despite having distinct sentiment (explicitly positive, implicitly negative) 
* Is this an expression of excellent categorization?  
* The balanced and clustered vector loadings suggest so





## Web application

The web application can be downloaded from [ZEW git](https://git.zew.de/ub-public-finance/ecb-speeches-flask)

It can be executed on your notebooks

The web application is written in `Python`

The core is advanced (web server stuff...)

But periphery is extendable by researchers <br> and by student workers with IT affinity

<!--pagebreak-->

Web application connects to OpenAI ChatGPT 4

It requires an API key from OpenAI inc

If you request many embeddings, OpenAI may require money for it

At least, embeddings are stored locally; <br> 
openAI is only asked _once_ per text-element

<!--pagebreak-->

Convenient uploading and arranging  <br> various elements of text classification

* Contexts
* Benchmark statements (goal posts) 
* Texts to be classified

Some default data is loaded. <br>
Change according to your reserch.

Showing embeddings and similarity as charts

## Stage two: Chat completion

Going beyond embeddings

Using the _generative_ faculty of LLMs

Setting a context: "economics and government policy"

Setting `temperature` to zero => hallucinations practically disappear

### Distinction over vector distance of embeddings 

The `chat completion` stage provides additional refinement (over vector distance).

Subject to same considerations of the corpus.

Some internal dialogue - some wider context scope.

To some extent incomprehensible.

Very good results - inside the domains of the corpus.

Every researcher needs to draw a subjective line here.


### Hallucinations are not a problem

* Embeddings are deteministic anyway
* _Generative_ AI has some probabilistic element,  
  that can lead to erroneous results
    * Setting temperature to 0
    * Changing seed
    * => The concept classifications show only tiny variation

## Todo

### Ensemble approach

* Give me three variations
* Rank the results

### Few shots

* Proide schema for JSON output 
* also provide few shots
* also give reasoning steps - "thinking steps"

### Context from vector database

* Get similar chunks
* Include as context

Integrate a bunch of documents into an LLM vector database

### Chunk size for embeddings index

Too small chunks => too little context

Too large => Relevant results get diluted with irrelevant parts

Chunk size: 2-4 sentences.

For conceptual search: Bigger chunks

### Make database results into a nice answer

Send the initial question as chat completion query

Embed the embedding results as context 

```
You are an expert assistant. Based on the following retrieved information, answer the user's query:

Context: 
- [Chunk 1: ...]
- [Chunk 2: ...]
- [Chunk 3: ...]

Question: [User's original query]

Provide a clear and concise response based on the context.
```

### Indexing

pip install faiss-cpu
pip install faiss-gpu



## Conclusions

* Vector embeddings capture general relationship between two texts  
  but lack deep understanding of higher concepts
* Vector embeddings are immune to hallucinations
* Stable and reliable results
* Small variations, depending on LLM vendor and LLM training details
* Dimensionality of 3078 is a limiting factor for capturing meaning
* If LLM companies can increase dimensionality, <br> 
  the quality of analysis can increase further


## Sources

[Sergio Correia - Unlocking Data with LLM](https://www.youtube.com/watch?v=quf6jlJ-Mvg&t=3100s&pp=ygUyU2VyZ2lvIENvcnJlaWEgb24gVW5sb2NraW5nIEVjb25vbWljIERhdGEgd2l0aCBMTE0%3D)

[Kevin Bryan](https://youtu.be/LJGQjozWr0E)


---------------

## Technical documentation

* Purely technical - for software engineers and programmers
* Webserver setup for [production ](./production-setup.md)

### Indexing embeddings 

Directory   ./indexing-embeddings/autofaiss  contains some steps towards building an index for embeddings,
so that most closely matching embeddings can be searched and found quickly.

Unlike B-Tree indexes known from databases; indexes for embeddings are expensive to update.

Some index types (HNSW32) are less expensive for update, but slower in query.

Index type IVF4096 can be very fast (<15 ms) but each new vector takes a lot of computing.

Also: Each ChatGPT-O embedding needs 8 Bytes times 3078 slots space - 28 kB of data.


#### Indexing embeddings cont'd

The indices have similar size; an index of 800.000 embeddings needs 9 GB of space.

Indices can be used as memory mapped files, but still require a lot of memory.

One should considering a large index of "stock" embeddings - <br> 
and tiny "delta" indices for new data,  being merged at night.

If needed, a distributed index across several server machines needs to be built.


## Backup slides



### Scientific applications - cont'd

* EU asset purchasing programmes (APP):
    * Can embeddings  capture the discussion?  
    * Can text content be measured against economic theories?
* Research into local taxation:  
    * Reasoning about  _surrounding_ municipalities?    
    * Reasoning implicitly along the game theory concept <br> 
    of prisoner's dilemma?


### Problems

* LLMs are in many ways not well understood


## Context

* Sometimes necessary.  
  The corpus on `structured bonds` may be vastly different 
   in commercial real estate than in public finance.
* If the the texts are already littered with terms from the intended domain, it might be dropped.  
* Keep it short, to reduce noisy classification.
* We can test the effect of providing context on training sets with examples.
* Sometimes the context seems to reduce the distinctions (work needed)




### Generic solutions cont'd

* Tax incidence:  
    * Press releases   tax incentives for intellectual property?  
* Example for research into pension planning:  
    * How much weight is given in politicians' statements on any of the three pillars of retirement planning:  
    * legal pension vs. company pensions vs. private provison?



### Mathematical indicators for low-quality classification

* Widespread, low-magnitude values, sparse activations  
    classification is based on weak or noisy features.
* Balanced positive and negative values

---

* Higher entropy often correlates with a weak classification signal.  
   High entropy means a more "even" distribution across many dimensions. 
* Only few key features load - everything else is zero.  
  Not found in LLMs of 2024.


#### Mathematical indicators for low-quality classification - cont'd

* Dimensional Collapse:  
    vectors for many different inputs become very similar or lie in a lower-dimensional subspace.  
      Not found in LLMs of 2024.
* High cosine similarity between the embeddings of _different_ classes.  
    Model does distinguishing between those classes.  
    Model is weak for differences between categories
* Visualizing embeddings in reduced dimensionality (e.g., using t-SNE or PCA),  
  embeddings should ideally form distinct clusters.

