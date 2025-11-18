# E:\Convert_Image\test\test1.py
# Xử lý tất cả ảnh từ 1.jpg đến 50.jpg trong thư mục E:\Convert_Image\input_images
# Lưu kết quả vào E:\Convert_Image\output_images với tên như 1_edge_sketch.jpg

import sys
import os
import cv2
import numpy as np

# Thêm đường dẫn tuyệt đối đến src để import
sys.path.append(r'E:\Convert_Image\src')

from filters import to_gray_manual as to_gray
from filters import detect_edges_manual as detect_edges
# Không cần import toàn bộ sketch_effects vì chúng ta sẽ tái hiện từng bước manual

def main():
    # Định nghĩa thư mục input và output
    input_dir = r'E:\Convert_Image\input_images'
    output_dir = r'E:\Convert_Image\output_images'
    
    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(output_dir, exist_ok=True)
    
    print("Bắt đầu xử lý hiệu ứng edge_sketch cho tất cả ảnh...")
    
    for i in range(1, 51):
        input_path = os.path.join(input_dir, f"{i}.jpg")
        
        if not os.path.exists(input_path):
            print(f"Không tìm thấy file {input_path}. Bỏ qua.")
            continue
        
        # Đọc ảnh BGR bằng cv2
        img = cv2.imread(input_path)
        if img is None:
            print(f"Không thể đọc ảnh {input_path}. Kiểm tra định dạng file. Bỏ qua.")
            continue
        
        print(f"Xử lý ảnh {i}.jpg...")
        
        # Bước 1: Chuyển sang mức xám (manual)
        gray = to_gray(img)
        
        # Bước 2: Phát hiện biên (manual Sobel)
        edges = detect_edges(gray)
        
        # Bước 3: Đảo màu biên (sử dụng cv2.bitwise_not)
        edges_inv = cv2.bitwise_not(edges)
        
        # Bước 4: Chuyển sang BGR để tạo sketch cuối
        sketch = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        
        # Lưu ảnh sketch cuối cùng
        output_path = os.path.join(output_dir, f"{i}_edge_sketch.jpg")
        cv2.imwrite(output_path, sketch)
        print(f"Đã lưu ảnh sketch tại {output_path}")
    
    print("Hoàn tất! Kiểm tra thư mục output_images.")

if __name__ == "__main__":
    main()