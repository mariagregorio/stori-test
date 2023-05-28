# Stori email balance app

This app will send an email with the balance summary calculated from `data.csv` file, and save each record from that file in a MySQL database.
This app uses Amazon SES in sandbox mode, therefore only verified email addresses will be available to send the email. By default, the email will be sent to test address storitest2@gmail.com.
Contact developer to get a new email address added to SES verified identities.

## Requirements

- [Docker desktop](https://docs.docker.com/desktop/)

## Start app

1. Create .env file (use .env.example for guidance)
2. Run in root dir
   `docker-compose up`
