from PIL import Image
import numpy as np
import os

SIZE = 500

def getResult(img):
    Image.fromarray(np.uint8(img)).save('test.png')
    os.system('nocode.exe test.png > nul')
    return np.asarray(Image.open('result.png'))

img = np.zeros((SIZE,SIZE,3), dtype = int)
black = getResult(img)
# move = np.zeros(SIZE, dtype = int)
# np.savetxt('move.txt', move)
move = np.loadtxt('move.txt', dtype = int)
# print(move)
# exit()

def shuffle(img):
    new_img = np.zeros((SIZE,SIZE,3), dtype = int)
    for i in range(SIZE):
        new_img[:,i] = img[:,move[i]]
    return new_img

def compare(img):
    new_img = np.zeros((SIZE,SIZE,3), dtype = int)
    for i in range(SIZE):
        for j in range(SIZE):
            if (img[i,j] == black[i,j]).all():
                new_img[i,j,:] = 0
            else:
                new_img[i,j,:] = 255
    return new_img

flag = np.asarray(Image.open('flag_enc.png'))
flag = shuffle(compare(flag))
Image.fromarray(np.uint8(flag)).save('flag.png')

# for i in range(SIZE):
#     img[:,i,:] = 255
#     tf = getResult(img)
#     move[i] = -1
#     print('Checking: column %d' % i)
#     for j in range(SIZE):
#         if (tf[0,j] != black[0,j]).any():
#             move[i] = j
#             break
#     if move[i] == -1:
#         print('Wrong: column %d' % i)
#     img[:,i,:] = 0

# print(move)