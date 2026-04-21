import hashlib

text = input("Enter message: ")
data = text.encode()
digest = hashlib.md5(data).hexdigest()
print("Message:", text)
print("MD5 Digest:", digest)
