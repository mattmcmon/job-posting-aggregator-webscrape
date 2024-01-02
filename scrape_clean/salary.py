'''
95-888 C1
Group C4
    Matt McMonagle - mmcmonag
    Paris Chen - danyang2
    Yongbo Li - yongbol
    Yufei Lei - yufeilei

This module scrapes and cleans the salary information from salary.com
'''
# -*-coding:utf-8-*-
import requests
import csv
from bs4 import BeautifulSoup
import time

# csv file name
CSV_FILE_NAME = "data/salary.csv"
# csv title
CSV_TITLE = ["City", "Salary 10th Percentile (for the city)", "Salary 25th Percentile (for the city)", "Salary 50th Percentile (for the city)", "Salary 75th Percentile (for the city)", "Salary 90th Percentile (for the city)"]


def main():
    """
    Main Function
    :return:
    """
    save_csv(CSV_FILE_NAME, CSV_TITLE)
    cities = get_cities()
    for city_name, city_code in cities:
        data = [""] * len(CSV_TITLE)
        data[0] = city_name
        url = f"https://www.salary.com/tools/salary-calculator/data-scientist-i/{city_code}?type=base"
        soup = get_soup(url)
        table = soup.find("table", class_="table-chart")
        trs = table.find_all("tr")[1:]
        for tr in trs:
            tds = tr.find_all("td")
            td0_text = tds[0].get_text(strip=True)
            if td0_text.startswith("10th"):
                data[1] = tds[1].get_text(strip=True)
            elif td0_text.startswith("25th"):
                data[2] = tds[1].get_text(strip=True)
            elif td0_text.startswith("50th"):
                data[3] = tds[1].get_text(strip=True)
            elif td0_text.startswith("75th"):
                data[4] = tds[1].get_text(strip=True)
            elif td0_text.startswith("90th"):
                data[5] = tds[1].get_text(strip=True)
        print(data)
        save_csv(CSV_FILE_NAME, data)


def get_cities():
    """
    Get cities data
    :return:
    """
    url = "https://www.salary.com/research/salary/select-location"
    soup = get_soup(url)
    city_divs = soup.find_all("div", class_="sal-city-list")
    data = []
    for div in city_divs[1:]:
        links = div.find_all("a")
        for link in links:
            href = link.get("href")
            city_name = link.get_text(strip=True)
            city_code = href.split("/")[-1]
            data.append((city_name, city_code))
    return data


def get_soup(url):
    """
    Fetch html content
    :param url:
    :return:
    """
    try:
        time.sleep(5)
        response = requests.get(url, timeout=60, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        })
        if response.status_code != 200:
            raise Exception("Web request exception")
        response.encoding = "utf-8"
        text = response.text
        return BeautifulSoup(text, "html.parser")
    except Exception as e:
        print(e)
        return get_soup(url)


def save_csv(file_name, row):
    """
    Save data
    :param file_name:
    :param row:
    :return:
    """
    if not row:
        return
    with open(file_name, "a", encoding="utf-8-sig", newline="") as file:
        csv_write = csv.writer(file)
        csv_write.writerow(row)


if __name__ == '__main__':
    main()
