import os

import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_xml_download_url(detail_url: str):
    return detail_url.replace("document", 'download_xml')


def download_xml(xml_location, detail_url):
    xml_download_url = get_xml_download_url(detail_url)
    xml_filename = xml_download_url.split('=')[1]
    xml_filename = os.path.join(xml_location, xml_filename)
    if os.path.exists(xml_filename):
        return xml_filename
    # print(xml_download_url)
    try:
        # Send GET request to get content
        response = requests.get(xml_download_url, timeout=10)  # Set timeout to avoid infinite waiting
        response.raise_for_status()  # Check if request is successful (status code 200)

        with open(xml_filename, "wb") as f:
            f.write(response.content)  # Write binary content
        print(f"File successfully downloaded to: {xml_filename}")
        return xml_filename
    except requests.exceptions.RequestException as e:
        return None


def crawl_frederick_delius_works(xml_location):
    works_data = []  # Store work data
    base_domain = "https://delius.music.ox.ac.uk/catalogue"
    for i in range(1, 8):
        url = f'https://delius.music.ox.ac.uk/catalogue/navigation.html?page={i}'
        try:
            # Send request to get page content
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Throw exception if status code is not 200
            response.encoding = response.apparent_encoding  # Automatically identify encoding

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            works = soup.select("div.results")
            # print(len(works))
            work_items = soup.find_all("div", class_="workListItem")
            for item in work_items:
                work_data = {}
                a_tag = item.find_parent("a")
                if a_tag and "href" in a_tag.attrs:
                    relative_href = a_tag["href"]
                    if relative_href.startswith("./"):
                        full_href = f"{base_domain}/{relative_href.lstrip('./')}"
                    elif relative_href.startswith("/"):
                        full_href = f"{base_domain}{relative_href}"
                    else:
                        full_href = relative_href
                    work_data["Detail Page Link"] = full_href
                else:
                    work_data["Detail Page Link"] = None
                xml_filename = download_xml(xml_location, work_data["Detail Page Link"])
                work_data["XML Filename"] = xml_filename
                print(work_data)
                works_data.append(work_data)
            print(len(work_items))
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except Exception as e:
            print(f"Error during crawling: {e}")
    return works_data
