# Flipkart Web Scraper and Visualizer

This project provides a web application and PowerBI dashboard for scraping product data from Flipkart based on user-provided keywords or URLs, and visualizing the results.

## Contents

- `Multipage-URL-Input.ipynb`: Jupyter notebook for scraping data based on URL provided by the user and the number of pages.
- `User-Input-Keyword-Analysis.ipynb`: Jupyter notebook for scraping data based on the keyword and the number of pages provided by the user.
- `Flipkart_Web`
  - `templates`
    - `index.html`: Frontend for input form of keyword and number of pages.
    - `results.html`: Frontend for showcasing output and graphs based on the form input.
  - `app.py`: Python Flask code for the web app, with functionality similar to the `User-Input-Keyword-Analysis.ipynb` notebook.
- `flipkart_viz.pbix`: Microsoft PowerBI file for visualizing scraped data.

## Jupyter Notebooks

### Multipage-URL-Input.ipynb

This notebook allows users to scrape product data from Flipkart based on a specific URL and the number of pages to scrape.

#### Usage
1. Open the notebook.
2. Run all cells.
3. Enter the URL of the product search page.
4. Enter the number of pages to scrape.
5. Wait for the data to be loaded.
6. View the output.

### User-Input-Keyword-Analysis.ipynb

This notebook allows users to scrape product data from Flipkart based on a keyword and the number of pages to scrape, and provides visualizations of the results.

#### Usage
1. Open the notebook.
2. Run all cells.
3. Enter the keyword of your choice.
4. Enter the number of pages to scrape.
5. Wait for the data to be loaded.
6. View the output with visualizations.

## Web Application

### Structure

- `index.html`: Input form for keyword and number of pages.
- `results.html`: Displays the output and graphs based on the form input.
- `app.py`: Flask application that handles form submission, data scraping, and rendering of results.

### Usage

1. Run `app.py` using Python.
   ```sh
   python app.py
   ```
