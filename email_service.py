import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from itertools import groupby
import calendar


def calculate_total_balance(data):
    total = 0
    for row in data:
        total += row["Transaction"]
    return total


def get_transactions_group_averages(row):
    debit_transactions = []
    credit_transactions = []
    for item in row:
        if item["Transaction"] < 0:
            debit_transactions.append(item["Transaction"])
        else:
            credit_transactions.append(item["Transaction"])
    result = {}
    if (len(debit_transactions) > 0):
        result["Debit average"] = sum(
            debit_transactions) / len(debit_transactions)
    else:
        result["Debit average"] = None
    if (len(credit_transactions) > 0):
        result["Credit average"] = sum(
            credit_transactions) / len(credit_transactions)
    else:
        result["Credit average"] = None
    return result


def calculate_monthly_summary(data):
    data.sort(key=lambda row: row['Date'])
    result = {}
    for key, row in groupby(data, key=lambda row: row['Date'][:7]):
        result_key = f"{calendar.month_name[int(key[5:])]}, {key[:4]}"
        result_value = {}
        row = list(row)
        result_value["Total transactions"] = len(row)
        averages = get_transactions_group_averages(row)
        result_value["Debit average"] = averages["Debit average"]
        result_value["Credit average"] = averages["Credit average"]
        result[result_key] = result_value
    return result


def create_month_summary_html(month, total, debit_avg, credit_avg):
    return """
    <p>
        <b>{}</b>
    </p>
    <p>Total transactions: <b>{}</b><br>
        Debit average: <b>$ {}</b><br>
        Credit average: <b>$ {}</b>
    </p>""".format(
        month, total, debit_avg, credit_avg)


def create_summary_html(total, monthly_summary_string):
    return """
    <html>
        <head></head>
        <body>
            <a href=\"https://www.storicard.com/\" target=\"_blank\">
                <img src=\"https://i.ibb.co/VSgm677/complete-logo-0f6b7ce5.png\" alt=\"Stori\">
            </a>
            <p>Total balance: <b>$ {}</b></p>
            <hr>""".format(
        total) + monthly_summary_string + "</body></html>"


def create_email_body(data):
    total = calculate_total_balance(data)
    monthly_summary = calculate_monthly_summary(data)
    monthly_summary_string = ""
    for item in monthly_summary.items():
        monthly_summary_string += create_month_summary_html(item[0],
                                                            item[1]["Total transactions"],
                                                            item[1]["Debit average"],
                                                            item[1]["Credit average"])
    body = create_summary_html(total,  monthly_summary_string)
    return body


recipients = ["storitest2@gmail.com",
              "airam.greg@gmail.com",
              "alan.ramirez@storicard.com",
              "ignacio.romero@storicard.com"]


def send_email(data):
    load_dotenv()
    client = boto3.client(
        'ses',
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    sender = "Stori <storitest2@gmail.com>"
    subject = "Your Stori Balance"
    charset = "UTF-8"
    body = create_email_body(data)
    for recipient in recipients:
        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': [recipient],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': charset,
                            'Data': body,
                        },
                    },
                    'Subject': {
                        'Charset': charset,
                        'Data': subject,
                    },
                },
                Source=sender,
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent to", recipient),
            print("MessageId", response['MessageId'])
    return
