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
    convolutional_code = conv_decode("000" + Packet_ver_Huffman.huffman_bit_string + "000",list_of_conv )
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


"""
Day la nho Gemini lam ho :3
"""
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



"""
Về bản chất, thuật toán này không sai,nhưng với tôi nó chưa đủ hiệu quả. Vì cơ bản ở đây tôi đặt câu hỏi là :
nếu 2 bit trước đó ở trạng thái này thì bit nào mới là bit tốt nhất để nối với nó, điều này chưa thỏa mã được tôi.
"""
def GreedY_Viterbi_Algorithm(processed_bits_string):
    transition_matrix_B = {
        #00           0-00                                  1-00
        0: {0: {"next": 0, "encode": Binary_Object('000')}, 1: {"next": 2, "encode": Binary_Object("111")} , "code" : "0"},
        #01            0-01                                 1-01
        1: {0: {"next": 0, "encode": Binary_Object('110')}, 1: {"next": 2, "encode": Binary_Object("001")} , "code" : "0"},
        #10            0-10                                 1-10
        2: {0: {"next": 1, "encode": Binary_Object('101')}, 1: {"next": 3, "encode": Binary_Object("010")} , "code" : "1"},
        #11            0-11                                 1-11
        3: {0: {"next": 1, "encode": Binary_Object('011')}, 1: {"next": 3, "encode": Binary_Object("100")} , "code" : "1"},
    }
    bits_to_process = [Binary_Object(processed_bits_string[i:i+3]) for i in range(0, len(processed_bits_string), 3)]

    
    #1. Initialization
    first_symbol = bits_to_process[0]
    second_symbol = bits_to_process[1]
    surival_path = [] # Time,Path
    cost_path = [{}] #Time,path:cost
    #Vi 2 bit dau da duoc chen them so 0 de ma hoa nen ta can xet rieng truowng hop nay
    #00-00
    cost_path[0][0] = (Binary_Object("000") - first_symbol) + (Binary_Object("000") - second_symbol)
    #10-00
    cost_path[0][2] = (Binary_Object("000") - first_symbol) + (Binary_Object("111") - second_symbol)
    #0-1-00
    cost_path[0][1] = (Binary_Object("111") - first_symbol) + (Binary_Object("101") - second_symbol)
    #1-1-00
    cost_path[0][3] = (Binary_Object("111") - first_symbol) + (Binary_Object("010") - second_symbol)
    tim_min = cost_path[0][0]
    first_path = 0
    for i in range(4):
        if cost_path[0][i] <= tim_min:
            tim_min = cost_path[0][i]  # Đã sửa lỗi cập nhật min
            first_path = i
    surival_path.append(first_path)
    #2 Performnace
    for i in range(len(bits_to_process)):
        prev_state = surival_path[-1]
        surival_path.append(
            transition_matrix_B[prev_state][0]["next"] 
            if (transition_matrix_B[prev_state][0]["encode"] - bits_to_process[i]) < (transition_matrix_B[prev_state][1]["encode"] - bits_to_process[i]) 
            else transition_matrix_B[prev_state][1]["next"]
        )
    res = ""
    for i in surival_path:
        res += transition_matrix_B[i]["code"]

    return res



"""
Vì vậy, ở đây, tôi muốn đặt thêm một điều kiện tốt hơn để tối ưu được nó:
tôi sẽ đặt ở đây 2 câu hỏi:
1. Nếu đây là bit 0, thi trang thai nao la tot nhat voi no,Nếu đây là bit 1 thì trạng thái nào là tốt nhất với nó
2. Nếu trạng thái hiện tại là tốt nhất với nó thì đâu là trạng thái trước đó tốt nhát với nó trong trường hợp bit hiện tại là bit 1 và tương tự như bit 0

"""
def DynamicPrograming_Viterbi_Algorithm(processed_bits_string):
    
    #Tôi vẫn giũa lại điều kiện cốt lõi so với bài toán trên, nhưng tôi sẽ thêm vào 2 nhân tốt mới
    transition_matrix_B = {
        #00           0-00                                  1-00
        0: {0: {"next": 0, "encode": Binary_Object('000')}, 1: {"next": 2, "encode": Binary_Object("111")} , "code" : "0"},
        #01            0-01                                 1-01
        1: {0: {"next": 0, "encode": Binary_Object('110')}, 1: {"next": 2, "encode": Binary_Object("001")} , "code" : "0"},
        #10            0-10                                 1-10
        2: {0: {"next": 1, "encode": Binary_Object('101')}, 1: {"next": 3, "encode": Binary_Object("010")} , "code" : "1"},
        #11            0-11                                 1-11
        3: {0: {"next": 1, "encode": Binary_Object('011')}, 1: {"next": 3, "encode": Binary_Object("100")} , "code" : "1"},
    }
    bits_to_process = [Binary_Object(processed_bits_string[i:i+3]) for i in range(0, len(processed_bits_string), 3)]
    surival_cost = {0: 0, 1: float('inf'), 2: float('inf'), 3: float('inf')} # Li do o state 0 = 0 vi toi da cho 3 bit dau o pah tren kia la 000 roi
    surival_path = []# Luu lai nhung con duong toi uu cua tung state
    for T in range(0,len(bits_to_process)):
        current_cost = {} #Cost cua hien tai
        current_path = {} #Trang thai cua hien tai
        symbol = bits_to_process[T]
        #1. Neu doan bit dau la 0, ta co 2 state: 0,1
        cost_from_0 = surival_cost[0] + (transition_matrix_B[0][0]["encode"] - symbol)
        cost_from_1 = surival_cost[1] + (transition_matrix_B[1][0]["encode"] - symbol)
        current_cost[0] = min(cost_from_0, cost_from_1)
        current_path[0] = 0 if cost_from_0 < cost_from_1 else 1

        cost_from_2 = surival_cost[2] + (transition_matrix_B[2][0]["encode"] - symbol)
        cost_from_3 = surival_cost[3] + (transition_matrix_B[3][0]["encode"] - symbol)
        current_cost[1] = min(cost_from_2, cost_from_3)
        current_path[1] = 2 if cost_from_2 < cost_from_3 else 3

        #2. Neu doan bit dau vao la 1, ta co 2 state: 2,3
        cost_from_0_b1 = surival_cost[0] + (transition_matrix_B[0][1]["encode"] - symbol)
        cost_from_1_b1 = surival_cost[1] + (transition_matrix_B[1][1]["encode"] - symbol)
        current_cost[2] = min(cost_from_0_b1, cost_from_1_b1)
        current_path[2] = 0 if cost_from_0_b1 < cost_from_1_b1 else 1

        cost_from_2_b1 = surival_cost[2] + (transition_matrix_B[2][1]["encode"] - symbol)
        cost_from_3_b1 = surival_cost[3] + (transition_matrix_B[3][1]["encode"] - symbol)
        current_cost[3] = min(cost_from_2_b1, cost_from_3_b1)
        current_path[3] = 2 if cost_from_2_b1 < cost_from_3_b1 else 3

        surival_path.append(current_path)
        for i in range(4):
            surival_cost[i] = current_cost[i]

    true_path = 0
    total_bits_error = float("inf")
    for i in range(4):
        if surival_cost[i] < total_bits_error:
            total_bits_error = surival_cost[i]
            true_path = i

    decoded_bits_list = []
    for current_path_dict in reversed(surival_path):
        prev_state = current_path_dict[true_path]
        decoded_bits_list.append(transition_matrix_B[prev_state]["code"])
        true_path = prev_state
    decoded_bits_list.reverse()
    res = "".join(decoded_bits_list)
    len_of_bits = len(res)
    res_clean = res[3:-3]
    return res_clean,total_bits_error,len_of_bits



