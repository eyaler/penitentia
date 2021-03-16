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
show_images = True

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

def to_int(lst):
    if flip_bits:
        lst = [1-d for d in lst]
    if reverse_bits:
        lst = lst[::-1]
    return int(''.join(str(d) for d in lst), 2)

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
ch_a = Counter()
ch_b = Counter()
ch_c = Counter()
ch_d = Counter()
tup_a = Counter()
tup_b = Counter()
tup_c = Counter()
tup_d = Counter()
tup_a_red = Counter()
tup_b_red = Counter()
tup_c_red = Counter()
tup_d_red = Counter()
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
                    images[id][row][col].bytes_a[line] = to_int(bytes_a)
                    images[id][row][col].bytes_b[line] = to_int(bytes_b)
                    images[id][row][col].bytes_c[line] = to_int(bytes_c)
                    images[id][row][col].bytes_d[line] = to_int(bytes_d)
                    ch_a[images[id][row][col].bytes_a[line]] += 1
                    ch_b[images[id][row][col].bytes_b[line]] += 1
                    ch_c[images[id][row][col].bytes_c[line]] += 1
                    ch_d[images[id][row][col].bytes_d[line]] += 1
            tup_a[tuple(images[id][row][col].bytes_a)] += 1
            tup_b[tuple(images[id][row][col].bytes_b)] += 1
            tup_c[tuple(images[id][row][col].bytes_c)] += 1
            tup_d[tuple(images[id][row][col].bytes_d)] += 1
            if is_red:
                tup_a_red[tuple(images[id][row][col].bytes_a)] += 1
                tup_b_red[tuple(images[id][row][col].bytes_b)] += 1
                tup_c_red[tuple(images[id][row][col].bytes_c)] += 1
                tup_d_red[tuple(images[id][row][col].bytes_d)] += 1
            print(id,row,col,images[id][row][col])
    cv2.imwrite(output_folder+'/'+filename, img)
    if show_images:
        cv2.imshow('',img)
        cv2.setWindowTitle('', filename)
        ch = cv2.waitKey(0)
        if ch==27:
            cv2.destroyWindow('')
            show_images = False
print('a:',len(ch_a),ch_a.most_common(15))
print('b:',len(ch_b),ch_b.most_common(15))
print('c:',len(ch_c),ch_c.most_common(15))
print('d:',len(ch_d),ch_d.most_common(15))
print('a:',len(tup_a),tup_a.most_common(15))
print('b:',len(tup_b),tup_b.most_common(15))
print('c:',len(tup_c),tup_c.most_common(15))
print('d:',len(tup_d),tup_d.most_common(15))
print('a_red:',len(tup_a_red),tup_a_red.most_common(15))
print('b_red:',len(tup_b_red),tup_b_red.most_common(15))
print('c_red:',len(tup_c_red),tup_c_red.most_common(15))
print('d_red:',len(tup_d_red),tup_d_red.most_common(15))
print('red:',sum(cnt_red.values()),cnt_red)
for red in chk_red:
    if chk_red[red]!=cnt_red[red]:
        print('Wrong red count in %s: found %d instead of %d'%(red,cnt_red[red],chk_red[red]))
