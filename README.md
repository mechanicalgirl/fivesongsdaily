fivesongsdaily
===============

To run locally:

- Run this one time to create the virtualenv:

`python3 -m venv venv`

- Activate the virtualenv at the beginning of every session:

```
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

- initialize the db

```flask --app fivesongs init-db```


- To start up the app (and restart after code changes):

```flask --app fivesongs run --debug```



