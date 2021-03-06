import nacl.encoding
import nacl.public
import nacl.utils

class WhisperKey():
  def __init__(self, key=None):
    if key is None:
      self.generate_keypair()

    else:
      if isinstance(key, bytes) or isinstance(key, str):
        try:
          self._private_key = nacl.public.PrivateKey(key, encoder=nacl.encoding.Base64Encoder)

        except Exception as e:
          raise Exception("Error generating key from given str or bytes object: ", e)

      elif isinstance(key, nacl.public.PrivateKey):
        self._private_key = key

      else:
        raise Exception("Not a valid key.")

  def generate_keypair(self):
    self._private_key = nacl.public.PrivateKey.generate()

  def get_private_key(self, stringify=False, as_image=False, image=None):
    if stringify:
      return (
        self._private_key
        .encode(encoder=nacl.encoding.Base64Encoder)
        .decode("utf-8")
      )

    elif as_image:
      # Accessible afterwards by parsing all characters after 2321.
      # If the image changes, the ability to parse it changes as well.
      # Wise to include an identifier in the future for the use of custom images.
      file_contents = None

      if image:
        file_contents = image.read()
      
      else:
        with open("whisper/static/img/key_small.png", "br") as f:
          file_contents = f.read()

        private_key = self._private_key.encode(encoder=nacl.encoding.Base64Encoder)
        file_contents += private_key

      return file_contents

    else:
      return self._private_key

  def get_public_key(self, stringify=False):
    public_key = self._private_key.public_key

    if stringify:
      return (
        public_key
        .encode(encoder=nacl.encoding.Base64Encoder)
        .decode("utf-8")
      )

    else:
      return public_key

  def encrypt_message(self, message, public_key, nonce=None):
    # Verify that we can convert the public_key to an nacl.public.PublicKey instance
    if isinstance(public_key, nacl.public.PublicKey):
      pass

    elif isinstance(public_key, str) or isinstance(public_key, bytes): # pragma: no cover
      public_key = nacl.public.PublicKey(public_key, encoder=nacl.encoding.Base64Encoder)

    elif isinstance(public_key, WhisperKey): # pragma: no cover
      public_key = public_key.get_public_key()

    else:
      raise Exception("Invalid public key provided.")

    # Make sure our message is a bytes object, or convert it to one.
    if isinstance(message, bytes): # pragma: no cover
      pass

    elif isinstance(message, str):
      message = bytes(message, "utf-8")

    else: # pragma: no cover
      raise Exception("Message is not bytes or str.")

    box = nacl.public.Box(self._private_key, public_key)
    nonce = nonce or nacl.utils.random(24)
    
    # Message will be prepended with a 32 character nonce, which can be parsed out elsewhere.
    encrypted_message = box.encrypt(message, nonce, encoder=nacl.encoding.Base64Encoder)
    return encrypted_message.decode("utf-8")

  def decrypt_message(self, message, public_key):
    # Verify that we can convert the public_key to an nacl.public.PublicKey instance
    if isinstance(public_key, nacl.public.PublicKey):
      pass

    elif isinstance(public_key, str) or isinstance(public_key, bytes): # pragma: no cover
      public_key = nacl.public.PublicKey(public_key, encoder=nacl.encoding.Base64Encoder)

    elif isinstance(public_key, WhisperKey): # pragma: no cover
      public_key = public_key.get_public_key()

    else:
      raise Exception("Invalid public key provided.")

    # Make sure our message is a bytes object, or convert it to one.
    if isinstance(message, bytes): # pragma: no cover
      pass

    elif isinstance(message, str):
      message = bytes(message, "utf-8")

    else: # pragma: no cover
      raise Exception("Message is not bytes or str.")

    box = nacl.public.Box(self._private_key, public_key)

    nonce = message[:32]
    _message = message[32:]

    encrypted_message = nacl.utils.EncryptedMessage(message)
    decrypted = box.decrypt(encrypted_message, encoder=nacl.encoding.Base64Encoder)

    return decrypted.decode("utf-8")

if __name__ == "__main__": # pragma: no cover
  sender = WhisperKey()
  receiver = WhisperKey()

  nonce = bytes([x for x in range(24)])

  out_message = sender.encrypt_message(
    message="This is our test message, we'll see how it turns out in the end.",
    public_key=receiver,
    nonce=nonce
  )

  print("Our private key")
  print("================================================")
  print(sender.get_private_key(stringify=True))

  print("\n")

  print("Their public key")
  print("================================================")
  print(receiver.get_public_key(stringify=True))

  print("\n")

  print("Their private key")
  print("================================================")
  print(receiver.get_private_key(stringify=True))

  print("\n")

  print("Our public key")
  print("================================================")
  print(sender.get_public_key(stringify=True))

  print("\n")

  print("Final output message")
  print("================================================")
  print(out_message)

  print("\n")

  print("Decrypted")
  print("================================================")
  print(receiver.decrypt_message(message=out_message, public_key=sender.get_public_key()))