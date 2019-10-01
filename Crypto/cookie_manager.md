# cookie_manager

解压得到一个 .py 脚本：

```python
import random
import sys
import os
import string
from hashlib import sha256
import SocketServer
from Crypto.Cipher import AES
# from flag import flag


def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)


def unpad(s):
    l = ord(s[-1])
    if l < len(s) and all([c == s[-1] for c in s[-1 * l:]]):
        return s[:-1 * l]
    else:
        return False


def encrypt(msg, iv, key):
    enc = AES.new(key, AES.MODE_CBC, iv)
    return enc.encrypt(msg)


def decrypt(cipher, iv, key):
    dec = AES.new(key, AES.MODE_CBC, iv)
    return dec.decrypt(cipher)


def check_hash(salt, msg, sig):
    return sha256(salt + msg).hexdigest() == sig.encode("hex")


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
        self.request.settimeout(15)
        req = self.request
        KEY, iv, salt = [os.urandom(16) for _ in range(3)]
        user, passwd = [os.urandom(4) for _ in range(2)]
        cookie = "admin:0;user:%s;pass:%s" % (user, passwd)
        sig = sha256(salt + cookie).hexdigest()
        hash_len = len(sig)
        cookie = pad(cookie)
        cipher = (iv + encrypt(cookie, iv, KEY)).encode("hex") + sig
        req.sendall("Your cookie:%s\n" % (cipher))
        while True:
            try:
                req.sendall('Give me your cookie(hex):')
                msg_hex = req.recv(1024).strip()
                msg = msg_hex.decode("hex")
                assert len(msg) > (16 + hash_len / 2)
                iv, cookie_cipher, sig = msg[:16], msg[16: -hash_len / 2], msg[-hash_len / 2:]
                cookie_pad = decrypt(cookie_cipher, iv, KEY)
                cookie = unpad(cookie_pad)
                if not cookie:
                    req.sendall("No No No ~\n")
                    continue
                if not check_hash(salt, cookie, sig):
                    req.sendall("No No No !\n")
                    continue
                tmp = {}
                for _ in cookie.split(b";"):
                    k, v = _.split(b":")
                    tmp[k] = v
                if tmp['admin'] == '1':
                    req.sendall("Welcome admin! Here is your flag: %s" % ('flag'))
                    return
                else:
                    req.sendall("bye bye\n")
                    return
            except Exception as e:
                req.sendall("Invalid cookie %s\n" % e)


class ThreadedServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 23333
    print 'Run in port:23333'
    server = ThreadedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()

```

算法流程：随机生成 key, salt, iv，以及用户名和密码。cookie 为 `"admin:0;user:%s;pass:%s" % (user, passwd)`。首先对 salt+cookie 做 SHA256 得到 sig；然后对 cookie 进行 AES 加密，模式为 CBC；最后显示 iv+cipher+sig，要求用户输入 iv+cipher+sig 格式的 hex 串，在经过 AES 解密和 SHA256 检验后，若 cookie 内 admin 值为 1，则输出 flag。

首先观察代码有这么一小段：

```python
if not cookie:
    req.sendall("No No No ~\n")
    continue
if not check_hash(salt, cookie, sig):
    req.sendall("No No No !\n")
    continue
```

说明我们可以通过程序判断 AES_CBC 解密是否成功，那么就可以在已知 iv 的前提条件下利用 Padding Oracle Attack 获取全部原文。

同时由于能判断  AES_CBC 解密是否成功，还可以利用字节反转攻击任意构造明文。具体如下：

首先随机生成密文并分块，然后用 Padding Oracle Attack 求得最后一块明文，再利用字节反转攻击通过修改倒数第二块密文间接修改最后一块明文，然后再用 Padding Oracle Attack 求得倒数第二块明文……如此循环便可以实现伪造任意文本的密文和 iv 了。

再想想 SHA256 有啥可以攻破的地方。有的，哈希长度溢出攻击。所以我们在已知原先明文的基础上可以应用哈希长度溢出攻击，伪造一个特定的后缀任意的明文的 sig。

那么整个思路就很清晰了：先通过 Padding Oracle Attack 得到原先明文，然后使用 Hash Length Extension Attack 伪造一个特定的后缀为 `;admin:1` 明文的 sig，再通过 Padding Oracle Attack + 字节反转攻击伪造出当前特定明文的密文和 iv，解决！

附代码 `cookie.py`：

```python
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
```

