#!/bin/bash

# Set ENV variable to "prod"
export ENV="prod"

# Prompt user for DATABASE_URL and export to ENV variable
read -p "Enter DATABASE_URL: " DATABASE_URL
export DATABASE_URL="$DATABASE_URL"

# Prompt user for SECRET_KEY and export to ENV variable
read -p "Enter SECRET_KEY: " SECRET_KEY
export SECRET_KEY="$SECRET_KEY"

# Prompt user for OPENAI_API_KEY and export to ENV variable
read -p "Enter OPENAI_API_KEY: " OPENAI_API_KEY
export OPENAI_API_KEY="$OPENAI_API_KEY"

# Run the Python script
python app/recipes_to_database.py
