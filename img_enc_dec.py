import sys
import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import io
from PIL import Image
import base64
from base64 import b64decode
from io import BytesIO
from numpy import asarray

# This program encrypts a jpg With AES-256. The encrypted image contains more data than the original image (e.g. because of 
# padding, IV etc.). Therefore the encrypted image has one row more. Supported are CBC and ECB mode.

# Set mode
mode = AES.MODE_CBC
#mode = AES.MODE_ECB
if mode != AES.MODE_CBC and mode != AES.MODE_ECB:
    print('Only CBC and ECB mode supported...')
    sys.exit()

# Set sizes
keySize = 32
ivSize = AES.block_size if mode == AES.MODE_CBC else 0
    #
# Start Encryption ----------------------------------------------------------------------------------------------
#

# Load original image
# imageOrig = cv2.imread("original.jpg")
# rowOrig, columnOrig, depthOrig = imageOrig.shape

# Check for minimum width
# minWidth = (AES.block_size + AES.block_size) // depthOrig + 1
# if columnOrig < minWidth:
#     print('The minimum width of the image must be {} pixels, so that IV and padding can be stored in a single additional row!'.format(minWidth))
#     sys.exit()

# Display original image
# cv2.imshow("Original image", imageOrig)
# cv2.waitKey()

# Convert original image data to bytes
# imageOrigBytes = imageOrig.tobytes()

# Encrypt
key = b'\xf0\xcc\x7f\x85\x14)\xe7\x13\x8a\xc8j\xee\x0b&n\xf23\xbe\xeb\x0f\x85\xcb\xa3\xb4\xae\\\x93\x9d\x17\x0b4\xfc'
iv = b'^\\\xe6M~\xc3\x08\x81\xcd\xe2\xb5\xfb\x06\xa8\xa0\xc0'
def encrypt(imgInput):
    imageOrig = cv2.imread(imgInput)
    rowOrig, columnOrig, depthOrig = imageOrig.shape

    imageOrigBytes = imageOrig.tobytes()
    
    cipher = AES.new(key, AES.MODE_CBC, iv) if mode == AES.MODE_CBC else AES.new(key, AES.MODE_ECB)
    imageOrigBytesPadded = pad(imageOrigBytes, AES.block_size)
    ciphertext = cipher.encrypt(imageOrigBytesPadded)

    # Convert ciphertext bytes to encrypted image data
    #    The additional row contains columnOrig * DepthOrig bytes. Of this, ivSize + paddedSize bytes are used 
    #    and void = columnOrig * DepthOrig - ivSize - paddedSize bytes unused
    paddedSize = len(imageOrigBytesPadded) - len(imageOrigBytes)
    void = columnOrig * depthOrig - ivSize - paddedSize
    ivCiphertextVoid = iv + ciphertext + bytes(void)
    imageEncrypted = np.frombuffer(ivCiphertextVoid, dtype = imageOrig.dtype).reshape(rowOrig + 1, columnOrig, depthOrig)

    # Display encrypted image
    # cv2.imshow("Encrypted image", imageEncrypted)
    # cv2.waitKey()

    # Save the encrypted image (optional)
    #    If the encrypted image is to be stored, a format must be chosen that does not change the data. Otherwise, 
    #    decryption is not possible after loading the encrypted image. bmp does not change the data, but jpg does. 
    #    When saving with imwrite, the format is controlled by the extension (.jpg, .bmp). The following works:
    cv2.imwrite(imgInput, imageEncrypted)
    # imageEncrypted = cv2.imread("topsecretEnc.bmp")
    return imageEncrypted

def convertBase64toDataImg(img_data):
    img_data += '=='
    image = Image.open(BytesIO(b64decode(img_data.split(',')[1])))
    return image
#   
# Start Decryption ----------------------------------------------------------------------------------------------
#
def decrypt(imageEncrypted):
    # Convert encrypted image data to ciphertext bytes
    
    rowEncrypted, columnOrig, depthOrig = imageEncrypted.shape
    rowOrig = rowEncrypted - 1
    encryptedBytes = imageEncrypted.tobytes()

    iv = encryptedBytes[:ivSize]
    imageOrigBytesSize = rowOrig * columnOrig * depthOrig
    paddedSize = (imageOrigBytesSize // AES.block_size + 1) * AES.block_size - imageOrigBytesSize
    encrypted = encryptedBytes[ivSize : ivSize + imageOrigBytesSize + paddedSize]

    # Decrypt
    cipher = AES.new(key, AES.MODE_CBC, iv) if mode == AES.MODE_CBC else AES.new(key, AES.MODE_ECB)
    decryptedImageBytesPadded = cipher.decrypt(encrypted)
    decryptedImageBytes = unpad(decryptedImageBytesPadded, AES.block_size)

    # Convert bytes to decrypted image data
    # decryptedImage = np.frombuffer(decryptedImageBytes, imageEncrypted.dtype).reshape(rowOrig, columnOrig, depthOrig)
    
    # Display decrypted image
    # cv2.imshow("Decrypted Image", decryptedImage)
    # cv2.imwrite("topsecretDec.bmp", decryptedImage)
    # cv2.waitKey()

    return decryptedImageBytes

# Close all windows
cv2.destroyAllWindows()
def main():
    imageEncrypted = encrypt()
    decrypt(imageEncrypted)
if __name__ == '__main__':
    main()