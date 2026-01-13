import sqlite3

conn = sqlite3.connect("memory.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    mood TEXT,
    facts TEXT
)
""")
conn.commit()

def get_user(user_id):
    c.execute("SELECT * FROM users WHERE user_id=?", (str(user_id),))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (str(user_id), "", "neutral", ""))
        conn.commit()
        return {"name":"", "mood":"neutral", "facts":""}
    return {"name":row[1], "mood":row[2], "facts":row[3]}

def save_user(user_id, name=None, mood=None, facts=None):
    user = get_user(user_id)
    if name is not None: user["name"] = name
    if mood is not None: user["mood"] = mood
    if facts is not None: user["facts"] = facts

    c.execute("""
    UPDATE users SET name=?, mood=?, facts=? WHERE user_id=?
    """, (user["name"], user["mood"], user["facts"], str(user_id)))
    conn.commit()
