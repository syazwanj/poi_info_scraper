import os
import requests
import time
import csv
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from places_api_test import make_request
from utils import format_grouped_opening_hours, parse_opening_hours

# base_url = "https://www.parkwayparade.com.sg/opening-hours/"


class StoreInfo:
    def __init__(
        self, name, regenerate_directory_page, will_grab_store_images, need_selenium
    ):
        self.name = name  # CSV will be named Store_Info_<name>.csv
        self.store_info_csv_name = f"Store_Info_{self.name}.csv"
        # self.base_url = "https://www.parkwayparade.com.sg/"
        # self.all_stores_url = "opening-hours/"
        # self.store_page_url = "store-directory/"
        self.all_stores_csv_name = f"{self.name}_Directory.csv"
        self.store_soup = None

        # For web scraping
        self.need_selenium = need_selenium
        self.regenerate_directory_page = regenerate_directory_page
        self.will_grab_store_images = will_grab_store_images

        # Storing results
        self.mall_folder = f"./output/{self.name}"

    def run_init_checks(self):
        self.check_mall_folder_exists()
        self.check_directory_page_exists()

    def check_mall_folder_exists(self):
        if not os.path.exists(self.mall_folder):
            os.makedirs(self.mall_folder)

    def check_directory_page_exists(self):
        directory_html_page = f"{self.mall_folder}/{self.name}.html"
        if not os.path.exists(directory_html_page) or self.regenerate_directory_page:
            if self.need_selenium:
                pass
            else:
                page = requests.get(f"{self.base_url}{self.all_stores_url}")
                self.soup = BeautifulSoup(page.content, "html.parser")
                with open(directory_html_page, "wb") as fp:
                    fp.write(page.content)
        else:
            with open(directory_html_page, "r") as fp:
                self.soup = BeautifulSoup(fp, "html.parser")

    def save_scraped_data(self, **kwargs):
        # set 'image' as kwarg to save store images.
        # All other kwargs will be saved into csv file
        headings = [k for k in kwargs.keys() if k != "image"]
        data = [i for i in kwargs.values()]

        with open(
            f"{self.mall_folder}/StoreInfo_{self.name}.csv",
            mode="a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # Check if file is empty
                # Write header
                writer.writerow(headings)

            # Write content
            writer.writerow(data)

    def visit_stores(self, store_links: list[str], heading_class: str = "page-title"):
        # Perform some filtering to ensure we don't include bare domains
        store_links = [
            url for url in store_links if url.lstrip("/") != self.store_page_url
        ]
        # store_links = store_links[54:]
        self.store_page_title = ""
        print("\n".join(store_links))
        print(f"Total stores: {len(store_links)}")
        time.sleep(2)

        # Visit the links
        for index, store in enumerate(store_links, start=1):
            print(f"Visiting {store} | {index} of {len(store_links)}")
            try:
                store_page = requests.get(f"{self.base_url}{store}")
                store_page.encoding = "utf-8"
                self.store_soup = BeautifulSoup(
                    store_page.content, "html.parser")
                self.store_page_title = (
                    self.store_soup.find(class_=heading_class)
                    .get_text()
                    .strip()
                    .replace("/", "-")
                )
            except ConnectionError:
                print("Unable to visit" + store)
                continue

            # Make the request to the places API
            google_poi_info = self.make_places_api_request()

            # Check that the info is for the correct place
            API_location_response = f'{google_poi_info["displayName"]["text"]} - {google_poi_info["formattedAddress"]}'

            hours_string = self.grab_opening_hours(
                places_poi_info=google_poi_info)
            description = self.grab_description()
            telephone = self.grab_telephone(places_poi_info=google_poi_info)
            website = self.grab_website(places_poi_info=google_poi_info)
            if self.will_grab_store_images:
                self.grab_store_images()
            self.save_scraped_data(
                Store=self.store_page_title,
                Description=description,
                Website=website,
                Telephone=telephone,
                Hours=hours_string,
                APIResponse=API_location_response,
            )

    def grab_store_links(self, *args, **kwargs):
        pass

    def grab_opening_hours(self, *args, **kwargs):
        if "places_poi_info" in kwargs.keys():
            try:
                opening_hours_json = kwargs["places_poi_info"]["regularOpeningHours"]
                opening_hours_dict = parse_opening_hours(opening_hours_json)
                opening_hours_grouped = format_grouped_opening_hours(
                    opening_hours_dict)

                return opening_hours_grouped
            except KeyError:
                print("Unable to retrieve value for", self.store_page_title)

        return "NIL"

    def grab_description(self):
        pass

    def grab_telephone(self, *args, **kwargs):
        telephone_nos = []
        # # From website
        # tel_link = self.store_soup.find("a", href=lambda x: x and x.startswith("tel:"))
        # if tel_link:
        #     dir_telephone_info = tel_link.get_text()
        #     telephone_nos.append(f"{dir_telephone_info} (Directory)")

        # From API
        if "places_poi_info" in kwargs.keys():
            google_telephone_info = "+65 " + kwargs["places_poi_info"].get(
                "nationalPhoneNumber", "NIL"
            )
            if "NIL" not in google_telephone_info:
                telephone_nos.append(google_telephone_info)

        if telephone_nos:
            return "/".join(telephone_nos)

        return ""

    def grab_website(self, *args, **kwargs):
        if "places_poi_info" in kwargs.keys():
            return kwargs["places_poi_info"].get("websiteUri", "NIL")

        return "NIL"

    def grab_store_images(self):
        pass

    def make_places_api_request(self):
        resp = make_request(self.name, self.store_page_title)

        return resp


def main(mode=0):
    # if not os.path.exists("page.html"):
    #     page = requests.get(base_url)
    #     soup = BeautifulSoup(page.content, "html.parser")
    #     with open("page.html", "wb") as f:
    #         f.write(page.content)
    # else:
    #     with open("page.html", "r") as f:
    #         soup = BeautifulSoup(f, "html.parser")

    # if mode == 1:
    #     store_links = grab_store_links(soup, "/store-directory/")
    #     visit_store(store_links)
    pass

    # Visit stores


if __name__ == "__main__":
    main(mode=1)
