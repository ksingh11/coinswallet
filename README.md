# Coins Wallet (prototype) API 1.0

Payment wallet prototype application, featuring basic functionality APIs. Project built using [Django framework](https://github.com/django/django) on python.

## Features
- Registers a client application to make API calls, to get `client_id` and `client_secret`.
- Register users, who will be wallet owners.
- Authenticate user, to get access_token.
- Make API calls, with header `Authorization Bearer token`

## Quick links
- [API Overview](api-overview.md)

## Setup (To run locally)
 - Create a Python 2.7 virtualenv
        
        virtualenv [-p path/to/python2.7] venv

- activate python virtual environment:
  
        source venv/bin/activate

- Install dependencies:
        
        pip install -r requirements.txt


- Setup Database:
    move to sub-directory `coinswallet/`, then run migrations to create database. Using only `sqlite3` DB for development.
    
        cd coinswallet/
        python manage.py migrate

- Load pre-configured fixtures:

        python manage.py loaddata fixtures/initial_data.json

- Start server:

        python manage.py runserver


## Quick Setup:
- Using shell script, `setup.sh` placed in project root.

        source setup.sh

## Running the tests:
- Run test fixture for both, unit and functional test:

        python manage.py test


## Code Linting:
- Run code linting with `flake8`, using `.flake8` config file.

        flake8 <directory|filename>
        e.g. $ flake8 coinswallet/


## Project's Django Apps:
- wallet_core: core wallet logic, holding all the logics and interacting with DB
- api_v1: wrapper over wallet logic, which is responsible for handling api calls, and interaction with wallet's core module'


## Third party Django Packages:
- [django-rest-framework](https://github.com/encode/django-rest-framework)
- [django-oauth-toolkit](https://github.com/evonove/django-oauth-toolkit)
- [flake8](https://github.com/PyCQA/flake8)


## Usage Directions:
- Setup Project
- Load fixtures (optional, but recommended for testing)
- Create django super user, or use already created with fixtures:

        username: kaushal
        password: secret_pass
       
- Start django server
- Login to django admin
- create new OAuth Client:
 create with `client_type: confidential`, `Authorization grant type: Resource owner password-based`. 
 Or use already created application with fixtures.
 
        Application detail in fixture:
        name: MobileApp
        client_id: 6LnALs4wMmYcVPn7Tol6joXpJXSEb9BCEsr3o6Bn
        client_secret: uzDYdXGbbYBstWmo06YmNuLG2IxBviUMpT3pFYaMcptPYaMMAnWYSI86Ngx6BWCi5UlVQHcUYjP0HPbDONGycD6fYJN75TAYfDeWptFcYM8zDdpZTaXfwg4s9KXJBKJl
 
- Generate access token for username `kaushal`, password: `secret_pass`:

        curl -X POST -d "grant_type=password&username=kaushal&password=secret_pass" -u"6LnALs4wMmYcVPn7Tol6joXpJXSEb9BCEsr3o6Bn:uzDYdXGbbYBstWmo06YmNuLG2IxBviUMpT3pFYaMcptPYaMMAnWYSI86Ngx6BWCi5UlVQHcUYjP0HPbDONGycD6fYJN75TAYfDeWptFcYM8zDdpZTaXfwg4s9KXJBKJl" http://localhost:8000/o/token/


        response: {"access_token": <access_token>, "token_type": "Bearer", "expires_in": 6000, "refresh_token": <refresh_token>, "scope": "transact view"}

- Use any rest client with Authorization header, to test APIs. [API Overview](api-overview.md)


## Feedback and Queries:
- mail at: [kaushal@zostel.com](mailto:kaushal@zostel.com)