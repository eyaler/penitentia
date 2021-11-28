from collections import Counter, defaultdict, namedtuple
import os
import time

import cv2
try:
    import wget
except Exception:
    pass


url = 'https://www.hydeandrugg.com/media/Content'
images_folder = 'images'
marks_folder = 'marks'
hex_folder = 'hex'
y0 = 59
x0 = 55
yx_last = {'1,1': (1018, 1158), '1,2': (1018, 1158), '1,3': (1016, 1155), '1,4': (1016, 1155), 
           '2,1': (1015, 1155), '2,2': (1016, 1155), '2,3': (1010, 1149), '2,4': (1012, 1151), 
           '3,1': (1021, 1160), '3,2': (1016, 1158), '3,3': (1017, 1156), '3,4': (1015, 1154), 
           '4,1': (1016, 1156), '4,2': (1016, 1155), '4,3': (1019, 1159), '4,4': (1019, 1159)}
dline = (111-y0) / 3
dy = 6
dx = (118-x0) / 3
xtol = 4
a = '01234567'
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


def to_hex(byte):
    return ('0' + hex(byte)[2:])[-2:]


def to_byte(lst):
    if flip_bits:
        lst = [1 - d for d in lst]
    if reverse_bits:
        lst = lst[::-1]
    byte = int(''.join(str(d) for d in lst), 2)
    if as_hex:
        byte = to_hex(byte)
    return byte


def to_dword(lst, as_hex):
    if as_hex:
        if type(lst[0]) == int:
            lst = [to_hex(b) for b in lst]
        return ''.join(lst)
    return tuple(lst)


os.makedirs(images_folder, exist_ok=True)
os.makedirs(marks_folder, exist_ok=True)
os.makedirs(hex_folder + '/' + a, exist_ok=True)
os.makedirs(hex_folder + '/' + b, exist_ok=True)
os.makedirs(hex_folder + '/' + c, exist_ok=True)
os.makedirs(hex_folder + '/' + d, exist_ok=True)
for j in range(1, 5):
    for i in range(1, 5):
        filename = 'penitentia %d,%d.png' % (j, i)
        while not os.path.exists(images_folder + '/' + filename):
            print('downloading:', url + '/' + filename)
            try:
                wget.download(url + '/' + filename, images_folder)
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
dword_a_red_colocation = defaultdict(list)
dword_b_red_colocation = defaultdict(list)
dword_c_red_colocation = defaultdict(list)
dword_d_red_colocation = defaultdict(list)
cnt_red = Counter()
chk_red = {'1,1': 14, '1,2': 10, '1,3': 11, '1,4': 13, '2,1': 14, '2,2': 16, '2,3': 8, '2,4': 9, '3,1': 11, '3,2': 7, '3,3': 7, '3,4': 8, '4,1': 10, '4,2': 7, '4,3': 11, '4,4': 21}
Quad = namedtuple('Quad', ['bytes_a', 'bytes_b', 'bytes_c', 'bytes_d', 'is_red'])

