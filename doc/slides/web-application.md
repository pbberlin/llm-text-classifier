# Demo web application

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
