from bs4 import BeautifulSoup
from numpy import source
import pandas as pd

import requests

url = "https://www.amazon.com/MSI-Thin-Bezel-Quad-Core-i5-10300H-Keyboard/dp/B098JFL5DK"


def get_product_details(product_amazon_url):
    """
    takes url, 
    return : dictionary of product details
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/ 537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    
    resp = requests.get(product_amazon_url, headers=headers)
    s = BeautifulSoup(resp.content, features="lxml")

    soup = BeautifulSoup(resp.content, 'html.parser')
    img_results = soup.find_all('div', {'class': 'imgTagWrapper'})
    
    try:
        img_url = img_results[0].img['src']
    except:
        img_url = "Not available"

    #print(img_url)
    results2 = soup.find_all('span', {'class': 'a-icon-alt'})
    #rating = results2[0].text
    
    

    product_details = {}
    product_details['image_url'] = img_url
    #product_details['rating'] = rating
    


    
    table_data = s.find('table', id="productDetails_techSpec_section_1") #class_="a-keyvalue prodDetTable"
    rows = table_data.find_all('tr')

    

    for i in rows:
        td = i.find('td')
        th = i.find('th')
        td_text = td.text.encode("ascii", "ignore")
        td_text = td_text.decode().strip()
        th_text = th.text.strip()
        product_details[th_text] = td_text    
    
    #print(type(product_details))

    return product_details
    
    
    
   



if __name__ == "__main__":
    products = []
    product_search_results_df = pd.read_csv(r"tv_pagelist3.csv")
    # iterate row in
    for i, product_row in product_search_results_df.iterrows():
        product_url = product_row["product_url"]
        product_details_dict = get_product_details(product_url)

        
        print("new details", product_details_dict, "\n\n")
        # update row, with abo dict
        product_row = dict(product_row)
        product_details_dict.update(product_row)
        products.append(product_details_dict)
        #print(product_url, "done..")
    
    
    # convert it to df , and store

    products_df_wide = pd.DataFrame(products)
    products_df_wide.to_csv("detailed_tv_120_3.csv")
