#  Software architecture

### FastAPI

* Endpoint Doc
* Comfort funcs to extract request data into objects <br>
   but this is not very interesting

* Jinja2 templates - similar to Flask - but better function injection

* Development server with auto-reload

* Router objects in submodules
    * Endpoint implementations in separate files

* Database code structure
    * create models from shared base
    * instantiate database
    * create schema from models above
    * ---
    * `Depends(get_db)` makes database session available in endpoints
    * Ugly but accaptable solution for get_db outside endpoints




## Database integration

We have several things to consider

* Pydantic vs Dataclasses  <br>
https://medium.com/@danielwume/exploring-pydantic-and-dataclasses-in-python-a-comprehensive-comparison-c3269eb606af
=> Pydantic seems slightly better - but the clincher comes below

* Pydantic models vs. SQLalchemy models:
We would need *both*. And we would need a mapper back and forth for each entity.
And the mapping is not even trivial. Especially for composite objects.
And the Pydantic classes need to be two-pronged -  Embeddings(EmbeddingsBase),
  where the outer class contains the database cols (id, lastchanged..)
  and the inner contains the idiosyncratic entity fields.
  We would have four classes for each entity to content with.
  There is some mapper lib "SQLObjects" - but this does not reduce complexity.
  Even if we would go with pydantic classes close to FastAPI endpoints,
  there is a lot of syntactic complexity and logic even for minimal REST stuff.
  Pydantic only offer some comfort in validation. We reject Pydantic.

* Use sqlalchemy models only.  
  * Little support for JSON serializaton. 
  * No support for validation.

=> decision:

* Use dataclasses 
* Add JSON serializaton via [dataclasses-json](https://pypi.org/project/dataclasses-json/)
* dataclasses-json also provied `JSON schema export` 

* Use dataclasses for _everything_s
   * Model definition
   * Database objects
   * FastAPI endpoint typing



## Svelte component

* The requesting of a prompt for chat completion is done via async http.
* We want the prompt to show up instantly.
* And then show a progress animation and finally the multiple responses.
* Also we want a `pipeline` of chat completion.
* We have custom javascript (file `llm-answer-js.html`) 
* We also have a compiled svelte component:


..\js\llm-query-svelte\


## JSONForms

* We want to generate HTML code for edit forms from dataclasses.
* There is no solution in Python.
* We convert our dataclasses to json schema files
* We feed these into JSONForms (JavaScript+Node)
* We give some layout specification
* We receive HTML forms

[Vue seed](https://github.com/eclipsesource/jsonforms-vue-seed)

..\js\jsonforms-vue-seed\





## Ideas

### Pocketbase

* Use pocketbase for config, contexts, prompts, benchmarks, templates
* `pocketbase.exe serve  --dir=./data/pb_data  --migrationsDir=./data/pb_migrations`
* Store additonal tables in the same DB file
* Nice UI - but onerous to ORM the data into JSON
    * We would have to use the Javascript API and serialize the JSON into Pydantic class instances


