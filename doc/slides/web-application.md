# Demo web application


Web application on git.zew.de <br> <small> https://git.zew.de/ub-public-finance/llm-text-classifier </small>

Web application be run on your notebooks

Written in `Python`

Periphery extendable by researchers <br> and by student workers with IT affinity

<!--pagebreak-->

Web application connects to OpenAI <br>
 (online connection)

Requires an API key from OpenAI inc

OpenAI may charge you for heavy use

Any results are stored locally; <br> 
OpenAI is only asked _once_ per prompt

<!--pagebreak-->

Convenient uploading and arranging of data

* Texts to be mined
* Benchmark statements - belief statements 
* Pipelines of prompts

Some default data is provided

Expand according to your reserch


### Hallucinations not a problem

* Generative AI has some probabilistic element,  
  that can lead to erroneous results
    * Setting temperature to 0
    * Changing seed
    * => Replies show only tiny variation

Setting `temperature` to zero <br> 
=> hallucinations practically disappear
