from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


requiredParams = {
    'encode': {
        'publicKey': 'The filename of the public key, ' +
        'matched to the private key used for decryption.'
    },
    'decode': {
        'privateKey': 'The filename of the private key, ' +
        'matched to the public key used for decryption.'
    }
}


def encode(data, params):
    keyString = open(params['publicKey']).read()
    key = RSA.importKey(keyString)
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(data)
    return ciphertext


def decode(data, params):
    keyString = open(params['privateKey']).read()
    key = RSA.importKey(keyString)
    cipher = PKCS1_OAEP.new(key)
    message = cipher.decrypt(data)
    return message
