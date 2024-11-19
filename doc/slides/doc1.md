# Using LLMs in our research

## 

![conquer unknown land](./img/conquer-unkown-land.jpg){: style="width:80%"}  <br>
Research an unknown land

## Overview

* Provide inspiration along your research
{: #an_id .a_class somekey='some value' }
* Cutoff: What is useful, possible - what is illusory
* Develop the details during projects
* Limited overview


#### Overview cont'd - 1

* Extracting `tagged` numbers from large texts
    * Requires preprocessing of texts
    * Techniques for self-validation
* Extracting `contextual` tax rates 
    * i.e. previous, suggested or competing rates
    * Requires preparatory stage<br>
        * Explain concept  <br>
          `reference municipality` 
        * Ask if text contains `tax rates` <br> from `reference municipality`

#### Overview cont'd - 2

Where is the cutoff? - Example from another research area:

* Simple macro concept: "How inflationary is statement `x`"?
    * Will work well
* Effects of inflation on demand - assuming ISLM model economy - <br> channels and effects
    * Will work somewhat 
    * Corpus must be `thick` on `ISLM model`
    * Requires advanced prompting techniques

<!-- * Improvement on existing methods <br> such as [bag of words](https://en.wikipedia.org/wiki/Bag-of-words_model)?
{: .small } -->


#### Overview cont'd - 3

If extracting numbers and measuring content was largely successful: 

* Restructure the remaining work, so that humans can do easily
    * Validation by crowd workers
* Robustness 
* Scientific documentation 
* Reproducibility

<!-- I built some piece of software for quick testing and prototyping -->







### Projects benefitting from LLMs

1.  GuW project - <br> 
    mining speeches on central bank policies 
1.  CbCR projects  - extracting   
taxation parameters from weakly structured texts 
2.  Municipal taxation - council minutes - <br>
  extracting
    * Business tax rates
    * Periods in time
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


### => Time to establish some foundations


## Cross sectional solution - generic solution

<table>
    <tr>
        <td style="width:33%" >GuW</td>
        <td style="width:33%" >CbCR</td>
        <td style="width:33%" >Business tax</td>
    </tr><tr><td colspan="3" style="text-align: center">crawling</td>
    </tr><tr><td colspan="3" style="text-align: center">PDF extraction, cleansing</td>
    </tr><tr><td colspan="3" style="text-align: center">number  extraction</td>
    </tr><tr><td colspan="3" style="text-align: center">concept extraction</td>
    </tr><tr><td colspan="3" style="text-align: center">validation</td>
    </tr>
</table>

#### Solution cont'd

* `pbu` has created some foundational tools <br>
  (demo below)
* Extend these tools -  <br> 
  in cooperation with the researchs <br>
   along the projects

## Fundamental instructions <br> for researchers

* Some capabilities of LLMs are so staggering,  
  that one assumes, they are capable at everything
* Strenght and limitations below

## Corpus

* Corpus is a major determinant of what LLMs can and cannot do
* It helps to ask: <br> How much material is out there on a specific concept?
* `Sentiment` is a positive example
* `Number extraction` is a positive example

### Corpus thickness - sentiment

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


#### Sentiment cont'd - some extended prompt design

![sentiment for unknown things 1](./img/prompt-1.jpg){: style="width:80%"}

#### Sentiment cont'd - "answer" by the LLM 

![sentiment for unknown things 2](./img/prompt-2.jpg){: style="width:90%"}

Nuance and ambiguity is precisely captured


#### Corpus cont'd

* Two realms
    * Reality 
    * The language corpus of the entire Internet

<!-- 
There are all kinds of differences between  
reality and the language corpus  

Linguistics researches this

Also [philosophy](https://en.wikipedia.org/wiki/Ludwig_Wittgenstein)


 Corpus biases

* We _cannot_ derive any statement about the relationship  
   between the LLM corpus and actual reality 
 -->

* LLMs can only make claims about the corpus
* Results reflect the depth, <br> the distribution and biases of the corpus

#### Corpus cont'd

* Consider  less popular concepts, <br>
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

Ask for "dental crown swallowed" <br> or (German:)  "Krone verschluckt".

Result is  95%  verbatim  <br> from a  _single_ [ news source](https://praxistipps.focus.de/krone-verschluckt-das-sollten-sie-beachten_109630)



### Thin corpus 3

* _Standard_ programming task
* Scaffolding, templating, rewriting
* Huge productivity gains

As soon as one  <span class="fragment"> - unwittingly  </span>   <span class="fragment"> - strays off - </span>

one gets misleading, non-working, time-wasting stuff

* <small>Svelte version 5 component   </small>
* <small>Streaming a HTML response using flask  </small>
* <small>SQLAlchemy count of records from table  </small>



## Limitation 2

* Second perspective of LLM limitation
* "Dimensions of Meaning"

## Granularity - tokenization

* Limited granularity<br>
  ![Granularity](./img/embeddings-granularity.jpg)
* `2023` is not encoded as a singular entity

## Internal represenation of tokens

* Each token has a "vector of meanings" - an `embedding`
* LLMs cannot go very far beyond these dimensions
* Illustration below


## On Embeddings

* Each embeddings consists of 3078 numbers  -   
each in the range of one trillon.
* Embeddings for the word  
  <a  target="embeds" href="../embeddings-price-compr.json" > price   </a> <br>
    * 20 pages
    * -1  to  +1
    * few > |0.2|
    * 16 digits precision, seems only the first 5 matter

## Skip 

* We skip some explanations and go straight towards
* [Examples](./slides/#/29) (URL + 4)

#### On Embeddings cont'd

* Embeddings capture `meaning` 
* Vector distance measures similarity
* ![embeddings](./img/embeddings-text.jpg){: style="width:90%" }
{: .nobullet  }

#### On Embeddings cont'd

* Core Concepts (~1000) 
* Essentially a "vocabulary of thought" 

* Dimensions seem to differ
    * If we ask for "Pasta, Nudeln, Spaghetti",  <br> 
    85 might represent the egg ingredient


#### On Embeddings cont'd

* Advanced concepts have `distributed representations`
    * For instance embeddings of `inflation in economics`  
    * Associated with  `price levels`, `money supply` and  `interest rates` ...
    * These core concepts in turn have stable representations
    * => Embedding for `inflation in economics` is robust


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
 "Significant" positive and negative `embedding` values - 32 values of biggest magnitude.<br>
 Short grey bars indicate identical dimensions (48%) - 52% are _distinct_.<br>
 Even identical dimensions have different values. <br>
  <small>Second and third series are shifted right by two pixels, to make  overlap visible</small>
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
    * The cluster for the concept of `price` ?  
    * The rest is other nuances: good, bad - near future, distant future...


### How much meaning can be captured?

Given this internal representaion: 

How well can LLM capture our  _concepts of research_? 

We have explore and test. 

### Skipping to prompt techniques

I skip further instructions on embeddings  - and continue with the third major dimension.

=> Prompt techniques

(Slide 38)

### Example for exploring the cutoff

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







## Chat completion

* `Chat completion` is what you know from ChatGPT website
* Signifant step beyond embeddings

### Embeddings vs Chat Completion

* Embeddings only `pool` the tokens
* Chat completion adds `positional vector` to each token

#### Chat completion cont'd

* Enriched embeddings are fed into the huge transformer model
* => `inference` step

#### Chat completion cont'd

* The researcher should enrich the prompt before inference
* => `prompt techniques`

## Prompt techniques

* Advanced prompt strategies for science

<!-- todo: role and context -->

### Increase precision 1 - give template

* Provide JSON schema for output 
    * See web app
* Provide `few shots`
    * Question A - Answer A 
    * Question B - Answer B
    * ...
      * Scope the maximum variety 
      * Edge cases
    * The actual question 

### Increase precision 2 - multi-stage

Give reasoning steps - "thinking steps"

* Give me the effects of `ECB bond purchases` on `aggregate demand`.
* Instead of asking directly, ask along  
    * `ECB bond purchases` effect on `interest rates`
    * `Interest rates` changes caused by ... what is effect on `mortgages`
    * `Interest rates` changes caused by ... what is effect on `stocks`
    * `Mortgages` effect on demand
    * `Stocks` effect on demand

#### Increase precision 2 - multi-stage - cont'd

* Also when asking for programming template <br> 
  with three or more functional dimensions
    * Break it down into several steps


### Math

* LLMs cannot do math

Instead

* Send question: Are there any things  <br> that need to be computed in `statement`?
* Response:  `verbal description` of computation
* Write me Python code to do that computation
* Execute Python on _your_ computer

#### Example for Math

* We have 233345322132 organisms <br> with 49224224233 cells
* Tell my the multiplication you want to do

### Questions on contents of large documents

* Break docs into chunks
* Compute embedding of chunks
* Compute embedding of question
* Select chunks similar to question by embedding
* Send 

### Include most recent data

* Articulate `Hypothesis`
* Programm Google web search for `Hypothesis`
* Concatenate `results` into `list-of-paragraphs`
* Ask LLM: Is `Hypothesis` confirmed by list of `list of paragraphs`?


### Validation 1 - ensemble approach

* Ask three distinct variations of `question` - separately
* Go for maximum variation
* Collect three `results`
* Send the three `results` for voting

### Validation 2 - follow up

Using follow up questions

* "Give me the authors from this `paragraph`
* Answer: Jane Brown, Joe Black, Kathrin Halucinatorix
* A user tells me, following autors are <br> in that `paragraph` (Quote previous answer) -  is this true?
    * Yes / No
* No implies failed validation

### Validation 3 - follow up

Using follow up questions

* Give me tax rate from `paragraph`s
*  40%
* A user tells me, following tax rate is <br> in that `paragraph`: "40%" -  is this true?
    * Yes / No
* No implies failed validation

### OCR 

* Extracting text from pictures, images
* Superior to `tesseract`

### Use in academia teaching

* Spell check
* Content of lectures as "Teaching Assistant"
* Create exam questions from content of lectures
* Not just multiple-choice
* For generic teaching: [Khan academy](https://www.khanacademy.org/)

### Deceive fraud detection

* Rewrite this, so the content is the same, <br> but it does not look like it comes from an LLM
* Better: Agree on a code word that is <br>  not on the internet to include into your communication
* Cheating detection is impossible

### Demo web application

[Demo](./web-application.md)



### Context dynamically from vector database

<!-- Integrate a bunch of documents into an LLM vector database -->

* Collect texts containing your reasoning
   * Fiscal Dominance
   * Narratives
* Compute embeddings
* Get similar chunks 
* Include as context for question

### Context size

* Claims on context size are false

* GPT-4o is [not reliable](https://www.heise.de/news/GPT-4-Turbos-bestes-neues-Feature-funktioniert-nicht-besonders-toll-9528751.html) beyond 7000 letters.


### Chunk size for your vector database 

Too small chunks => too little context

Too large => Relevant results get diluted with irrelevant parts

Chunk size: 2-4 sentences.

For conceptual search: Bigger chunks


### Make database results into a nice answer

Send initial question as chat completion query

Embed the embedding results as context 

```
You are an expert assistant. 
Based on the following retrieved information, answer the user's query:

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


### Embeddings vs Chat Completion

* Use cheap `embeddings` for coarse pre-selection of text by relevance
* Use `embeddings` to measure basic concepts
* Use expensive `LLM chat-completion` to _measure_ advanced concepts
* Find the cutoff, where LLMs can still "reason" reliably


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



