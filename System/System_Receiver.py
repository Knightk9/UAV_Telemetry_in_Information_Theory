import sys
import os

import System
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import hàm gộp quy trình mới của bạn thay vì import hàm lẻ cũ
from Chanel.Binary_Object import Receiver



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
    list_of_function = [Receiver]

    # Kích hoạt hệ thống đa luồng
    System.performance(list_of_function, path_input, path_output)