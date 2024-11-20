# Flask web application

```sh
pip install -r requirements.txt
pip install -r requirements.txt -U
cls && python web-app.py
```

Open your browser http://localhost:8001

More on [embeddings](./doc/README.md) 


Import ECB speeches

```sh
cls && python web-app.py --ecb=True
```

## Ideas - Pocketbase

* Use pocketbase for config, contexts, prompts, benchmarks, templates
* `pocketbase.exe serve  --dir=./data/pb_data  --migrationsDir=./data/pb_migrations`
* Store additonal tables in the same DB file
* Nice UI - but onerous to ORM the data into JSON
    * We would have to use the Javascript API and serialize the JSON into Pydantic class instances

## FastAPI

* Endpoint Doc
* Comfort funcs to extract request data into objects

## Ideas - Pydantic

* Use Pydantic classes for contexts, prompts, benchmarks, templates
* Easy database ORM 
* Pydantic classes => create JSON schema  
* Use [JSONForms](https://jsonforms.io/) to generate the HTML forms
* JSONForms needs to be a separate project