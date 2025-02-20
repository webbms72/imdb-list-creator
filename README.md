# IMDb List Manager

This Python script helps you manage your IMDb movie lists. It reads movie titles from a CSV file and can create or update an IMDb list with those titles.  It also includes a dry run mode to preview changes before applying them.

## Overview

This script automates the process of adding movies to your IMDb lists.  Instead of manually searching and adding each movie, you can provide a CSV file containing the movie titles, and the script will handle the rest.  It uses the `imdbpy` library to interact with the IMDb database.  A key feature is the dry run mode, which allows you to see exactly what changes the script *would* make to your list without actually modifying it. This is extremely useful for testing and ensuring your CSV file is correctly formatted.

## Command Line Usage

The script is run from the command line using Python.  Here's how:

```bash
python imdb_list_manager.py [options]
```
Where imdb_list_manager.py is the name of your Python script.

Options:

CSV File: The path to your CSV file containing the movie titles. This is a required argument. The CSV file should have a column named "title" with the movie titles.
List Name: The name of the IMDb list to create or update. If a list with this name doesn't exist, it will be created. If this option is not provided, the default list name "My Movie List" will be used.
Dry Run: Use the --dry-run or -d flag to perform a dry run. In dry run mode, the script will print the actions it would take without actually modifying your IMDb list. This is highly recommended before running the script in live mode.
Examples:

Dry run:
```bash
python imdb_list_manager.py movie_list.csv --dry-run
```

Actual update: 
```bash
python imdb_list_manager.py movie_list.csv "My Awesome Movie Collection"
```

Using short flag for dry run:
```bash
python imdb_list_manager.py movie_list.csv -d
```

# Developer Instructions

To set up the development environment and run the script, follow these steps:

- Clone the repository (if applicable): If you're working with a Git repository, clone it to your local machine.
- Create a virtual environment (recommended):

```bash
python3 -m venv .venv  # Create a virtual environment
source .venv/bin/activate  # Activate the environment (Linux/macOS)
.venv\Scripts\activate  # Activate the environment (Windows)
```

## Install the dependencies:

```bash
pip install -r requirements.txt
```

(Make sure you have a requirements.txt file in your project directory.  If not, create one with the necessary libraries: imdbpy, requests, and pandas.)

- Prepare your CSV file: Create a CSV file (e.g., movie_list.csv) with a column named "title" containing the movie titles you want to add to your IMDb list.
- Run the script: Use the command-line instructions described above to run the script, remembering to use the --dry-run option first to test your CSV and configuration.
- Authentication: The script will prompt you to authenticate with your IMDb account when you run it.  This is necessary for the script to access and modify your lists.
- Be mindful of IMDb's rate limits: The script includes a time.sleep(1) to pause between API calls.  Avoid making too many requests in a short period to prevent your IP from being blocked.
- Error handling: The script includes basic error handling, but you may want to add more robust error handling for production use.
- Customization: You can customize the script by modifying the list name, CSV file path, and other parameters.  You can also extend the script to add more features, such as searching for movies by other criteria or managing multiple lists.
