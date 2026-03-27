import csv
import logging
from dataclasses import dataclass, field
from typing import List
import time
import pandas as pd
from pandas import DataFrame


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


def transform_from_html(parliamentary_session_name: str, html_content: str) -> pd.DataFrame:
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", class_="views-table views-view-table cols-3")

    # Instantiating an empty DataFrame with specified columns
    df = pd.DataFrame(columns=["parliamentary_session_name", "bill_number", "bill_name", "url_title", "sponsors"])

    rows = table.find("tbody").find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        bill_number = cols[0].text.strip()
        bill_link_element = cols[1].find("a")
        bill_name = bill_link_element.text.strip() if bill_link_element else ""
        url_title = ROOT_DOMAIN + bill_link_element["href"].lstrip("/")

        sponsors_list = []
        sponsors = cols[2].find_all("article", class_="node--type-bill-sponsor")
        for sponsor in sponsors:
            sponsor_name = sponsor.find("div", class_="field--name-field-full-name-by-last-name").text.strip()
            sponsor_title_element = sponsor.find("div", class_="field--name-field-sponsor-role")
            sponsor_title = sponsor_title_element.text.strip() if sponsor_title_element else ""
            sponsors_list.append({"name": sponsor_name, "title": sponsor_title})

        # Appending row to df directly
        df = df.append({
            "parliamentary_session_name": parliamentary_session_name,
            "bill_number": bill_number,
            "bill_name": bill_name,
            "url_title": url_title,
            "sponsors": sponsors_list,
        }, ignore_index=True)

    return df

def load_to_csv(df:DataFrame):
    # Expand the 'sponsors' list into a DataFrame, if the 'sponsors' column exists
    if 'sponsors' in df.columns:
        sponsors_df = pd.json_normalize(df['sponsors'].explode()).add_prefix('sponsor_')
        sponsors_df.index = df.index.repeat(df['sponsors'].str.len())  # Align the index with the original df
        # Drop the original 'sponsors' column from df and join the expanded sponsors_df
        df = df.drop(columns=['sponsors']).join(sponsors_df).reset_index(drop=True)

    # Use the global CSV_FILENAME variable for the output file name
    df.to_csv(CSV_FILENAME, index=False, encoding='utf-8')


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
