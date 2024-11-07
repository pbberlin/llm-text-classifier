# Text classification using LLMs


## Overview

* High level overview
* Give an intuition
* => Inspiration
{: #an_id .a_class somekey='some value' }


## Application in research

* LLMs have been used to conduct _sentiment analysis_
* The empirical evidence was good



### Projects with potential use for LLMs

1.  GuW project<br>
    mining speeches on central bank policies 
1.  CbCR projects  - extracting   
taxation parameters from weakly structured texts 
2.  Municipal taxation - council minutes<br>
  extracting
    * Business tax rates
    * Period in time
    * Own municipality vs. other municipalities


### Mining of text for  _concepts_

* Perceived `competitive networks`
* Tax multipliers 
* Various `narratives`
* ...

<!-- additional page break -->
<!--pagebreak-->

Projects with potential cont'd 

<!-- : value='4'  -->
* Financial markets dept
    * Pension policy research  -  <br>
      classify text against concepts
    * Financial literacy research - <br>
      limits of capturing `financial calculus` with LLMs


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



### Generic solutions

1. Extract numbers with _conditions_  
    * Business tax rate for Hintertupfingen for 2023
    * Previous  rate for 2023, 2022
    * Business tax rate of adjacent municipality
2. Validation
    * Can we outsource the validation of extracted data  
      to platforms like Mechanical Turk
    * Cost
    * Automation


<!-- additional page break -->
<!--pagebreak-->

Generic solutions cont'd

3. Can we use LLM embeddings to quantify text <br>
 against more avanced concepts? 
    * Not just `favorable`  vs `unfavorable`.
    * How much `alignment` between a benchmark <br> and some piece of text.

<!-- additional page break -->
<!--pagebreak-->

Generic solutions cont'd

* EU asset purchasing programmes (APP):
    * Can embeddings  capture the discussion?  
    * Can text content be measured against economic theories?
* Research into local taxation:  
    * Reasoning about  _surrounding_ municipalities?    
    * Reasoning implicitly along the game theory concept <br> 
    of prisoner's dilemma?


### Validation

* If we reach useful result with LLM, <br> how to measure quality? How to validate?
* Can we contract out these task <br> to "clickworker" companies?
* At what cost?


## Bag of words

* How much do LLM embeddings improve on existing methods <br> such as [bag of words](https://en.wikipedia.org/wiki/Bag-of-words_model)?
* Effort? Cost?


### Results so far

* Use cheap embeddings to make a coarse pre-selection of text by relevance
* Use expensive LLM chat-completion to measure relevant parts
* Try to find the cutoff, where the LLMs can still "reason" reliably
    * All things inflation - yes
    * Effects of inflation going into an ISLM model economy - all the channels and effects - somewhat - if the corpus is thick
* Restructure the remaining work and validation, so that humans can do it as easy as possible

### Delimination I - Language

Consider following two realms

* Reality 
* The language corpus of the entire Internet


There are all kinds of differences between  
reality and the language corpus.  
<!-- For some, reality itself might be questionable.   -->

The science of linguistics researches this. 

Also [philosophy](https://en.wikipedia.org/wiki/Ludwig_Wittgenstein). 

#### Delimination I - Language - cont'd

* We _cannot_ make any statement about the relationship  
   between the internet language corpus and actual reality 
* LLMs can only make claims about the _second_ realm
* LLMs give a probabilistic extract <br>
of the _internet language corpus_

#### Delimination I - Language - cont'd

* Consider controversial concepts, <br>
for instance [Supply-side economics](https://en.wikipedia.org/wiki/Supply-side_economics)
* Supply-side economics contains some more realistic assumptions<br> 
  such as cheaper factors increase supply.
* Other assumptions are considered more debatable:
    *  An increase in supply _might_ pay for lost revenue, <br> under more or less extreme conditions.
    {: style="margin-left:6rem" .myclass }


## Delimination II - Generative AI

* The _classification_ faculty of LLM is expressed  
 in large vectors - the _`embeddings`_
* The _generative_ AI is built upon embeddings
* _Generative_ AI has some probabilistic element,  
that can lead to erroneous results


<!-- <small> More on `embeddings` later. </small> -->



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

* Two statements containing identical words - difference is only in punctuation
    * I am giving up  drinking until this is over.
    * I am giving up. Drinking until this is over.
* ![considerably different](./img/embeddings-drinking-until.jpg)
{: .nobullet }
*  Chart: "Significant" positive and negative [embedding] values - 32 values of biggest magnitude.<br>
 Short grey bars indicate identical dimensions (48%) - 52% are _distinct_.<br>
 Even identical dimensions have different values.
{: .small }

 
#### On Embeddings cont'd

* LLMs put heavy weights on punctuation tokens
* _Preceding_ words heavily influence the weighting of a word
* ![embeddings](./img/embeddings-text.jpg)
{: .nobullet }

#### On Embeddings cont'd

* Vector dimensions can be seen as "[principal components](https://en.wikipedia.org/wiki/Principal_component_analysis)" of  the language corpus. 
* As of October 2024, LLM models express the meaning of language in vectors of 3078 dimensions.
* These dimensions (think `principal components`) are derived by expensive AI training
* For a given LLM, embeddings are _deterministic_. No variation. No hallucination.
* Building block for the `generative` AI components

#### On Embeddings cont'd

* Most dimensions cannot be associated with words or concepts.
* They rather represent `shades` of language - <br>
such as "positivity" or "short term future", "long term future"


#### On Embeddings cont'd

* Variations and translations of the word `price` <br>
* ![Example price](./img/embeddings-price.jpg)
{: .nobullet }
* All load highly negative on dimension 87, <br>
and highly positive on dimensions 528 and 57
* Maybe, these is the cluster for the concept of a price in the context of economics?  


#### On Embeddings cont'd

* No common sense meaning <br> for many `principal components`
* Local clusters of LLM cells <br> might be [associated](https://www.economist.com/science-and-technology/2024/07/11/researchers-are-figuring-out-how-large-language-models-work) with some language concepts
* Correct classification _may_ be indicated  <br> by loadings on localized clusters

<!-- * Failed classification may be indicated <br> by small loadings all over the vector space. -->
<!-- * Resulting in a weak and diffuse classification.  -->

### Limitations for the generative Part of LLMs

* _Sentiment_ analysis: <br>
  categorization as `positive` and `negative` is very good,  
  even if evaluated _concepts_ are not represented in the corpus.  
* The embeddings will capture  the valuation aspect <br> even for unknown concepts
    * Apfeldachschlüssel wäre für uns alle ein großer Gewinn, <br> 
      wenn er die Chromodysterose absolviert hat. <br>
      Davon kann man nur träumen.

<!--pagebreak-->

<pre style="font-size:40%; line-height: 80%">
You are an economic policy analyst.

The speech text is: "ApfeldachSchlüssel wäre für uns alle ein großer Gewinn, 
  wenn er die Chromodysterose absolviert hat. 
  Davon kann man nur träumen."

Make sure to give an objective analysis based on the content of the speech.

I need a thorough textual analysis on how much the speech aligns 
with the concept of favorable, beneficial, good and positive.

Determine whether the speech agrees, disagrees, or remains neutral on 
concept of favorable, beneficial, good and positive.

Provide a percentage score for alignment.

Use the following json format for your response:

{{
    "agreement":        "<agrees/disagrees/neutral>",
    "alignment":         <percentage_score>
    "textual_analysis":  <text>
}}
</pre>

<pre style="font-size:50%">
{
    "agreement": "neutral",
    "alignment": 50,
    "textual_analysis": "The speech text mentions 'ApfeldachSchlüssel' as a potential 'big gain'
     (translated from 'großer Gewinn') for everyone, 
     indicating a positive outcome if certain conditions are met. 
     Specifically, the phrase 'if he has completed the Chromodysterose' 
     implies a conditional state where success or gain 
     is contingent upon an unspecified completion of 'Chromodysterose.' 
     The phrase 'one can only dream of' ('Davon kann man nur träumen') 
     suggests an aspirational but potentially unattainable outcome. 
     Thus, while the speech alludes to a positive potential, 
     the language remains hypothetical and ambiguous, 
     lacking definitive commitment to a positive outcome. 
     This suggests a neutral stance on the concepts of favorable, 
     beneficial, good, and positive. 
     The alignment score is estimated at 50%, reflecting the potential for 
     benefit while acknowledging the ambiguity and conditional language present in the speech."
}

</pre>


#### Limitations for the generative Part of LLMs cont'd

Thin corpus

* Huge amounts of material about [Hamlet](https://en.wikipedia.org/wiki/Hamlet) 
* Little material on the German novel [Effi Briest](https://en.wikipedia.org/wiki/Effi_Briest)

=> Questions about _details_ about the romantic relationship <br> between the protagonists (Hamlet and Ophelia, Effi and Crampas)  
   are answered with enormous breadth or with hallucinations  <br> drawn from U.S. movies (the next best thing).

With thin corpus coverage, the quality of classification might also suffer.




But even _advanced concepts of research_ seem to be captured very well in embeddings. 

Example: Purchase of government bonds by the EU

Take two statements around the concept of `central bank`, `central bank intervention`, the `market for government bonds` and important macro variables:

* The European Central Bank (ECB) did take a strongly active position in recent years by purchasing sovereign bonds of euro countries. This strongly active position of the ECB should continue.

* The European Central Bank (ECB) purchase programmes for sovereign bonds of euro countries will increase money supply and eventually increase expectations of the price level.

The data points of the _second_ series are shifted right by two pixels, in order to make the almost perfect overlap visible.

![strong similarity](./img/embeddings-ecb-gvt-bond-purchase.jpg)

The embeddings of the two statements from a relatively specific scientific domain show strong similarities.

* Despite very different wording

* Despite having distinct sentiment (explicitly positive, implicitly negative) 

* Is this an expression of excellent categorization?  

* Or are these just extreme loadings, indicating a failure to capture meaning beyond some major anchors?

* More work needed

## Context

* Sometimes necessary.  
  The corpus on `structured bonds` may be vastly different 
   in commercial real estate than in public finance.

* If the the texts are already littered with terms from the intended domain, it might be dropped.  

* Keep it short, to reduce noisy classification.

* We can test the effect of providing context on training sets with examples.

* Sometimes the context seems to reduce the distinctions (work needed)


## Web application

The web application can be downloaded from [ZEW git](https://git.zew.de/ub-public-finance/ecb-speeches-flask).

It can be executed on your notebooks.

The web application is written in `Python`.

The core is advanced (web server stuff...)

But the periphery is extendable by researchers and by student workers.

The web application connects to OpenAI ChatGPT 4.  
It requires an API key from OpenAI inc.  

If you request many embeddings, OpenAI may require money for it.

At least, embeddings are stored locally; openAI is only asked _once_ per text-element.

The web application allows for uploading and arranging various elements of text classification

* contexts
* benchmark statements (goal posts) 
* and texts to be classified

Some default data is loaded.  
You can change according to your reserch.

It displays embeddings and similarity as charts.


## Conclusion

* Vector embeddings capture the general relationship between two texts  
  but lack deep understanding of specific concepts.

* Vector embeddings are immune to the hallucination problem.

* The results are stable and reliable.  
  Small variations might occur, depending on the LLM vendor and LLM training details.

* The current dimensionality of 3078 is a limiting factor for capturing meaning and similarity.

* If LLM companies can increase the dimensionality in the future, the quality of analysis can increase further. 

## Extension: Chatbot

By directly engaging with a chatbot,  
we can get more insight into how the chatbot interprets the meaning and implications of a statement within the broader context of economics and government policies.

By setting the `temperature` to zero, we minimize hallucinations.


## Sources

[Sergio Correia - Unlocking Data with LLM](https://www.youtube.com/watch?v=quf6jlJ-Mvg&t=3100s&pp=ygUyU2VyZ2lvIENvcnJlaWEgb24gVW5sb2NraW5nIEVjb25vbWljIERhdGEgd2l0aCBMTE0%3D)


---------------

## Technical documentation

This is purely technical - for software engineers and programmers

### Production webserver

See ./production-setup.md


### Indexing

Directory   ./indexing-embeddings/autofaiss  contains some steps towards building an index for embeddings,
so that most closely matching embeddings can be searched and found quickly.

Unlike B-Tree indexes known from databases; indexes for embeddings are expensive to update.

Some index types (HNSW32) are less expensive for update, but slower in query.

Index type IVF4096 can be very fast (<15 ms) but each new vector takes a lot of computing.

Also: Each ChatGPT-O embedding needs 8 Bytes times 3078 slots space - 28 kB of data.

The indices have similar size; an index of 800.000 embeddings needs 9 GB of space.

Indices can be used as memory mapped files, but still require a lot of memory.

One should considering a large index of "stock" embeddings - and tiny "delta" indices for new data,  
being merged at night.

If needed, a distributed index across several server machines needs to be built.


## Backup slides

### Problems

* LLMs are in many ways not well understood

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

