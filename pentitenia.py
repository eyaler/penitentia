import cv2
import os
from collections import namedtuple, Counter
import wget
import time

url = 'https://www.hydeandrugg.com/media/Content'
images_folder = 'images'
output_folder = 'output'
y0 = 59
x0 = 55
y_last = 1018
x_last = 1158
bad_ids = {'2,3':(1010,1149), '2,4':(1012,1149), '3,1':(1020,x_last), '3,4':(1015,x_last)}
dline = (111-y0)/3
dy = 6
dx = (118-x0)/3
xtol = 4
b = '01237654'
c = '04152637'
d = '04512673'
flip_bits = False
reverse_bits = False
as_hex = True
show_images = True
mc_len = 20

'''
note: 0 is MSB unless flip_bits

a:
0123
4567

b:
0123
7654

c:
0246
1357

d:
0347
1256
'''

def to_byte(lst):
    if flip_bits:
        lst = [1-d for d in lst]
    if reverse_bits:
        lst = lst[::-1]
    byte = int(''.join(str(d) for d in lst), 2)
    if as_hex:
        byte = ('0'+hex(byte)[2:])[-2:]
    return byte

def to_dword(lst):
    if as_hex:
        return ''.join(lst)
    return tuple(lst)

os.makedirs(images_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
for j in range(1,5):
    for i in range(1,5):
        filename = 'penitentia %d,%d.png'%(j,i)
        while not os.path.exists(images_folder+'/'+filename):
            print('downloading:',url+'/'+filename)
            try:
                wget.download(url+'/'+filename, images_folder)
            except Exception:
                pass

images = {}
byte_a = Counter()
byte_b = Counter()
byte_c = Counter()
byte_d = Counter()
dword_a = Counter()
dword_b = Counter()
dword_c = Counter()
dword_d = Counter()
dword_a_red = Counter()
dword_b_red = Counter()
dword_c_red = Counter()
dword_d_red = Counter()
cnt_red = Counter()
chk_red = {'1,1': 14, '1,2': 10, '1,3': 11, '1,4': 13, '2,1': 14, '2,2': 16, '2,3': 8, '2,4': 9, '3,1': 11, '3,2': 7, '3,3': 7, '3,4': 8, '4,1': 10, '4,2': 7, '4,3': 11, '4,4': 21}
Quad = namedtuple('Quad', ['bytes_a', 'bytes_b', 'bytes_c', 'bytes_d', 'is_red'])

for filename in os.listdir(images_folder):
    img = cv2.imread(images_folder+'/'+filename)
    id = filename.split(' ')[1].split('.')[0]
    images[id] = []
    for row in range(12):
        images[id].append([])
        for col in range(12):
            images[id][row].append([])
            drow = ((bad_ids[id][0] if id in bad_ids else y_last) - y0) / 11
            dcol = ((bad_ids[id][1] if id in bad_ids else x_last) - x0) / 11
            y = int(y0 + row * drow)
            x = int(x0 + col * dcol)
            x1 = max(x - xtol, 0)
            x2 = min(x + xtol + 1, img.shape[1])
            is_red = img[y,x1:x2, 2].min() > 128
            cnt_red[id] += is_red
            images[id][row][col] = Quad([0]*4, [0]*4, [0]*4, [0]*4, is_red)
            for line in range(4):
                bytes_a = [0]*8
                bytes_b = [0]*8
                bytes_c = [0]*8
                bytes_d = [0]*8
                i = 0
                for side in range(2):
                    y = int(y0 + row * drow + line * dline + (2 * side - 1) * dy)
                    for bit in range(4):
                        x = int(x0 + col * dcol + bit * dx)
                        x1 = max(x - xtol, 0)
                        x2 = min(x + xtol + 1, img.shape[1])
                        if img[y, x1:x2, 1].min() < 128:
                            bytes_a[i] = 1
                            bytes_b[int(b[i])] = 1
                            bytes_c[int(c[i])] = 1
                            bytes_d[int(d[i])] = 1
                        img[y, x1:x2] = [is_red*255, 255*(1-is_red), 0]
                        i += 1
                    images[id][row][col].bytes_a[line] = to_byte(bytes_a)
                    images[id][row][col].bytes_b[line] = to_byte(bytes_b)
                    images[id][row][col].bytes_c[line] = to_byte(bytes_c)
                    images[id][row][col].bytes_d[line] = to_byte(bytes_d)
                    byte_a[images[id][row][col].bytes_a[line]] += 1
                    byte_b[images[id][row][col].bytes_b[line]] += 1
                    byte_c[images[id][row][col].bytes_c[line]] += 1
                    byte_d[images[id][row][col].bytes_d[line]] += 1
            dword_a[to_dword(images[id][row][col].bytes_a)] += 1
            dword_b[to_dword(images[id][row][col].bytes_b)] += 1
            dword_c[to_dword(images[id][row][col].bytes_c)] += 1
            dword_d[to_dword(images[id][row][col].bytes_d)] += 1
            if is_red:
                dword_a_red[to_dword(images[id][row][col].bytes_a)] += 1
                dword_b_red[to_dword(images[id][row][col].bytes_b)] += 1
                dword_c_red[to_dword(images[id][row][col].bytes_c)] += 1
                dword_d_red[to_dword(images[id][row][col].bytes_d)] += 1
            if as_hex:
                print(id, row, col, ''.join(images[id][row][col].bytes_a), ''.join(images[id][row][col].bytes_b),
                  ''.join(images[id][row][col].bytes_c), ''.join(images[id][row][col].bytes_d), is_red)
            else:
                print(id,row,col,images[id][row][col])
    cv2.imwrite(output_folder+'/'+filename, img)
    if show_images:
        cv2.imshow('',img)
        cv2.setWindowTitle('', filename)
        ch = cv2.waitKey(0)
        if ch==27:
            cv2.destroyWindow('')
            show_images = False
print('a:',len(byte_a),byte_a.most_common(mc_len))
print('b:',len(byte_b),byte_b.most_common(mc_len))
print('c:',len(byte_c),byte_c.most_common(mc_len))
print('d:',len(byte_d),byte_d.most_common(mc_len))
print('a:',len(dword_a),dword_a.most_common(mc_len))
print('b:',len(dword_b),dword_b.most_common(mc_len))
print('c:',len(dword_c),dword_c.most_common(mc_len))
print('d:',len(dword_d),dword_d.most_common(mc_len))
print('a_red:',len(dword_a_red),dword_a_red.most_common(mc_len))
print('b_red:',len(dword_b_red),dword_b_red.most_common(mc_len))
print('c_red:',len(dword_c_red),dword_c_red.most_common(mc_len))
print('d_red:',len(dword_d_red),dword_d_red.most_common(mc_len))
print('red:',sum(cnt_red.values()),cnt_red)
for red in chk_red:
    if chk_red[red]!=cnt_red[red]:
        print('Wrong red count in %s: found %d instead of %d'%(red,cnt_red[red],chk_red[red]))
