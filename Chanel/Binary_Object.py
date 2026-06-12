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
    

def transmitter_ver_2(path_input,path_output):
    p1 = Binary_Object("111")
    p2 = Binary_Object("101")
    p3 = Binary_Object("110")
    list_of_conv = [p1, p2, p3]
    
    Packet_ver_Huffman = Huffman_Encoder(path_input)
    convolutional_code = conv_decode("00" + Packet_ver_Huffman.huffman_bit_string + "00",list_of_conv )
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
        
    print(f"Da xu ly file thanh cong (Timestamp: {tx_timestamp:.2f})")
    print(Packet_ver_Huffman)
    return full_path_output



def viterbi_sliding_window(processed_bits_str):
    # 1. Khởi tạo FSM chuẩn quy ước dịch trái của bạn
    FSM = {
        0: {0: {"next": 0, "encode": Binary_Object('000')}, 1: {"next": 2, "encode": Binary_Object("111")}},
        1: {0: {"next": 0, "encode": Binary_Object('110')}, 1: {"next": 2, "encode": Binary_Object("001")}},
        2: {0: {"next": 1, "encode": Binary_Object('101')}, 1: {"next": 3, "encode": Binary_Object("010")}},
        3: {0: {"next": 1, "encode": Binary_Object('011')}, 1: {"next": 3, "encode": Binary_Object("100")}},
    }
    
    # Tách chuỗi bit nhận được thành mảng các cụm 3 bit (Binary_Object)
    received_chunks = [Binary_Object(processed_bits_str[i:i+3]) for i in range(0, len(processed_bits_str), 3)]
    total_chunks = len(received_chunks)
    
    # Định nghĩa chiều dài cửa sổ trượt (Truncation Depth)
    L = 30 
    
    # Khởi tạo ma trận Path Metric và Traceback với kích thước cố định: 4 hàng x (L + 1) cột
    pm_matrix = [[float('inf')] * (L + 1) for _ in range(4)]
    traceback_matrix = [[None] * (L + 1) for _ in range(4)]
    
    # Điểm neo xuất phát lý tưởng
    pm_matrix[0][0] = 0
    
    decoded_bits = []
    
    # -------------------------------------------------------------------------
    # GIAI ĐOẠN 1: Nạp đầy cửa sổ ban đầu (Từ bước t = 1 đến t = L)
    # -------------------------------------------------------------------------
    for t in range(1, min(L + 1, total_chunks + 1)):
        current_chunk = received_chunks[t - 1]
        next_pm = [float('inf')] * 4
        
        for current_state in range(4):
            if pm_matrix[current_state][t - 1] == float('inf'):
                continue
            for input_bit in [0, 1]:
                branch = FSM[current_state][input_bit]
                next_state = branch["next"]
                
                branch_metric = current_chunk - branch["encode"] # Dùng phép trừ overload của bạn
                total_metric = pm_matrix[current_state][t - 1] + branch_metric
                
                if total_metric < next_pm[next_state]:
                    next_pm[next_state] = total_metric
                    traceback_matrix[next_state][t] = (current_state, input_bit)
                    
        for s in range(4):
            pm_matrix[s][t] = next_pm[s]

    # -------------------------------------------------------------------------
    # GIAI ĐOẠN 2: Chạy cuốn chiếu (Sliding Window) cho phần dữ liệu còn lại
    # -------------------------------------------------------------------------
    # Con trỏ đọc cụm bit tiếp theo từ file (bắt đầu từ cụm thứ L + 1)
    chunk_idx = L 
    
    while chunk_idx < total_chunks:
        # A. TRACEBACK NGƯỢC 30 BƯỚC ĐỂ LẤY BIT ĐẦU CỬA SỔ (Cột 1)
        # Tìm trạng thái tốt nhất ở cuối cửa sổ (Cột L)
        best_state = 0
        min_m = pm_matrix[0][L]
        for s in range(1, 4):
            if pm_matrix[s][L] < min_m:
                min_m = pm_matrix[s][L]
                best_state = s
                
        # Đi ngược từ cột L về cột 1
        curr_s = best_state
        first_bit_in_window = None
        for t_back in range(L, 0, -1):
            prev_s, input_bit = traceback_matrix[curr_s][t_back]
            if t_back == 1:
                first_bit_in_window = input_bit # Hốt lấy bit tại cột 1
            curr_s = prev_s
            
        decoded_bits.append(str(first_bit_in_window))
        
        # B. DỊCH CHUYỂN CỬA SỔ (SHIFT TRÁI MA TRẬN 1 CỘT)
        for s in range(4):
            for t in range(1, L):
                pm_matrix[s][t] = pm_matrix[s][t + 1]
                traceback_matrix[s][t] = traceback_matrix[s][t + 1]
                
        # C. NẠP CỤM 3 BIT MỚI VÀO CỘT L CUỐI CÙNG
        next_chunk = received_chunks[chunk_idx]
        next_pm = [float('inf')] * 4
        
        for current_state in range(4):
            if pm_matrix[current_state][L - 1] == float('inf'):
                continue
            for input_bit in [0, 1]:
                branch = FSM[current_state][input_bit]
                next_state = branch["next"]
                
                branch_metric = next_chunk - branch["encode"]
                total_metric = pm_matrix[current_state][L - 1] + branch_metric
                
                if total_metric < next_pm[next_state]:
                    next_pm[next_state] = total_metric
                    traceback_matrix[next_state][L] = (current_state, input_bit)
                    
        for s in range(4):
            pm_matrix[s][L] = next_pm[s]
            
        chunk_idx += 1 # Tiến tới cụm bit tiếp theo trong file

    # -------------------------------------------------------------------------
    # GIAI ĐOẠN 3: Thu hoạch nốt các bit còn lại kẹt trong cửa sổ khi hết dữ liệu
    # -------------------------------------------------------------------------
    # Lúc này không nạp thêm nữa, chỉ đơn giản đứng ở cột L và traceback toàn bộ phần còn lại
    best_state = 0
    min_m = pm_matrix[0][L]
    for s in range(1, 4):
        if pm_matrix[s][L] < min_m:
            min_m = pm_matrix[s][L]
            best_state = s
            
    rem_bits = []
    curr_s = best_state
    for t_back in range(L, 0, -1):
        if traceback_matrix[curr_s][t_back] is None:
            break
        prev_s, input_bit = traceback_matrix[curr_s][t_back]
        rem_bits.append(str(input_bit))
        curr_s = prev_s
        
    rem_bits.reverse()
    decoded_bits.extend(rem_bits)
    
    # Gom thành chuỗi hoàn chỉnh
    decoded_string = "".join(decoded_bits)
    
    # Cắt bỏ 2 bit mồi '00' ở ĐẦU và 2 bit đuôi '00' ở CUỐI mà máy phát đã chèn
    clean_huffman_string = decoded_string[2:-2]
    
    return clean_huffman_string


