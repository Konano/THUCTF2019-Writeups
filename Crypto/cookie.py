# -*- coding: utf-8 -*-
# @Author: NanoApe
# @Date:   2019-09-19 00:15:17
# @Last Modified by:   NanoApe
# @Last Modified time: 2019-09-19 09:49:19

import random
import sys
import os
import string
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.number import *
from Crypto.Util.strxor import strxor
import math
# import gmpy2
from libnum import *
from pwn import *
import hashpumpy

def proof_of_work(suffix, sig):
    for c1 in (string.ascii_letters + string.digits):
        for c2 in (string.ascii_letters + string.digits):
            for c3 in (string.ascii_letters + string.digits):
                for c4 in (string.ascii_letters + string.digits):
                    proof = c1+c2+c3+c4+suffix
                    digest = sha256(proof.encode('utf-8')).hexdigest()
                    if digest == sig:
                        return proof[:4]

def substr(s, a, b):
    return s[s.find(a)+len(a) : s.find(b)]

def check_cache(iv, cipher):
    global sig, conn
    conn.sendline((iv+cipher+sig).encode('hex'))
    result = conn.recvline()
    conn.recvuntil('Give me your cookie(hex):')
    return result[-2] == '!'

def get_middle(cipher):
    print(cipher.encode('hex'))
    global BLOCK
    iv = [chr(0) for i in range(BLOCK)]
    middle = [chr(0) for i in range(BLOCK)]
    for i in range(BLOCK):
        for j in range(i):
            iv[BLOCK-1 - j] = strxor(middle[BLOCK-1 - j], chr(i+1))
        fg = False
        for o in range(256):
            iv[BLOCK-1 - i] = chr(o)
            if check_cache("".join(iv), "".join(iv)+cipher):
                middle[BLOCK-1 - i] = strxor(iv[BLOCK-1 - i], chr(i+1))
                fg = True
                print(i, middle[BLOCK-1 - i])
                break
        if fg == False:
            exit()
    return "".join(middle)

def find_plain_text(iv, cipher):
    global BLOCK
    BLOCK = len(iv)
    plain_text = ''
    for i in range(len(cipher) // BLOCK):
        middle = get_middle(cipher[i*BLOCK : (i+1)*BLOCK])
        if i == 0:
            plain_text += strxor(middle, iv)
        else:
            plain_text += strxor(middle, cipher[(i-1)*BLOCK : i*BLOCK])
    return plain_text

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def get_cipher(cookie):
    global BLOCK
    cipher = ''
    iv = '86b2ccdf1a32df4168ab2e52f9d2febe'.decode('hex')
    for i in range(len(cookie) // BLOCK):
        cipher = iv + cipher
        middle = get_middle(iv)
        iv = strxor(middle, cookie[-BLOCK:])
        cookie = cookie[:-BLOCK]
    return iv, cipher

# conn = remote('localhost', 23333)
conn = remote('cookiemanager.game.redbud.info', 23333)
# context.log_level = 'debug'
begin = conn.recvline()
print(begin)
conn.recvuntil('Give me XXXX:')
conn.sendline(proof_of_work(substr(begin, '+', ')'), substr(begin, ' == ', '\n')))
cookie = conn.recvline()
print(cookie)
conn.recvuntil('Give me your cookie(hex):')
cookie = substr(cookie, ':', '\n').decode('hex')
iv, cookie_cipher, sig = cookie[:16], cookie[16: -32], cookie[-32:]
plain_text = find_plain_text(iv, cookie_cipher)
print(sig.encode('hex'))
print(plain_text[:-5].encode('hex'))
os.system('hash_extender --data %s --data-format hex --secret 16 --append %s --append-format hex --signature %s --format sha256' % (plain_text[:-5].encode('hex'), ';admin:1'.encode('hex'), sig.encode('hex')))
sig = raw_input()[:-1].decode('hex')
cookie = raw_input()[:-1].decode('hex')
iv, cookie_cipher = get_cipher(pad(cookie))
conn.sendline((iv+cookie_cipher+sig).encode('hex'))
conn.interactive()
