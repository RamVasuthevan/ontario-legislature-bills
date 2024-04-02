import csv
import logging
from dataclasses import dataclass, field
from typing import List
import time

import requests
from bs4 import BeautifulSoup

from src import util
from src import parliaments

util.configure_logging()

ROOT_DOMAIN: str = "https://www.ola.org/"
CSV_FILENAME: str = "bills.csv"


@dataclass
class SponsorInfo:
    name: str
    title: str = ""


@dataclass
class BillInfo:
    parliamentary_session_name: str
    bill_number: str
    bill_name: str
    url_title: str
    sponsors: List[SponsorInfo] = field(default_factory=list)


def extract_from_url(parliament_url) -> str:
    response = requests.get(parliament_url)
    response.raise_for_status()
    return response.text


def transform_from_html(
    parliamentary_session_name: str, html_content: str
) -> List[BillInfo]:
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", class_="views-table views-view-table cols-3")

    rows = table.find("tbody").find_all("tr")
    bill_info_list = []

    for row in rows:
        cols = row.find_all("td")
        bill_number = cols[0].text.strip()
        bill_link_element = cols[1].find("a")
        bill_name = bill_link_element.text.strip() if bill_link_element else ""
        url_title = ROOT_DOMAIN + bill_link_element["href"].lstrip("/")

        bill_sponsors = []
        sponsors = cols[2].find_all("article", class_="node--type-bill-sponsor")
        for sponsor in sponsors:
            sponsor_name = sponsor.find(
                "div", class_="field--name-field-full-name-by-last-name"
            ).text.strip()
            sponsor_title_element = sponsor.find(
                "div", class_="field--name-field-sponsor-role"
            )
            sponsor_title = (
                sponsor_title_element.text.strip() if sponsor_title_element else ""
            )
            bill_sponsors.append(SponsorInfo(name=sponsor_name, title=sponsor_title))

        bill_info_list.append(
            BillInfo(
                parliamentary_session_name,
                bill_number,
                bill_name,
                url_title,
                bill_sponsors,
            )
        )

    return bill_info_list


def load_to_csv(bills_data: List[BillInfo]):
    with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as csvfile:
        FIELD_NAMES = [
            "parliament",
            "bill_number",
            "bill",
            "url_title",
        ]  # make sure to use these names
        max_sponsors = len(max(bills_data, key=lambda x: len(x.sponsors)).sponsors)

        for i in range(max_sponsors):
            FIELD_NAMES.extend([f"sponsor_name{i+1}", f"sponsor_title{i+1}"])

        writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
        writer.writeheader()

        for bill in bills_data:
            row = {
                "parliament": bill.parliament,
                "bill_number": bill.bill_number,
                "bill": bill.bill,
                "url_title": bill.url_title,
            }
            for i, sponsor in enumerate(bill.sponsors):
                row[f"sponsor_name{i+1}"] = sponsor.name
                row[f"sponsor_title{i+1}"] = sponsor.title
            writer.writerow(row)


def get_all_bills_from_parliament(
    parliament: parliaments.ParliamentInfo,
) -> List[BillInfo]:
    logging.info(
        f"Starting to extract bills data for {parliament.parliamentary_session_name} from {parliament.url}"
    )
    html_content = extract_from_url(parliament.url)
    time.sleep(util.WAIT_SECONDS)
    bill_info_list = transform_from_html(
        parliament.parliamentary_session_name, html_content
    )
    logging.info(
        f"Data extracted and processed for {parliament.parliamentary_session_name}. {len(bill_info_list)} records extracted."
    )
    return bill_info_list

def get_all_bills_from_csv() -> List[BillInfo]:
    bills_data = []
    with open(CSV_FILENAME, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parliament = row["parliament"]
            bill_number = row["bill_number"]
            bill = row["bill"]
            url_title = row["url_title"]
            sponsors = []
            for i in range(1, 6):
                sponsor_name = row.get(f"sponsor_name{i}")
                sponsor_title = row.get(f"sponsor_title{i}")
                if sponsor_name:
                    sponsors.append(SponsorInfo(name=sponsor_name, title=sponsor_title))
            bills_data.append(
                BillInfo(
                    parliamentary_session_name=parliament,
                    bill_number=bill_number,
                    bill_name=bill,
                    url_title=url_title,
                    sponsors=sponsors,
                )
            )
    return bills_data


if __name__ == "__main__":
    TEST_PARLIAMENT = parliaments.ParliamentInfo(
        parliamentary_session_name="36th Parliament, 1st Session",
        url="https://www.ola.org/en/legislative-business/bills/parliament-36/session-1",
        start_date="September 26, 1995",
        end_date="December 18, 1997",
    )
    get_all_bills_from_parliament(TEST_PARLIAMENT)
