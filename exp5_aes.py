# AES SubBytes & ShiftRows (4x4 Matrix)
# Example AES state matrix
state = [
    [0x19, 0xa0, 0x9a, 0xe9],
    [0x3d, 0xf4, 0xc6, 0xf8],
    [0xe3, 0xe2, 0x8d, 0x48],
    [0xbe, 0x2b, 0x2a, 0x08]
]

# AES S-Box (partial for demo, use full in exam if needed)
sbox = [
    [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30,
     0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
    # (complete S-box required in real implementation)
]

def print_state(s):
    for row in s:
        print([hex(x) for x in row])
    print()

def sub_bytes(state):
    for i in range(4):
        for j in range(4):
            row = state[i][j] >> 4
            col = state[i][j] & 0x0F
            state[i][j] = sbox[row][col]
    return state

def shift_rows(state):
    state[1] = state[1][1:] + state[1][:1]
    state[2] = state[2][2:] + state[2][:2]
    state[3] = state[3][3:] + state[3][:3]
    return state

print("Original:")
print_state(state)
state = sub_bytes(state)
print("After SubBytes:")
print_state(state)
state = shift_rows(state)
print("After ShiftRows:")
print_state(state)


# AES Encryption & Decryption
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

key = b'This is a key123'  # 16 bytes

def encrypt(msg):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(msg.encode(), AES.block_size))
    return cipher.iv, ciphertext

def decrypt(iv, ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode()

msg = input("Enter message: ")
iv, encrypted = encrypt(msg)
print("Encrypted:", encrypted)
decrypted = decrypt(iv, encrypted)
print("Decrypted:", decrypted)
