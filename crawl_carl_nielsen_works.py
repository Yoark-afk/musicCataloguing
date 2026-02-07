import os
import requests
from bs4 import BeautifulSoup
import csv
import time

# Target URL
base_url = "https://www.kb.dk/dcm/cnw/index.xq"
# Request headers (simulate browser visit to avoid anti-crawling)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_xml_download_url(detail_url):
    """Extract the actual download link of the XML file from the detail page"""
    try:
        response = requests.get(detail_url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")

        # Find XML download button (locate by button text and link characteristics)
        xml_button = soup.select_one("a[href*='download'][href*='xml'], a[href*='DOWNLOAD'][href*='XML']")
        if not xml_button:
            # Alternative selector: adjust according to page structure (if above search fails, try this)
            xml_button = soup.select_one("a[href*='download.xq'][href*='format=xml']")

        if not xml_button:
            print(f"XML download link not found: {detail_url}")
            return None

        # Extract and complete the download link
        xml_relative_url = xml_button["href"]
        if xml_relative_url.startswith("http"):
            return xml_relative_url
        elif xml_relative_url.startswith("/"):
            return f"https://www.kb.dk{xml_relative_url}"
        else:
            return f"https://www.kb.dk/dcm/cnw/{xml_relative_url.lstrip('./')}"

    except requests.exceptions.RequestException as e:
        print(f"Detail page request failed ({detail_url}): {e}")
        return None
    except Exception as e:
        print(f"Failed to extract XML link ({detail_url}): {e}")
        return None


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
    return None


def crawl_carl_nielsen_works(xml_location):
    works_data = []  # Store work data
    i = 1
    while i < 24:
        local_works_data = []
        url = f'https://www.kb.dk/dcm/cnw/index.xq?page={i}&itemsPerPage=20&sortby=null%2Cwork_number'
        try:
            # Send request to get page content
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Throw exception if status code is not 200
            response.encoding = response.apparent_encoding  # Automatically identify encoding

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Find work list (adjust selector according to page structure, assuming works are in table or specific container)
            # Note: Actually need to modify selector according to real DOM structure of the page, the following is a general example
            works = soup.select("table.result_table")  # Assuming works are in table rows

            for idx, work in enumerate(works[:], 1):  # Skip header row
                work_data = {}
                # Extract CNW number (adjust according to page structure)
                cnw_number = work.select_one("td:nth-child(1)").get_text(strip=True) if work.select_one("td:nth-child(1)") else ""
                work_data["CNW Number"] = cnw_number
                # Extract work title (Danish + English)
                title_elem = work.select_one("td:nth-child(2)")
                if title_elem:
                    title_text = title_elem.get_text(strip=True, separator=" | ")
                    # work_data["Work Title"] = title_text

                    onclick_attr = work.get("onclick", "")
                    if "location.href='" in onclick_attr:
                        relative_link = onclick_attr.split("'")[1]  # Extract './document.xq?n=xx' part
                        root_domain = "https://www.kb.dk/dcm/cnw"
                        absolute_link = f"{root_domain}/{relative_link.lstrip('./')}"  # Concatenate into complete URL
                        work_data["Detail Page Link"] = absolute_link
                        xml_filename = download_xml(xml_location, absolute_link)
                        work_data["XML Filename"] = xml_filename
                if work_data["Detail Page Link"] and work_data["XML Filename"]:
                    local_works_data.append(work_data)
                    print(work_data)
                else:
                    raise Exception
                # if work_data.get("Work Title") and work_data.get("Detail Page Link"):
                #     works_data.append(work_data)
                #     print(f"Scraped {cnw_number}: {work_data['Work Title']}")
                #     print(work_data)
                time.sleep(0.5)  # Delay to avoid being blocked due to too fast requests
            works_data.extend(local_works_data)
            i += 1
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except Exception as e:
            # print(f"Error during crawling: {e}")
            continue
    # # Save data to CSV file
    # with open("carl_nielsen_works.csv", "w", newline="", encoding="utf-8-sig") as f:
    #     fieldnames = ["CNW Number", "Work Title", "Detail Page Link", 'XML Filename']
    #     writer = csv.DictWriter(f, fieldnames=fieldnames)
    #     writer.writeheader()
    #     writer.writerows(works_data)

    # print(f"\nCrawling completed! A total of {len(works_data)} works were obtained, and the data has been saved to carl_nielsen_works.csv")
    return works_data
