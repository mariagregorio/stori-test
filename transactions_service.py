from mysql import connector
from dotenv import load_dotenv
import os

def save_transactions_data(data):
    load_dotenv()

    db = connector.connect(host=os.getenv("DB_HOST"), 
                                user=os.getenv("DB_USER"), 
                                passwd=os.getenv("DB_PASSWD"), 
                                port=os.getenv("DB_PORT"), 
                                database=os.getenv("DB_NAME"))
    db_cursor = db.cursor()
    for row in data:
        db_cursor.execute("""INSERT INTO Transaction (t_id, t_value, t_date) 
                        VALUES (%(id)s, %(transaction)s, %(date)s) 
                        ON DUPLICATE KEY UPDATE t_value=%(transaction)s, t_date=%(date)s""", 
                        {"id": int(row["Id"]), "transaction": row["Transaction"], "date": row["Date"]} )
    print("Saved records to DB")
    db.commit()
    db.close()