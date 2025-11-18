# 🖼️ Convert Image - Ứng Dụng Chuyển Đổi Định Dạng Hình Ảnh

Ứng dụng này cung cấp một giao diện người dùng đơn giản (GUI) được xây dựng bằng **Python Tkinter** để giúp người dùng dễ dàng chuyển đổi các tệp hình ảnh từ định dạng này sang định dạng khác.

## ✨ Tính Năng Chính

* Giao diện thân thiện, dễ sử dụng.
* Hỗ trợ chuyển đổi nhiều định dạng hình ảnh phổ biến (ví dụ: PNG, JPG, BMP, WEBP, v.v.).
* Xử lý hình ảnh hàng loạt (Batch Processing) (nếu có).
* Tùy chọn chất lượng đầu ra (ví dụ: đối với JPEG).

## ⚙️ Yêu Cầu Hệ Thống

* Python 3.x
* Các thư viện được liệt kê trong `requirements.txt` (thường bao gồm Pillow/PIL cho xử lý ảnh).

## 🚀 Cài Đặt và Chạy Ứng Dụng

Thực hiện các bước sau để thiết lập và chạy ứng dụng trên máy tính của bạn.

### 1. Cài Đặt Thư Viện Phụ Thuộc

Trước hết, đảm bảo bạn đã cài đặt tất cả các thư viện Python cần thiết. Sử dụng `pip` để cài đặt các gói từ file `requirements.txt`:

pip install -r requirements.txt

### 2. Khởi chạy ứng dụng
* Chạy script chính của GUI từ thư mục gốc của dự án:

python gui\app_tkinter.py

* Ứng dụng sẽ mở ra, cho phép bạn chọn tệp đầu vào, định dạng đầu ra và bắt đầu thao tác chuyển đổi hình ảnh.
