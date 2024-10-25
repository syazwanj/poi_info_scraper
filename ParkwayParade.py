from scraper import StoreInfo
import requests
import os
from places_api_test import make_request

name = "ParkwayParade"
regenerate_directory_page = False
grab_store_images = False
need_selenium = False


class ParkwayParade(StoreInfo):
    def __init__(self):
        super().__init__(
            name, regenerate_directory_page, grab_store_images, need_selenium
        )
        self.base_url = "https://www.parkwayparade.com.sg/"
        self.all_stores_url = "opening-hours/"
        self.store_page_url = "store-directory/"

    def grab_store_links(self):
        store_links = [
            a["href"]
            for a in self.soup.find_all("a", href=True)
            if self.store_page_url in a["href"]
        ]

        return store_links

    # def grab_opening_hours(self):  # Old method
    #     hours_string = ""
    #     for day_row in self.store_soup.find_all(
    #         "div", class_="flex justify-between py-1"
    #     ):
    #         day = day_row.find_all("span")[0].get_text().strip()
    #         hours = day_row.find_all("span")[1].get_text().strip()
    #         hours_string = hours_string + f"{day}: {hours}\n"
    #     return hours_string

    def grab_description(self, *args, **kwargs):
        description = ""
        parent_div = self.store_soup.find("div", class_="rich-text")

        # Extracting all text from the parent div
        all_text = parent_div.get_text(separator="\n\n", strip=True).replace("â€™", "'")
        description = all_text

        return description

    # def grab_telephone(self, *args, **kwargs):
    #     telephone_info = "NIL"
    #     tel_link = self.store_soup.find("a", href=lambda x: x and x.startswith("tel:"))
    #     if tel_link:
    #         telephone_info = tel_link.get_text()

    #     return telephone_info

    def grab_store_images(self):
        # Step 1: Find the parent div or picture tag with unique attributes (like class)
        parent_div = self.store_soup.find(
            "div", class_="inline-block border border-solid border-brand p-4 md:w-full"
        )

        # Step 2: Inside the parent, find the specific img tag
        img_tag = parent_div.find("img")  # Locate the img tag inside the parent div

        # Step 3: Extract the image URL
        img_url = img_tag["src"]

        # Complete the URL if it is relative
        if img_url.startswith("/"):
            img_url = (
                self.base_url + img_url[1:]
            )  # self.base_url already has a trailing '/'

        # Step 4: Send a request to download the image
        response = requests.get(img_url)

        # Step 5: Save the image to a file (as PNG)
        image_save_folder = f"{self.mall_folder}/store-logos"
        if not os.path.exists(image_save_folder):
            os.mkdir(image_save_folder)
        if response.status_code == 200:
            with open(f"{image_save_folder}/{self.store_page_title}.png", "wb") as file:
                file.write(response.content)
            print(f"Image saved successfully as '{self.store_page_title}.png'.")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")


if __name__ == "__main__":
    parkway_parade = ParkwayParade()
    store_links = parkway_parade.grab_store_links()
    parkway_parade.visit_stores(store_links)
