from typing import Text
import os


TEST_RUN = os.getenv('TEST_RUN', "False") == "True"
if TEST_RUN:
    from dotenv import load_dotenv

    load_dotenv()


POSTGRES_HOST = os.getenv('POSTGRES_HOST', "localhost")
POSTGRES_PORT = os.getenv('POSTGRES_PORT', "5432")
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME', "monitoring_db")
POSTGRES_USER = os.getenv('POSTGRES_USER', "admin")
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', "admin")

DATABASE_URI: Text = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}"
