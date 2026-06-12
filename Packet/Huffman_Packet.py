import os
from Packet import Huffman_encoding
import pandas as pd
from collections import Counter
import json
import time


class Huffman_Encoder():
    def __init__(self,path_file):
        #1 Luu lai ten de con ghi lai file
        file_name = os.path.basename(path_file)
        name,extension = os.path.splitext(file_name)
        self.name = name
        try:
            with open(path_file, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            print(f"[PACKET] Đã nạp thành công file: {file_name} ({len(raw_text)} ký tự)")
        except Exception as e:
            print(f"[LỖI PACKET] Không thể đọc file tại {path_file}. Chi tiết: {e}")
            return


        tokens = list(raw_text)
        token_counts = Counter(tokens)
        probabilities_dict = {symbol : count / len(tokens) for symbol,count in token_counts.items()}

        encoder_dict,decoder_dict = Huffman_encoding.Huffman_Function(probabilities_dict)

        self.decoder_dict = decoder_dict

        huffman_bit_string = ''.join([encoder_dict[token] for token in raw_text])
        self.huffman_bit_string = huffman_bit_string

        original_size_bits = len(raw_text)*8
        compressed_size_bits = len(huffman_bit_string)
        compression_ratio = compressed_size_bits/original_size_bits
        self.compression_ratio = compression_ratio
        self.entropy = Huffman_encoding.calculate_entropy(probabilities_dict)
    

    def __str__(self):
        # Dùng dấu toán tử ba nháy để viết chuỗi trên nhiều dòng cho đẹp
        return (
            f"========================================\n"
            f"📊 [HUFFMAN ENCODER STATUS]\n"
            f" -> Trạng thái: Đã mã hóa thành công file '{self.name}'\n"
            f" -> Entropy của nguồn: {self.entropy:.4f}\n"
            f" -> Tỷ lệ nén (Compression Ratio): {self.compression_ratio:.4f}\n"
            f"========================================"
        )

def Save_the_Huffman_File(path_input, path_output):
    Huffman_Packet = Huffman_Encoder(path_input)
    new_file_name_Huffman = f"{Huffman_Packet.name}_processed.json"
    full_path_output = os.path.join(path_output, new_file_name_Huffman)
    
    # 🕒 Lấy nhãn thời gian thực tế lúc file Huffman chuẩn bị xuất xưởng
    tx_timestamp = time.time() 
    
    packet_data = {
        "metadata": {
            "tx_timestamp": tx_timestamp, # 💾 Ghi thẳng nhãn thời gian hệ thống vào file
            "entropy": Huffman_Packet.entropy,
            "compression_ratio": Huffman_Packet.compression_ratio
        },
        "decoder_dict": Huffman_Packet.decoder_dict,
        "Huffman_bits": Huffman_Packet.huffman_bit_string
    }
    
    with open(full_path_output, 'w', encoding='utf-8') as f:
        json.dump(packet_data, f, ensure_ascii=False, indent=4)
        
    print(f"Da chuyen thanh Huffman file thanh cong (Timestamp: {tx_timestamp:.2f})")
    print(Huffman_Packet)
    return full_path_output