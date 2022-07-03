def encrypt(message,n,e, block_size=2):
    encrypted_blocks = []
    ciphertext = -1

    if (len(message) > 0):
        ciphertext = ord(message[0])

    for i in range(1, len(message)):
        if (i % block_size == 0):
            encrypted_blocks.append(ciphertext)
            ciphertext = 0

        # multiply by 1000 to shift the digits over to the left by 3 places
        # because ASCII codes are a max of 3 digits in decimal
        ciphertext = ciphertext * 1000 + ord(message[i])

    # add the last block to the list
    encrypted_blocks.append(ciphertext)

    # encrypt all of the numbers by taking it to the power of e
    # and modding it by n
    for i in range(len(encrypted_blocks)):
        encrypted_blocks[i] = str((encrypted_blocks[i]**e) % n)

    encrypted_message = "".join(encrypted_blocks)

    return str(encrypted_message)
from secrets import SystemRandom
from random import randrange
from math import gcd
from decimal import Decimal
from miller_rabin import miller_rabin

# Public exponent e shall be 2**16 < e < 2**256. FIPS 186-4. B.3.1
E = 65537

def getprime(bits: int) -> int:
    """Generate a random bits size prime number"""
    
    secure_randrange = SystemRandom().randrange
    
    #  Prime shall be (lowlimit < p < 2**bits-1). FIPS 186-4. B.3.1
    lowlimit = int(Decimal(2**0.5) * Decimal(2**(bits - 1)))
    lowlimit |= 1 # n += 1 if n is odd
    highlimit = 2**bits    
    while True:
        p = secure_randrange(lowlimit, highlimit, 2)
        
        # (p–1) shall be relatively prime to e. FIPS 186-4. B.3.1
        if gcd(E, p - 1) == 1:            
            if miller_rabin(p):
                return p

def rsa_keys(nlen: int) -> [int, int]:
    """Get public and private keys.
    Method: FIPS 186-4, Appendix B.3.3.
    Using these method p, q may be generated with lengths of 1024 or 1536 bits
    (512 bits shall not). FIPS186-4. Appendix B.3.1. Criteria for IFC Key Pairs
    """    

    if nlen not in (2048, 3072):
        print('Error. Use bits == 2048 or 3072')
        return 0, 0

    bits = nlen//2
    p = getprime(bits)
    while True:
        q = getprime(bits)
        
        # FIPS 186-4. B.3.1
        if abs(p - q) > 2**(bits-100):

            # Euler's totient function.
            phi = (p - 1) * (q - 1)

            # Verify that phi and e are coprime. FIPS 186-4. B.3.1
            if gcd(E, phi) == 1:
                n = p * q
                
                # Private (or decryption) exponent d
                d = pow(E, -1, phi)
                
                # If phi ≤ d ≤ 2**(nlen//2), new p, q, d shall be determined.
                if 2**bits < d < phi:
                    public_key = (E, n)
                    private_key = (d, n)
                    return public_key, private_key


if __name__ == '__main__':
    RSA_KEY = rsa_keys(2048)
    #print(RSA_KEY[0])
    print(RSA_KEY[1][0])
    print(RSA_KEY[1][1])
