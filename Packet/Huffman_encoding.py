import heapq
from collections import deque
import math

class Node:
    def __init__(self, original_symbol, probility, Huffman_code = "", left = None, right = None):
        self.original_symbol = original_symbol
        self.Huffman_code = Huffman_code
        self.probility = probility
        self.left = left
        self.right = right
        
    def __str__(self):
        return f"(Ki goc {self.original_symbol} duoc chuyen doi thanh {self.Huffman_code})"
        
    def __lt__(self, other):
        return self.probility < other.probility
        
    def Replace(self, other):
        parent = Node("", self.probility + other.probility, "", self, other)
        return parent

    def Assign_to_the_Huffman_Code(self):
        if self is None:
            return
        q = deque([self])
        while q:
            node = q.popleft()
            if node.left:
                node.left.Huffman_code = node.Huffman_code + '0'
                q.append(node.left)
            if node.right:
                node.right.Huffman_code = node.Huffman_code + '1'
                q.append(node.right)

def Building_Huffman_Tree(argument):
    heap = [Node(str(sym), prob) for sym, prob in argument.items()] # Ép ký tự về str để đồng bộ
    heapq.heapify(heap)
    while len(heap) > 1:
        the_left = heapq.heappop(heap)
        the_right = heapq.heappop(heap)
        new_element = the_left.Replace(the_right)
        heapq.heappush(heap, new_element)
    the_root = heapq.heappop(heap)
    return the_root

def Huffman_Function(input_argument = None):
    if not input_argument:
        print("Dữ liệu đầu vào rỗng!")
        return {}, {}
        
    root = Building_Huffman_Tree(input_argument)
    #print("Da tao cay thanh cong")
    root.Assign_to_the_Huffman_Code()
    #print("Da tao thanh cong ma Huffman")
    #print("-------Bo Ma HuffMan------")
    
    q = deque([root])
    decoder_dict = {}
    encoder_dict = {}
    
    while q:
        node = q.popleft()
        if node.left is None and node.right is None:
            #print(node)
            # Tạo cả 2 bộ từ điển để phục vụ cho cả bên phát lẫn bên nhận
            decoder_dict[node.Huffman_code] = node.original_symbol
            encoder_dict[node.original_symbol] = node.Huffman_code
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
            
    return encoder_dict, decoder_dict

# Truyền trực tiếp Dict tần suất (argument) vào để tính Entropy gốc
def calculate_entropy(argument):
    entropy = 0.0 # Khởi tạo giá trị tích lũy
    for prob in argument.values():
        if prob > 0:
            entropy -= prob * math.log2(prob)
    return entropy

#Phối hợp Dict tần suất và Dict mã hóa để tính Chiều dài trung bình
def calculate_average_length(argument, encoder_dict):
    average_length = 0.0 # Khởi tạo giá trị tích lũy
    for symbol, prob in argument.items():
        symbol_str = str(symbol)
        if symbol_str in encoder_dict:
            average_length += prob * len(encoder_dict[symbol_str])
    return average_length

def encode_file_to_huffman_string(data_elements, encoder_dict):
    bit_string_result = ""
    for element in data_elements:
        element_str = str(element) 
        if element_str in encoder_dict:
            bit_string_result += encoder_dict[element_str]
        else:
            print(f"Cảnh báo: Phát hiện phần tử lạ '{element_str}' không có trong bộ mã!")
    return bit_string_result