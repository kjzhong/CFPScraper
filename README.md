# Call for Paper Scraper

Call for Paper Scraper (CFPS) is a Python program for scraping CFPs from IS Journals

## Installation

Create a virtual environment and use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

Tested with Python 3.8 on WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

This program is meant to be run automatically from a server daily. This means it was built with the following in mind:
* Robustness - errors should be caught and handled
* Errors should be logged for debugging
* It shouldn't need user input to run


```bash
source .venv/bin/activate
python3 runner.py
```

## Program Structure

* Scrape sites
    * Open page
    * Look for a way to build a list
    * Look for attributes within each list
    * Combine into a dictionary
    * Add dictionary to 'data' list
* Build CSV

## Assumptions
* Journals won't have so many CFPs they spill over into more pages
* No (major/any) changes to page structure

# Project Context
This is the final assignment submission for the T3 2020 iteration of INFS2822 by me. This code was created in less than 24 hours and should be judged with that in mind.

Thanks Blair Wang and Matthew Perry for the great course.
