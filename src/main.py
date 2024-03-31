import logging
import time

from src import bills, log_config, parliaments, statuses

log_config.configure_logging()

WAIT_SECONDS = 1


def main():
    logging.info(
        "Starting the extraction process for parliament data from the URL: "
        + parliaments.PARLIAMENTS_URL
    )
    parliament_html_content = parliaments.extract()
    time.sleep(WAIT_SECONDS)
    parliament_data = parliaments.transform(parliament_html_content)
    logging.info(
        f"Parliament data extraction and transformation completed. {len(parliament_data)} records extracted."
    )

    parliaments.load(parliament_data)
    logging.info(
        f"Parliament data saved to '{parliaments.CSV_FILENAME}' successfully!"
    )

    all_bill_data = []
    logging.info("Starting the extraction process for bill data.")

    for parliament in parliament_data:
        logging.info(
            f"Extracting bill data for {parliament.url} from {parliament.url}"
        )

        bill_html_content = bills.extract(parliament.url)
        time.sleep(WAIT_SECONDS)
        bill_data = bills.transform(parliament.url, bill_html_content)
        all_bill_data.extend(bill_data)
    logging.info(
        f"Bill data extraction and transformation completed. {len(all_bill_data)} records extracted."
    )

    bills.load(all_bill_data)
    logging.info(
        f"Detailed bill data saved to '{bills.CSV_FILENAME}' successfully!"
    )


    all_status_data = []
    logging.info("Starting the extraction process for status data.")
    for bill in all_bill_data:
        logging.info(
            f"Extracting status data for Bill {bill.bill_number}, {bill.bill_title}, {bill.parliament} from {bill.url_title+statuses.STATUS_URL_SUFFIX}"
        )

        status_html_content = statuses.extract(bill.url_title)
        time.sleep(WAIT_SECONDS)
        status_data = statuses.transform(bill.parliament, bill.bill_number, bill.bill_title, status_html_content)
        all_status_data.extend(status_data)
    logging.info("Status data extraction and transformation completed. {len(all_status_data)} records extracted.")

    statuses.load(all_status_data)
    logging.info(f"Status data saved to '{statuses.CSV_FILENAME}' successfully!")



if __name__ == "__main__":
    main()
