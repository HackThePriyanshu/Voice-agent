import sqlite3


DB_NAME = "memory.db"


def create_memory_table():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_message(role, message):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO conversation (role, message) VALUES (?, ?)",
        (role, message)
    )

    conn.commit()
    conn.close()


def get_messages():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, message
        FROM conversation
        ORDER BY id
    """)

    messages = cursor.fetchall()

    conn.close()

    return messages


def get_recent_messages(limit=10):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, message
        FROM conversation
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    messages = cursor.fetchall()

    conn.close()

    # Oldest → newest order
    messages.reverse()

    return messages

def save_fact(fact):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM facts WHERE fact = ?",
        (fact,)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO facts (fact) VALUES (?)",
            (fact,)
        )

    conn.commit()
    conn.close()

def get_facts():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT fact
        FROM facts
        ORDER BY id
    """)

    facts = cursor.fetchall()

    conn.close()

    return [fact[0] for fact in facts]

def remove_duplicate_facts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM facts
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM facts
            GROUP BY fact
        )
    """)

    conn.commit()
    conn.close()




if __name__ == "__main__":
    create_memory_table()
    print("✅ Memory database created successfully!")