for filename in os.listdir(images_folder):
    img = cv2.imread(images_folder + '/' + filename)
    id = filename.split(' ')[1].split('.')[0]
    images[id] = []
    with open(hex_folder + '/' + a + '/' + id + '.txt', 'w') as fa, open(hex_folder + '/' + b + '/' + id + '.txt', 'w') as fb, open(hex_folder + '/' + c + '/' + id + '.txt', 'w') as fc, open(hex_folder + '/' + d + '/' + id + '.txt', 'w') as fd:
        for row in range(12):
            images[id].append([])
            for col in range(12):
                images[id][row].append([])
                drow = (yx_last[id][0]-y0) / 11
                dcol = (yx_last[id][1]-x0) / 11
                y = int(y0 + row*drow)
                x = int(x0 + col*dcol)
                x1 = max(x - xtol, 0)
                x2 = min(x + xtol + 1, img.shape[1])
                is_red = img[y, x1:x2, 2].min() > 128
                cnt_red[id] += is_red
                images[id][row][col] = Quad([0] * 4, [0] * 4, [0] * 4, [0] * 4, is_red)
                for line in range(4):
                    bytes_a = [0] * 8
                    bytes_b = [0] * 8
                    bytes_c = [0] * 8
                    bytes_d = [0] * 8
                    i = 0
                    for side in range(2):
                        y = int(y0 + row*drow + line*dline + (2*side-1)*dy)
                        for bit in range(4):
                            x = int(x0 + col*dcol + bit*dx)
                            x1 = max(x - xtol, 0)
                            x2 = min(x + xtol + 1, img.shape[1])
                            if img[y, x1:x2, 1].min() < 128:
                                bytes_a[i] = 1
                                bytes_b[int(b[i])] = 1
                                bytes_c[int(c[i])] = 1
                                bytes_d[int(d[i])] = 1
                            img[y, x1:x2] = [is_red * 255, 255 * (1-is_red), 0]
                            i += 1
                        images[id][row][col].bytes_a[line] = to_byte(bytes_a)
                        images[id][row][col].bytes_b[line] = to_byte(bytes_b)
                        images[id][row][col].bytes_c[line] = to_byte(bytes_c)
                        images[id][row][col].bytes_d[line] = to_byte(bytes_d)
                        byte_a[images[id][row][col].bytes_a[line]] += 1
                        byte_b[images[id][row][col].bytes_b[line]] += 1
                        byte_c[images[id][row][col].bytes_c[line]] += 1
                        byte_d[images[id][row][col].bytes_d[line]] += 1
                dword_a[to_dword(images[id][row][col].bytes_a, as_hex)] += 1
                dword_b[to_dword(images[id][row][col].bytes_b, as_hex)] += 1
                dword_c[to_dword(images[id][row][col].bytes_c, as_hex)] += 1
                dword_d[to_dword(images[id][row][col].bytes_d, as_hex)] += 1
                if is_red:
                    dword_a_red[to_dword(images[id][row][col].bytes_a, as_hex)] += 1
                    dword_b_red[to_dword(images[id][row][col].bytes_b, as_hex)] += 1
                    dword_c_red[to_dword(images[id][row][col].bytes_c, as_hex)] += 1
                    dword_d_red[to_dword(images[id][row][col].bytes_d, as_hex)] += 1
                    dword_a_red_colocation[(to_dword(images[id][row][col].bytes_a, as_hex), row + 1, col + 1)].append(id)
                    dword_b_red_colocation[(to_dword(images[id][row][col].bytes_b, as_hex), row + 1, col + 1)].append(id)
                    dword_c_red_colocation[(to_dword(images[id][row][col].bytes_c, as_hex), row + 1, col + 1)].append(id)
                    dword_d_red_colocation[(to_dword(images[id][row][col].bytes_d, as_hex), row + 1, col + 1)].append(id)
                if as_hex:
                    print(id, row, col, ''.join(images[id][row][col].bytes_a), ''.join(images[id][row][col].bytes_b), 
                          ''.join(images[id][row][col].bytes_c), ''.join(images[id][row][col].bytes_d), is_red)
                else:
                    print(id, row, col, images[id][row][col])
                prefix = ' ' if col > 0 else '\n' if row > 0 else ''
                fa.write(prefix + to_dword(images[id][row][col].bytes_a, True))
                fb.write(prefix + to_dword(images[id][row][col].bytes_b, True))
                fc.write(prefix + to_dword(images[id][row][col].bytes_c, True))
                fd.write(prefix + to_dword(images[id][row][col].bytes_d, True))
    cv2.imwrite(marks_folder + '/' + filename, img)
    if show_images:
        cv2.imshow('', img)
        cv2.setWindowTitle('', filename)
        ch = cv2.waitKey(0)
        if ch == 27:
            cv2.destroyWindow('')
            show_images = False

print('a:', len(byte_a), byte_a.most_common(mc_len))
print('b:', len(byte_b), byte_b.most_common(mc_len))
print('c:', len(byte_c), byte_c.most_common(mc_len))
print('d:', len(byte_d), byte_d.most_common(mc_len))
print('a:', len(dword_a), dword_a.most_common(mc_len))
print('b:', len(dword_b), dword_b.most_common(mc_len))
print('c:', len(dword_c), dword_c.most_common(mc_len))
print('d:', len(dword_d), dword_d.most_common(mc_len))
print('a_red:', len(dword_a_red), dword_a_red.most_common(mc_len))
print('b_red:', len(dword_b_red), dword_b_red.most_common(mc_len))
print('c_red:', len(dword_c_red), dword_c_red.most_common(mc_len))
print('d_red:', len(dword_d_red), dword_d_red.most_common(mc_len))
print('red:', sum(cnt_red.values()), cnt_red)
for x in [dword_a_red_colocation, dword_b_red_colocation, dword_c_red_colocation, dword_d_red_colocation]:
    for k, v in list(x.items()):
        if len(v) < 2:
            del x[k]
print('a_red_colocation:', len(dword_a_red_colocation), sorted(dword_a_red_colocation.items(), key=lambda x: (-len(x[1]), x[0])))
print('b_red_colocation:', len(dword_b_red_colocation), sorted(dword_b_red_colocation.items(), key=lambda x: (-len(x[1]), x[0])))
print('c_red_colocation:', len(dword_c_red_colocation), sorted(dword_c_red_colocation.items(), key=lambda x: (-len(x[1]), x[0])))
print('d_red_colocation:', len(dword_d_red_colocation), sorted(dword_d_red_colocation.items(), key=lambda x: (-len(x[1]), x[0])))

for red in chk_red:
    if chk_red[red] != cnt_red[red]:
        print('Wrong red count in %s: found %d instead of %d' % (red, cnt_red[red], chk_red[red]))


import matplotlib.pyplot as plt
import networkx as nx


G = nx.Graph()
for edges in dword_a_red_colocation.values():
    for i in range(len(edges) - 1):
        for j in range(i + 1, len(edges)):
            G.add_edge(edges[i], edges[j])
for i in range(1, 5):
    for j in range(1, 5):
        G.add_node('%d,%d' % (i, j))
print('connected components:', list(nx.connected_components(G)))
nx.draw(G, with_labels=True)
plt.savefig('network.png')
plt.show()
