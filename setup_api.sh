#!/bin/bash

# Crear entorno (environment) para API
python -m venv api_env

# Activar entorno para API donde instalaremos todos lo necesario
source api_env/Scripts/activate 

# Instaciión de dependencias para ejecutar API
pip install -r requirements.txt