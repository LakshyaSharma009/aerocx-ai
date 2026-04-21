# S-DES Key Generation
P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
P8 = [6, 3, 7, 4, 8, 5, 10, 9]

def permute(key, table):
    return ''.join(key[i - 1] for i in table)

def left_shift(bits, shifts):
    return bits[shifts:] + bits[:shifts]

def generate_keys(key):
    print("Original Key:", key)
    key = permute(key, P10)
    print("After P10:", key)
    left = key[:5]
    right = key[5:]
    # LS-1
    left = left_shift(left, 1)
    right = left_shift(right, 1)
    combined = left + right
    k1 = permute(combined, P8)
    print("K1:", k1)
    # LS-2
    left = left_shift(left, 2)
    right = left_shift(right, 2)
    combined = left + right
    k2 = permute(combined, P8)
    print("K2:", k2)
    return k1, k2

key_input = input("Enter 10-bit binary key: ")
generate_keys(key_input)


# DES Encryption & Decryption
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

def des_encrypt(plaintext, key):
    cipher = DES.new(key, DES.MODE_ECB)
    padded_text = pad(plaintext.encode(), DES.block_size)
    ciphertext = cipher.encrypt(padded_text)
    return ciphertext

def des_decrypt(ciphertext, key):
    cipher = DES.new(key, DES.MODE_ECB)
    decrypted = unpad(cipher.decrypt(ciphertext), DES.block_size)
    return decrypted.decode()

key = b'8bytekey'  # must be 8 bytes
plaintext = input("Enter message: ")
cipher = des_encrypt(plaintext, key)
print("Encrypted:", cipher)
decrypted = des_decrypt(cipher, key)
print("Decrypted:", decrypted)
