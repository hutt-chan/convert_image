# E:\Convert_Image\test\test.py
# Xử lý tất cả ảnh từ 1.jpg đến 50.jpg trong thư mục E:\Convert_Image\input_images
# Lưu kết quả vào E:\Convert_Image\output_images với tên như 1_pencil_sketch.jpg

import sys
import os
import cv2
import numpy as np

# Thêm đường dẫn tuyệt đối đến src để import
sys.path.append(r'E:\Convert_Image\src')

from filters import to_gray_manual as to_gray
# Không cần import toàn bộ sketch_effects vì chúng ta sẽ tái hiện từng bước manual

def main():
    # Định nghĩa thư mục input và output
    input_dir = r'E:\Convert_Image\input_images'
    output_dir = r'E:\Convert_Image\output_images'
    
    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(output_dir, exist_ok=True)
    
    print("Bắt đầu xử lý hiệu ứng pencil_sketch cho tất cả ảnh...")
    
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
        
        # Bước 2: Đảo màu (sử dụng cv2.bitwise_not)
        inv = cv2.bitwise_not(gray)
        
        # Bước 3: Làm mờ Gaussian (tạm dùng cv2 cho tốc độ, kernel lớn 21x21)
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        
        # Bước 4: Phép chia để tạo hiệu ứng chì (sửa lỗi chia 0)
        gray_float = gray.astype(np.float64)
        blur_float = blur.astype(np.float64)
        blur_inv_float = 255.0 - blur_float
        blur_inv_float[blur_inv_float == 0] = 1  # Tránh chia 0
        sketch_float = cv2.divide(gray_float, blur_inv_float, scale=256.0)
        sketch = sketch_float.astype(np.uint8)
        
        # Chuyển sang BGR để lưu (nếu cần, nhưng sketch là gray)
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        # Lưu ảnh sketch cuối cùng
        output_path = os.path.join(output_dir, f"{i}_pencil_sketch.jpg")
        cv2.imwrite(output_path, sketch_bgr)
        print(f"Đã lưu ảnh sketch tại {output_path}")
    
    print("Hoàn tất! Kiểm tra thư mục output_images.")

if __name__ == "__main__":
    main()