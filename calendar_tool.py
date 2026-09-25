import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    # Render / production
    if os.getenv("GOOGLE_REFRESH_TOKEN"):
        creds = Credentials(
            token=None,
            refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=SCOPES,
        )

        return build(
            "calendar",
            "v3",
            credentials=creds
        )

    # Local development
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build(
        "calendar",
        "v3",
        credentials=creds
    )


def get_upcoming_events(max_results=10):

    service = get_calendar_service()

    events_result = service.events().list(
        calendarId="primary",
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    if not events:
        return "No upcoming events found."

    result = []

    for event in events:

        start = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        summary = event.get(
            "summary",
            "No title"
        )

        result.append(
            f"{summary} - {start}"
        )

    return "\n".join(result)

def create_calendar_event(summary, start_datetime, end_datetime):
    service = get_calendar_service()

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_datetime,
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": "Asia/Kolkata",
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return {
        "summary": created_event.get("summary"),
        "start": created_event["start"].get("dateTime"),
        "link": created_event.get("htmlLink"),
    }


if __name__ == "__main__":

    print("Creating test event...\n")

    result = create_calendar_event(
        "AI Agent Test",
        "2026-09-26T17:00:00+05:30",
        "2026-09-26T17:30:00+05:30"
    )

    print("Event created successfully!")
    print("Title:", result["summary"])
    print("Start:", result["start"])
    print("Link:", result["link"])