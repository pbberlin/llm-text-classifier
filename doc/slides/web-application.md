# Demo web application


<a href='https://git.zew.de/ub-public-finance/llm-text-classifier' >ZEW git</a>

https://git.zew.de/ub-public-finance/llm-text-classifier

It can be executed on your notebooks

The web application is written in `Python`

The core is advanced (web server stuff...)

But periphery is extendable by researchers <br> and by student workers with IT affinity

<!--pagebreak-->

Web application connects to OpenAI ChatGPT 4

It requires an API key from OpenAI inc

If you make excessive requests, OpenAI may charge you

Any results are stored locally; <br> 
openAI is only asked _once_ per prompt

<!--pagebreak-->

Convenient uploading and arranging  <br> various elements of text classification

* Texts to be classified
* Benchmark statements - belief statements 
* Pipelines of prompts

Some default data is loaded. <br>
Expand according to your reserch.


### Hallucinations are not a problem

* _Generative_ AI has some probabilistic element,  
  that can lead to erroneous results
    * Setting temperature to 0
    * Changing seed
    * => The concept classifications show only tiny variation

Setting `temperature` to zero => hallucinations practically disappear
