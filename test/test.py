# E:\Convert_Image\test\test.py
# Giả sử file test.jpg nằm trong cùng thư mục với test.py (E:\Convert_Image\test\)
# Sử dụng đường dẫn tuyệt đối đến src như được cung cấp: E:\Convert_Image\src

import sys
import os
import cv2
import numpy as np

# Thêm đường dẫn tuyệt đối đến src để import
sys.path.append(r'E:\Convert_Image\src')

from filters import to_gray_manual as to_gray
# Không cần import toàn bộ sketch_effects vì chúng ta sẽ tái hiện từng bước manual

def main():
    # Đường dẫn đến ảnh đầu vào
    input_path = os.path.join(os.path.dirname(__file__), 'test.jpg')
    
    if not os.path.exists(input_path):
        print(f"Không tìm thấy file {input_path}. Hãy đặt test.jpg vào thư mục test.")
        return
    
    # Đọc ảnh BGR bằng cv2
    img = cv2.imread(input_path)
    if img is None:
        print("Không thể đọc ảnh. Kiểm tra định dạng file.")
        return
    
    print("Bắt đầu tạo hiệu ứng pencil_sketch từng bước...")
    
    # Bước 1: Chuyển sang mức xám (manual)
    gray = to_gray(img)
    cv2.imwrite('step1_gray.jpg', gray)
    print("Bước 1: Đã lưu ảnh xám tại step1_gray.jpg")
    
    # Bước 2: Đảo màu (sử dụng cv2.bitwise_not)
    inv = cv2.bitwise_not(gray)
    cv2.imwrite('step2_inv.jpg', inv)
    print("Bước 2: Đã lưu ảnh đảo màu tại step2_inv.jpg")
    
    # Bước 3: Làm mờ Gaussian (tạm dùng cv2 cho tốc độ, kernel lớn 21x21)
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    cv2.imwrite('step3_blur.jpg', blur)
    print("Bước 3: Đã lưu ảnh làm mờ tại step3_blur.jpg")
    
    # Bước 4: Phép chia để tạo hiệu ứng chì (sửa lỗi chia 0)
    gray_float = gray.astype(np.float64)
    blur_float = blur.astype(np.float64)
    blur_inv_float = 255.0 - blur_float
    blur_inv_float[blur_inv_float == 0] = 1  # Tránh chia 0
    sketch_float = cv2.divide(gray_float, blur_inv_float, scale=256.0)
    sketch = sketch_float.astype(np.uint8)
    
    # Chuyển sang BGR để lưu (nếu cần, nhưng sketch là gray)
    sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('step4_sketch.jpg', sketch_bgr)
    print("Bước 4: Đã lưu ảnh sketch cuối cùng tại step4_sketch.jpg")
    
    # Tùy chọn: Hiển thị các bước bằng cv2 (comment nếu không cần)
    # cv2.imshow('Step 1: Gray', gray)
    # cv2.imshow('Step 2: Inverted', inv)
    # cv2.imshow('Step 3: Blurred', blur)
    # cv2.imshow('Step 4: Sketch', sketch)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    print("Hoàn tất! Kiểm tra các file step*.jpg trong thư mục test.")

if __name__ == "__main__":
    main()