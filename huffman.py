
from io import BytesIO
from os.path import exists
import pickle
 
 
# Узел дерева
class Node:
    def __init__(self, byte, freq, left=None, right=None):
        self.byte = byte
        self.freq = freq
        self.left = left
        self.right = right
 
    def __lt__(self, other):
        return self.freq < other.freq
 
 
# Кодирование
def encode(root, s, code):
 
    if root is None:
        return
 
    if root.left is None and root.right is None:
        code[root.byte] = s if len(s) > 0 else '1'
 
    encode(root.left, s + '0', code)
    encode(root.right, s + '1', code)

 
# Декодирование
def decode(huffman_tree, text):
    root = huffman_tree 
    res = ''
    for i in text:
        if i == '1':
            root = root.right
        else:
            root = root.left
        if root.left is None and root.right is None:
            res += "{:02x} ".format(root.byte)
            root = huffman_tree
    return res[:-1]

# Из множества узлов строим упорядоченное дерево
def tree(nodes):
    for i in range(len(nodes)//2, 0, -1):
        first_to_last(nodes, i)

def last_to_first(nodes, startpos, pos):
    byte = nodes[pos]
    while pos > startpos:
        parentpos = (pos - 1) // 2 
        parent = nodes[parentpos]
        if byte < parent:
            nodes[pos] = parent
            pos = parentpos
            continue
        break
    nodes[pos] = byte

def first_to_last(nodes, pos):
    endpos = len(nodes)
    startpos = pos
    byte = nodes[pos]
    byteildpos = 2*pos + 1   
    while byteildpos < endpos:
        rightpos = byteildpos + 1
        if rightpos < endpos and not nodes[byteildpos] < nodes[rightpos]:
            byteildpos = rightpos
        nodes[pos] = nodes[byteildpos]
        pos = byteildpos
        byteildpos = 2*pos + 1
    nodes[pos] = byte
    last_to_first(nodes, startpos, pos)

# добавляем узел в дерево с учетом порядка
def tree_push(nodes, item):
    nodes.append(item)
    last_to_first(nodes, 0, len(nodes)-1)

# забираем узел с наименьшей частотой
def tree_pop(nodes):
    last_elem = nodes.pop() 
    if nodes:
        returnitem = nodes[0]
        nodes[0] = last_elem
        first_to_last(nodes, 0)
        return returnitem
    return last_elem

# Построение дерева
def buildHuffmanTree(text):
 
    if len(text) == 0:
        return 0
 
    freq = {i: text.count(i) for i in set(text)}
 
    huffman_tree = [Node(k, v) for k, v in freq.items()]
    tree(huffman_tree)
 
    while len(huffman_tree) != 1:
 
        left = tree_pop(huffman_tree)
        right = tree_pop(huffman_tree)
 
        total = left.freq + right.freq
        tree_push(huffman_tree, Node(None, total, left, right))
    
    return huffman_tree[0], freq
    

while True:
    
    print('Введите опцию:')
    print('1 - архивировать')
    print('2 - разархивировать')
    print('3- выход')
    
    option = input()
    
    if option not in ['1', '2', '3']:
        print('Неправильная опция!')
   
    elif option == '1':
        print('Введите путь к файлу:')
        path = input()
        if not exists(path):
              print('Данного файла не существует!')
        else:
            f = open(path, "rb")
            file_type = path.split('.')[-1]
            text = f.read()
            f.close()
            root, freq = buildHuffmanTree(text)
            
            if root == 0:
                print('Файл пустой!')
            
            else:
                huffmanCode = {}
                encode(root, '', huffmanCode)
                s = ''
                for c in text:
                    s += huffmanCode.get(c)
                freq['file_type'] = file_type
                freq['last_byte'] = s[len(s) - len(s) % 8:]
                f = open(path[:-len(file_type)] + 'zmh', 'wb')
                pickle.dump(freq, f)
                h = list("{:02x} ".format(int(s[i : i + 8], 2))  for i in range(0, len(s), 8))
                hh = ''
                
                for i in h:
                    hh += i
                
                hh = hh[:-1]
                f.write(bytearray.fromhex(hh))
                f.close()
                print('Файл:', path[:-len(file_type)] + 'zmh', 'сохранен!')

    elif option == '2':
        print('Введите путь к файлу:')
        path = input()
        
        if not exists(path):
            print('Данного файла не существует!')
       
        elif path.split('.')[-1] != 'zmh':
            print('Неверный формат!')
        
        else:
            f = open(path, 'rb')
           
            try:
                freq = pickle.load(f)
            except:
                print('Не получается разархивировать!')
                break
            
            text = f.read()
            res = ''
            
            for i in text:
                res += '{0:08b}'.format(i)
            
            res = res[:-8] + freq['last_byte']
            file_type = freq['file_type']
            del freq['last_byte']
            del freq['file_type']
            huffman_tree = [Node(k, v) for k, v in freq.items()]
            tree(huffman_tree)
            
            while len(huffman_tree) != 1:
                left = tree_pop(huffman_tree)
                right = tree_pop(huffman_tree)
                total = left.freq + right.freq
                tree_push(huffman_tree, Node(None, total, left, right))
            res = decode(huffman_tree[0], res)
            
            with open(path[:-3] + file_type, "wb") as f:
                f.write(bytearray.fromhex(res))
                f.close()
            print('Файл:', path[:-3] + file_type, 'сохранен!')

    elif option == '3':
        break
    