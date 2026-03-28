import pymysql
import logging
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 25060))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")


def get_db_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            ssl={
                "reject_hostname": False
            }
        )
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Error connecting to MySQL Database: {e}")
        raise

if __name__ == "__main__":
    try:
        conn = get_db_connection()
        print("✅ Successfully connected to the DigitalOcean MySQL database!")
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version")
            result = cursor.fetchone()
            print(f"📊 Database Version: {result['version']}")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
