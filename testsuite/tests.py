from whisper import _database, _init, _utils, _crypto
import unittest
import sqlite3
import random
import json
import os

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

  def test_delete_disposable(self):
    # Generate a random ID to test disposable deletion
    random_ID = str(round(random.random() * 100000))

    # Insert message into DB
    c = self.db.cursor()
    c.execute("INSERT INTO messages "
      "VALUES (?, ?, ?, ?)",
      (random_ID, "sender", "content", "password")
    )

    self.db.commit()

    _database.delete_disposable(random_ID, self.db)
    
    message = _database.get_disposable(random_ID, self.db)
    self.assertEqual(message, None)

  def test_get_stats(self):
    c = self.db.cursor()
    c.execute("INSERT OR IGNORE INTO stats "
      "VALUES (1, 0)"
    )

    self.db.commit()

    stats = _database.get_stats(self.db)
    self.assertIsInstance(stats, tuple)
    self.assertTrue(len(stats) == 1)

  def test_update_stats(self):
    # Create a point of reference
    def fetch_stats(db):
      c = db.cursor()
      c.execute("SELECT sent "
        "FROM stats "
        "WHERE id = 1"
      )

      return c.fetchone()
    
    old_stats = fetch_stats(self.db)
    
    # Update stats and make sure the result is old stats + 1
    _database.update_stats("sent", self.db)
    new_stats = fetch_stats(self.db)

    self.assertEqual(int(new_stats[0]), int(old_stats[0]) + 1)

class InitTestCase(unittest.TestCase):  
  def test_init_db(self):
    _init.init_db()
    db = sqlite3.connect("whisper/db/whisper.db")
    
    self.assertIsInstance(db, sqlite3.Connection)

  def test_init_config(self):
    # Backup and delete existing config for testing, if it exists
    if os.path.exists('./config'):
      original_config = None
      
      with open('config', 'r') as f:
        original_config = f.read()
      
      with open('config.bak', 'w') as f:
        f.write(original_config)

      os.remove("./config")

    # Generate new config
    with self.assertRaises(Exception) as e:
      _init.init_config()

    self.assertTrue("API Key not specified in config. Sign up at http://mailgun.com" in str(e.exception))

    with open("./config", "r") as f:
      self.data = json.load(f)
      self.data['api_key'] = "testapikey"
      
    with open("./config", "w") as f:
      json.dump(self.data, f, indent=2)

    with self.assertRaises(Exception) as ex:
      _init.init_config()

    self.assertTrue("Domain not specified in config." in str(ex.exception))

    with open("./config", "w") as f:
      self.data['domain'] = "testunittests.com"
      json.dump(self.data, f, indent=2)

    config = _init.init_config()  
    self.assertIsInstance(config, dict)

    # Restore original config, if it exists.
    if os.path.exists('./config.bak'):
      original_config = None
      
      with open('config.bak', 'r') as f:
        original_config = f.read()

      with open('config', 'w') as f:
        f.write(original_config)

      os.remove("./config.bak")

class UtilsTestCase(unittest.TestCase):
  def test_gen_id(self):
    ID = _utils.gen_id()

    # Returns a 10 character string
    self.assertTrue(len(ID) is 10)
    self.assertIsInstance(ID, str)

    # No duplicates
    ID_list = [_utils.gen_id() for x in range(10)]
    self.assertTrue(len(set(ID_list)) is 10)

  def test_gen_password(self):
    password = _utils.gen_password()

    # Returns a 7 character string
    self.assertTrue(len(password) is 7)
    self.assertIsInstance(password, str)

  def test_format_number(self):
    formatted_number = _utils.format_number("1 (888) 555-5555")
    self.assertEqual(formatted_number, ('8885555555', 'united states'))

    formatted_number = _utils.format_number("1.888.555.5555")
    self.assertEqual(formatted_number, ('8885555555', 'united states'))

    formatted_number = _utils.format_number("888 555-5555")
    self.assertEqual(formatted_number, ('8885555555', 'united states'))

    with self.assertRaises(Exception) as e:
      formatted_number = _utils.format_number("fake number")

    self.assertTrue("Not a valid phone number." in str(e.exception))

  @unittest.skip("This cannot be safely tested without spamming.")
  def test_send_sms(self):
    #response = _utils.send_sms(None, None, None)
    pass

  @unittest.skip("This cannot be tested without an API key, or tested regularly without spamming.")
  def test_send_email(self):
    #response = _utils.send_email(None, None, None, None)
    pass

