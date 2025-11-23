import tkinter as tk
from tkinter import filedialog, Scale, HORIZONTAL, Label, Frame, Canvas, Button, messagebox
from PIL import ImageTk
import sys
import os

# --- Cấu hình đường dẫn để import code từ src ---
# Đoạn này giúp Python tìm thấy thư mục 'src' nằm ngang hàng với 'gui'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import các module xử lý ảnh
from src.utils import load_image_as_array, array_to_image
from src.sketch_effects import sketch_effect, cartoon_effect

class PhotoToSketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần mềm Chuyển Ảnh thành Tranh Vẽ (Xử lý Thủ Công)")
        self.root.geometry("1200x750")
        
        # Biến lưu dữ liệu ảnh
        self.src_img = None       # Ảnh gốc (Numpy Array)
        self.processed_img = None # Ảnh kết quả (PIL Image Object)

        # Biến lưu ảnh hiển thị trên canvas (để tránh bị Garbage Collection thu hồi)
        self.tk_orig = None
        self.tk_proc = None

        self._setup_ui()

    def _setup_ui(self):
        # --- Vùng Điều Khiển (Trái) ---
        control_frame = Frame(self.root, width=280, bg="#f0f0f0", padx=15, pady=15)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        # Giữ kích thước cố định cho khung điều khiển
        control_frame.pack_propagate(False) 
        
        Label(control_frame, text="BẢNG ĐIỀU KHIỂN", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=(0, 20))

        # 1. Nút tải và lưu
        Button(control_frame, text="📂 Tải Ảnh", command=self.load_image, bg="#3498db", fg="white", font=("Arial", 11, "bold"), height=2).pack(fill=tk.X, pady=5)
        Button(control_frame, text="💾 Lưu Kết Quả", command=self.save_image, bg="#2ecc71", fg="white", font=("Arial", 11, "bold"), height=2).pack(fill=tk.X, pady=5)
        
        # 2. Chọn hiệu ứng
        Label(control_frame, text="Chọn Hiệu Ứng:", bg="#f0f0f0", font=("Arial", 11, "bold")).pack(pady=(25, 5), anchor="w")
        
        self.effect_var = tk.StringVar(value="Original")
        modes = [
            ("Ảnh Gốc", "Original"), 
            ("Sketch (Tranh Chì)", "Sketch"), 
            ("Cartoon (Hoạt hình)", "Cartoon")
        ]
        
        for text, mode in modes:
            tk.Radiobutton(control_frame, text=text, variable=self.effect_var, value=mode, 
                           command=self.apply_effect, bg="#f0f0f0", font=("Arial", 10)).pack(anchor="w", pady=2)

        # 3. Slider điều chỉnh
        Label(control_frame, text="Điều chỉnh tham số:", bg="#f0f0f0", font=("Arial", 11, "bold")).pack(pady=(25, 5), anchor="w")
        Label(control_frame, text="(Độ mờ / Độ mịn)", bg="#f0f0f0", font=("Arial", 9, "italic")).pack(anchor="w")
        
        self.param_scale = Scale(control_frame, from_=1, to=15, orient=HORIZONTAL, bg="#f0f0f0")
        self.param_scale.set(5)
        self.param_scale.pack(fill=tk.X)
        
        # Chỉ xử lý khi thả chuột để tránh lag (vì thuật toán code tay chạy nặng)
        self.param_scale.bind("<ButtonRelease-1>", lambda x: self.apply_effect())

        # --- Vùng Hiển Thị (Phải) ---
        display_frame = Frame(self.root, bg="#333333")
        display_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        self.canvas = Canvas(display_frame, bg="#333333")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # Sự kiện resize cửa sổ -> vẽ lại ảnh
        self.canvas.bind("<Configure>", lambda event: self.show_images())

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg *.bmp")])
        if path:
            try:
                # Load ảnh và resize sơ bộ nếu ảnh quá to (để demo mượt hơn)
                self.src_img = load_image_as_array(path)
                
                # Mặc định khi mới load thì ảnh kết quả = ảnh gốc
                self.processed_img = array_to_image(self.src_img)
                
                self.apply_effect()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở ảnh: {e}")

    def apply_effect(self):
        # Nếu chưa load ảnh thì không làm gì cả
        if self.src_img is None:
            return
        
        # Hiển thị trạng thái đang xử lý (con trỏ chuột xoay)
        self.root.config(cursor="watch")
        self.root.update() # Cập nhật UI ngay lập tức
        
        try:
            mode = self.effect_var.get()
            
            # SỬA LỖI 1: Ép kiểu int cho giá trị từ Slider
            val = int(self.param_scale.get())
            
            res_array = None

            if mode == "Sketch":
                # Sketch dùng Gaussian Blur -> val là blur_radius (int)
                res_array = sketch_effect(self.src_img, blur_radius=val)
                
            elif mode == "Cartoon":
                # Cartoon dùng Bilateral Filter -> val là sigma_space (int)
                # edge_threshold cố định hoặc có thể thêm slider khác
                res_array = cartoon_effect(
                    self.src_img, 
                    edge_threshold=100, 
                    sigma_space=val,    # Truyền int vào đây
                    sigma_color=75
                )
            else:
                # Chế độ ảnh gốc
                res_array = self.src_img

            # Chuyển numpy array thành PIL Image để hiển thị
            self.processed_img = array_to_image(res_array)
            self.show_images()
            
        except Exception as e:
            print(f"Lỗi xử lý: {e}")
            messagebox.showerror("Lỗi Thuật Toán", str(e))
        finally:
            # Trả lại con trỏ chuột bình thường
            self.root.config(cursor="")

    def show_images(self):
        # SỬA LỖI 2: Kiểm tra kỹ cả 2 biến ảnh trước khi hiển thị
        if self.src_img is None or self.processed_img is None: 
            return
        
        # Lấy kích thước canvas hiện tại
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        if cw < 100 or ch < 100: return # Chưa render xong giao diện
        
        # Tính toán kích thước hiển thị (chia đôi màn hình)
        target_w = (cw // 2) - 10 # Trừ margin
        target_h = ch - 40
        
        # --- Xử lý Ảnh Gốc ---
        img_orig_pil = array_to_image(self.src_img)
        # Copy và resize để hiển thị (không ảnh hưởng ảnh gốc)
        img_orig_pil.thumbnail((target_w, target_h)) 
        self.tk_orig = ImageTk.PhotoImage(img_orig_pil)
        
        # --- Xử lý Ảnh Kết Quả ---
        # Copy processed_img để resize
        img_proc_view = self.processed_img.copy()
        img_proc_view.thumbnail((target_w, target_h))
        self.tk_proc = ImageTk.PhotoImage(img_proc_view)
        
        # Vẽ lên Canvas
        self.canvas.delete("all")
        
        # Ảnh trái (Gốc)
        self.canvas.create_image(cw//4, ch//2, image=self.tk_orig, anchor=tk.CENTER)
        self.canvas.create_text(cw//4, 20, text="ẢNH GỐC", fill="white", font=("Arial", 12, "bold"))
        
        # Ảnh phải (Kết quả)
        self.canvas.create_image(3*cw//4, ch//2, image=self.tk_proc, anchor=tk.CENTER)
        self.canvas.create_text(3*cw//4, 20, text="KẾT QUẢ", fill="white", font=("Arial", 12, "bold"))

    def save_image(self):
        if self.processed_img:
            path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg")]
            )
            if path:
                self.processed_img.save(path)
                messagebox.showinfo("Thành công", "Đã lưu ảnh!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoToSketchApp(root)
    root.mainloop()