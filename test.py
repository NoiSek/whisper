import random
import string

def gen_password():
  chars = string.digits
  
  password = "".join([random.choice(chars) for x in range(6)])
  password = "%s-%s" % (password[:3], password[3:])
  return password

print(gen_password())