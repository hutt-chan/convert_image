import numpy as np
from PIL import Image

def load_image_as_array(filepath):
    """Đọc ảnh từ đường dẫn và chuyển thành numpy array RGB"""
    img = Image.open(filepath).convert('RGB')
    # Resize ảnh nếu quá lớn để xử lý nhanh hơn (tùy chọn)
    img.thumbnail((800, 800)) 
    return np.array(img)

def array_to_image(img_array):
    """Chuyển numpy array trở lại thành PIL Image để hiển thị"""
    return Image.fromarray(np.clip(img_array, 0, 255).astype('uint8'))

def normalize_image(img):
    """Chuẩn hóa giá trị về 0-255"""
    return np.clip(img, 0, 255).astype(np.uint8)