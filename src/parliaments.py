import csv
import logging
from dataclasses import asdict, dataclass
from typing import List
import time
import pandas as pd
from pandas import DataFrame

import requests
from bs4 import BeautifulSoup

from src import util

util.configure_logging()

ROOT_DOMAIN: str = "https://www.ola.org/"
PARLIAMENTS_URL: str = ROOT_DOMAIN + "en/legislative-business/bills"
CSV_FILENAME: str = "parliaments.csv"


def extract_from_web() -> str:
    response = requests.get(PARLIAMENTS_URL)
    response.raise_for_status()
    return response.text


def transform_from_web(html_content: str) -> DataFrame:
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.select_one("#block-de-theme-content > article > div > div > table")
    rows = table.find_all("tr")[1:]

    df = DataFrame(
        columns=["parliamentary_session_name", "url", "start_date", "end_date"]
    )

    for row in rows:
        cols = row.find_all("td")
        parliamentary_session_name_col = cols[0].find("a")
        parliamentary_session_name: str = parliamentary_session_name_col.text.strip()
        url: str = ROOT_DOMAIN + parliamentary_session_name_col["href"].lstrip("/")
        start_date: str = cols[1].text.strip()
        end_date: str = cols[2].text.strip()

        df = df.append(
            {
                "parliamentary_session_name": parliamentary_session_name,
                "url": url,
                "start_date": start_date,
                "end_date": end_date,
            },
            ignore_index=True,
        )

    return df


def load_to_csv(df: DataFrame):
    df.to_csv(CSV_FILENAME, index=False)


def get_all_parliaments() -> DataFrame:
    logging.info(
        "Starting the extraction process for parliament data from the URL: "
        + PARLIAMENTS_URL
    )
    parliament_df = extract_from_web()
    time.sleep(util.WAIT_SECONDS)
    parliament_data = transform_from_web(parliament_df)
    logging.info(
        f"Parliament data extraction and transformation completed. {len(parliament_data)} records extracted."
    )
    return parliament_data


def get_all_parliaments_from_csv() -> DataFrame:
    return pd.read_csv(CSV_FILENAME)


if __name__ == "__main__":
    get_all_parliaments()
