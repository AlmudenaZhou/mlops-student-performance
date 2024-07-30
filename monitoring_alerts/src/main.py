import os
import ast

from dotenv import load_dotenv

from tools.prepare_data import calculate_data_drift
from tools.send_email_basic import send_email_basic


load_dotenv()
RECIPIENT_LIST = ast.literal_eval(os.getenv("RECIPIENT_LIST"))
PROJECT_NAME = os.getenv("PROJECT_NAME")
LINK_URL = os.getenv("LINK_URL")

is_alert, html, html_bytes = calculate_data_drift()


def basic_email():
    if is_alert:
        send_email_basic(
            project_name=PROJECT_NAME,
            link_url=LINK_URL,
            recipient_list=RECIPIENT_LIST,
        )


if __name__ == "__main__":
    basic_email()
