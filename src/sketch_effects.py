import numpy as np
from .filters import rgb_to_gray, convolution, gaussian_kernel, sobel_filters, bilateral_filter_manual
from .utils import normalize_image

def sketch_effect(img_array, blur_radius=5):
    """
    Hiệu ứng 1: Chuyển ảnh thành tranh vẽ chì (Sketch)
    Quy trình: Gray -> Invert -> Gaussian Blur -> Color Dodge
    """
    # 1. Chuyển xám
    gray = rgb_to_gray(img_array)
    
    # 2. Tạo ảnh âm bản
    inv_gray = 255 - gray
    
    # 3. Làm mờ ảnh âm bản (Gaussian Blur)
    sigma = blur_radius if blur_radius > 0 else 1
    kernel_size = int(2 * sigma + 1)
    kernel = gaussian_kernel(kernel_size, sigma)
    blurred_inv = convolution(inv_gray, kernel)
    
    # 4. Color Dodge (Trộn ảnh)
    # Công thức: Final = Gray / (1 - Blurred_Inv/255)
    # Code an toàn tránh chia cho 0:
    def dodge(front, back):
        result = front * 255 / (255 - back + 1e-5) 
        result[result > 255] = 255
        result[back == 255] = 255
        return result

    final_sketch = dodge(gray, blurred_inv)
    return normalize_image(final_sketch)

def cartoon_effect(img_array, edge_threshold=100, sigma_color=50, sigma_space=5):
    """
    Hiệu ứng Cartoon nâng cao với Edge-Preserving Filter
    """
    # 1. Làm mịn bảo toàn biên (Edge-preserving smoothing)
    # Thay thế Gaussian Blur bằng Bilateral Filter
    # diameter=7: Vùng lân cận vừa phải
    # sigma_color: Càng lớn thì các vùng màu càng dễ bị hòa trộn (nhưng vẫn giữ biên nét)
    smooth = bilateral_filter_manual(img_array, diameter=7, sigma_color=sigma_color, sigma_space=sigma_space)
    
    # 2. Lượng tử hóa màu (Color Quantization) trên ảnh đã làm mịn
    # Giảm nhiễu trước khi giảm màu giúp mảng màu phẳng và đẹp hơn
    num_colors = 9
    quantized = np.floor(smooth / (256/num_colors)) * (256/num_colors)
    
    # 3. Phát hiện biên (Edge Detection)
    # Dùng ảnh đã làm mịn để tìm biên -> Biên sẽ "sạch" hơn, ít nhiễu hạt
    gray = rgb_to_gray(smooth) 
    edges = sobel_filters(gray)
    
    # Tạo mask biên (Đen/Trắng)
    edge_mask = np.where(edges > edge_threshold, 0, 1).astype(np.float32)
    # Mở rộng kích thước mask để nhân với ảnh màu 3 kênh
    edge_mask = np.stack([edge_mask]*3, axis=2) 
    
    # 4. Kết hợp
    cartoon = quantized * edge_mask
        
    return normalize_image(cartoon)