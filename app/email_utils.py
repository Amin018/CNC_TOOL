import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

def _get_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is not set")
    return value

EMAIL_HOST: str = _get_env("EMAIL_HOST")
EMAIL_PORT: int = int(_get_env("EMAIL_PORT"))
EMAIL_USER: str = _get_env("EMAIL_USER")
EMAIL_PASSWORD: str = _get_env("EMAIL_PASSWORD")
EMAIL_LEADER: str = _get_env("EMAIL_LEADER")
EMAIL_TOOL: str = _get_env("EMAIL_TOOL")

# -------------------------------------------------
# Email sending function
# -------------------------------------------------
def send_changeover_email(
    changeover_id: int,
    machine_name: str,
    created_by: str,
    to_email: str = EMAIL_LEADER
) -> None:
    """
    Send CNC changeover notification email.
    """

    msg = MIMEMultipart()
    msg["From"] = f"CNC Changeover System <{EMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = f"New Changeover Created - {machine_name}"

    body = f"""
        A NEW Changeover has been Created.

        Changeover ID : {changeover_id}
        Machine       : {machine_name}
        Created By    : {created_by}

        Please log in to the CNC system for details.
        """

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

def concur_done_email(
    changeover_id: int,
    machine_name: str,
    concur_by: str,
    to_email: str = EMAIL_TOOL
) -> None:
    """
    Send CNC concur notification email.
    """

    msg = MIMEMultipart()
    msg["From"] = f"CNC Changeover System <{EMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = f"New Concur - {machine_name}"

    body = f"""
        A changeover has been Concurred.

        Changeover ID : {changeover_id}
        Machine       : {machine_name}
        Concurred By    : {concur_by}

        Please log in to the CNC system for details.
        """

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


def send_toolrequest_email(
    tool_id: int,
    machine_name: str,
    tool: str,
    created_by: str,
    to_email: str = EMAIL_LEADER
) -> None:
    

    msg = MIMEMultipart()
    msg["From"] = f"CNC System <{EMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = f"New Tool Change Requested - {machine_name}"

    body = f"""
        A new Tool Change has been created.

        Request ID    : {tool_id}
        Machine       : {machine_name}
        Tool          : {tool}
        Created By    : {created_by}

        Please log in to the CNC system for details.
        """

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

def concur_toolrequest_email(
    tool_id: int,
    machine_name: str,
    tool: str,
    concur_by: str,
    to_email: str = EMAIL_TOOL
) -> None:
    

    msg = MIMEMultipart()
    msg["From"] = f"CNC System <{EMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = f"New Tool Change Requested - {machine_name}"

    body = f"""
        A new Tool Change has been Concurred.

        Request ID    : {tool_id}
        Machine       : {machine_name}
        Tool          : {tool}
        Concurred By  : {concur_by}

        Please log in to the CNC system for details.
        """

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)