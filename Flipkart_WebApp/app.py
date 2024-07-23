from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import plotly.express as px
import plotly.graph_objects as go
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        num_pages = int(request.form['num_pages'])
        flipkart_df = scrape_flipkart(keyword, num_pages)

        total_products = len(flipkart_df)
        

        cheapest_product = flipkart_df.loc[flipkart_df['price'].idxmin()]
        costliest_product = flipkart_df.loc[flipkart_df['price'].idxmax()]
        highest_rated_product = flipkart_df.loc[flipkart_df['stars'].idxmax()]
        least_discounted_product = flipkart_df.loc[flipkart_df['discount_%'].idxmin()]
        highest_discounted_product = flipkart_df.loc[flipkart_df['discount_%'].idxmax()]

        summary_stats = {
            'cheapest_product': cheapest_product.to_dict(),
            'costliest_product': costliest_product.to_dict(),
            'highest_rated_product': highest_rated_product.to_dict(),
            'least_discounted_product': least_discounted_product.to_dict(),
            'highest_discounted_product': highest_discounted_product.to_dict()
        }

        # Create plots
        
        # Count of Products per Brand
        brand_counts = flipkart_df['brand_name'].value_counts().reset_index()
        brand_counts.columns = ['brand_name', 'count']

        fig_ct_of_prod = px.bar(brand_counts, x='brand_name', y='count', title='Count of Products per Brand', labels={'brand_name': 'Brand', 'count': 'Count'}, text='count')
        
        ct_of_prod_plot = fig_ct_of_prod.to_html(full_html=False, default_height=500, default_width=600)
        
        # Average Stars per Brand
        avg_stars_per_brand = flipkart_df.groupby('brand_name')['stars'].mean().reset_index().round(1)
        avg_stars_per_brand.columns = ['brand_name', 'avg_stars']
        
        fig_avg_stars = px.line(avg_stars_per_brand, x='brand_name', y='avg_stars', 
                                title='Average Stars by Brand',
                                markers=True, labels={'brand_name': 'Brand', 'avg_stars': 'Average Stars'}, text='avg_stars')
        
        avg_stars_plot = fig_avg_stars.to_html(full_html=False, default_height=500, default_width=600)

        # Average Discount per Brand
        avg_disc_per_brand = flipkart_df.groupby('brand_name')['discount_%'].mean().reset_index().sort_index().round(1)
        avg_disc_per_brand.columns = ['brand_name', 'avg_disc']
        avg_disc_per_brand = avg_disc_per_brand.sort_values(by='avg_disc', ascending=False)
        
        fig_avg_disc = px.line(avg_disc_per_brand, x='brand_name', y='avg_disc', 
                                title='Average Discount by Brand',
                                markers=True, labels={'brand_name': 'Brand', 'avg_disc': 'Average Discount'}, text='avg_disc')
        
        avg_disc_plot = fig_avg_disc.to_html(full_html=False, default_height=500, default_width=600)
        
        # Average Reviews per Brand
        avg_review_by_brand = flipkart_df.groupby('brand_name')['reviews'].sum().reset_index().round(0)
        avg_review_by_brand.columns = ['brand_name', 'avg_reviews']
        avg_review_by_brand = avg_review_by_brand.sort_values(by='avg_reviews', ascending=False)
        
        fig_avg_reviews = px.line(avg_review_by_brand, x='brand_name', y='avg_reviews', 
                                  title='Total Reviews by Brand',
                                  markers=True, labels={'brand_name': 'Brand', 'avg_reviews': 'Average Reviews'}, text='avg_reviews')
        fig_avg_reviews.update_traces(textposition='top center')
        
        avg_reviews_plot = fig_avg_reviews.to_html(full_html=False, default_height=500, default_width=600)
        
        # Total Ratings per Brand
        brand_ratings = flipkart_df.groupby('brand_name')['ratings'].sum().reset_index()
        brand_ratings.columns = ['brand_name', 'total_ratings']
        brand_ratings = brand_ratings.sort_values(by='total_ratings', ascending=False)
        
        fig_brand_ratings = px.line(brand_ratings, x='brand_name', y='total_ratings', 
                                    title='Total Ratings by Brand',
                                    markers=True, labels={'brand_name': 'Brand', 'total_ratings': 'Total Ratings'}, text='total_ratings')
        fig_brand_ratings.update_traces(textposition='top center')
        
        brand_ratings_plot = fig_brand_ratings.to_html(full_html=False, default_height=500, default_width=600)
        
        # Discount Counts
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        labels = [f'{bins[i]}-{bins[i+1]}%' for i in range(len(bins) - 1)]
        
        flipkart_df['discount_bin'] = pd.cut(flipkart_df['discount_%'], bins=bins, labels=labels, include_lowest=True)
        
        discount_counts = flipkart_df['discount_bin'].value_counts().reset_index()
        discount_counts.columns = ['Discount Range', 'Count']
        discount_counts = discount_counts.sort_values(by='Discount Range')
        
        fig_discount_counts = px.bar(discount_counts, x='Discount Range', y='Count', 
                                     title='Product Count by Discount % Range',
                                     labels={'Discount Range': 'Discount % Range', 'Count': 'Product Count'})
        
        discount_counts_plot = fig_discount_counts.to_html(full_html=False, default_height=500, default_width=600)
        
        return render_template('results.html',
                               keyword=keyword,
                               total_products=total_products,
                               num_pages=num_pages,
                               summary_stats=summary_stats,
                               ct_of_prod_plot=ct_of_prod_plot,
                               avg_stars_plot=avg_stars_plot,
                               avg_disc_plot=avg_disc_plot,
                               avg_reviews_plot=avg_reviews_plot, 
                               brand_ratings_plot=brand_ratings_plot,
                               discount_counts_plot=discount_counts_plot)
    
    return render_template('index.html')

