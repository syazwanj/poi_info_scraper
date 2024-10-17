import os
import requests
import time
import csv
from bs4 import BeautifulSoup

base_url = "https://www.parkwayparade.com.sg/opening-hours/"


def grab_store_links(soup: BeautifulSoup, url_format: str) -> list[str]:
    store_links = [a['href'] for a in soup.find_all(
        'a', href=True) if url_format in a['href']]

    return store_links


def grab_opening_hours(store_soup):
    hours_string = ""
    for day_row in store_soup.find_all('div', class_="flex justify-between py-1"):
        day = day_row.find_all('span')[0].get_text().strip()
        hours = day_row.find_all('span')[1].get_text().strip()
        hours_string = hours_string + f"{day}: {hours}\n"
    return hours_string


def grab_description(store_soup):
    description = ""
    parent_div = store_soup.find('div', class_="rich-text")

    # Extracting all text from the parent div
    all_text = parent_div.get_text(
        separator="\n\n", strip=True).replace("â€™", "'")
    description = all_text
    # paragraphs = [p.get_text().replace('â€œ', '“').replace('â€', '”')
    #               for p in parent_div.find_all('p')]
    # description = "\n\n".join(paragraphs)

    return description


def grab_telephone(store_soup):
    telephone_info = "NIL"
    tel_link = store_soup.find('a', href=lambda x: x and x.startswith("tel:"))
    if tel_link:
        telephone_info = tel_link.get_text()

    return telephone_info


def visit_store(store_links: list[str], store_base_url="https://www.parkwayparade.com.sg"):
    store_links = store_links[1:-1]
    print(store_links)
    time.sleep(2)

    # Open csv file in append mode or create the file if it doesn't exist
    csv_filename = "store_info_pp.csv"

    with open(csv_filename, mode='a', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Check if file is empty
            # write header
            writer.writerow(["Store", "Description", "Telephone", "Hours"])

    # Visit the links
    all_stores = {}
    for store in store_links:
        all_stores[store] = {}
        print(f"Visiting {store}")
        try:
            store_page = requests.get(f"{store_base_url}{store}")
            # print(store_page.headers.get('Content-Type'))
            store_page.encoding = 'utf-8'
            store_soup = BeautifulSoup(store_page.content, "html.parser")
        except:
            print("Unable to visit " + store)
            continue

        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            hours_string = grab_opening_hours(store_soup)
            description = grab_description(store_soup)
            telephone = grab_telephone(store_soup)
            writer.writerow([store, description, telephone, hours_string])
        time.sleep(0.5)


def main(mode=0):
    if not os.path.exists("page.html"):
        page = requests.get(base_url)
        soup = BeautifulSoup(page.content, "html.parser")
        with open("page.html", "wb") as f:
            f.write(page.content)
    else:
        with open("page.html", "r") as f:
            soup = BeautifulSoup(f, "html.parser")

    if mode == 1:
        store_links = grab_store_links(soup, "/store-directory/")
        visit_store(store_links)


if __name__ == "__main__":
    main(mode=1)
