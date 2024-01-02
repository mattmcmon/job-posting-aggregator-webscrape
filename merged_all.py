'''
95-888 C1
Group C4
    Matt McMonagle - mmcmonag
    Paris Chen - danyang2
    Yongbo Li - yongbol
    Yufei Lei - yufeilei

This module contains the code to merge all of the web scraped data
'''
### Warning: takes 2-25 minutes to run, depending on the city ###

import pandas as pd
import csv
import os
import numpy as np
import difflib
import warnings

def merge():
    # Read the CSV files
    salary_df = pd.read_csv("data/salary.csv")
    data_scientist_df = pd.read_csv("data/cleaned_data_science_indeed.csv")
    property_prices_df = pd.read_csv("data/property_prices.csv")
    
    salary_df.columns= ["City", "Salary 10th Percentile (for the city)", "Salary 25th Percentile (for the city)", 
                        "Salary 50th Percentile (for the city)", "Salary 75th Percentile (for the city)", 
                        "Salary 90th Percentile (for the city)"]

    # Format data_scientist_df
    # Drop first column
    data_scientist_df = data_scientist_df.iloc[:,1:]
    # Drop identical rows based on specific columns
    data_scientist_df = data_scientist_df.drop_duplicates(subset=['position', 'company_cleaned', 'city', 'status', 'min_salary', 'max_salary'])
    # Reset the index after dropping rows
    data_scientist_df = data_scientist_df.reset_index(drop=True)

    # Format property_prices_df
    # Remove some columns in property_prices_df:
    property_prices_df = property_prices_df.iloc[:,:-1]
    selected_columns = ['City', 'Price To Income Ratio']
    property_prices_df = property_prices_df[selected_columns]
    
    # Format salary_df
    # add Remote row in salary_df and property_prices_df
    salary_df.loc[len(salary_df)] = ["Remote"] + ["0.00"] * (len(salary_df.columns) - 1)
    property_prices_df.loc[len(property_prices_df)] = ["Remote"] + ["0.00"] * (len(property_prices_df.columns) - 1)

    # keep the avg salary of each city
    columns_to_convert = salary_df.columns[1:]
    salary_df[columns_to_convert] = salary_df[columns_to_convert].replace('[\$,]', '', regex=True).astype(float)
    salary_df = salary_df.groupby('City').mean().reset_index()

    # Ensure the "city" column in the 3 dataframes is in the same format (e.g., all lower case) before merging
    # add lowercase city names (including remote)to the last column
    salary_df['City'] = salary_df['City'].str.lower()
    data_scientist_df['city'] = data_scientist_df['city'].str.lower()
    property_prices_df['City'] = property_prices_df['City'].str.lower()

    # Merge the first two dataframes using the 'city' column
    merged_df = pd.merge(data_scientist_df, salary_df, left_on='city', right_on='City', how='left')
    # Drop rows with NaN values in the "Position" column
    merged_df = merged_df.dropna(subset=['position'])
    merged_df = merged_df.fillna("Not Applicable")
    # Reset the index after dropping rows
    merged_df = merged_df.reset_index(drop=True)

    # Merge the property price dataframe using the 'city' column
    merged_df = pd.merge(merged_df, property_prices_df, left_on='city', right_on='City', how='left')
    # Drop rows with NaN values in the "Position" column
    merged_df = merged_df.dropna(subset=['position'])
    merged_df = merged_df.fillna("Not Applicable")
    # Reset the index after dropping rows
    merged_df = merged_df.reset_index(drop=True)
    

    # Load the H1B_file.xlsx file
    H1B_df = pd.read_excel("data/H1B_file.xlsx")

    # Add a new column 'H1B' to the cleaned dataframe
    merged_df['H1B'] = 'No'  # Default value is 'No'

    # Function to find the best match for each company
    def find_best_match(company_name):
        ratios = H1B_df['EMPLOYER_NAME'].apply(lambda x: difflib.SequenceMatcher(None, x, company_name).ratio())
        best_match_index = ratios.idxmax()
        best_match_ratio = ratios[best_match_index]
        return H1B_df.at[best_match_index, 'EMPLOYER_NAME'], best_match_ratio

    # Apply the function to the 'company_cleaned' column
    merged_df['H1B'] = merged_df['company_cleaned'].apply(
        lambda x: 'Yes' if find_best_match(x)[1] >= 0.7 else 'No'
    )

    # Drop unnecessary columns
    merged_df = merged_df.drop(['Best_Match', 'Similarity_Ratio'], axis=1, errors='ignore')
    
    # Save the updated dataframe to a new CSV file
    merged_df.to_csv("data/merged_all.csv", index=False)
    print("Updated merged_all CSV is written.")

if __name__ == "__main__":
    merge()