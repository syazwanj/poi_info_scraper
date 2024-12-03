import os
import dotenv
import requests
import logging
import json

# For reading in API Key
dotenv.load_dotenv(".env")

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": f"{os.environ.get('GOOGLE_MAPS_API_KEY')}",
    "X-Goog-FieldMask": "places.formattedAddress,places.displayName.text,places.nationalPhoneNumber,places.regularOpeningHours.periods,places.websiteUri",
}
request_url = "https://places.googleapis.com/v1/places:searchText"


def make_request(mall: str, poi: str) -> dict:
    """
    Only returns the first result that is obtained.

    By default, fields are: formattedAddress, displayName, nationalPhoneNumber, regularOpeningHours.periods, websiteUrl
    """
    timeout = 0.5  # in seconds
    query = f"Singapore {mall} {poi}"
    data = {"textQuery": query, "regionCode": "sg"}

    # Make the request
    print(f"Query: {query}. Making request to Google's Places API...")
    resp = requests.post(
        request_url,
        json=data,
        headers=headers,
    )
    resp.encoding = "utf-8"

    return resp.json()["places"][0]


# For testing
search_term = "Parkway Parade Challenger"
params = {
    "textQuery": search_term,
    "regionCode": "sg",
}


def main():
    print(f'API key: {headers["X-Goog-Api-Key"]}')
    resp = requests.post(request_url, json=params, headers=headers, timeout=1.0)
    resp.encoding = "utf-8"
    ans: dict = resp.json()
    for k, v in ans["places"][0].items():
        print(f"{k}: {v}")
    with open("places.json", "w", encoding="utf8") as fp:
        json.dump(ans, fp)


if __name__ == "__main__":
    main()
