import os
from typing import Text

TEST_RUN = os.getenv('TEST_RUN', "False") == "True"
if TEST_RUN:
    from dotenv import load_dotenv

    load_dotenv()


host = os.getenv('POSTGRES_HOST', "localhost")
port = os.getenv('POSTGRES_PORT', "5432")
db_name = os.getenv('POSTGRES_DB_NAME', "monitoring_db")
user = os.getenv('POSTGRES_USER', "admin")
password = os.getenv('POSTGRES_PASSWORD', "admin")

DATABASE_URI: Text = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
