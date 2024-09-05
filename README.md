# Wikipedia Scraping Script

Enjoy Scraping!

This script allows users to scrape articles from Wikipedia (English). It extracts content from specified articles, processes the text, and follows links to gather additional articles based on user-defined parameters.

## Features

- Connects to Wikipedia articles and retrieves content.
- Cleans up HTML content by removing unwanted elements such as ads, scripts, and references.
- Recursively follows links to extract additional articles.
- Provides progress updates and handles network errors gracefully.

## Requirements

To run this script, you need to install the following Python libraries:

1. `requests` - For making HTTP requests.
2. `beautifulsoup4` - For parsing HTML content.

You can install the required libraries using pip:

```bash
pip install requests beautifulsoup4 
