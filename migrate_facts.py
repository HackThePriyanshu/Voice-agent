
import sqlite3
from memory import save_fact

SOURCE_DB = "memory.db"

conn = sqlite3.connect(SOURCE_DB)
cursor = conn.cursor()

cursor.execute("""
    SELECT user_id, fact
    FROM facts
    WHERE user_id IS NOT NULL
""")

facts = cursor.fetchall()
conn.close()

migrated = 0

for user_id, fact in facts:
    save_fact(user_id, fact)
    migrated += 1

print(f"Migration complete. Facts processed: {migrated}")
