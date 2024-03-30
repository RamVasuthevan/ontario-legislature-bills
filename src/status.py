import csv
import logging
from dataclasses import asdict, dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

from src import log_config

log_config.configure_logging()

STATUS_URL_SUFFIX = "/status"
CSV_FILENAME: str = "statuses.csv"

@dataclass
class StatusInfo:
    date: str
    bill_stage: str
    activity: str
    committee: str



def extract(bill_url: str) -> str:
    status_url = bill_url + STATUS_URL_SUFFIX
    response = requests.get(status_url)
    response.raise_for_status()
    return response.text

def transform(html_content: str) -> List[StatusInfo]:
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    status_info_list = []
    
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        date = cells[0].text.strip()
        bill_stage = cells[1].text.strip()
        activity = cells[2].text.strip()
        committee = cells[3].text.strip()
        
        status_info = StatusInfo(date, bill_stage, activity, committee)
        status_info_list.append(status_info)
    
    return status_info_list

def load(statuses_data: List[StatusInfo]) -> None:
    with open(CSV_FILENAME, "w", newline="") as csvfile:
        FIELD_NAMES = ["date", "bill_stage", "activity", "committee"]
        writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)

        writer.writeheader()
        for status in statuses_data:
            writer.writerow(asdict(status))

if __name__ == "__main__":
    TEST_BILL_URL = "https://www.ola.org/en/legislative-business/bills/parliament-36/session-1/bill-1/"

    logging.info(
        f"Starting to extract bills data for {TEST_BILL_URL}"
    )
    html_content = extract(TEST_BILL_URL)
    bill_info_list = transform(html_content)
    load(bill_info_list)
    logging.info(
        f"Data extracted, processed, and saved to '{CSV_FILENAME}' successfully!"
    )

