# -*- coding: utf-8 -*-
# @Author: NanoApe
# @Date:   2019-09-18 15:07:29
# @Last Modified by:   NanoApe
# @Last Modified time: 2019-09-29 17:34:39

import numpy as np
import copy

box = [0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16]

box2 = [0,1,2,4,8,0x10,0x20,0x40,0x80,0x1b,0x36,0x6c,0xd8,0xab,0x4d,0x9a]

_box = np.zeros(256, dtype = int)
for i in range(256):
    for j in range(256):
        if box[j] == i:
            _box[i] = j
            break

def preKey(K, o):                            # checked
    _K = copy.deepcopy(K)
    for i in range(4):
        for j in range(1,4):
            _K[i,j] ^= K[i,j-1]
    for i in range(4):
        _K[i,0] ^= box[_K[(i+1)%4,3]]
        if i == 0:
            _K[i,0] ^= box2[o]
    return _K

def nextKey(K, o):                           # checked
    _K = copy.deepcopy(K)
    for j in range(4):
        for i in range(4):
            if j == 0:
                _K[i,j] ^= box[K[(i+1)%4,3]]
                if i == 0:
                    _K[i,j] ^= box2[o]
            else:
                _K[i,j] ^= _K[i,j-1]
    return _K

def rowKey(K):                               # checked
    _K = np.zeros((4,4), dtype = int)
    for i in range(4):
        for j in range(4):
            _K[i,j] = K[i,(j+i)%4]
    return _K

def colKey(K):                               # checked
    for j in range(4):
        K[:,j] = K[:,j].max()
    return K

def testKey(K):                              # checked
    _K = np.zeros((4,4), dtype = int)
    for i in range(4):
        for j in range(4):
            _K[i,j] = max(K[i,j], K[(i+1)%4,j])
    for j in range(4):
        if (_K[:,j] == 0).sum() < 2:
            _K[:,j] = 1
    return 1 - _K

def rowOne(i, j):
    # return i, (j-i+4)%4
    return i + ((j-i+4)%4)*4
    # print(i + j*4)
    # print(i, j)
    # return i + j*4

def pair(o, column):
    K = np.zeros((4,4), dtype = int)
    i = o%4
    j = o//4
    K[i,j] = 1
    K = rowKey(K)
    K = colKey(K)
    K[i,j] = 1
    K = rowKey(K)
    K = testKey(K)
    K[i,j] = 0
    # print(o, column, K)
    for _i in range(4):
        if K[_i,column] + K[(_i+1)%4,column] == 2:
            return rowOne(_i, column), rowOne((_i+1)%4, column), rowOne((_i+2)%4, column), rowOne((_i+3)%4, column)
    return -1, -1, -1, -1

# for o in range(16):
#     for j in range(4):
#         print(o, j, pair(o, j))

Key = np.zeros(16, dtype = int)
Key[:] = -1
pos = np.zeros(6, dtype = int)
pos[:] = -1
k0 = np.zeros((6,16), dtype = int)
k1 = np.zeros((6,16), dtype = int)
file = open('cipher.txt', 'r')
for i in range(6):
    _str = file.readline()[:-1].decode('hex')
    for j in range(16):
        k0[i,j] = ord(_str[j])
    _str = file.readline()[:-1].decode('hex')
    for j in range(16):
        k1[i,j] = ord(_str[j])
    file.readline()

finded = [[[[] for xor in range(256)] for grid in range(16)] for num in range(6)]
for o in range(6):
    for i in range(16):
        for k in range(256):
            finded[o][i][_box[k0[o,i]^k]^_box[k1[o,i]^k]].append(k)
# exit()

def find(xor, num, where):
    return finded[num][where][xor]

def _rev(num, a):
    return _box[Key[a]^k0[num,a]] ^ _box[Key[a]^k1[num,a]]

debug = False

def dfs(num, column):
    global Key, pos, debug
    if num == 6:
        return True
        # if column == 3:
        #     file = open('key.txt', 'a')
        #     file.write(str(Key) + '\n')
        #     file.close()
        #     print(Key)
        #     return False
        # num = 0
        # column += 1
    if pos[num] == -1:
        if dfs(num + 1, column):
            return True
        return False
        # for i in range(16):
        #     pos[num] = i
        #     if dfs(num, column):
        #         return True
        # pos[num] = -1
        # return False
    # if debug and num == 2 and column == 0:
    #     print(Key, num, column)
    a0, a1, a2, a3 = pair(pos[num], column)
    if a0 == -1:
        if dfs(num + 1, column):
            return True
    else:
        if Key[a0] == -1 and Key[a1] == -1 and Key[a2] == -1 and Key[a3] == -1:
            for o in range(256):
                for i0 in find(o, num, a0):
                    Key[a0] = i0
                    for i1 in find(o, num, a1):
                        Key[a1] = i1
                        for p in range(256):
                            for i2 in find(p, num, a2):
                                Key[a2] = i2
                                for i3 in find(o^p, num, a3):
                                    Key[a3] = i3
                                    if dfs(num + 1, column):
                                        return True
            Key[a0] = Key[a1] = Key[a2] = Key[a3] = -1
        elif Key[a0] != -1 and Key[a1] != -1 and Key[a2] != -1 and Key[a3] != -1:
            if _rev(num, a0) != _rev(num, a1):
                return False
            if _rev(num, a0) ^ _rev(num, a2) != _rev(num, a3):
                return False
            if dfs(num + 1, column):
                return True
        else:
            print('BUG')

    return False

