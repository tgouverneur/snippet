import string
import random

def randString(size=32, chars=string.ascii_letters + string.digits):
         return ''.join(random.choice(chars) for x in range(size))
