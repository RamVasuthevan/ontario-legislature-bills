import logging

from src import bills, log_config, parliaments, statuses

log_config.configure_logging()


def get_all_parliaments() -> list[parliaments.ParliamentInfo]:
    parliament_html_content = parliaments.extract()
    parliament_data = parliaments.transform(parliament_html_content)
    return parliament_data


def get_all_bills_for_parliament(
    parliament: parliaments.ParliamentInfo,
) -> list[bills.BillInfo]:
    logging.info(f"Extracting bill data for {parliament.url} from {parliament.url}")

    bill_html_content = bills.extract(parliament.url)
    bill_data = bills.transform(parliament.url, bill_html_content)
    return bill_data

def get_all_status_for_bill(bill: bills.BillInfo) -> list[statuses.StatusInfo]:
    logging.info(
        f"Extracting status data for Bill {bill.bill_number}, {bill.bill_title}, {bill.parliament} from {bill.url_title+statuses.STATUS_URL_SUFFIX}"
    )

    status_html_content = statuses.extract(bill.url_title)
    status_data = statuses.transform(
        bill.parliament, bill.bill_number, bill.bill_title, status_html_content
    )
    return status_data

def etl_all_data():
    logging.info(
        "Starting the extraction process for parliament data from the URL: "
        + parliaments.PARLIAMENTS_URL
    )
    parliament_data = get_all_parliaments()
    parliaments.load(parliament_data)
    logging.info(
        f"Parliament data extraction and transformation completed. {len(parliament_data)} records extracted."
    )
    logging.info(f"Parliament data saved to '{parliaments.CSV_FILENAME}' successfully!")

    all_bill_data = []
    logging.info("Starting the extraction process for bill data.")
    for parliament in parliament_data:
        all_bill_data.extend(get_all_bills_for_parliament(parliament))
    logging.info(
        f"Bill data extraction and transformation completed. {len(all_bill_data)} records extracted."
    )
    bills.load(all_bill_data)
    logging.info(f"Detailed bill data saved to '{bills.CSV_FILENAME}' successfully!")

    all_status_data = []
    logging.info("Starting the extraction process for status data.")
    for bill in all_bill_data:
        all_status_data.extend(get_all_status_for_bill(bill))
    logging.info(
        "Status data extraction and transformation completed. {len(all_status_data)} records extracted."
    )
    statuses.load(all_status_data)
    logging.info(f"Status data saved to '{statuses.CSV_FILENAME}' successfully!")

def etl_all_data_for_current_parliamentary_session():
    logging.info(
        "Starting the extraction process for parliament data from the URL: "
        + parliaments.PARLIAMENTS_URL
    )
    parliament_data = get_all_parliaments()
    parliaments.load(parliament_data)
    logging.info(
        f"Parliament data extraction and transformation completed. {len(parliament_data)} records extracted."
    )
    logging.info(f"Parliament data saved to '{parliaments.CSV_FILENAME}' successfully!")

    current_parliamentary_session = parliaments[-1]
    logging.info("Starting the extraction process for bill data for {current_parliamentary_session.parliament}."):
    all_bill_data=get_all_bills_for_parliament(current_parliamentary_session)
    logging.info(
        f"Bill data extraction and transformation completed. {len(all_bill_data)} records extracted."
    )
    bills.load(all_bill_data)
    logging.info(f"Detailed bill data saved to '{bills.CSV_FILENAME}' successfully!")

    all_status_data = []
    logging.info("Starting the extraction process for status data.")
    for bill in all_bill_data:
        all_status_data.extend(get_all_status_for_bill(bill))
    logging.info(
        "Status data extraction and transformation completed. {len(all_status_data)} records extracted."
    )
    statuses.load(all_status_data)
    logging.info(f"Status data saved to '{statuses.CSV_FILENAME}' successfully!")

if __name__ == "__main__":
    main()
