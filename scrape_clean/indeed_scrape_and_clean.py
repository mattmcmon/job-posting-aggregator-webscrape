'''
95-888 C1
Group C4
    Matt McMonagle - mmcmonag
    Paris Chen - danyang2
    Yongbo Li - yongbol
    Yufei Lei - yufeilei

This is the module that scrapes and cleans the job data from Indeed.com
'''
# Used to export web scraped results to .csv
import csv
# Used for timing scraping to avoid being blocked from indeed.com
from time import sleep
# Used for randomizing timing 
from random import randint
# Used for web scraping
from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
# Allows searching through website
from selenium.webdriver.common.by import By
# Used for showing an error when a searched element doesn't exist
from selenium.common.exceptions import NoSuchElementException
# Used for creating DataFrames and data manipulation
import pandas as pd
# Used for regular expression
import re

def scrape():
    # Customize Chrome browser options
    option= webdriver.ChromeOptions()
    # Opens Chrome in incognito mode
    option.add_argument("--incognito")
    # Finding location, position, sorted by date and starting page (0)
    url = 'https://www.indeed.com/jobs?q={}&l={}&radius=35&filter=0&sort=date&start={}'
    # Ask for user input on what job they would like to search
    #job=input('What position are you looking for?\n')
    job = 'Data+Science'
    location=input('What location are you looking for jobs in (for example, "Pittsburgh, PA")?\n')
    # Reformat string that user inputs to replicate format of Indeed URL
    # job.replace(' ', '+')
    location = location.replace(' ', '+').replace(',', '')

    # Pass Chrome browser options from above
    driver = webdriver.Chrome(options=option)
    # Opens Indeed webpage based on the user's input
    driver.get(url.format(job,location,0))
    # Gets the total number of job postings from the HTML
    postings=driver.find_element(By.CLASS_NAME,'jobsearch-JobCountAndSortPane-jobCount').text
    # Removes the comma (if one exists) from the string of number of jobs
    for char in postings:
        if char == ',':
            postings = postings.replace(',','')
    # Calculates the number of iterable pages (# of jobs/15 per page)
    pages=int(postings.split(' ')[0])//15
    # If only one page of results, adjust pages variable to 1 (instead of 0)
    if pages == 0:
        pages += 1

    # Close the browser
    driver.quit() 
    # Outputs the number of pages found for the Indeed search result
    print('Number of job pages:',pages)

    # Create empty lists to store web scraped data
    job_list=[]
    job_description_list_href=[]
    salary_list=[]

    # Reopens Chrome to continue scraping each page of results
    driver = webdriver.Chrome(options=option)
    # Sleeps for a random interval to avoid Indeed from preventing access
    sleep(randint(1, 4))

    for num in range(0,pages):
        # Reopens broswer to each page of results and scrapes data
        driver.get(url.format(job,location,num*10))
        # Waits a random length of time
        sleep(randint(1, 3))
        # Returns first reference to data that matches ID for job cards
        job_page = driver.find_element(By.ID,"mosaic-jobResults")
        # Returns all the items matching class
        jobs = job_page.find_elements(By.CLASS_NAME,"job_seen_beacon")

        for val in jobs:
            # Name of each job posting
            job_title = val.find_element(By.CLASS_NAME,"jobTitle")   
            # Adds job posting information to job_list variable 
            job_list.append([job_title.text,
                            # URL to job posting on Indeed
                            job_title.find_element(By.CSS_SELECTOR,"a").get_attribute("href"),
                            # Name of company posting job
                            val.find_element(By.CLASS_NAME,"companyName").text,
                            # Location of company
                            val.find_element(By.CLASS_NAME,"companyLocation").text,
                            # Job posting date
                            val.find_element(By.CLASS_NAME,"date").text])
            try:
                # Adds salary information listed under class tag, if available
                salary_list.append(val.find_element(By.CLASS_NAME,"salary-snippet-container").text)
            except NoSuchElementException: 
                try:
                    # If salary not provided, search for tag that contains salary esitimate
                    salary_list.append(val.find_element(By.CLASS_NAME,"estimated-salary").text)
                except NoSuchElementException:
                    # If not estimate exists, append None
                    salary_list.append(None)

    # Create a loop to merge job_list and salary_list
    count = 0
    job_salary_list = []
    for job in job_list:
            job.append(salary_list[count]) 
            job_salary_list.append(job)
            count += 1

    # Write data extracted from Indeed to csv file called 'indeed_jobs'
    # Saved into same directory as this script
    with open('data/indeed_jobs.csv', 'wt', encoding = 'utf-8') as file:
        filewriter = csv.writer(file)
        filewriter.writerows(job_salary_list)

    # Close Chrome when finished
    driver.quit()

    # Alert user that searching has finished
    print("The application has finished searching for " 
          "job postings on Indeed.")

