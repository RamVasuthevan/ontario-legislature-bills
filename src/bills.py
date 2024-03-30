import csv
import logging
from dataclasses import dataclass, field
from typing import List

import requests
from bs4 import BeautifulSoup

from src import log_config

log_config.configure_logging()

ROOT_DOMAIN: str = "https://www.ola.org/"
CSV_FILENAME: str = "bills.csv"


@dataclass
class SponsorInfo:
    name: str
    title: str = ""


@dataclass
class BillInfo:
    parliament: str
    bill_number: str
    bill_title: str
    url_title: str
    sponsors: List[SponsorInfo] = field(default_factory=list)


def extract(parliament_url) -> str:
    response = requests.get(parliament_url)
    response.raise_for_status()
    return response.text


def transform(parliament: str,, html_content: str) -> List[BillInfo]:
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", class_="views-table views-view-table cols-3")

    rows = table.find("tbody").find_all("tr")
    bill_info_list = []

    for row in rows:
        cols = row.find_all("td")
        bill_number = cols[0].text.strip()
        bill_link_element = cols[1].find("a")
        bill_title = bill_link_element.text.strip() if bill_link_element else ""
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
            BillInfo(parliament, bill_number, bill_title, url_title, bill_sponsors)
        )

    return bill_info_list


def load(bills_data: List[BillInfo]):
    with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as csvfile:
        FIELD_NAMES = ["parliament", "bill_number", "bill_title", "url_title"]
        max_sponsors = len(max(bills_data, key=lambda x: len(x.sponsors)).sponsors)

        for i in range(max_sponsors):
            FIELD_NAMES.extend([f"sponsor_name{i+1}", f"sponsor_title{i+1}"])

        writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
        writer.writeheader()

        for bill in bills_data:
            row = {
                "parliament": bill.parliament,
                "bill_number": bill.bill_number,
                "bill_title": bill.bill_title,
                "url_title": bill.url_title,
            }
            for i, sponsor in enumerate(bill.sponsors):
                row[f"sponsor_name{i+1}"] = sponsor.name
                row[f"sponsor_title{i+1}"] = sponsor.title
            writer.writerow(row)


if __name__ == "__main__":
    TEST_URL = "en/legislative-business/bills/parliament-42/session-2/"
    TEST_PARLIAMENT = "42nd Parliament, Session 2"

    logging.info(
        f"Starting to extract bills data for {TEST_PARLIAMENT} from {ROOT_DOMAIN + TEST_URL}"
    )
    html_content = extract(ROOT_DOMAIN + TEST_URL)
    bill_info_list = transform(TEST_PARLIAMENT, html_content)
    load(bill_info_list)
    logging.info(
        f"Data extracted, processed, and saved to '{CSV_FILENAME}' successfully!"
    )
