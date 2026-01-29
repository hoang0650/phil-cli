#!/bin/bash

echo "Installing Phil-CLI..."

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install it first."
    exit
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install anthropic openai python-dotenv docker rich sqlalchemy

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file. Please add your API keys."
    echo "ANTHROPIC_API_KEY=" > .env
    echo "OPENAI_API_KEY=" >> .env
    echo "PHIL_MODEL=claude-3-5-sonnet-20241022" >> .env
fi

echo "Setup complete. To run Phil-CLI:"
echo "source venv/bin/activate"
echo "python3 -m phil-cli.phil"
