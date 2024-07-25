import sqlite3

def fetch_conversation_history(db_file='users.db'):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Fetch all records from the conversation_history table
    cursor.execute("SELECT name, email FROM users")
    rows = cursor.fetchall()

    # Print the conversation history
    print("Conversation History from Database:")
    for row in rows:
        email, name = row
        print(f"{name}: {email}")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    fetch_conversation_history()
