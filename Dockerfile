FROM python:3.11.3
RUN pip install mysql-connector-python boto3 python-dotenv
COPY . .