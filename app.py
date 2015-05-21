from bottle import Bottle, TEMPLATE_PATH, static_file, request, template, run
from bottle_sqlite import SQLitePlugin

from whisper import _database
from whisper import _models
from whisper import _utils
from whisper import _init

import datetime, json, sys

# Extend the bottle class to initialize the DB and config
class WhisperApp(Bottle):
 
  def __init__(self, catchall=True, autojson=True):
    self.app_config = _init.init_config() # Necessary due to naming conflicts in the Bottle class
    self.database = _database
    self.utils = _utils
    self.models = _models
    self.private_key = self.models.WhisperKey(self.app_config.get("private_key"))

    _init.init_db()
    super().__init__()

app = WhisperApp()
app.install(SQLitePlugin(dbfile="whisper/db/whisper.db"))
TEMPLATE_PATH.insert(0, 'whisper/views')

# Todo: add cookies.
@app.route('/', template="index")
def index(db):
  sent = app.database.get_stats(db)
  
  if sent is None:
    return dict(sent=None)

  else:
    return dict(sent=sent[0])

@app.route('/faq', template="faq")
def faq():
  return dict()

# Todo: Allow the original sender to view and optionally destroy message using cookies.
@app.route('/disposable/<message_id>')
@app.route('/disposable/<message_id>/<auth>')
def view_whisper(message_id, db, auth=None):
  message = app.database.get_disposable(message_id, db)

  if message is None:
    return template("disposable_expired")

  sender, content, password = message

  if password:
    if auth is not None and auth == password:
      app.database.delete_disposable(message_id, db)
      app.database.update_stats("opened", db)
      return template("disposable", sender=sender, content=content)  

    return template("disposable_auth", sender=sender, message_id=message_id)
  
  app.database.delete_disposable(message_id, db)
  app.database.update_stats("opened", db)
  return template("disposable", sender=sender, content=content)

@app.post('/disposable/verify')
def verify_whisper(db):
  query = request.forms.get('password')
  message_id = request.forms.get('message_id')

  message = app.database.get_disposable(message_id, db)

  if message is None:
    return json.JSONEncoder().encode({
      "success": "false"
    })

  sender, content, password = message
  
  result = "true" if password == query else "false"

  return json.JSONEncoder().encode({
    "success": result
  })

@app.post('/send')
def send_whisper(db):
  # If performance ever becomes a problem, implement a global 
  # message queue. Extremely unlikely performance will ever be a concern, 
  # but this function is a potential bottleneck.
  sender = request.forms.get('sender') or "Anonymous"
  content = request.forms.get('content')
  options = request.forms.get('options')

  # Check for illegal option combinations
  if "p" in options and "t" in options:
    return json.JSONEncoder().encode({
      "success": "false",
      "response": "Password protection and Two-Factor Authentication cannot be enabled at the same time."
    })

  if len(options) > 1 and "m" not in options:
    return json.JSONEncoder().encode({
      "success": "false",
      "response": "These options are not possible without 'm' (email) specified."
    })

  try:
    message_id = app.utils.gen_id()
    message = app.models.WhisperMessage(message_id, sender, contents, options, db)
    url = "http://%s/disposable/%s" % (app.app_config.get("domain"), message_id)

    # e -- Encrypt message using PyNaCl.
    if "e" in options:
      recipient_key = app.models.WhisperKey()
      message.encrypt(recipient_key, app.private_key)

    # m -- Send whisper over email
    if "m" in options:
      message.format()

      if len(options) > 1:
        message.save()
        html = template("email", sender=sender, content=message.formatted_content, url=url, domain=app.app_config.get("domain"))
        
        if "e" in options:
          response = app.utils.send_email(address=message.options.get("m"), sender=sender, content=html, config=app.app_config, key=message.options.get("e"))
        
        else:
          response = app.utils.send_email(address=message.options.get("m"), sender=sender, content=html, config=app.app_config)

      else:
        html = template("email", sender=sender, content=message.formatted_content, url=None, domain=app.app_config.get("domain"))
        response = app.utils.send_email(address=options.get("m"), sender=sender, content=html, config=app.app_config)

    else:
      message.save()
      app.database.update_stats("sent", db)

      response = json.JSONEncoder().encode({
        "success": "true",
        "response": url
      })

    return response

  except Exception as e:
    return json.JSONEncoder().encode({
      "success": "false",
      "response": str(e)
    })

@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='./whisper/static/')

@app.route('/test/<email_address>')
def send_test(email_address):
  sender = "Gary Provost"
  address = email_address
  content = (
    "&ldquo;This sentence has five words. Here are five more words. Five-word sentences are fine. But several together become monotonous. Listen to what is happening. The writing is getting boring. The sound of it drones. It's like a stuck record. The ear demands some variety.\n\n"
    "Now listen.\n"
    "I vary the sentence length, and I create music. Music. The writing sings.\n"
    "It has a pleasant rhythm, a lilt, a harmony.\n"
    "I use short sentences.\n"
    "And I use sentences of medium length.\n"
    "And sometimes, when I am certain the reader is rested, I will engage him with a sentence of considerable length, a sentence that burns with energy and builds with all the impetus of a crescendo, the roll of the drums, the crash of the cymbals&emdash;sounds that say listen to this, it is important.&rdquo; "
  ).encode('ascii', 'xmlcharrefreplace')

  html = template("email", sender=sender, content=content, url=None, domain=app.app_config.get("domain"))
  #response = app.utils.send_email(address=address, sender=sender, content=html, config=app.app_config)

  return html

# Never use this in production.
if "debug" in sys.argv:
  if "vagrant" in sys.argv:
    # 0.0.0.0 will not play nice with your other listening addresses.
    app.run(host="0.0.0.0", port=8080, debug=True, reloader=True)

  else:
    app.run(host="localhost", port=8080, debug=True, reloader=True)    

else:
  # Run in production
  app.run(port=8080, workers=4, server='gunicorn')