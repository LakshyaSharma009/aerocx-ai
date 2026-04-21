# SHA-1 Hash
import hashlib

message = input("Enter message: ")
msg_bytes = message.encode()
sha1 = hashlib.sha1(msg_bytes).hexdigest()
print("Message:", message)
print("SHA-1 Hash:", sha1)


# MD5 Hash
import hashlib

text = input("Enter message: ")
data = text.encode()
digest = hashlib.md5(data).hexdigest()
print("Message:", text)
print("MD5 Digest:", digest)
