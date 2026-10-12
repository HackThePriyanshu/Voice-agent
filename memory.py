
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(database_url)


def create_memory_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id BIGSERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    fact TEXT NOT NULL,
                    UNIQUE (user_id, fact)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS pending_calendar_events (
                    id BIGSERIAL PRIMARY KEY,
                    summary TEXT NOT NULL,
                    start_datetime TEXT NOT NULL,
                    end_datetime TEXT NOT NULL,
                    thread_id TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS pending_gmail_emails (
                    id BIGSERIAL PRIMARY KEY,
                    to_email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    thread_id TEXT
                )
            """)


# =========================
# FACT MEMORY
# =========================

def save_fact(user_id, fact):
    if not user_id:
        raise ValueError("user_id is required")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO facts (user_id, fact)
                VALUES (%s, %s)
                ON CONFLICT (user_id, fact) DO NOTHING
            """, (user_id, fact))


def get_facts(user_id):
    if not user_id:
        return []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT fact
                FROM facts
                WHERE user_id = %s
                ORDER BY id
            """, (user_id,))

            return [row[0] for row in cur.fetchall()]


# =========================
# CALENDAR PENDING MEMORY
# =========================

def save_pending_event(
    thread_id,
    summary,
    start_datetime,
    end_datetime
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM pending_calendar_events
                WHERE thread_id = %s
            """, (thread_id,))

            cur.execute("""
                INSERT INTO pending_calendar_events
                (summary, start_datetime, end_datetime, thread_id)
                VALUES (%s, %s, %s, %s)
            """, (
                summary,
                start_datetime,
                end_datetime,
                thread_id
            ))


def get_pending_event(thread_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT summary, start_datetime, end_datetime
                FROM pending_calendar_events
                WHERE thread_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (thread_id,))

            return cur.fetchone()


def clear_pending_event(thread_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM pending_calendar_events
                WHERE thread_id = %s
            """, (thread_id,))


# =========================
# GMAIL PENDING MEMORY
# =========================

def save_pending_gmail_email(
    thread_id,
    to_email,
    subject,
    body
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM pending_gmail_emails
                WHERE thread_id = %s
            """, (thread_id,))

            cur.execute("""
                INSERT INTO pending_gmail_emails
                (to_email, subject, body, thread_id)
                VALUES (%s, %s, %s, %s)
            """, (
                to_email,
                subject,
                body,
                thread_id
            ))


def get_pending_gmail_email(thread_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT to_email, subject, body
                FROM pending_gmail_emails
                WHERE thread_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (thread_id,))

            return cur.fetchone()


def clear_pending_gmail_email(thread_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM pending_gmail_emails
                WHERE thread_id = %s
            """, (thread_id,))
