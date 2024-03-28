import logging
import time

from src import bills, log_config, parliaments

log_config.configure_logging()

WAIT_SECONDS = 2 

def main():
    logging.info(
        "Starting the extraction process for parliament data from the URL: "
        + parliaments.PARLIAMENTS_URL
    )
    parliament_html_content = parliaments.extract()
    time.sleep(WAIT_SECONDS)
    parliament_data = parliaments.transform(parliament_html_content)
    parliaments.load(parliament_data)
    logging.info(
        f"Parliament data extraction and processing completed. {len(parliament_data)} records loaded."
    )

    all_bill_data = []
    logging.info("Starting the extraction process for bill data.")

    for parliament in parliament_data:
        parliament_url = parliament.url
        parliament_name = parliament.parliament
        logging.info(
            f"Extracting bill data for {parliament_name} from {parliament_url}"
        )

        bill_html_content = bills.extract(parliament_url)
        time.sleep(WAIT_SECONDS)
        bill_data = bills.transform(parliament_name, bill_html_content)
        all_bill_data.extend(bill_data)

    bills.load(all_bill_data)
    logging.info(
        f"Bill data extraction and processing completed. {len(all_bill_data)} records loaded."
    )

    logging.info(
        f"Data extracted, processed, and saved to '{parliaments.CSV_FILENAME}' and '{bills.CSV_FILENAME}' successfully!"
    )


if __name__ == "__main__":
    main()
