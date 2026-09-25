import os
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]


def get_gmail_service():
    # ==============================
    # RENDER / PRODUCTION
    # ==============================

    if os.getenv("GOOGLE_GMAIL_REFRESH_TOKEN"):

        creds = Credentials(
            token=None,
            refresh_token=os.getenv("GOOGLE_GMAIL_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=GMAIL_SCOPES,
        )

        return build(
            "gmail",
            "v1",
            credentials=creds
        )

    # ==============================
    # LOCAL DEVELOPMENT
    # ==============================

    creds = None

    if os.path.exists("gmail_token.json"):
        creds = Credentials.from_authorized_user_file(
            "gmail_token.json",
            GMAIL_SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                GMAIL_SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("gmail_token.json", "w") as token:
            token.write(creds.to_json())

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


# =========================================================
# 1. UNREAD EMAILS
# =========================================================

def get_unread_emails(max_results=10):

    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return "No unread emails found."

    output = []

    for message in messages:

        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=[
                "From",
                "Subject",
                "Date"
            ]
        ).execute()

        headers = msg.get(
            "payload",
            {}
        ).get(
            "headers",
            []
        )

        data = {}

        for header in headers:
            data[header["name"]] = header["value"]

        output.append(
            f"ID: {message['id']}\n"
            f"From: {data.get('From', 'Unknown')}\n"
            f"Subject: {data.get('Subject', 'No subject')}\n"
            f"Date: {data.get('Date', 'Unknown')}"
        )

    return "\n\n".join(output)


# =========================================================
# 2. SEARCH EMAILS
# =========================================================

def search_emails(query, max_results=10):

    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return "No emails found."

    output = []

    for message in messages:

        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=[
                "From",
                "To",
                "Subject",
                "Date"
            ]
        ).execute()

        headers = msg.get(
            "payload",
            {}
        ).get(
            "headers",
            []
        )

        data = {}

        for header in headers:
            data[header["name"]] = header["value"]

        output.append(
            f"ID: {message['id']}\n"
            f"From: {data.get('From', 'Unknown')}\n"
            f"To: {data.get('To', 'Unknown')}\n"
            f"Subject: {data.get('Subject', 'No subject')}\n"
            f"Date: {data.get('Date', 'Unknown')}"
        )

    return "\n\n".join(output)


# =========================================================
# 3. READ SPECIFIC EMAIL
# =========================================================

def read_email(message_id):

    service = get_gmail_service()

    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    payload = msg.get("payload", {})

    headers = payload.get("headers", [])

    data = {}

    for header in headers:
        data[header["name"]] = header["value"]

    body = extract_email_body(payload)

    return (
        f"From: {data.get('From', 'Unknown')}\n"
        f"To: {data.get('To', 'Unknown')}\n"
        f"Subject: {data.get('Subject', 'No subject')}\n"
        f"Date: {data.get('Date', 'Unknown')}\n\n"
        f"Body:\n{body}"
    )


def extract_email_body(payload):

    if "parts" in payload:

        for part in payload["parts"]:

            if part["mimeType"] == "text/plain":

                data = part["body"].get("data")

                if data:
                    return base64.urlsafe_b64decode(
                        data
                    ).decode(
                        "utf-8",
                        errors="ignore"
                    )

            if part["mimeType"].startswith("multipart/"):

                body = extract_email_body(part)

                if body:
                    return body

    body_data = payload.get(
        "body",
        {}
    ).get(
        "data"
    )

    if body_data:

        return base64.urlsafe_b64decode(
            body_data
        ).decode(
            "utf-8",
            errors="ignore"
        )

    return "No readable email body found."


# =========================================================
# 4. SEND EMAIL
# =========================================================

def send_email(to, subject, body):

    service = get_gmail_service()

    message = (
        f"To: {to}\r\n"
        f"Subject: {subject}\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"\r\n"
        f"{body}"
    )

    encoded_message = base64.urlsafe_b64encode(
        message.encode("utf-8")
    ).decode("utf-8")

    result = service.users().messages().send(
        userId="me",
        body={
            "raw": encoded_message
        }
    ).execute()

    return f"Email sent successfully. Message ID: {result['id']}"


# =========================================================
# 5. CREATE DRAFT
# =========================================================

def create_email_draft(to, subject, body):

    service = get_gmail_service()

    message = (
        f"To: {to}\r\n"
        f"Subject: {subject}\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"\r\n"
        f"{body}"
    )

    encoded_message = base64.urlsafe_b64encode(
        message.encode("utf-8")
    ).decode("utf-8")

    draft = service.users().drafts().create(
        userId="me",
        body={
            "message": {
                "raw": encoded_message
            }
        }
    ).execute()

    return f"Draft created successfully. Draft ID: {draft['id']}"


# =========================================================
# 6. EMAIL SUMMARY DATA
# =========================================================

def get_emails_for_summary(max_results=10):

    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return "No emails found."

    output = []

    for message in messages:

        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        payload = msg.get("payload", {})

        headers = payload.get("headers", [])

        data = {}

        for header in headers:
            data[header["name"]] = header["value"]

        body = extract_email_body(payload)

        output.append(
            f"From: {data.get('From', 'Unknown')}\n"
            f"Subject: {data.get('Subject', 'No subject')}\n"
            f"Date: {data.get('Date', 'Unknown')}\n"
            f"Body: {body}"
        )

    return "\n\n--- EMAIL ---\n\n".join(output)