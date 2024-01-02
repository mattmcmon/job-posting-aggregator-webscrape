'''
95-888 C1
Group C4
    Matt McMonagle - mmcmonag
    Paris Chen - danyang2
    Yongbo Li - yongbol
    Yufei Lei - yufeilei

This module does the following to clean H1B files:
1. Download the files.
2. Keep only essential columns: "EMPLOYER_NAME", "VISA_CLASS", and "JOB_TITLE".
3. Filter rows where "VISA_CLASS" values are "H-1B".
4. Filter rows where "JOB_TITLE" values contain specified keywords.
5. Clean "EMPLOYER_NAME" values using regular expressions.
'''
# Download H-1B files for the past three years
import requests

def h1b_scrape():
    url = "https://www.dol.gov/agencies/eta/foreign-labor/performance"
    file_urls = ["https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY2022_Q4.xlsx",
                "https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY2022_Q3.xlsx",
                "https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY2022_Q2.xlsx",
                "https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY2022_Q1.xlsx",
                ]

    for file_url in file_urls:
        # Send a GET request to each file URL
        response = requests.get(file_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract the file name from the URL
            file_name = file_url.split("/")[-1]

            # Save the file locally
            with open(f'data/{file_name}', 'wb') as file:
                file.write(response.content)
            print(f"{file_name} downloaded successfully!")
        else:
            print(f"Download failed for {file_url}. Status code: {response.status_code}")

    # Clean H-1B data for the last three years
    import pandas as pd
    import re
    import os

    # list of downloaded file names in files_list
    files_list = ["LCA_Disclosure_Data_FY2022_Q4.xlsx",
                "LCA_Disclosure_Data_FY2022_Q3.xlsx",  
                "LCA_Disclosure_Data_FY2022_Q2.xlsx",
                "LCA_Disclosure_Data_FY2022_Q1.xlsx"
                ]

    # Keywords for filtering in the 'JOB_TITLE' column
    keywords = ["Data", "Machine Learning", "ML", "AI", "Artificial Intelligence", 
                "Deep Learning", "Business Intelligence"]

    for file_name in files_list:
        # Read the Excel file
        df = pd.read_excel(f'data/{file_name}')

        # Keep only the specified columns and overwrite the original file
        df[['EMPLOYER_NAME', 'VISA_CLASS', 'JOB_TITLE']].to_excel(f'data/{file_name}', index=False)

        print(f"Columns selected and excess columns removed in {file_name}.")
    
        # (1) Filter rows based on the 'H1B' column value
        df = df[df['VISA_CLASS'] == 'H-1B']

        # (2) Filter rows based on 'JOB_TITLE' column containing specified keywords
        df = df[df['JOB_TITLE'].str.contains('|'.join(keywords), na=False, case=False)]
        
        # (3) Clean 'EMPLOYER_NAME' column
        df['EMPLOYER_NAME'] = df['EMPLOYER_NAME'].apply(lambda name: re.sub(r'[^a-z\s]', '', name.lower()))
        df['EMPLOYER_NAME'] = df['EMPLOYER_NAME'].apply(lambda name: re.sub(r'\b(?:llc|inc|corporation|platforms|bank|university|company|solutions|technologies|associates|limited|services)\b', '', name))

        # Keep only the specified columns and overwrite the original file
        df[['EMPLOYER_NAME', 'VISA_CLASS', 'JOB_TITLE']].to_excel(f'data/{file_name}', index=False)
        
        print(f"Operations completed for {file_name}.")

    # Combine all the updated files into a single dataframe
    # Placeholder for the list of dataframes
    dfs = []

    for modified_file_name in files_list:
        # Read the updated Excel file
        df = pd.read_excel(f'data/{modified_file_name}')

        # Append the dataframe to the list
        dfs.append(df)

    # Concatenate the dataframes into one
    final_df = pd.concat(dfs, ignore_index=True)

    # Save the final dataframe to a new Excel file
    final_df.to_excel("data/H1B_file.xlsx", index=False)

    print("Process completed. Combined modified files saved as H1B_file.xlsx")