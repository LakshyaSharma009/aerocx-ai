# Rail Fence Cipher
def rail_fence_encrypt(text, depth=2):
    text = text.replace(" ", "").lower()
    rails = ['' for _ in range(depth)]
    row = 0
    direction = 1
    for char in text:
        rails[row] += char
        row += direction
        if row == 0 or row == depth - 1:
            direction *= -1
    return ''.join(rails).upper()

def rail_fence_decrypt(cipher, depth=2):
    n = len(cipher)
    # Create pattern
    pattern = [['\n' for _ in range(n)] for _ in range(depth)]
    row, direction = 0, 1
    for col in range(n):
        pattern[row][col] = '*'
        row += direction
        if row == 0 or row == depth - 1:
            direction *= -1
    # Fill pattern with ciphertext
    index = 0
    for i in range(depth):
        for j in range(n):
            if pattern[i][j] == '*' and index < n:
                pattern[i][j] = cipher[index]
                index += 1
    # Read plaintext
    result = ""
    row, direction = 0, 1
    for col in range(n):
        result += pattern[row][col]
        row += direction
        if row == 0 or row == depth - 1:
            direction *= -1
    return result.upper()

# Example
text = "meet me after the toga party"
cipher = rail_fence_encrypt(text, 2)
print("Cipher Text:", cipher)
plain = rail_fence_decrypt(cipher, 2)
print("Decrypted Text:", plain)


# Columnar Transposition Cipher
def encrypt_columnar(plaintext, key):
    plaintext = plaintext.replace(" ", "").lower()
    cols = len(key)
    rows = (len(plaintext) + cols - 1) // cols
    # Fill matrix row-wise
    matrix = [['x' for _ in range(cols)] for _ in range(rows)]
    k = 0
    for i in range(rows):
        for j in range(cols):
            if k < len(plaintext):
                matrix[i][j] = plaintext[k]
                k += 1
    # Read column-wise based on key
    ciphertext = ""
    for num in range(1, cols + 1):
        col = key.index(str(num))
        for row in range(rows):
            ciphertext += matrix[row][col]
    return ciphertext.upper()

def decrypt_columnar(ciphertext, key):
    ciphertext = ciphertext.lower()
    cols = len(key)
    rows = len(ciphertext) // cols
    matrix = [['' for _ in range(cols)] for _ in range(rows)]
    k = 0
    for num in range(1, cols + 1):
        col = key.index(str(num))
        for row in range(rows):
            matrix[row][col] = ciphertext[k]
            k += 1
    plaintext = ""
    for i in range(rows):
        for j in range(cols):
            plaintext += matrix[i][j]
    return plaintext.rstrip('x').upper()

# Example
key = "4312567"
text = "attack postponed until two am"
cipher = encrypt_columnar(text, key)
print("Cipher Text:", cipher)
plain = decrypt_columnar(cipher, key)
print("Decrypted Text:", plain)
