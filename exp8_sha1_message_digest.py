import hashlib

message = input("Enter message: ")
msg_bytes = message.encode()
sha1 = hashlib.sha1(msg_bytes).hexdigest()
print("Message:", message)
print("SHA-1 Hash:", sha1)
