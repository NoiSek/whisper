from whisper import _database, _utils
import datetime

class WhisperMessage():
  def __init__(self, unique_id, sender, content, options, db):
    self.unique_id = id
    self.sender = sender
    self.content = content
    self.options = options
    self.db = db

    self.formatted_content = None

    # o -- Owner, retain the ability to view and delete whispers after transmission.
    if "o" in self.options:
      self.options['o'] = _utils.gen_id()

    # x -- Expire after a given time
    if "x" in self.options:
      current_time = datetime.datetime.now()
        
      if options['x'] == 1:
        self.options['x'] = str(current_time + datetime.timedelta(minutes=10))

      elif options['x'] == 2:
        self.options['x'] = str(current_time + datetime.timedelta(hours=1))

      elif options['x'] == 3:
        self.options['x'] = str(current_time + datetime.timedelta(days=1))

      else:
        self.options['x'] = str(current_time + datetime.timedelta(weeks=1))

    # t -- Two Factor Authentication, 2-factor over SMS.
    if "t" in options:
      password = _utils.gen_password()
      self.options['p'] = password
      number, country = _utils.format_number(number=options.get("t"))

      sms_content = (
        "Someone has sent you a Whisper. "
        "Use this code along with the URL sent to your email address to read your whisper: %s" 
        % (password)
      )
      _utils.send_sms(number=number, country=country, message=sms_content)

  def digest(self):
    return {
      "unique_id": self.unique_id,
      "sender": self.sender,
      "content": self.formatted_content or self.content,
      "options": self.options
    }

  def encrypt(self, recipient_key, app_key):
    self.content = app_key.encrypt_message(self.content, recipient_key)
    self.options['e'] = recipient_key.get_private_key(as_image=True)

  def format(self):
    # A messy way of compiling all of the flags down into one description.
    if len(self.options) > 1:
      self.formatted_content = "Someone has sent you a whisper anonymously.\n"

      if "e" in self.options:
        self.formatted_content += (
          "To open this message, you will need to use the image attached to unlock your encrypted whisper. "
          "This image is a private key, keep it safe! Save it to your computer and drag and drop the key "
          "on your message when ready: "
        )

      if "t" in self.options:
        self.formatted_content += (
          "To open this message, use the confirmation code sent over SMS to (%s) *** %s.\n" 
          % (self.options.get("t")[:3], self.options.get("t")[6:])
        )

      if "x" in self.options and "d" in self.options:
        self.formatted_content += (
          "The contents of this message will be destroyed once viewed or "
          "the following date has been reached: %s. View your message here:"
          % (self.options.get("x"))
        )
      
      elif "x" in self.options:
        formatted_content += (
          "The contents of this message will be destroyed once "
          "the following date has been reached: %s. View your message here: "
          % (self.options.get("x"))
        )

      elif "d" in self.options:
        self.formatted_content += "The contents of this message will be destroyed upon viewing: "

      elif "t" in self.options:
        self.formatted_content += "View your message here: "

  def save(self):
    _database.create_disposable(self.digest(), self.db)