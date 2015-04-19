from whisper import _utils, _crypto

import inspect
import sqlite3
import json
import os

def init_db():
  
  try:
    db = sqlite3.connect("whisper/db/whisper.db")
    c = db.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS messages("
      "id INT PRIMARY KEY,"
      "sender TEXT,"
      "content TEXT,"
      "owner TEXT,"
      "expiration_date TEXT,"
      "self_destruct TEXT,"
      "password TEXT)"
    )

    c.execute("CREATE TABLE IF NOT EXISTS stats("
      "id INT PRIMARY KEY,"
      "sent INT)"
    )

    db.commit()
    db.close()
    
  except Exception as e: # pragma: no cover
    raise Exception("Couldn't initialize DB. ", e)

def init_config():
  # Worth noting because this uses dicts, there is no way to predict the order it will be written to disk.
  # Consider using ordered tuples if more config options are necessary in the future.

  if not os.path.exists('./config'):
    with open("./config", "w") as f:
      f.write(inspect.cleandoc(
        r'''
        {
          "api_key": "",
          "domain": "yourdomain.com",
          "salt": "%s",
          "private_key": ""
        }''' % _utils.gen_id(10)) + '\n')

  try:
    with open("./config", "r") as f:
      data = json.load(f)

  except Exception as e: # pragma: no cover
    raise Exception("Failed to load config! ", e)

  if data.get("api_key") == "" or data.get("api_key") == None:
    raise Exception("API Key not specified in config. Sign up at http://mailgun.com")

  if data.get("domain") == "yourdomain.com":
    raise Exception("Domain not specified in config. Change yourdomain.com to the domain you configured on http://mailgun.com.")

  if data.get("salt") == "" or data.get("salt") == None: # pragma: no cover
    data['salt'] = _utils.gen_id(10)

    with open("./config", "w") as f:
      json.dump(data, f, indent=2)

  if data.get("private_key") == "" or data.get("private_key") == None:
    key = _crypto.WhisperKey()
    data['private_key'] = key.get_private_key(stringify=True)

    with open("./config", "w") as f:
      json.dump(data, f, indent=2)

  if data.get("public_key") == "" or data.get("public_key") == None:
    key = _crypto.WhisperKey(data.get("private_key"))
    data['public_key'] = key.get_public_key(stringify=True)

    with open("./config", "w") as f:
      json.dump(data, f, indent=2)
  
  return data