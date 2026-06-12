import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import hàm gộp quy trình mới của bạn thay vì import hàm lẻ cũ
from Chanel.Binary_Object import transmitter_ver_2 

def performance(list_of_function, path_input, path_output):
    processed_path_file = set() # Dùng set() để tra cứu nhanh
    signal = True

    # Khởi tạo một mảng lộ trình nội bộ từ 2 tham số đầu vào để cấp cho vòng lặp Pipeline
    list_of_paths = [path_input, path_output]

    # Khởi tạo một Pool chứa tối đa 4 hoặc 8 luồng xử lý song song (tùy cấu hình máy)
    with ThreadPoolExecutor(max_workers=8) as executor:
        while signal:
            if os.path.exists(os.path.join(path_input, "stop.txt")):
                break

            unprocessed_path_file = []
            for root, dirs, files in os.walk(path_input):
                for file in files:
                    if file == "stop.txt": continue
                    path_file = os.path.join(root, file)
                    if path_file not in processed_path_file:
                        unprocessed_path_file.append(path_file)

            # Thay vì dùng vòng lặp FOR tuần tự, ta phát lệnh xử lý SONG SONG
            for path_file in unprocessed_path_file:
                # Định nghĩa một job gộp: chạy toàn bộ list_of_function cho 1 file
                def run_pipeline(p_file):
                    # p_file ban đầu là đường dẫn đầy đủ, ví dụ: "Khối_Nguồn/packet_1.json"
                    current_file_path = p_file 
                    
                    for i, function in enumerate(list_of_function):
                        # Đầu vào của hàm i chính là thư mục ở vị trí i
                        # Đầu ra của hàm i chính là thư mục ở vị trí i + 1
                        next_folder_output = list_of_paths[i + 1]
                        
                        # Chạy hàm xử lý (Hàm này sẽ đọc file cũ, ghi file mới sang folder mới và xóa file cũ)
                        function(current_file_path, next_folder_output)
                        
                        # Cập nhật lại đường dẫn mới của file để hàm tiếp theo biết đường mà tìm
                        file_name = os.path.basename(current_file_path)
                        current_file_path = os.path.join(next_folder_output, file_name)
                
                # Giao việc cho ThreadPool, luồng nào rảnh sẽ tự động hốt file chạy luôn
                executor.submit(run_pipeline, path_file)
                
                # Lưu vết luôn vào set
                processed_path_file.add(path_file)
            
            # Thêm một nhịp nghỉ ngắn để vòng lặp while không chiếm dụng 100% tài nguyên CPU
            time.sleep(0.5)


# --- CHƯƠNG TRÌNH CHÍNH ---

if __name__ == "__main__":
    # Nhập đường dẫn và tự động gọt bỏ dấu ngoặc kép dư thừa nếu có
    path_input = input("👉 Hãy nhập path đầu vào (hoặc kéo thả folder vào đây): ").strip('\'"')
    path_output = input("👉 Hãy nhập path đầu ra (hoặc kéo thả folder vào đây): ").strip('\'"')
    
    # Kiểm tra nếu người dùng bấm Enter bỏ trống không nhập gì
    if not path_input or not path_output:
        print("❌ [LỖI] Đường dẫn không được để trống!")
        sys.exit(1)

    # Đảm bảo các thư mục tồn tại trước khi chạy để không bị lỗi OS
    os.makedirs(path_input, exist_ok=True)
    os.makedirs(path_output, exist_ok=True)

    # Đưa duy nhất hàm quy trình gộp (RAM-based) vào danh sách xử lý
    list_of_function = [transmitter_ver_2]

    # Kích hoạt hệ thống đa luồng
    performance(list_of_function, path_input, path_output)