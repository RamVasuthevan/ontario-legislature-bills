import csv
import requests
from dataclasses import dataclass, asdict
from typing import List
from bs4 import BeautifulSoup

# Magic variables
ROOT_DOMAIN: str = "https://www.ola.org/"
PARLIAMENTS_URL: str = ROOT_DOMAIN + "en/legislative-business/bills"
CSV_FILENAME: str = "parliaments.csv"


@dataclass
class ParliamentInfo:
    parliament: str
    url: str
    start_date: str
    end_date: str


def extract() -> str:
    response = requests.get(PARLIAMENTS_URL)
    response.raise_for_status()  # Still throw an error for non-200 status codes
    return response.text


def transform(html_content: str) -> List[ParliamentInfo]:
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.select_one("#block-de-theme-content > article > div > div > table")
    rows = table.find_all("tr")[1:]  # Assuming the first row is the header

    bills_data = []
    for row in rows:
        cols = row.find_all("td")
        parliament_col = cols[0].find("a")
        parliament = parliament_col.text.strip()
        url = ROOT_DOMAIN + parliament_col["href"].lstrip("/")
        start_date = cols[1].text.strip()
        end_date = cols[2].text.strip()

        bill_info = ParliamentInfo(
            parliament=parliament, url=url, start_date=start_date, end_date=end_date
        )
        bills_data.append(bill_info)

    return bills_data


def load(bills_data: List[ParliamentInfo]):
    with open(CSV_FILENAME, "w", newline="") as csvfile:
        fieldnames = ["parliament", "url", "start_date", "end_date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for bill in bills_data:
            writer.writerow(asdict(bill))


if __name__ == "__main__":
    try:
        html_content = extract()
        extracted_data = transform(html_content)
        load(extracted_data)
        print(f"Data extracted, processed, and saved to '{CSV_FILENAME}' successfully!")
    except requests.RequestException as e:
        print(f"An error occurred during extraction: {e}")
