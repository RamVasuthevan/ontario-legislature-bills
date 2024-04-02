import csv
import logging
from dataclasses import asdict, dataclass
from typing import List
import time

import requests
from bs4 import BeautifulSoup

from src import util
from src import bills

util.configure_logging()

STATUS_URL_SUFFIX = "/status"
CSV_FILENAME: str = "statuses.csv"


@dataclass
class StatusInfo:
    parliamentary_session_name: str
    bill_number: str
    bill_name: str
    date: str
    bill_stage: str
    activity: str
    committee: str


def extract_from_url(bill_url: str) -> str:
    status_url = bill_url + STATUS_URL_SUFFIX
    response = requests.get(status_url)
    response.raise_for_status()
    print(response.text)
    return response.text


def transform_from_html(
    parliamentary_session_name, bill_number, bill_name, html_content: str
) -> List[StatusInfo]:
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")

    status_info_list = []

    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        date = cells[0].text.strip()
        bill_stage = cells[1].text.strip()
        activity = cells[2].text.strip()
        committee = cells[3].text.strip()

        status_info = StatusInfo(
            parliamentary_session_name,
            bill_number,
            bill_name,
            date,
            bill_stage,
            activity,
            committee,
        )
        status_info_list.append(status_info)

    return status_info_list


def load_to_csv(statuses_data: List[StatusInfo]) -> None:
    with open(CSV_FILENAME, "w", newline="") as csvfile:
        FIELD_NAMES = [
            "parliament",
            "bill_number",
            "bill_name",
            "date",
            "bill_stage",
            "activity",
            "committee",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)

        writer.writeheader()
        for status in statuses_data:
            writer.writerow(asdict(status))


def get_all_statuses_from_bill(bill: bills.BillInfo) -> List[StatusInfo]:
    logging.info(
        f"Extracting status data for Bill {bill.bill_number}, {bill.bill_name}, {bill.parliamentary_session_name} from {bill.url+STATUS_URL_SUFFIX}"
    )
    print()
    html_content = extract_from_url(bill.url)
    time.sleep(util.WAIT_SECONDS)
    statuses = transform_from_html(
        bill.parliamentary_session_name,
        bill.bill_number,
        bill.bill_name,
        html_content,
    )
    logging.info(
        f"Status data extraction and transformation completed. {len(statuses)} records extracted."
    )
    return statuses


def get_all_statuses_from_csv() -> List[StatusInfo]:
    with open(CSV_FILENAME, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        statuses = [StatusInfo(**row) for row in reader]
    return statuses


if __name__ == "__main__":
    TEST_BILL = bills.BillInfo(
        parliamentary_session_name="36th Parliament, 1st Session",
        bill_number="1",
        bill_name="Executive Council Amendment Act, 1995",
        url_title="https://www.ola.org/en/legislative-business/bills/parliament-36/session-1/bill-1",
        sponsors=[bills.SponsorInfo(name="Eves, Hon. Ernie", title="Deputy Premier")],
    )
    get_all_statuses_from_bill(TEST_BILL)
