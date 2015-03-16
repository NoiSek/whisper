from whisper import _database, _init, _utils
import unittest
import sqlite3
import random
import json

class DatabaseTestCase(unittest.TestCase):
  def setUp(self):
    _init.init_db()
    self.db = sqlite3.connect("whisper/db/whisper.db")

  def test_create_disposable(self):
    # Generate a random ID to test disposable creation
    random_ID = str(round(random.random() * 100000))
    _database.create_disposable(random_ID, "sender", "content", "password", self.db)

    # Grab message from DB
    c = self.db.cursor()
    c.execute("SELECT sender, content, password FROM messages WHERE id=?", (random_ID,))
    result = c.fetchone()

    sender, content, password = result
    self.assertEqual((sender, content, password), ("sender", "content", "password"))

  def test_retrieve_disposable(self):
    # Generate a random ID to test disposable retrieval
    random_ID = str(round(random.random() * 100000))

    # Insert message into DB
    c = self.db.cursor()
    c.execute("INSERT INTO messages "
      "VALUES (?, ?, ?, ?)",
      (random_ID, "sender", "content", "password")
    )

    self.db.commit()
    
    message = _database.get_disposable(random_ID, self.db)
    self.assertEqual(message, ("sender", "content", "password"))

class InitTestCase(unittest.TestCase):  
  def test_init_db(self):
    _init.init_db()
    db = sqlite3.connect("whisper/db/whisper.db")
    
    self.assertIsInstance(db, sqlite3.Connection)

  def test_init_config(self):
    with self.assertRaises(Exception) as e:
      try: 
        _init.init_config()

      except Exception:
        self.assertEqual(e.msg, "API Key not specified in config. Sign up at http://mailgun.com")

    with open("./config", "r") as f:
      self.data = json.load(f)

    with open("./config", "w") as f:
      self.data['api_key'] = "testapikey"
      json.dump(self.data, f, indent=2)

    with self.assertRaises(Exception) as e:
      try: 
        _init.init_config()

      except Exception:
        self.assertEqual(e.msg, "Domain not specified in config.")

    with open("./config", "w") as f:
      self.data['domain'] = "testunittests.com"
      json.dump(self.data, f, indent=2)

    config = _init.init_config()  
    self.assertIsInstance(config, dict)