def scrape_flipkart(keyword, num_pages):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    encoded_keyword = quote_plus(keyword)
    base_url = f'https://www.flipkart.com/search?q={encoded_keyword}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off'
    data = {
        'product_name': [],
        'price': [],
        'prev_price': [],
        'discount': [],
        'stars': [],
        'description': [],
        'delivery': [],
        'ratings': []
    }

    for page in range(1, num_pages + 1):
        url = f'{base_url}&page=' + str(page)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', class_=['CGtC98', 'VJA3rP', 'rPDeLR'])
        links_list = []
        for link in links:
            links_list.append(link.get('href'))

        for link in links_list:
            new_response = requests.get('https://www.flipkart.com' + link, headers=headers)
            prod_soup = BeautifulSoup(new_response.content, 'html.parser')

            data['product_name'].append(get_product_name(prod_soup))
            data['price'].append(get_price(prod_soup))
            data['prev_price'].append(get_prev_price(prod_soup))
            data['discount'].append(get_discnt(prod_soup))
            data['stars'].append(get_stars(prod_soup))
            data['description'].append(get_specs(prod_soup))
            data['delivery'].append(get_delivery(prod_soup))
            data['ratings'].append(get_ratings(prod_soup))

    flipkart_df = pd.DataFrame.from_dict(data)
    flipkart_df['price'] = flipkart_df['price'].str.replace('₹', '').str.replace(',', '')
    flipkart_df['prev_price'] = flipkart_df['prev_price'].str.replace('₹', '').str.replace(',', '')
    flipkart_df['price'].replace('', np.nan, inplace=True)
    flipkart_df['prev_price'].replace('', np.nan, inplace=True)
    flipkart_df['stars'].replace('', np.nan, inplace=True)

    flipkart_df['price'] = pd.to_numeric(flipkart_df['price'], errors='coerce')
    flipkart_df['prev_price'] = pd.to_numeric(flipkart_df['prev_price'], errors='coerce')
    flipkart_df['stars'] = pd.to_numeric(flipkart_df['stars'], errors='coerce')

    # flipkart_df['brand_name'] = flipkart_df['product_name'].apply(lambda x: x.split()[0])
    flipkart_df['brand_name'] = flipkart_df['product_name'].apply(lambda x: x.split()[0].title())


    flipkart_df['discount_%'] = flipkart_df['discount'].apply(clean_discount)
    flipkart_df['discount_%'].fillna(0, inplace=True)

    flipkart_df[['ratings', 'reviews']] = flipkart_df.apply(extract_ratings_reviews, axis=1)
    flipkart_df['ratings'] = pd.to_numeric(flipkart_df['ratings'], errors='coerce')
    flipkart_df['reviews'] = pd.to_numeric(flipkart_df['reviews'], errors='coerce')

    flipkart_df.to_csv('scraped_data.csv', index=False)

    return flipkart_df

def get_product_name(soup):
    try:
        title = soup.find('span', class_='VU-ZEz')
        title_value = title.text.strip()
    except AttributeError:
        title_value = ''
    
    return title_value

def get_price(soup):
    try:
        price = soup.find('div', class_='Nx9bqj CxhGGd')
        price_value = price.text.strip()
    except AttributeError:
        price_value = ''
    
    return price_value

def get_prev_price(soup):
    try:
        prev_price = soup.find('div', class_='yRaY8j A6+E6v')
        prev_price_value = prev_price.text.strip()
    except AttributeError:
        prev_price_value = ''
    
    return prev_price_value

def get_discnt(soup):
    try:
        discount = soup.find('div', class_='UkUFwK WW8yVX')
        discount_value = discount.text.strip()
    except AttributeError:
        discount_value = ''
    
    return discount_value

def get_stars(soup):
    try:
        rating = soup.find('div', class_='XQDdHH')
        rating_value = rating.text.strip()
    except AttributeError:
        rating_value = ''
    
    return rating_value

def get_specs(soup):
    try:
        rating = soup.find('div', class_='xFVion')
        rating_value = rating.text.strip()
    except AttributeError:
        rating_value = ''
    
    return rating_value

def get_delivery(soup):
    try:
        delivery = soup.find('span', class_='hcf08j').text.strip()
    except AttributeError:
        delivery = ''
    
    return delivery

def get_ratings(soup):
    try:
        ratings = soup.find('span', class_='Wphh3N').text.strip()
    except AttributeError:
        ratings = ''
    
    return ratings

def clean_discount(discount):
    if isinstance(discount, str) and 'off' in discount:
        return int(discount.split()[0].replace('%', ''))
    return None

def extract_ratings_reviews(row):
    ratings_reviews = row['ratings']
    ratings_match = re.search(r'(\d{1,3}(,\d{3})*) Ratings', ratings_reviews)
    reviews_match = re.search(r'(\d{1,3}(,\d{3})*) Reviews', ratings_reviews)
    
    if ratings_match:
        ratings = ratings_match.group(1).replace(',', '')
    else:
        ratings = None
    
    if reviews_match:
        reviews = reviews_match.group(1).replace(',', '')
    else:
        reviews = None
    
    return pd.Series([ratings, reviews])

if __name__ == '__main__':
    app.run(debug=True)