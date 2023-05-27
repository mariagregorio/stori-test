import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import datetime
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
        result["Debit average"] = sum(debit_transactions)/len(debit_transactions)
    else:
        result["Debit average"] = None
    if (len(credit_transactions) > 0):
        result["Credit average"] = sum(credit_transactions)/len(credit_transactions)
    else:
        result["Credit average"] = None
    return result

def calculate_monthly_summary(data):
    data.sort(key=lambda row: row['Date'])
    result = {}
    for key, row in groupby(data, key=lambda row:row['Date'][:7]):
        result_key = f"{calendar.month_name[int(key[5:])]}, {key[:4]}"
        result_value = {}
        row = list(row)
        result_value["Total transactions"] = len(row)
        averages = get_transactions_group_averages(row)
        result_value["Debit average"] = averages["Debit average"]
        result_value["Credit average"] = averages["Credit average"]
        result[result_key] = result_value
    return result

def create_email_body(data):
    total = calculate_total_balance(data)
    monthly_summary = calculate_monthly_summary(data)
    monthly_summary_string = ""
    for item in monthly_summary.items():
        monthly_summary_string += "<p><b>{}</b></p><p>Total transactions: <b>{}</b><br>Debit average: <b>$ {}</b><br>Credit average: <b>$ {}</b></p>".format(
            item[0], 
            item[1]["Total transactions"], 
            item[1]["Debit average"], 
            item[1]["Credit average"])
    body = "<html><head></head><body><a href=\"https://www.storicard.com/\" target=\"_blank\"><img src=\"https://i.ibb.co/VSgm677/complete-logo-0f6b7ce5.png\" alt=\"Stori\"></a><p>Total balance: <b>$ {}</b></p><hr>".format(total) + monthly_summary_string + "</body></html>"
    return body

SENDER = "Stori <storitest2@gmail.com>"
RECIPIENT = "storitest2@gmail.com"
SUBJECT = "Your Stori Balance"
CHARSET = "UTF-8"

load_dotenv()

client = boto3.client('ses',
                        region_name=os.getenv("AWS_REGION"),
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

def send_email(data):
  body = create_email_body(data)
  try:
    response = client.send_email(
        Destination={
            'ToAddresses': [
                RECIPIENT,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': body,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
    )
  except ClientError as e:
      print(e.response['Error']['Message'])
  else:
      print("Email sent"),
      print("MessageId", response['MessageId'])
  return response