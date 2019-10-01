from Crypto.Util.number import *
from Crypto.Util.strxor import strxor
from Crypto.Cipher import AES
import random, libnum, os, string
from hashlib import sha256
import SocketServer
from util import generate_special_RSA
from flag import FLAG

BLOCK_SIZE = 16


def generate_RSA():
    p = getPrime(1024)
    q = getPrime(1024)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = libnum.invmod(e, phi)
    assert (e * d) % phi == 1
    return n, e, d


def encrypt(e, n, message, key):
    IV = os.urandom(16)
    AES_OFB = AES.new(key, AES.MODE_OFB, IV)
    enc = AES_OFB.encrypt(message.decode("hex"))
    encrypt_key = pow(bytes_to_long(key), e, n)
    return encrypt_key, enc, IV


def decrypt(enc, encrypt_key, IV, d, n):
    IV = IV.decode("hex")
    MASK = (1 << (BLOCK_SIZE * 8)) - 1
    encrypt_key = int(encrypt_key, 16)
    key = pow(encrypt_key, d, n) & MASK
    key = long_to_bytes(key).rjust(BLOCK_SIZE, "\x00")
    AES_OFB = AES.new(key, AES.MODE_OFB, IV)
    dec = AES_OFB.decrypt(enc.decode("hex"))
    return dec


class Task(SocketServer.BaseRequestHandler):
    def proof_of_work(self):
        proof = ''.join(
            [random.choice(string.ascii_letters + string.digits) for _ in xrange(20)])
        digest = sha256(proof).hexdigest()
        self.request.send("sha256(XXXX+%s) == %s\n" % (proof[4:], digest))
        self.request.send('Give me XXXX:')
        x = self.request.recv(10)
        x = x.strip()
        if len(x) != 4 or sha256(x + proof[4:]).hexdigest() != digest:
            return False
        return True

    def handle(self):
        if not self.proof_of_work():
            return
        self.request.settimeout(30)
        req = self.request
        n, e, d = generate_RSA()
        KEY = os.urandom(BLOCK_SIZE)
        print KEY.encode("hex")
        req.sendall("Give you public key:\nn : %s \ne : %s\n" % (n, e))
        req.sendall("Welcome to my complex encrypt system!\n")
        req.sendall("You can choose:\n 1. decrypt something\n 2. encrypt something\n 3. get the flag\n")
        while True:
            try:
                req.sendall('Give me your choice :')
                choice = req.recv(10).strip()
                choice = int(choice)
                if choice == 1:
                    req.sendall("Give me the cipher in hex encode:\n")
                    enc = req.recv(1024).strip()
                    req.sendall("Give me the encrypted key in hex encode:\n")
                    encrypt_key = req.recv(2048).strip()
                    req.sendall("Give me the IV in hex encode:\n")
                    IV = req.recv(1024).strip()
                    msg = decrypt(enc, encrypt_key, IV, d, n)
                    req.sendall("Your message: %s\n" % (msg.encode("hex")))
                elif choice == 2:
                    req.sendall("Give me the message in hex encode\n")
                    msg = req.recv(1024).strip()
                    encrypt_key, enc, IV = encrypt(e, n, msg, KEY)
                    req.sendall("enc_key: %s \nenc: %s\nIV: %s\n" % (encrypt_key, enc.encode("hex"), IV.encode("hex")))
                elif choice == 3:
                    n1, n2, e1, e2 = generate_special_RSA()
                    xor_key = (KEY * 10)[:len(FLAG)]
                    m = strxor(xor_key, FLAG)
                    req.sendall("Your flag:\n")
                    req.sendall("n1 = %s\n" % (n1))
                    req.sendall("n2 = %s\n" % (n2))
                    req.sendall("e1 = %s\n" % (e1))
                    req.sendall("e2 = %s\n" % (e2))
                    req.sendall("c1 = %s\n" % (pow(bytes_to_long(m), e1, n1)))
                    req.sendall("c2 = %s\n" % (pow(bytes_to_long(m), e2, n2)))
                    req.sendall("See you next time~\n")
                    return
            except Exception as e:
                req.sendall("Something error! %s\n" % e)


class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 54321
    print 'Run in port:54321'
    server = ThreadedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()
