import sqlite3

db_path = "data/chinook.db"

conn = sqlite3.connect(
    f"file:{db_path}?mode=ro",
    uri=True
)

try:
    conn.execute("SELECT * FROM Artist LIMIT 5")
    print("SELECT succeeded")

    conn.execute("DELETE FROM Artist WHERE ArtistId = 1")
    print("ERROR: DELETE succeeded!")

except sqlite3.Error as e:
    print("Write blocked:")
    print(e)

finally:
    conn.close()
