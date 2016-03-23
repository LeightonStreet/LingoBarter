Lingo Barter
============

[![Build Status](https://travis-ci.org/LeightonStreet/LingoBarter.svg?branch=master)](https://travis-ci.org/LeightonStreet/LingoBarter)

Language Exchange Platform

### Run Lingobarter

Install needed packages in your local computer

You can install everything you need in your local computer or if preferred use a virtualenv for Python

#### Mongo

* Lingobarter requires a MongoDB instance running to connect.

    1. If you don't have a MongoDB instance running, you can quickly configure it:

        * Download from [here](https://www.mongodb.org/downloads)
        * Unzip the file
        * Open a separate console
        * Run it inside the MongoDB directory:
        ```bash
        ./bin/mongod --dbpath /tmp/
        ```
        > WARNING: If you want to persist the data, give another path in place of ```--dbpath /tmp```


    2. If you already have, just define your MongoDB settings:
        ```bash
        $ $EDITOR lingobarter/local_settings.py
        ===============lingobarter/lingobarter/local_settings.py===============
        MONGODB_DB = "yourdbname"
        MONGODB_HOST = 'your_host'
        MONGODB_PORT = 27017
        MONGODB_USERNAME = None
        MONGODB_PASSWORD = None
        =============================================================
        
        # You can also use envvars `export LINGOBARTER_MONGO_DB="yourdbname"` 
        ```

#### Python requirements
Install all needed python packages

> If you have a virtualenv, activate it! `source env/bin/activate` or `workon env`

```bash
pip install -r requirements/requirements.txt
```

#### Create admin user, sample data and run!

* Initial data, users and running commands


    3. Create a superuser  (required to login on admin interface)
        ```bash
        $ python manage.py accounts_createsuperuser
        you@email.com
        P4$$W0Rd
        ```

    4. Populate with sample data (optional if you want sample data for testing)
        ```bash
        $ python manage.py populate

        ```
        > credentials for /admin will be email: admin@example.com passwd: admin

    5. Run
        ```bash
        $ python manage.py runserver --host 0.0.0.0 --port 5000
        ```
        - Site on [http://localhost:5000](http://localhost:5000)
        - Admin on [http://localhost:5000/admin](http://localhost:5000/admin)
        