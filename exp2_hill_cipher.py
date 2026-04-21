import numpy as np

def mod_inverse_matrix(matrix, mod=26):
    det = int(round(np.linalg.det(matrix)))
    det_inv = pow(det % mod, -1, mod)
    matrix_adj = np.array(np.round(det * np.linalg.inv(matrix)), dtype=int)
    return (det_inv * matrix_adj) % mod

def hill_encrypt(plaintext, key_matrix):
    plaintext = plaintext.upper().replace(" ", "")
    n = len(key_matrix)
    while len(plaintext) % n != 0:
        plaintext += 'X'
    ciphertext = ""
    for i in range(0, len(plaintext), n):
        block = [ord(c) - ord('A') for c in plaintext[i:i+n]]
        encrypted_block = np.dot(key_matrix, block) % 26
        ciphertext += ''.join(chr(int(x) + ord('A')) for x in encrypted_block)
    return ciphertext

def hill_decrypt(ciphertext, key_matrix):
    inv_key = mod_inverse_matrix(key_matrix)
    n = len(key_matrix)
    plaintext = ""
    for i in range(0, len(ciphertext), n):
        block = [ord(c) - ord('A') for c in ciphertext[i:i+n]]
        decrypted_block = np.dot(inv_key, block) % 26
        plaintext += ''.join(chr(int(x) + ord('A')) for x in decrypted_block)
    return plaintext

# 2x2 key matrix
key_matrix = np.array([[3, 3], [2, 5]])

text = input("Enter message: ")
encrypted = hill_encrypt(text, key_matrix)
print("Encrypted:", encrypted)

decrypted = hill_decrypt(encrypted, key_matrix)
print("Decrypted:", decrypted)
