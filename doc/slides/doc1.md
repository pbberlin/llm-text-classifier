# LLMs as tools for research

<!-- ![conquer unknown land](./img/conquer-unkown-land.jpg){: style="width:80%"}  <br> -->
<!-- Research an unknown land -->


## Objective of Presentation

* Provide  intuition
* Examples from current research
{: #an_id .a_class somekey='some value' }
* Inspiration
    * Useful, Possible
    * Cutoff
    * Illusory

Developing details during projects


### Projects benefitting from LLMs

1.  CbCR projects  - extracting labeled taxation numbers  <br>
 from weakly structured texts 
    * Demo
2.  Municipal taxation - council minutes - <br>
  extracting business tax rates
    * Periods in time
    * `Competitive networks`
3.  GuW project - <br> 
    mining speeches on central bank policies 

## Cross sectional solution - generic solution

<table>
    <tr>
        <td style="width:33%" >CbCR</td>
        <td style="width:33%" >Business tax</td>
        <td style="width:33%" > &nbsp; GuW</td>
    </tr><tr><td colspan="3" style="text-align: center">crawling</td>
    </tr><tr><td colspan="3" style="text-align: center">PDF extraction, cleansing</td>
    </tr><tr><td colspan="3" style="text-align: center">number  extraction</td>
    </tr><tr><td colspan="3" style="text-align: center">concept extraction</td>
    </tr><tr><td colspan="3" style="text-align: center">validation</td>
    </tr>
</table>

### Cross sectional solution - cont'd 

* Playful prototyping
* Little or no coding, student workers
* Easy validation by crowd workers
* Documentation for publications 
    * Reproducibility




### Corpus thickness => nodes of faculty

![clusters of concepts](./img/clusters-a/clusters-concepts-a-10.jpg){: style="width:80%"}  <br>


### Biases and Gaps

* Strong representation  <br>of `established opinion`, `conventional wisdom`
* Smaller nodes might be influenced <br>   by `ideosyncratic thinking` 
* Even bigger nodes have `gaps`

<!-- 
* Take [Hamlet](https://en.wikipedia.org/wiki/Hamlet)
    * Any quirk, any background, <br> 
    such as implied succession, or Interest groups
    * `Joining Fortinbras`: Nothing  
 -->


## Prompt techniques

* `Activate` certain faculties

### Demo web application

[Demo CbCR](/slides/cbcr-example)


[Demo web application](/slides/web-application.md)


<!-- todo: role and context -->

### Give template

* Provide JSON schema for output 
    * See web app
* Provide `few shots`
    * Question A - Answer A 
    * Question B - Answer B
    * ...
      * Scope the maximum variety 
      * Edge cases
    * The actual question 

### Multi-stage

* Break the task down into several stages
* Summon two or three faculties each
    * i.e. table structure, 
    * timing, labelling
    * output structure

### Multi-stage - branches

* If `structure A` is not found,  
  try `structure B`

### Multi-stage - reasoning steps

* Give me the effects of `ECB bond purchases` on `aggregate demand`.
* Instead of asking directly, ask along  
    * `ECB bond purchases` effect on `interest rates`
    * `Interest rates` changes caused by ... what is effect on `mortgages`
    * `Interest rates` changes caused by ... what is effect on `stocks`
    * `Mortgages` effect on demand
    * `Stocks` effect on demand

### Large documents

* Must be broken into overlapping chunks of ~3 pages
* Academic research proves degrading results for over ~6000 words
    * Despite claims by companies 

### OCR 

* LLMs are superior to any OCR software, i.e. `tesseract`
* PDFs: Chunk them - but then feed them directly


### Validation 1 - follow up

Using follow up questions

* Give me tax rate from `paragraph`s
*  40%
* A user tells me, following tax rate is <br> in that `paragraph`: "40%" -  is this true?
    * Yes / No
* No implies failed validation


### Validation 2 - ensemble approach

* Ask three distinct variations of `question` - separately
* Go for maximum variation
* Collect three `results`
* Send the three `results` for voting


### Prompt technique sidenotes - Math

* LLMs cannot do math

Instead

* Send question: Are there any things  <br> that need to be computed in `statement`?
* Response:  `verbal description` of computation
* Write me Python code to do that computation
* Execute Python on _your_ computer

#### Example for Math

* We have 233345322132 organisms <br> with 49224224233 cells
* Tell my the multiplication you want to do


### Prompt technique sidenotes - include most recent data

* Articulate `Hypothesis`
* Programm a search engine for `Hypothesis`
* Concatenate `results` into `list-of-paragraphs`
* Ask LLM: Is `Hypothesis` confirmed by list of `list of paragraphs`?



### General sidenotes - use in academia teaching

* Spell check
* Content of lectures as "Teaching Assistant"
* Create exam questions from content of lectures
    * Not just multiple-choice
* For generic teaching: [Khan academy](https://www.khanacademy.org/)

### General sidenotes - everyday life

* Detection is impossible
* Awkward prose and idiosyncrasies <br> => not longer a sign for authenticity
    * Rewrite this, so the content is the same, <br> but it does not look like it comes from an LLM
* Agree on a code word that is <br>  not on the internet to 
    * Include into your communication