class CryptoTestCase(unittest.TestCase):
  def test_create_key(self):
    # In the future consider setting as self.nacl within setUp()
    import nacl.public
    import nacl.encoding

    with self.assertRaises(Exception) as e:
      fail_key = _crypto.WhisperKey("Bad String")

    self.assertTrue("Error generating key from given str or bytes object:" in str(e.exception))

    with self.assertRaises(Exception) as e:
      fail_key = _crypto.WhisperKey(123)

    self.assertTrue("Not a valid key." in str(e.exception))

    strkey = "zWoSH8+RYeqJt+UaJI9E9mbmcUQWDh9gjBYfWb5ziLk="
    self.assertIsInstance(_crypto.WhisperKey(strkey).get_private_key(), nacl.public.PrivateKey)

    key = _crypto.WhisperKey()
    otherkey = _crypto.WhisperKey()

    self.assertIsInstance(key.get_private_key(), nacl.public.PrivateKey)
    self.assertIsInstance(key.get_private_key(stringify=True), str)

    self.assertIsInstance(key.get_public_key(), nacl.public.PublicKey)
    self.assertIsInstance(key.get_public_key(stringify=True), str)

    # Use own private key to create a new WhisperKey obj
    key = _crypto.WhisperKey(key.get_private_key())

    self.assertIsInstance(key.get_private_key(), nacl.public.PrivateKey)
    self.assertIsInstance(key.get_private_key(stringify=True), str)

    self.assertIsInstance(key.get_public_key(), nacl.public.PublicKey)
    self.assertIsInstance(key.get_public_key(stringify=True), str)

  def test_encrypt_message(self):
    import nacl.public
    import nacl.encoding

    # Pre-generated keys for testing
    key = _crypto.WhisperKey("+Ras/eyqk/ASwkODnP6+fWDYSjLoPfGuouhpGV1QyJk=")
    otherkey_public = nacl.public.PublicKey("37hyRakD53ANLSUBvvYyf/iEuff7MmTn3ys/I1YBNg8=", encoder=nacl.encoding.Base64Encoder)

    # Test failure
    with self.assertRaises(Exception) as e:
      fail_encrypted_message = key.encrypt_message(
        message="Failure", 
        public_key=123
      )

    self.assertTrue("Invalid public key provided." in str(e.exception))

    # God save us all.
    nonce = bytes([x for x in range(24)])

    # Encrypt message using our pre-generated keys
    encrypted_message = key.encrypt_message(
      message="This is our test message, we'll see how it turns out in the end.", 
      public_key=otherkey_public, 
      nonce=nonce
    )

    self.assertIsInstance(encrypted_message, str)
    self.assertEqual(encrypted_message, "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXdgcorrdBhrx1Po1NtDJNSvFRxOdrfqsESGuxNu+aM+EeaZTSGvuOFvmROaU/86YqJis1h6yL9EDnE/6lqcM71/fqXgBOI+hiMRVBeaiAtVQ=")

  def test_decrypt_message(self):
    import nacl.public
    import nacl.encoding

    # Pre-generated keys for testing
    key = _crypto.WhisperKey("zWoSH8+RYeqJt+UaJI9E9mbmcUQWDh9gjBYfWb5ziLk=")
    otherkey_public = nacl.public.PublicKey("e6fmjnPg7xQVdddTt3JDWafhkZq2W2TsMxs7icKWbUs=", encoder=nacl.encoding.Base64Encoder)

    # Test failure
    with self.assertRaises(Exception) as e:
      fail_decrypted_message = key.decrypt_message(
        message="Failure",
        public_key=123
      )

    self.assertTrue("Invalid public key provided." in str(e.exception))

    # Decrypt our payload
    encrypted_message = "rZ7XgI1Kt3Eb5eMz6O2YT5qY53qdcDtxr+GbH9eirCKN2Vg782gABl6yACLQiZkbX/dEqNLbM+MhqrhWFzcXgvk1JxLvnxA6yw0a/KE4OxdtZJnGu9nzgntoMhy+9Azv611UjpH6VQI="
    decrypted_message = key.decrypt_message(
      message=encrypted_message, 
      public_key=otherkey_public
    )

    self.assertEqual(decrypted_message, "This is our test message, we'll see how it turns out in the end.")