def Receiver(path_file, path_output):
    # 1. Đọc dữ liệu JSON từ khối mô phỏng kênh truyền / khối phát
    with open(path_file, 'r', encoding='utf-8') as f:
        packet_data = json.load(f)
        
    # Sử dụng .get() để lấy an toàn cả 2 trường hợp đặt tên key
    processed_bits_str = packet_data.get("Processed_bits", packet_data.get("Huffman_bits"))
    
    # 2. Gọi thuật toán cửa sổ trượt Viterbi để sửa lỗi và giải mã chuỗi bit
    clean_huffman_string = viterbi_sliding_window(processed_bits_str)
    print(f"✔️ Đã giải mã Viterbi cuốn chiếu thành công!")
    
    # 3. 🛠️ ĐỒNG BỘ RAM: Cập nhật chuỗi bit sạch vào packet_data TRƯỚC KHI GIẢI MÃ NGUỒN
    packet_data["Processed_bits"] = clean_huffman_string
    
    # 🛠️ TRUYỀN THẲNG packet_data (đã sạch) sang cho bộ giải mã Huffman xử lý
    Huffman_Decoder(packet_data, path_output, os.path.basename(path_file))
    print(f"✔️ Đã giải mã Huffman thành công!")
    return clean_huffman_string


def Huffman_Decoder(packet_data, path_output_csv, file_name):
    # 🛠️ NHẬN TRỰC TIẾP packet_data TỪ RAM, không cần mở lại file trên ổ cứng nữa!
    
    # 1. Bóc tách các thành phần cần thiết từ dictionary truyền vào
    t_start = packet_data["metadata"]["tx_timestamp"]
    decoder_dict = packet_data["decoder_dict"]
    entropy = packet_data["metadata"]["entropy"]
    compression_ratio = packet_data["metadata"]["compression_ratio"]
    
    # Lấy chuỗi bit ĐÃ ĐƯỢC LÀM SẠCH bởi Viterbi ở hàm Receiver phía trên
    huffman_bits = packet_data["Processed_bits"]
    
    # --- BẮT ĐẦU QUÁ TRÌNH GIẢI MÃ CHUỖI BIT ---
    current_code = ""
    decoded_text_list = []
    
    for bit in huffman_bits:
        current_code += bit
        if current_code in decoder_dict:
            decoded_text_list.append(decoder_dict[current_code])
            current_code = ""  # Reset để tìm ký tự tiếp theo
            
    decoded_text = "".join(decoded_text_list)
    # --- QUÁ TRÌNH GIẢI MÃ KẾT THÚC XONG XUÔI ---
    
    # 2. 🕒 Chụp ngay mốc thời gian hệ thống tại thời điểm này
    t_end = time.time()
    total_delay = t_end - t_start
    
    # === XỬ LÝ GHI LẠI VÀO FILE .CSV NGUYÊN BẢN ===
    name, _ = os.path.splitext(file_name)
    clean_name = name.replace("_processed", "").replace("_huffmanver", "")
    csv_file_name = f"{clean_name}_recovered.csv"
    
    if path_output_csv is None:
        path_output_csv = os.getcwd()
        
    full_path_csv = os.path.join(path_output_csv, csv_file_name)
    
    with open(full_path_csv, 'w', encoding='utf-8') as csv_f:
        csv_f.write(decoded_text)
    
    # In báo cáo hiệu năng ra màn hình Terminal
    print(f"\n🏁 [RECEIVER] Đã giải mã xong file: {file_name}")
    print(f" -> 💾 Đã khôi phục file gốc tại: {full_path_csv}")
    print(f" -> Đô dài chuỗi bit sạch: {len(huffman_bits)} bits")
    print(f" -> Entropy của file: {entropy:.4f}")
    print(f" -> Compression_ratio: {compression_ratio:.4f}")
    print(f" -> Ký tự khôi phục: {len(decoded_text)} ký tự")
    print(f" ⏱️ => [TOTAL DELAY]: {total_delay:.6f} giây")
    
    return decoded_text, total_delay