from scraper import StoreInfo
import requests
import os
import json

name = "PLQMall"
regenerate_directory_page = False
grab_store_images = True
need_selenium = False


class PLQMall(StoreInfo):
    def __init__(self):
        self.base_url = "https://www.payalebarquarter.com/"
        self.all_stores_url = "directory/mall/?"
        self.store_page_url = "directory/mall/"
        super().__init__(
            name, regenerate_directory_page, grab_store_images, need_selenium
        )

    def grab_store_links(self):
        # Extract the JSON-like string inside the v-bind attribute
        v_bind_data = self.soup.find("directory")["v-bind"]

        # Convert it back to valid JSON
        json_data = json.loads(v_bind_data.replace("&quot;", '"'))
        # with open("example.json", "w") as fp:
        #     json.dump(json_data, fp)

        # Extract all the links that contain '/store-directory/'
        store_links = [
            entity["link"]
            for entity in json_data["allEntities"]
            if self.store_page_url in entity["link"]
        ]

        # Print the extracted links
        # print(store_links)

        return store_links

    # def grab_opening_hours(self):
    #     hours_string = ""
    #     for day_row in self.store_soup.find_all(
    #         "div", class_="flex justify-between py-1"
    #     ):
    #         day = day_row.find_all("span")[0].get_text().strip()
    #         hours = day_row.find_all("span")[1].get_text().strip()
    #         hours_string = hours_string + f"{day}: {hours}\n"
    #     return hours_string

    def grab_description(self):
        description = ""
        parent_div = self.store_soup.find("div", class_="rich-text")
        desc_div = parent_div.find("div", class_="hidden md:block")

        # Extracting all text from the parent div
        try:
            all_text = desc_div.get_text(separator=r"\n\n", strip=True).replace(
                "â€™", "'"
            )
            description = all_text
        except AttributeError:
            description = "NIL"

        return description

    # def grab_telephone(self):
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
    plq = PLQMall()
    store_links = plq.grab_store_links()
    plq.visit_stores(store_links, heading_class="text-brand-heading")
