import sqlite3

def create_disposable(digest, db):
  c = db.cursor()
  c.execute("INSERT INTO messages "
    "VALUES (?, ?, ?, ?, ?, ?)",
    (
      digest.get("unique_id"),
      digest.get("sender"),
      digest.get("content"),
      digest['options'].get("o", "None"),
      digest['options'].get("x", "None"),
      digest['options'].get("d", "None"),
      digest['options'].get("p", "None")
    )
  )

  db.commit()

def get_disposable(message_id, db):
  c = db.cursor()
  c.execute("SELECT sender, content, password FROM messages WHERE id=?", (message_id,))

  result = c.fetchone()

  if result is None:
    return None
  
  sender, content, password = result

  return (sender, content, password)

def delete_disposable(message_id, db):
  c = db.cursor()
  c.execute("DELETE FROM messages WHERE id=?", (message_id,))
  
  db.commit()

def get_stats(db):
  c = db.cursor()
  c.execute("SELECT sent "
    "FROM stats "
    "WHERE id = 1" 
  )
  
  return c.fetchone()

def update_stats(*args):
  # Hamstringed to track sent messages only for the foreseeable future, tracking the type
  # and number of messages both opened and sent could potentially be a security and privacy concern.
  event, db = args

  c = db.cursor()

  c.execute("INSERT OR IGNORE INTO stats "
    "VALUES (1, 0)"
  )

  c.execute("INSERT OR IGNORE INTO stats_historical "
    "VALUES(date('now'), 0)"
  )

  if event is "sent":
    c.execute("UPDATE stats "
      "SET sent = sent + 1 "
      "WHERE id = 1 "
    )

    c.execute("UPDATE stats_historical "
      "SET sent = sent + 1 "
      "WHERE date = date('now')"
    )

  db.commit()