# Diffie-Hellman
p = 23
g = 5
a = 6   # Private key of A
b = 15  # Private key of B

A = pow(g, a, p)
B = pow(g, b, p)
print("Public key of A:", A)
print("Public key of B:", B)

# Secret keys
secret_A = pow(B, a, p)
secret_B = pow(A, b, p)
print("Secret key (A):", secret_A)
print("Secret key (B):", secret_B)
