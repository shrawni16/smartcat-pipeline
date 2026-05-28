# Smartcat Translation Pipeline

An automated translation pipeline built with Python and the Smartcat REST API.

## What it does

Given a source text file, this pipeline automatically:

1. Creates a Smartcat translation project via API
2. Uploads the source document
3. Polls until the document is processed
4. Requests a translation export
5. Downloads the translated zip file (French + German)

## Tech stack

- Python 3
- Smartcat REST API
- `requests` library
- `python-dotenv` for credential management

## Setup

1. Clone the repo
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install requests python-dotenv`
5. Create a `.env` file with your Smartcat credentials:
6. Add your source text as `input.txt`
7. Run: `python3 main.py`

## Output

A `translated_output.zip` containing translated files for each target language.

## Author

Srabani Banerjee — [LinkedIn](https://www.linkedin.com/in/srabanibanerjee)
