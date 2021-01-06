#!/usr/bin/env bash

# this script will initialize python3 virtual environment, 
# if env exists it will just activate
# else it will create one and install all requirements, then will activate
# it also activate dotenv variables
#
# don't change permition to +x for this file, run it with source ". ./venv.sh"

export PYTHONPATH=.
ENV=.venv
ENV_ACTIVE=$ENV/bin/activate

if [[ ! -d $ENV ]]
then
	echo 'Initializing environment ...'
	python3 -m venv $ENV
	source ${ENV_ACTIVE}
	pip install --upgrade pip
	pip install wheel
	pip install -r requirements.txt
else	
	echo 'Activating virtual environment ...'
	source ${ENV_ACTIVE}
fi

# load dotenv
if [ -f .env ]
then
	echo 'Activating .env variables'
  source .env
fi
