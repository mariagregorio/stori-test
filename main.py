from pathlib import Path
import csv
from email_service import send_email
import datetime
from transactions_service import save_transactions_data


def main():
    with open("data.csv") as data:
        has_header = csv.Sniffer().has_header(data.readline())
        data.seek(0)
        reader = csv.DictReader(data, ("Id", "Date", "Transaction"))
        if has_header:
            next(reader)
        data = []
        for row in reader:
            row["Transaction"] = float(row["Transaction"])
            dateObject = row["Date"].split("/")
            row["Date"] = datetime.date(int(dateObject[2]), int(
                dateObject[0]), int(dateObject[1])).isoformat()
            data.append(row)
        send_email(data)
        save_transactions_data(data)


if __name__ == "__main__":
    main()
