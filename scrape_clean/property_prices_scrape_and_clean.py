'''
95-888 C1
Group C4
    Matt McMonagle - mmcmonag
    Paris Chen - danyang2
    Yongbo Li - yongbol
    Yufei Lei - yufeilei

This module scrapes and cleans the property price information from numbeo.com
'''

#!/usr/bin/env python
# coding: utf-8

### Scrape  https://www.numbeo.com/property-investment/country_result.jsp?country=United+States

import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
import numpy as np

# os.chdir("D:/WODEWENJIAN/CMU Fall since 0928/Python/Group Project")
def poperty_scrape():
    # Send a GET request to the URL
    url = "https://www.numbeo.com/property-investment/country_result.jsp?country=United+States"
    response = requests.get(url)

    # Create a Beautiful Soup object
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table with id "t2"
    table = soup.find("table", id="t2")

    # Extract the data from the table
    rows = table.find_all("tr")

    # Extract column names
    column_names = [
        'City',
        'Price To Income Ratio',
        'Gross Rental Yield City Center',
        'Gross Rental Yield Outside of Center',
        'Price To Rent Ratio City Center',
        'Price To Rent Ratio Outside Of City Center',
        'Mortgage As A Percentage Of Income',
        'Affordability Index'
    ]

    # Create a DataFrame to store the table data
    data = []
    for row in rows:
        cells = row.find_all("td")
        row_data = [cell.text.strip() for cell in cells[1:]]  # Exclude the first column
        data.append(row_data)

    df = pd.DataFrame(data, columns=column_names)
    df=df[1:]
    # Split the "City" column into "City" and "State" columns
    df[['City', 'State']] = df['City'].str.split(', ', n=1, expand=True)
    # Reorder the columns
    df = df[['City', 'State'] + list(df.columns[1:-1]) + [df.columns[-1]]]
    df = df.iloc[:, :-1]

    # Save the DataFrame to a CSV file
    df.to_csv("data/property_prices.csv", index=False)

    print("Successfully donwloaded property price data and saved to CSV.")