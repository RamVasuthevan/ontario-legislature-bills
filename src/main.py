import logging

from src import bills, parliaments, statuses, util

util.configure_logging()

WAIT_SECONDS = 1


def get_and_load_all_data():
    parliament_data = parliaments.get_all_parliaments()
    parliaments.load_to_csv(parliament_data)
    logging.info(f"Parliament data saved to '{parliaments.CSV_FILENAME}' successfully!")

    logging.info("Starting the extraction process for bill data.")
    all_bill_data = []
    for parliament in parliament_data:
        bill_data = bills.get_all_bills_from_parliament(parliament)
        all_bill_data.extend(bill_data)
        
    bills.load_to_csv(all_bill_data)
    logging.info(f"Bill data saved to '{bills.CSV_FILENAME}' successfully!")

    all_status_data = []
    logging.info("Starting the extraction process for status data.")
    for bill in all_bill_data:
        status_data = statuses.transform_from_html(
            bill.parliament, bill.bill_number, bill.bill_name, bill.url_title
        )
        all_status_data.extend(status_data)

    statuses.load_to_csv(all_status_data)
    logging.info(f"Status data saved to '{statuses.CSV_FILENAME}' successfully!")


def get_and_load_changed_data():
    parliament_data_from_url = parliaments.get_all_parliaments()
    parliaments.load_to_csv(parliament_data_from_url)
    logging.info(f"Parliament data saved to '{parliaments.CSV_FILENAME}' successfully!")

    parliament_data_from_csv = parliaments.get_all_parliaments_from_csv()

    parliamentary_session_names_from_url = {
        parliament.parliamentary_session_name for parliament in parliament_data_from_url
    }

    parliamentary_session_with_possible_changes = [ parliament for parliament in parliament_data_from_csv if parliament.parliamentary_session_name not in parliamentary_session_names_from_url or parliament.end_date == "Present"]
    parliamentary_session_with_possible_changes_names = {parliament.parliamentary_session_name for parliament in parliamentary_session_with_possible_changes}
    logging.info("Found the following parliamentary sessions with possible changes:")
    for parliament in parliamentary_session_with_possible_changes:
        logging.info(f" - {parliament.parliamentary_session_name}")
    
    logging.info("Get all bills from {bills.CSV_FILENAME}")
    all_bill_data = bills.get_all_bills_from_csv()
    bills_with_possible_changes = []
    for parliament in parliamentary_session_with_possible_changes:
        bill_data = bills.get_all_bills_from_parliament(parliament)
        bills_with_possible_changes.extend(bill_data)
    all_bill_data_from_parliaments_without_changes = [bill for bill in all_bill_data if bill.parliamentary_session_name not in parliamentary_session_with_possible_changes_names]
    all_bill_data = all_bill_data_from_parliaments_without_changes + bills_with_possible_changes

    bills.load_to_csv(all_bill_data)
    logging.info(f"Bill data saved to '{bills.CSV_FILENAME}' successfully!")

    logging.info("Get all statuses from {statuses.CSV_FILENAME}")
    all_status_data = statuses.get_all_statuses_from_csv()
    statuses_with_possible_changes = []
    for bill in bills_with_possible_changes:
        status_data = statuses.get_all_statuses_from_bill(bill)
        statuses_with_possible_changes.extend(status_data)
    
    all_status_data_from_bills_without_changes = [status for status in all_status_data if status.parliamentary_session_name not in parliamentary_session_with_possible_changes_names]
    all_status_data = all_status_data_from_bills_without_changes + statuses_with_possible_changes

    statuses.load_to_csv(all_status_data)
    logging.info(f"Status data saved to '{statuses.CSV_FILENAME}' successfully!")

if __name__ == "__main__":
    ## get_and_load_all_data()
    get_and_load_changed_data()
