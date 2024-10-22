#!/bin/bash
if ! command -v virtualenv &> /dev/null
then
    echo "virtualenv could not be found, installing..."
    pip install virtualenv
fi

virtualenv venv

source venv/bin/activate

pip install -r requirements.txt

echo "All dependencies are installed and the virtual environment is set up."
