import sys
import os
import time
# Lùi 2 tầng từ System/System.py để lên INFOMATION_THEORY_VER2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Packet.Huffman_Packet import Huffman_Encoder
import json


class Binary_Object:
    def __init__(self, bit_string):
        """
        Khởi tạo một thực thể đối tượng nhị phân.
        Đầu vào là một chuỗi ký tự bit (ví dụ: "100100").
        """
        # Đảm bảo dữ liệu nạp vào chỉ chứa '0' và '1'
        self.bits = bit_string

    def __len__(self):
        """Cho phép dùng hàm len(obj) giống như chuỗi bình thường"""
        return len(self.bits)

    def __str__(self):
        """Cho phép print(obj) ra chuỗi bit trực quan"""
        return self.bits

    def __repr__(self):
        return f"Binary_Object('{self.bits}')"

    def __add__(self, other):
        res = ""
        n = len(self.bits)
        for i in range(0,n):
            res += '0' if self.bits[i] == other.bits[i] else '1'
        return res
    # Hamming distance
    def __sub__(self, other):
        
        res = 0
        for i in range(len(self.bits)):
            if self.bits[i] != other.bits[i]:
                res = res + 1
        return res
    def __mul__(self,other):
        res = 0
        for i in range(len(self.bits)):
            res += 0 if (self.bits[i] == '0') or (other.bits[i] == '0') else 1
        res = res % 2
        return str(res)
    

    
def conv_decode(bits_string, list_of_conv):
    decode_chanel_bits = ""
    bits = Binary_Object(bits_string)
    K = len(list_of_conv[0].bits)
    
    # SỬA LỖI: Thêm + 1 để cửa sổ trượt không bỏ sót các bit cuối cùng của chuỗi phát
    for i in range(0, len(bits.bits) - K + 1):
        origianl_bits = Binary_Object(bits.bits[i : i + K])
        for conv in list_of_conv:
            conv_decode = conv * origianl_bits
            decode_chanel_bits += conv_decode
            
    return decode_chanel_bits
    
def transmitter_ver1(path_input, path_output):
    p1 = Binary_Object("111")
    p2 = Binary_Object("101")
    p3 = Binary_Object("110")
    list_of_conv = [p1, p2, p3]
    
    file_name = os.path.basename(path_input)
    name, extension = os.path.splitext(file_name)

    try:
        # Gom toàn bộ quá trình đọc, xử lý dữ liệu vào trong khối logic an toàn
        with open(path_input, 'r', encoding='utf-8') as f:
            packet_data = json.load(f)

        huffman_bits = packet_data["Huffman_bits"]
        
        # Tiến hành mã hóa chuỗi bit
        convolution_code = conv_decode(huffman_bits, list_of_conv)
        
        # Thực hiện hoán đổi cấu trúc Key JSON theo yêu cầu
        del packet_data["Huffman_bits"]
        packet_data["Convolution_bits"] = convolution_code

        # Thiết lập đường dẫn đầu ra cho file mới
        full_path_output = os.path.join(path_output, file_name)
        os.makedirs(path_output, exist_ok=True)

        with open(full_path_output, 'w', encoding='utf-8') as f:
            json.dump(packet_data, f, ensure_ascii=False, indent=4)
        print(f"✔️ Đã tạo file mới thành công tại: {full_path_output}")

        # Xóa file cũ chỉ khi mọi quá trình ghi file mới diễn ra trơn tru
        os.remove(path_input)
        print(f"🗑️ Đã xóa file cũ thành công: {path_input}")

    except Exception as e:
        print(f"❌ [LỖI KHỐI PHÁT] Quá trình xử lý file {file_name} thất bại. Chi tiết: {e}")
    

def transmitter_ver_2(path_input,path_output):
    p1 = Binary_Object("111")
    p2 = Binary_Object("101")
    p3 = Binary_Object("110")
    list_of_conv = [p1, p2, p3]
    
    Packet_ver_Huffman = Huffman_Encoder(path_input)
    convolutional_code = conv_decode(Packet_ver_Huffman.huffman_bit_string,list_of_conv)
    Packet_ver_Huffman.huffman_bit_string = convolutional_code
    new_file_name_Huffman = f"{Packet_ver_Huffman.name}_processed.json"
    full_path_output = os.path.join(path_output, new_file_name_Huffman)
    
    # 🕒 Lấy nhãn thời gian thực tế lúc file Huffman chuẩn bị xuất xưởng
    tx_timestamp = time.time() 
    
    packet_data = {
        "metadata": {
            "tx_timestamp": tx_timestamp, # 💾 Ghi thẳng nhãn thời gian hệ thống vào file
            "entropy": Packet_ver_Huffman.entropy,
            "compression_ratio": Packet_ver_Huffman.compression_ratio
        },
        "decoder_dict": Packet_ver_Huffman.decoder_dict,
        "Processed_bits": Packet_ver_Huffman.huffman_bit_string
    }
    
    with open(full_path_output, 'w', encoding='utf-8') as f:
        json.dump(packet_data, f, ensure_ascii=False, indent=4)
        
    print(f"Da chuyen thanh Huffman file thanh cong (Timestamp: {tx_timestamp:.2f})")
    print(Packet_ver_Huffman)
    return full_path_output



    