def Receiver(path_file, path_output):
    
    with open(path_file, 'r', encoding='utf-8') as f:
        packet_data = json.load(f)

    processed_bits_str = packet_data.get("Processed_bits", packet_data.get("Huffman_bits"))
    
    # Giải mã sửa lỗi bằng Viterbi
    clean_huffman_string, total_bits_error, len_of_bits = DynamicPrograming_Viterbi_Algorithm(processed_bits_str)
    print(f"✔️ Đã giải mã Viterbi cuốn chiếu thành công!")
    
    BER = total_bits_error / len_of_bits if len_of_bits > 0 else 0
    
    if BER > 0.5:
        print("❌ File da loi hon 50%, Khong the Ma hoa tiep duoc nua")
 
        
        # 🛠️ Tính toán Packet Loss real-time ngay trước khi thoát hàm


    
    packet_data["Processed_bits"] = clean_huffman_string
    
    # Giải mã nguồn và khôi phục CSV
    texxt, delay = Huffman_Decoder(packet_data, path_output, os.path.basename(path_file))
    
    # Tính thông lượng thực tế (bit/s hoặc ký tự/s)
    throughput = (len_of_bits - total_bits_error) / delay if delay > 0 else 0
    
    # 🛠️ Sửa lỗi chữ f nằm trong chuỗi in và làm tròn .2f cho gọn
    print(f" -> Ký tự khôi phục trên giây: {throughput:.2f} ký tự/s")
    print(f" -> Tỷ lệ ký tự bị lỗi (BER): {BER * 100:.2f} %")
    print(f"✔️ Đã giải mã Huffman thành công!")
    
    return clean_huffman_string


def Huffman_Decoder(packet_data, path_output_csv, file_name):
    t_start = packet_data["metadata"]["tx_timestamp"]
    decoder_dict = packet_data["decoder_dict"]
    entropy = packet_data["metadata"]["entropy"]
    compression_ratio = packet_data["metadata"]["compression_ratio"]
    huffman_bits = packet_data["Processed_bits"]
    
    current_code = ""
    decoded_text_list = []
    
    for bit in huffman_bits:
        current_code += bit
        if current_code in decoder_dict:
            decoded_text_list.append(decoder_dict[current_code])
            current_code = ""
            
    decoded_text = "".join(decoded_text_list)
    
    t_end = time.time()
    total_delay = t_end - t_start
    
    name, _ = os.path.splitext(file_name)
    clean_name = name.replace("_processed", "").replace("_huffmanver", "")
    csv_file_name = f"{clean_name}_recovered.csv"
    
    if path_output_csv is None:
        path_output_csv = os.getcwd()
        
    full_path_csv = os.path.join(path_output_csv, csv_file_name)
    
    with open(full_path_csv, 'w', encoding='utf-8') as csv_f:
        csv_f.write(decoded_text)
    
    print(f"\n🏁 [RECEIVER] Đã giải mã xong file: {file_name}")
    print(f" -> 💾 Đã khôi phục file gốc tại: {full_path_csv}")
    print(f" -> Độ dài chuỗi bit sạch: {len(huffman_bits)} bits")
    print(f" -> Entropy của file: {entropy:.4f}")
    print(f" -> Compression_ratio: {compression_ratio:.4f}")
    print(f" -> Ký tự khôi phục: {len(decoded_text)} ký tự")
    print(f" ⏱️ => [TOTAL DELAY]: {total_delay:.6f} giây")
    
    return decoded_text, total_delay