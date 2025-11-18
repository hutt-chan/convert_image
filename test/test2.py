# E:\Convert_Image\test\test2.py
# Giả sử file test.jpg nằm trong cùng thư mục với test2.py (E:\Convert_Image\test\)
# Sử dụng đường dẫn tuyệt đối đến src như được cung cấp: E:\Convert_Image\src

import sys
import os
import cv2
import numpy as np

# Thêm đường dẫn tuyệt đối đến src để import
sys.path.append(r'E:\Convert_Image\src')

from filters import to_gray_manual as to_gray
from filters import smooth_manual as smooth
from filters import detect_edges_manual as detect_edges
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
    
    print("Bắt đầu tạo hiệu ứng smooth_sketch từng bước...")
    
    # Bước 1: Chuyển sang mức xám (manual)
    gray = to_gray(img)
    cv2.imwrite('step1_gray.jpg', gray)
    print("Bước 1: Đã lưu ảnh xám tại step1_gray.jpg")
    
    # Bước 2: Làm mịn bảo toàn biên (manual bilateral)
    print("Đang lọc Bilateral (manual)... Vui lòng đợi...")
    blur = smooth(gray, "bilateral")
    print("Đã lọc xong Bilateral.")
    cv2.imwrite('step2_blur.jpg', blur)
    print("Bước 2: Đã lưu ảnh làm mịn tại step2_blur.jpg")
    
    # Bước 3: Phát hiện biên (manual Sobel)
    edges = detect_edges(blur)
    cv2.imwrite('step3_edges.jpg', edges)
    print("Bước 3: Đã lưu ảnh biên tại step3_edges.jpg")
    
    # Bước 4: Đảo màu biên (sử dụng cv2.bitwise_not)
    edges_inv = cv2.bitwise_not(edges)
    cv2.imwrite('step4_inv.jpg', edges_inv)
    print("Bước 4: Đã lưu ảnh đảo màu biên tại step4_inv.jpg")
    
    # Bước 5: Chuyển sang BGR để tạo sketch cuối
    sketch = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('step5_sketch.jpg', sketch)
    print("Bước 5: Đã lưu ảnh sketch cuối cùng tại step5_sketch.jpg")
    
    # Tùy chọn: Hiển thị các bước bằng cv2 (comment nếu không cần)
    # cv2.imshow('Step 1: Gray', gray)
    # cv2.imshow('Step 2: Blurred', blur)
    # cv2.imshow('Step 3: Edges', edges)
    # cv2.imshow('Step 4: Inverted Edges', edges_inv)
    # cv2.imshow('Step 5: Sketch', sketch)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    print("Hoàn tất! Kiểm tra các file step*.jpg trong thư mục test.")

if __name__ == "__main__":
    main()