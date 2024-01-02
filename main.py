'''
95-888 C1
Group C4
    Matt McMonagle - mmcmonag
    Paris Chen - danyang2
    Yongbo Li - yongbol
    Yufei Lei - yufeilei

This is the main file that will import all necessary modules 
(including the ones that we've created). This file can be run in your IDE
of choice. Follow the on-screen prompts (type the number on-screen for the
option you would like to select). This will display recommended Data Science 
jobs in the United States.
'''
# Used to access functions for scraping and cleaning Indeed.com
import scrape_clean.indeed_scrape_and_clean as isc
import scrape_clean.H1B_cleaned as h1b
import scrape_clean.property_prices_scrape_and_clean as prop
import scrape_clean.salary as sal
# Used to merge data
import merged_all as ma
# Show stats of dataset
import statistical_results as sr
# Used for creating DataFrames and data manipulation
import pandas as pd
# Used to exit program when user chooses
import sys
import os

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 150)

# Prompt user with options, then display
def show_options(job_merge):
    user_feedback = False
    while user_feedback == False:
        print("Would you like to add any of the following filters? Please select a number below:\n")
        user_filter_input = input('1. No filters\n'
                            '2. Companies offering H1B sponsorship\n'
                            '3. Remote jobs\n'
                            '4. Show job salary statistics\n'
                            '5. Quit\n'
                            '> ')
        if user_filter_input == "1":
            pass
            user_feedback = True
        elif user_filter_input == "2":
            job_merge = job_merge[job_merge['H1B'] == "Yes"]
            user_feedback = True
        elif user_filter_input == "3":
            job_merge = job_merge[job_merge['location'].str.contains('remote', case=False)]
            user_feedback = True
        elif user_filter_input == "4":
            sr.stat_salary_dist(job_merge)
        elif user_filter_input == "5":
            print("Thank you for using CareerMagnet. Have a great day!")
            sys.exit()
        else:
            print('\nInvalid input. Please type a number between 1 and 5.\n')
    return job_merge

# Sort job data based on minimum salary and show top 5 results
def sort_and_show(job_merge):
    sorted_jobs = job_merge.sort_values(by='min_salary', ascending=False)
    sorted_jobs = sorted_jobs.reset_index()
    sorted_jobs = sorted_jobs.loc[:,['position', 'company', 'location', 'salary', 
                                        'Salary 50th Percentile (for the city)', 
                                        'Price To Income Ratio','H1B', 'link']]
    print("\nHere are the top 5 positions based on minimum salary:\n")
    print(sorted_jobs.loc[0: 4])
    return sorted_jobs

# Allow user to display more positions if top 5 aren't sufficient
def show_more_jobs(sorted_jobs):
    show_jobs = True
    min_row = 0
    max_row = 4
    while show_jobs == True:
        more_jobs = input("Would you like to see more jobs (Y/N)?\n"
                            "> ")
        if more_jobs.lower() == "y":
            min_row += 5
            max_row += 5
            print("\nHere are the next 5 best positions based on minimum salary:\n")
            print(sorted_jobs.loc[min_row: max_row])
        elif more_jobs.lower() == "n":
            show_jobs = False
            print("Thank you for using CareerMagnet. Have a great day!")
        else:
            print("Incorrect input. Please type Y or N.")

# Display welcome message and info
print("\nWelcome to CareerMagnet, a job finder for Data Science-related professions."
      "\nOur application gathers data from Indeed.com, numbeo.com, salary.com, & dol.gov"
      "\nto provide a more complete job hunting experience for positions in Data Science.")
# Warn user of lengthy webscraping process
print("\nNOTE: If you choose to download live data,"
      "\nthe processing could take around 2-3 hours, depending on the jobs available in the"
      "\nlocation that you select. Doing a download of live data will also open and close"
      "\nyour browser. Additionally, The H1B sponsorship data is for last year"
      "\nso information may have changed.")
# Prompt user to see if they would like to use cached job data or download fresh
bad_response = True
while bad_response:
    try:
        user_download_resp = input("\nWould you like to download fresh job data or use the existing data? "
                            "Select by typing 1, 2, or 3 below:\n"
                            "\n1. Download"
                            "\n2. Use existing data"
                            "\n3. Quit\n"
                            "> ")
        response = int(user_download_resp)
    except:
        print('\nInvalid input. Please enter 1, 2, or 3.\n')
        resoponse = -1
    if response == 1:
        user_download_resp = "1"
        bad_response = False
    elif response == 2:
        user_download_resp = "2"
        bad_response = False
    elif response == 3:
        # Exits program
        print("Thank you for using CareerMagnet. Have a great day!")
        sys.exit()
    else:
        print("\nInvalid input.  Please enter 1, 2, or 3.")
        pass
    
# Re-confirm the user would like to download fresh data - web scraping can take over an hour
if user_download_resp == "1":
    bad_response = True
    while bad_response == True:
        user_confirm = input("Are you sure you would like to download? This could take an 2-3 hours,"
                                " depending on number of jobs offered in the chosen location."
                                "\n1. Yes, scrape and download."
                                "\n2. No, use existing data."
                                "\n3. Quit.\n"
                                "> ")
        if user_confirm == "1":
            user_download_resp = "1"
            bad_response = False
        elif user_confirm == "2":
            user_download_resp = "2"
            bad_response = False
        elif user_confirm == "3":
            # Exits program
            print("Thank you for using CareerMagnet. Have a great day!")
            sys.exit()
        else:
            print('Invalid input. Please enter a number 1-3.\n')

# Loop until user provides valid response
bad_response = True
while bad_response == True:
    # Scrape and merge data, then sort and display to user
    if user_download_resp == "1":
        # Scrape and clean indeed.com
        isc.scrape()
        isc.clean()
        # Scrape and clean property info from numbeo.com
        prop.poperty_scrape()
        # Scrape and clean h1b sponsorship info from DOL.gov
        h1b.h1b_scrape()
        # Scrape and clean data from salary.com
        sal.main()
        # Merge all the above scraped data into one file
        ma.merge()
        # Store merged data into Dataframe
        job_merge = pd.read_csv('data/merged_all.csv')
        show_jobs = show_options(job_merge)
        sorted_jobs = sort_and_show(show_jobs)
        show_more_jobs(sorted_jobs)
        bad_response = False
    # Sort and display already downloaded data for the user
    elif user_download_resp == "2":
        job_merge = pd.read_csv('data/cached_merged_data.csv')
        show_jobs = show_options(job_merge)
        sorted_jobs = sort_and_show(show_jobs)
        show_more_jobs(sorted_jobs)
        bad_response = False
    # Exit application
    elif user_download_resp == "3":
        print("Thank you for using CareerMagnet. Have a great day!")
        sys.exit()
    # Display error for invalid input
    else:
        print("Invalid input. Please enter a valid choice (1, 2, or 3):\n")

salary_csv = 'data/salary.csv'
if os.path.exists(salary_csv):
    # Use os.remove() to delete the file
    os.remove(salary_csv)
