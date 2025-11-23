import numpy as np

def rgb_to_gray(img_array):
    """Chuyển ảnh màu sang xám: 0.299R + 0.587G + 0.114B"""
    r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    return gray.astype(np.float32)

def convolution(image, kernel):
    """
    Hàm tích chập thủ công (Manual Convolution).
    Sử dụng kỹ thuật sliding window (cửa sổ trượt).
    """
    if len(image.shape) == 3: # Nếu là ảnh màu, xử lý từng kênh
        h, w, c = image.shape
        # Tạo ảnh kết quả rỗng
        output = np.zeros_like(image) 
        for i in range(c):
            output[:,:,i] = convolution(image[:,:,i], kernel)
        return output

    # Xử lý cho ảnh xám (2D)
    h, w = image.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    
    # Padding ảnh để giữ nguyên kích thước
    padded_img = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')
    output = np.zeros((h, w))

    # Lặp qua từng pixel (Vector hóa nhẹ để tối ưu tốc độ Python)
    # Thay vì 2 vòng lặp for lồng nhau tính từng pixel (rất chậm), 
    # ta lặp qua kernel để cộng dồn giá trị.
    for i in range(kh):
        for j in range(kw):
            # Dịch chuyển vùng ảnh tương ứng với vị trí kernel
            region = padded_img[i:i+h, j:j+w]
            output += region * kernel[i, j]
            
    return output

def gaussian_kernel(size, sigma):
    """Tạo hạt nhân Gaussian thủ công theo công thức toán học"""
    k = size // 2
    x, y = np.mgrid[-k:k+1, -k:k+1]
    normal = 1 / (2.0 * np.pi * sigma**2)
    g =  np.exp(-((x**2 + y**2) / (2.0*sigma**2))) * normal
    return g / g.sum() # Chuẩn hóa để tổng bằng 1

def sobel_filters(img_gray):
    """Phát hiện biên bằng toán tử Sobel"""
    # Kernel Sobel thủ công
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    
    ix = convolution(img_gray, kx)
    iy = convolution(img_gray, ky)
    
    magnitude = np.sqrt(ix**2 + iy**2)
    return magnitude / magnitude.max() * 255

def gaussian(x, sigma):
    """Hàm tính Gaussian cơ bản"""
    return (1.0 / (2 * np.pi * (sigma ** 2))) * np.exp(-(x ** 2) / (2 * (sigma ** 2)))

def bilateral_filter_manual(image, diameter, sigma_color, sigma_space):
    """
    Cài đặt Bilateral Filter thủ công (Vectorized NumPy).
    
    Args:
        image: Ảnh đầu vào (numpy array).
        diameter: Đường kính vùng lân cận (vd: 5, 7, 9).
        sigma_color: Độ lệch chuẩn cho màu sắc (lọc biên).
        sigma_space: Độ lệch chuẩn cho khoảng cách (làm mịn).
    """
    h, w, c = image.shape
    output = np.zeros_like(image)
    
    # Bán kính cửa sổ
    radius = diameter // 2
    
    # 1. Tạo ma trận Gaussian không gian (Spatial Gaussian) - Tính 1 lần dùng mãi
    # Tạo lưới tọa độ (x, y) từ -radius đến +radius
    y, x = np.mgrid[-radius:radius+1, -radius:radius+1]
    # Tính khoảng cách Euclidean bình phương
    spatial_dist_sq = x**2 + y**2
    # Tính trọng số không gian
    spatial_weights = np.exp(-spatial_dist_sq / (2 * sigma_space**2))
    
    # Pad ảnh để xử lý biên
    padded_img = np.pad(image, ((radius, radius), (radius, radius), (0, 0)), mode='symmetric').astype(np.float32)
    
    # Chuẩn hóa ảnh về 0-1 để tính toán mũ cho đỡ tràn số nếu cần, hoặc để float
    
    # 2. Quét qua từng pixel trong cửa sổ (Window sliding)
    # Thay vì loop qua từng pixel của ảnh (chậm), ta loop qua từng vị trí trong kernel (nhanh)
    
    # Khởi tạo tổng trọng số và tổng giá trị pixel
    sum_val = np.zeros_like(image, dtype=np.float32)
    sum_weight = np.zeros((h, w, 1), dtype=np.float32) # Giữ dimension để broadcast
    
    for i in range(diameter):
        for j in range(diameter):
            # Trích xuất vùng ảnh đã dịch chuyển (Shifted Image)
            # Vùng này tương ứng với pixel lân cận (i, j) của TẤT CẢ các pixel trung tâm
            neighbor_img = padded_img[i : i+h, j : j+w, :]
            
            # Tính sự khác biệt màu sắc (Intensity Difference)
            # ||Ip - Iq||^2
            color_diff = np.sum((neighbor_img - image)**2, axis=2, keepdims=True) # Gom kênh màu lại
            
            # Tính trọng số màu sắc (Range Kernel)
            # exp(-diff / 2*sigma^2)
            color_weights = np.exp(-color_diff / (2 * sigma_color**2))
            
            # Trọng số tổng hợp = Spatial * Range
            # Spatial weight tại vị trí (i, j) là hằng số
            w_spatial = spatial_weights[i, j]
            total_weight = w_spatial * color_weights
            
            # Cộng dồn
            sum_val += neighbor_img * total_weight
            sum_weight += total_weight
            
    # 3. Chuẩn hóa (Normalization)
    output = sum_val / sum_weight
    
    return np.clip(output, 0, 255).astype(np.uint8)