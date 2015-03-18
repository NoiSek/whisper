from whisper import _utils

import nacl.encoding
import nacl.public
import nacl.utils
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
      "password TEXT)"
    )

    c.execute("CREATE TABLE IF NOT EXISTS stats("
      "id INT PRIMARY KEY,"
      "sent INT,"
      "sent_plaintext INT,"
      "sent_disposable INT,"
      "sent_twofactorauth INT,"
      "messages_opened INT)"
    )

    c.execute("CREATE TABLE IF NOT EXISTS stats_historical("
      "date DATE PRIMARY KEY,"
      "sent INT,"
      "sent_plaintext INT,"
      "sent_disposable INT,"
      "sent_twofactorauth INT,"
      "messages_opened INT)"
    )

    db.commit()
    db.close()
    
  except Exception as e:
    raise Exception("Couldn't initialize DB. ", e)

def init_config():

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

  except Exception as e:
    raise Exception("Failed to load config! ", e)

  if data.get("api_key") == "":
    raise Exception("API Key not specified in config. Sign up at http://mailgun.com")

  if data.get("domain") == "yourdomain.com":
    raise Exception("Domain not specified in config.")

  if data.get("salt") == "":
    data['salt'] = _utils.gen_id(10)

    with open("./config", "w") as f:
      json.dump(data, f, indent=2)

  if data.get("private_key") == "":
    data['private_key'] = (
      nacl.public.PrivateKey.generate()
      .encode(encoder=nacl.encoding.URLSafeBase64Encoder)
      .decode("utf-8")
    )

    with open("./config", "w") as f:
      json.dump(data, f, indent=2)

  if data.get("public_key") is None:
    data['public_key'] = (
      nacl.public.PrivateKey(data['private_key'], encoder=nacl.encoding.URLSafeBase64Encoder)
      .public_key
      .encode(encoder=nacl.encoding.URLSafeBase64Encoder)
      .decode("utf-8")
    )

    with open("./config", "w") as f:
      json.dump(data, f, indent=2)
  
  return data