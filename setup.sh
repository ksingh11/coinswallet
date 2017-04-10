#!/bin/bash

# create virtualenv for python 2.7
virtualenv venv

# activate python virtual environment
source venv/bin/activate

# install pip requirements
pip install -r requirements.txt

# Run Code linting, validate against PEP8
echo 'Code linting for project directory'
echo 'flake8 coinswallet/'
flake8 coinswallet/

# move to project directory
echo 'Jumping into project directory: coinswallet'
cd coinswallet/

# migrate database
echo 'Migrating database...'
echo 'python manage.py migrate'
python manage.py migrate

# Load fixtures
echo 'Loading fixtures...'
echo 'python manage.py loaddata fixtures/initial_data.json'
python manage.py loaddata fixtures/initial_data.json

# Run tests
echo 'Running tests...'
echo 'python manage.py test'
python manage.py test

# Run server
echo 'start server'
echo 'python manage.py runserver'
python manage.py runserver
