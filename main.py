import parliaments
import bills

def main():
    parliament_html_content = parliaments.extract()
    parliament_data = parliaments.transform(parliament_html_content)
    parliaments.load(parliament_data)  

    all_bill_data = []

    for parliament in parliament_data:
        parliament_url = parliament.url
        parliament_name = parliament.parliament
        bill_html_content = bills.extract(parliament_url)
        bill_data = bills.transform(parliament_name,bill_html_content)
        all_bill_data.extend(bill_data) 

    bills.load(all_bill_data)

if __name__ == "__main__":
    main()
