import nacl.encoding
import nacl.public
import nacl.utils

def generate_keypair():
  private_key = (
    nacl.public.PrivateKey.generate()
    .encode(encoder=nacl.encoding.URLSafeBase64Encoder)
    .decode("utf-8")
  )

  public_key = (
    nacl.public.PrivateKey(private_key, encoder=nacl.encoding.URLSafeBase64Encoder)
    .public_key
    .encode(encoder=nacl.encoding.URLSafeBase64Encoder)
    .decode("utf-8")
  )

  return (private_key, public_key)

def encrypt_message(recipient_public_key, message, config):
  # Transform strings into their respective key objects
  whisper_private_key = nacl.public.PrivateKey(config.get("private_key"), encoder=nacl.encoding.Base64Encoder)
  recipient_public_key = nacl.public.PublicKey(recipient_public_key, encoder=nacl.encoding.Base64Encoder)
  
  box = nacl.public.Box(whisper_private_key, recipient_public_key)
  nonce = nacl.utils.random(24)
  
  encrypted_message = box.encrypt(message, nonce, encoder=nacl.encoding.Base64Encoder)
  decrypted_message = box.decrypt

  return encrypted_message