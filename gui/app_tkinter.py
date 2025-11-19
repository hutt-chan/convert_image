# gui/app_tkinter.py
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from main import apply_effect

class ConvertApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Convert Image — Chuyển ảnh thành tranh vẽ')
        self.geometry('1300x800')

        self.orig_img = None
        self.processed_img = None
        self.current_path = None
        self.effect = tk.StringVar(value='sketch')
        self.filter_type = tk.StringVar(value='bilateral')

        # ==================== LEFT PANEL ====================
        ctrl = tk.Frame(self, width=200, bg='#f0f0f0')
        ctrl.pack(side='left', fill='y', padx=15, pady=15)
        ctrl.pack_propagate(False)

        # -------- Khung chứa các nút phía trên --------
        ctrl_buttons = tk.Frame(ctrl, bg='#f0f0f0')
        ctrl_buttons.pack(fill='x', pady=(0, 20))

        tk.Button(
            ctrl_buttons, text='📁  Mở ảnh', command=self.open_image,
            font=('Segoe UI', 8, 'bold'),
            bg='#333', fg='white', height=1
        ).pack(fill='x', padx=5, pady=5)

        tk.Button(
            ctrl_buttons, text='👁️  Xem trước', command=self.preview,
            bg='#4CAF50', fg='white',
            font=('Segoe UI', 8, 'bold'), height=1
        ).pack(fill='x', padx=5, pady=5)

        tk.Button(
            ctrl_buttons, text='💾  Lưu ảnh đã xử lý', command=self.save_processed,
            bg='#2196F3', fg='white',
            font=('Segoe UI', 8, 'bold'), height=1
        ).pack(fill='x', padx=5, pady=5)

        # -------- Scrolled frame cho các controls phía dưới --------
        canvas = tk.Canvas(ctrl, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(ctrl, orient='vertical', command=canvas.yview)
        ctrl_scrollable = tk.Frame(canvas, bg='#f0f0f0')

        ctrl_scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=ctrl_scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # -------- Các control trong scrolled frame --------
        tk.Label(ctrl_scrollable, text='Hiệu ứng', font=('Segoe UI', 10, 'bold'),
                 bg='#f0f0f0').pack(anchor='w', padx=5, pady=(10,5))

        tk.Radiobutton(ctrl_scrollable, text='Sketch (bút chì)', variable=self.effect,
                       value='sketch', command=self.update_controls,
                       bg='#f0f0f0').pack(anchor='w', padx=5)

        tk.Radiobutton(ctrl_scrollable, text='Cartoon (màu phẳng)', variable=self.effect,
                       value='cartoon', command=self.update_controls,
                       bg='#f0f0f0').pack(anchor='w', padx=5, pady=(0,20))

        # Loại filter làm mịn
        tk.Label(ctrl_scrollable, text='Loại filter làm mịn', font=('Segoe UI', 10, 'bold'),
                 bg='#f0f0f0').pack(anchor='w', padx=5, pady=(10,5))
        tk.Radiobutton(ctrl_scrollable, text='Bilateral (giữ biên)', variable=self.filter_type,
                       value='bilateral', command=self.update_controls,
                       bg='#f0f0f0').pack(anchor='w', padx=5)
        tk.Radiobutton(ctrl_scrollable, text='Gaussian (làm mịn đều)', variable=self.filter_type,
                       value='gaussian', command=self.update_controls,
                       bg='#f0f0f0').pack(anchor='w', padx=5, pady=(0,20))

        # Các thanh thông số
        tk.Label(ctrl_scrollable, text='Blur radius', font=('Segoe UI', 10),
                 bg='#f0f0f0').pack(anchor='w', padx=5)
        self.blur = tk.Scale(ctrl_scrollable, from_=0, to=8, orient='horizontal')
        self.blur.set(2)
        self.blur.pack(fill='x', padx=5, pady=(0,15))

        tk.Label(ctrl_scrollable, text='Độ đậm nét (Edge strength)', font=('Segoe UI', 10),
                 bg='#f0f0f0').pack(anchor='w', padx=5)
        self.strength = tk.Scale(ctrl_scrollable, from_=0.5, to=3.0,
                                 resolution=0.1, orient='horizontal')
        self.strength.set(1.2)
        self.strength.pack(fill='x', padx=5, pady=(0,20))

        # Sketch only
        self.sigma_r_lbl = tk.Label(ctrl_scrollable, text='Bilateral intensity (giữ biên)', font=('Segoe UI', 10),
                                    bg='#f0f0f0')
        self.sigma_r = tk.Scale(ctrl_scrollable, from_=20, to=150,
                                orient='horizontal')
        self.sigma_r.set(50)

        # Cartoon only
        self.edge_thresh_lbl = tk.Label(ctrl_scrollable, text='Edge threshold (Cartoon)',
                                        font=('Segoe UI', 10), bg='#f0f0f0')
        self.edge_thresh = tk.Scale(ctrl_scrollable, from_=10, to=150,
                                    orient='horizontal')
        self.edge_thresh.set(60)

        self.poster_lbl = tk.Label(ctrl_scrollable, text='Posterize levels (Cartoon)',
                                   font=('Segoe UI', 10), bg='#f0f0f0')
        self.poster = tk.Scale(ctrl_scrollable, from_=2, to=16,
                               orient='horizontal')
        self.poster.set(6)

        self.update_controls()

        # ==================== RIGHT PANEL ====================
        right_frame = tk.Frame(self)
        right_frame.pack(side='right', expand=True, fill='both', padx=15, pady=15)

        self.canvas_orig = tk.Canvas(right_frame, bg='#333333')
        self.canvas_orig.pack(side='left', expand=True, fill='both')
        tk.Label(self.canvas_orig, text='Ảnh gốc', fg='white',
                 bg='#333333', font=('Segoe UI', 14)).place(x=15, y=15)

        sep = tk.Frame(right_frame, width=2, bg='gray')
        sep.pack(side='left', fill='y')

        self.canvas_proc = tk.Canvas(right_frame, bg='#333333')
        self.canvas_proc.pack(side='right', expand=True, fill='both')
        tk.Label(self.canvas_proc, text='Sau khi xử lý', fg='white',
                 bg='#333333', font=('Segoe UI', 14)).place(x=15, y=15)

        self.canvas_orig.bind('<Configure>', lambda e: self.show_both())
        self.canvas_proc.bind('<Configure>', lambda e: self.show_both())

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Quay về ảnh gốc", command=self.reset_preview)
        self.canvas_proc.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def update_controls(self):
        eff = self.effect.get()
        filt = self.filter_type.get()

        # Ẩn tất cả
        self.sigma_r_lbl.pack_forget()
        self.sigma_r.pack_forget()
        self.edge_thresh_lbl.pack_forget()
        self.edge_thresh.pack_forget()
        self.poster_lbl.pack_forget()
        self.poster.pack_forget()

        if eff == 'sketch':
            if filt == 'bilateral':
                self.sigma_r_lbl.pack(anchor='w', padx=5)
                self.sigma_r.pack(fill='x', padx=5, pady=(0,20))
        else:
            self.edge_thresh_lbl.pack(anchor='w', padx=5)
            self.edge_thresh.pack(fill='x', padx=5, pady=(0,5))
            self.poster_lbl.pack(anchor='w', padx=5)
            self.poster.pack(fill='x', padx=5, pady=(0,30))
            if filt == 'bilateral':
                self.sigma_r_lbl.pack(anchor='w', padx=5)
                self.sigma_r.pack(fill='x', padx=5, pady=(0,20))

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[('Images', '*.png *.jpg *.jpeg *.bmp *.gif')])
        if not path: return
        self.current_path = path
        self.orig_img = Image.open(path).convert('RGB')
        self.processed_img = self.orig_img.copy()
        self.show_both()

    def show_both(self):
        if not self.orig_img: return
        self._show_on_canvas(self.canvas_orig, self.orig_img)
        img_to_show = self.processed_img if self.processed_img else self.orig_img
        self._show_on_canvas(self.canvas_proc, img_to_show)

    def _show_on_canvas(self, canvas, pil_img):
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 10 or ch < 10: return
        w, h = pil_img.size
        scale = min((cw-30)/w, (ch-60)/h, 1.0)
        new_w, new_h = int(w*scale), int(h*scale)
        resized = pil_img.resize((new_w, new_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        canvas.delete('all')
        canvas.create_image(cw//2, ch//2, image=photo, anchor='center')
        canvas.image = photo

    def preview(self):
        if not self.orig_img:
            messagebox.showwarning('Lỗi', 'Chưa mở ảnh!')
            return
        params = {
            'blur_radius': self.blur.get(),
            'edge_strength': self.strength.get(),
            'filter_type': self.filter_type.get(),
        }
        if self.effect.get() == 'sketch':
            if self.filter_type.get() == 'bilateral':
                params['sigma_r'] = self.sigma_r.get()
        else:
            params['edge_thresh'] = self.edge_thresh.get()
            params['posterize_levels'] = self.poster.get()
            if self.filter_type.get() == 'bilateral':
                params['sigma_r'] = self.sigma_r.get()

        self.processed_img = apply_effect(self.orig_img, effect=self.effect.get(), params=params)
        self.show_both()

    def save_processed(self):
        if not self.processed_img:
            messagebox.showwarning('Chưa có ảnh xử lý', 'Vui lòng bấm "Xem trước" trước.')
            return
        # Sửa: Để người dùng tự chọn folder, đặt tên file và định dạng
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("BMP files", "*.bmp"), ("GIF files", "*.gif")],
            initialfile=f"{os.path.splitext(os.path.basename(self.current_path))[0]}_{self.effect.get()}"  # Gợi ý tên mặc định
        )
        if not save_path:
            return  # Hủy thì không làm gì
        self.processed_img.save(save_path)
        messagebox.showinfo('Thành công', f'Đã lưu:\n{save_path}')

    def reset_preview(self):
        if self.orig_img:
            self.processed_img = self.orig_img.copy()
            self.show_both()

if __name__ == '__main__':
    app = ConvertApp()
    app.mainloop()