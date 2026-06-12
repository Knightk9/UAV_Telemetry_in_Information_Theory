import time
# Bấm giờ bắt đầu

start_cpu = time.perf_counter()

# ... Chạy thuật toán Huffman Encoding ở đây ...

# Bấm giờ kết thúc


# Tính thời gian CPU tiêu tốn (đơn vị: giây)

condition = True
while (condition):
    text_input = int(input("Nhap ki hieu vao: "))
    if text_input == 1:
        condition = False
    
    end_cpu = time.perf_counter()

cpu_duration = end_cpu - start_cpu
print(f"Thuật toán chạy mất: {cpu_duration:.6f} giây")