import csv
import logging
from dataclasses import asdict, dataclass
from typing import List
import time

import requests
from bs4 import BeautifulSoup

from src import util

util.configure_logging()

ROOT_DOMAIN: str = "https://www.ola.org/"
PARLIAMENTS_URL: str = ROOT_DOMAIN + "en/legislative-business/bills"
CSV_FILENAME: str = "parliaments.csv"


@dataclass
class ParliamentInfo:
    parliamentary_session_name: str
    url: str
    start_date: str
    end_date: str


def extract_from_url() -> str:
    response = requests.get(PARLIAMENTS_URL)
    response.raise_for_status()
    return response.text


def transform_from_html(html_content: str) -> List[ParliamentInfo]:
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.select_one("#block-de-theme-content > article > div > div > table")
    rows = table.find_all("tr")[1:]

    bills_data = []
    for row in rows:
        cols = row.find_all("td")
        parliamentary_session_name_col = cols[0].find("a")
        parliamentary_session_name = parliamentary_session_name_col.text.strip()
        url = ROOT_DOMAIN + parliamentary_session_name_col["href"].lstrip("/")
        start_date = cols[1].text.strip()
        end_date = cols[2].text.strip()

        bill_info = ParliamentInfo(
            parliamentary_session_name=parliamentary_session_name,
            url=url,
            start_date=start_date,
            end_date=end_date,
        )
        bills_data.append(bill_info)

    return bills_data


def load_to_csv(bills_data: List[ParliamentInfo]):
    with open(CSV_FILENAME, "w", newline="") as csvfile:
        FIELD_NAMES = ["parliamentary_session_name", "url", "start_date", "end_date"]
        writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)

        writer.writeheader()
        for bill in bills_data:
            writer.writerow(asdict(bill))

def get_all_parliaments() -> List[ParliamentInfo]:
    logging.info(
        "Starting the extraction process for parliament data from the URL: "
        + PARLIAMENTS_URL
    )
    parliament_html_content = extract_from_url()
    time.sleep(util.WAIT_SECONDS)
    parliament_data = transform_from_html(parliament_html_content)
    logging.info(
        f"Parliament data extraction and transformation completed. {len(parliament_data)} records extracted."
    )
    return parliament_data

def get_all_parliaments_from_csv() -> List[ParliamentInfo]:
    with open(CSV_FILENAME, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        parliament_data = [ParliamentInfo(**row) for row in reader]
    return parliament_data


if __name__ == "__main__":
    get_all_parliaments()