# pos = [4, 2, 2, 10, 5, 13]
# fg = True
# for i in range(4):
#     Key[:] = -1
#     if dfs(0, i) == False:
#         fg = False
#         break
# print(fg)
# exit()

def nextPos(fg):
    global pos
    tmp = 5
    while tmp >= 0 and pos[tmp] == -1:
        tmp -= 1
    if tmp != 5:
        if fg:
            pos[tmp+1] = 0
            return True
    while tmp >= 0 and pos[tmp] == 15:
        tmp -= 1
    if tmp < 0:
        return False
    pos[tmp] += 1
    while tmp + 1 < 6:
        tmp += 1
        pos[tmp] = -1
    return True

count = 0
while True:
    fg = True
    print(pos.reshape(-1))
    # count += 1
    # if count % 100 == 0:
        # print(pos.reshape(-1))
    for i in range(4):
        Key[:] = -1
        if dfs(0, i) == False:
            fg = False
            break
    if fg and pos[5] != -1:
        file = open('key.txt', 'a')
        file.write(str(pos) + '\n')
        file.close()
    if nextPos(fg) == False:
        break

dfs(0, 0)
# print(Key)

# key = np.zeros((4,4), dtype = int)
# for i in range(10):
#     key = nextKey(key, i+1)
# print(key)

# def _xor(msg, key):
#     _msg = copy.deepcopy(msg)
#     for i in range(4):
#         for j in range(4):
#             _msg[i,j] ^= key[i,j]
#     return _msg

# def _row(msg):
#     _msg = copy.deepcopy(msg)
#     for i in range(4):
#         for j in range(4):
#             _msg[i,j] = msg[i,(j-i+4)%4]
#     return _msg

# def _subb(msg):
#     _msg = copy.deepcopy(msg)
#     for i in range(4):
#         for j in range(4):
#             _msg[i,j] = _box[msg[i,j]]
#     return _msg

# for o in range(6):
#     msg0 = np.zeros((4,4), dtype=int)
#     for i in range(4):
#         for j in range(4):
#             msg0[i,j] = k0[o,j*4+i]
#     msg0 = _subb(_row(_xor(msg0, key)))
#     msg1 = np.zeros((4,4), dtype=int)
#     for i in range(4):
#         for j in range(4):
#             msg1[i,j] = k1[o,j*4+i]
#     msg1 = _subb(_row(_xor(msg1, key)))
#     msg = _xor(msg0, msg1)
#     print(msg)
#     for num in range(16):
#         fg = True
#         for col in range(4):
#             a1, a2 = pair(num, col)
#             if a1 == -1:
#                 continue
#             # print(num, col, a1, a2)
#             if msg[a1%4, col] != msg[a2%4, col]:
#                 fg = False
#                 break
#         if fg:
#             print(num)
#             break

# def xor(msg, key):
#     _msg = copy.deepcopy(msg)
#     for i in range(4):
#         for j in range(4):
#             _msg[i,j] ^= key[i,j]
#     return _msg

# def subb(msg):
#     _msg = copy.deepcopy(msg)
#     for i in range(4):
#         for j in range(4):
#             _msg[i,j] = box[msg[i,j]]
#     return _msg

# def row(msg):
#     _msg = copy.deepcopy(msg)
#     for i in range(4):
#         for j in range(4):
#             _msg[i,j] = msg[i,(j+i)%4]
#     return _msg

# def colcal(a):
#     return ((a>>7)*27 ^ (a<<1)%256)%256

# def col(msg):
#     _msg = copy.deepcopy(msg)
#     for j in range(4):
#         tmp = 0
#         for i in range(4):
#             tmp ^= msg[i,j]
#         for i in range(4):
#             _msg[i,j] ^= tmp ^ colcal(msg[i,j] ^ msg[(i+1)%4,j])
#     return _msg

# key = np.zeros((4,4), dtype=int)
# msg = np.zeros((4,4), dtype=int)
# for j in range(4):
#     for i in range(4):
#         msg[i,j] = ord('0')+j*4+i
# print(msg)
# msg = xor(msg, key)
# for i in range(9):
#     key = nextKey(key, i+1)
#     msg = xor(col(row(subb(msg))), key)
# key = nextKey(key, 10)
# msg = xor(row(subb(msg)), key)
# print(key)
# print(msg)

# from Crypto.Cipher import AES
# from Crypto import Random

# iv = ''.join([chr(0) for x in range(16)])
# key = ''.join([chr(0) for x in range(16)])
# msg = ''.join([chr(ord('0')+x) for x in range(16)])
# print(msg)
# print(key.encode('hex'))
# print(AES.new(key, AES.MODE_ECB).encrypt(msg).encode('hex'))