def clean():
    pd.options.display.float_format = '{:.2f}'.format

    def convert_min_salary(cell):
        if isinstance(cell, str) and 'K' in cell:
            return float(cell.replace('K','')) * 1000
        else:
            return float(cell)
        
    def convert_max_salary(cell):
        if isinstance(cell, str) and 'K' in cell:
            return float(cell.replace('K','')) * 1000
        else:
            return cell

    # Create header names for indeed dataframe
    headers = ['position', 'link', 'company', 'location', 'status', 'salary', 'company_cleaned']

    # Read indeed.com web scrape data for Data Science jobs in the US
    indeed = pd.read_csv('data/indeed_jobs.csv', names=headers)

    indeed = indeed[indeed['salary'].notna()]

    # Clean salary column of indeed data
    indeed['salary'] = indeed['salary'].str.replace('Estimated ', '', regex=True)
    indeed['salary'] = indeed['salary'].str.replace(' a year', '', regex=True)
    indeed['salary'] = indeed['salary'].str.replace('$', '')
    indeed['salary'] = indeed['salary'].str.replace(',', '', regex=True)

    # Create min and max salary dataframe to clean the data
    salary_ranges = indeed['salary'].str.split('-', expand=True)
    salary_ranges.columns = ['min_salary', 'max_salary']
    indeed = pd.concat([indeed, salary_ranges], axis=1)

    indeed = indeed[indeed['max_salary'].notna()]

    
    # # Clean min salary column
    indeed['min_salary'] = indeed['min_salary'].str.replace(',', '', regex=True)
    indeed['min_salary'] = indeed['min_salary'].str.replace('From ', '', regex=True)
    indeed['min_salary'] = indeed['min_salary'].str.replace('Up to ', '', regex=True)
    indeed['min_salary'] = indeed['min_salary'].apply(convert_min_salary)

    # Clean max salary column
    indeed['max_salary'] = indeed['max_salary'].str.replace(',', '', regex=True)
    indeed['max_salary'] = indeed['max_salary'].str.replace('From ', '', regex=True)
    indeed['max_salary'] = indeed['max_salary'].str.replace('Up to ', '', regex=True)
    indeed['max_salary'] = indeed['max_salary'].apply(convert_max_salary)

    hourly_idx = 0
    monthly_idx = 0
    for cell in indeed['max_salary']:
        if isinstance(cell, str) and ' an hour' in cell:
            hourly_idx = indeed[indeed['max_salary'] == cell].index
            indeed.loc[hourly_idx,'max_salary'] = indeed.loc[hourly_idx,'max_salary'].str.replace(' an hour', '').astype(float) * 40 * 52
            indeed.loc[hourly_idx,'min_salary'] = indeed.loc[hourly_idx,'min_salary'].astype(float) * 40 * 52

        if isinstance(cell, str) and ' a month' in cell:
            monthly_idx = indeed[indeed['max_salary'] == cell].index
            indeed.loc[monthly_idx,'max_salary'] = indeed.loc[monthly_idx,'max_salary'].str.replace(' a month', '').astype(float) * 12
            indeed.loc[monthly_idx,'min_salary'] = indeed.loc[monthly_idx,'min_salary'].astype(float) * 12

    # Convert company names to lowercase and remove special characters for ease of merging data
    special_chars = r"[,.!@#$%^&*()-=+'?:;]"

    indeed['company_cleaned'] = indeed['company'].str.lower().replace(special_chars, '', regex=True)

    df_index = 0
    for cell in indeed['company_cleaned']:
        if re.search(r'.*llc', cell) != None:
            df_index = indeed[indeed['company_cleaned'] == cell].index
            indeed.loc[df_index, 'company_cleaned'] = cell.replace(' llc', '')
        
        if re.search(r'.*inc', cell) != None:
            df_index = indeed[indeed['company_cleaned'] == cell].index
            indeed.loc[df_index, 'company_cleaned'] = cell.replace(' inc', '')

        if re.search(r'.*corporation', cell) != None:
            df_index = indeed[indeed['company_cleaned'] == cell].index
            indeed.loc[df_index, 'company_cleaned'] = cell.replace(' corporation', '')


    # create dataframe for splitting location into separate city and state columns
    location_df = indeed['location'].str.split(',', expand=True)
    location_df.columns = ['city', 'state']
    location_df['state'] = location_df['state'].fillna('')

    df_index = 0
    zip_pat = r' [^0-9]*.*$'
    for cell in location_df['state']:
        if re.search(zip_pat, cell) != None:
            df_index = location_df[location_df['state'] == cell].index
            cell = str(cell).strip()
            location_df.loc[df_index, 'state'] = cell.split(' ')[0]
    
    # Combine the re-formatted location data to the indeed dataframe
    indeed = pd.concat([indeed, location_df], axis=1)

    # Remove duplicate job postings in DataFrame
    indeed = indeed.drop_duplicates()

    # Output cleaned DataFrame to CSV file
    indeed.to_csv('data/cleaned_data_science_indeed.csv')

    # Display to user that data has been cleaned
    print("Indeed data has been cleaned.\n")

if __name__ == "__main__":
    scrape()
    clean()