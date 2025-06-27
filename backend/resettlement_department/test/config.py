import os

import dotenv
import psycopg2
from psycopg2 import extensions

dotenv.load_dotenv() 

TEST_HOST = os.environ['TEST_HOST']
TEST_PORT = os.environ['TEST_PORT']
TEST_PASSWORD = os.environ['TEST_PASSWORD']
TEST_USER = os.environ['TEST_USER']
TEST_DATABASE = os.environ['TEST_DATABASE']

def get_connection() -> extensions.connection:
    try:
        conn = psycopg2.connect(
            user=TEST_USER,
            host=TEST_HOST,
            database=TEST_DATABASE,
            password=TEST_PASSWORD,
            port=TEST_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise

try:
    connection = get_connection()
    print("Connection established successfully!")
    connection.close()
except Exception as e:
    print(f"Failed to establish connection: {e}")