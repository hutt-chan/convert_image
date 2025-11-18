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

        # ==================== LEFT PANEL ====================
        ctrl = tk.Frame(self, width=280, bg='#f0f0f0')
        ctrl.pack(side='left', fill='y', padx=15, pady=15)
        ctrl.pack_propagate(False)

        # -------- Khung chứa các control phía trên --------
        ctrl_top = tk.Frame(ctrl, bg='#f0f0f0')
        ctrl_top.pack(fill='both', expand=True)

        tk.Button(ctrl_top, text='Mở ảnh', command=self.open_image,
                  font=14, bg='#333', fg='white').pack(fill='x', pady=8)

        tk.Label(ctrl_top, text='Hiệu ứng', font=('Segoe UI', 12, 'bold'),
                 bg='#f0f0f0').pack(anchor='w', pady=(30,5))

        tk.Radiobutton(ctrl_top, text='Sketch (bút chì)', variable=self.effect,
                       value='sketch', command=self.update_controls,
                       bg='#f0f0f0').pack(anchor='w')

        tk.Radiobutton(ctrl_top, text='Cartoon (màu phẳng)', variable=self.effect,
                       value='cartoon', command=self.update_controls,
                       bg='#f0f0f0').pack(anchor='w', pady=(0,20))

        # Các thanh thông số
        tk.Label(ctrl_top, text='Blur radius', font=10,
                 bg='#f0f0f0').pack(anchor='w')
        self.blur = tk.Scale(ctrl_top, from_=0, to=8, orient='horizontal')
        self.blur.set(2)
        self.blur.pack(fill='x', pady=(0,15))

        tk.Label(ctrl_top, text='Độ đậm nét (Edge strength)', font=10,
                 bg='#f0f0f0').pack(anchor='w')
        self.strength = tk.Scale(ctrl_top, from_=0.5, to=3.0,
                                 resolution=0.1, orient='horizontal')
        self.strength.set(1.2)
        self.strength.pack(fill='x', pady=(0,20))

        # Sketch only
        self.thresh_lbl = tk.Label(ctrl_top, text='Threshold (Sketch)', font=10,
                                   bg='#f0f0f0')
        self.thresh = tk.Scale(ctrl_top, from_=10, to=200,
                               orient='horizontal')
        self.thresh.set(100)

        self.sigma_r_lbl = tk.Label(ctrl_top, text='Bilateral intensity (giữ biên)', font=10,
                                    bg='#f0f0f0')
        self.sigma_r = tk.Scale(ctrl_top, from_=20, to=150,
                                orient='horizontal')
        self.sigma_r.set(50)

        # Cartoon only
        self.edge_thresh_lbl = tk.Label(ctrl_top, text='Edge threshold (Cartoon)',
                                        font=10, bg='#f0f0f0')
        self.edge_thresh = tk.Scale(ctrl_top, from_=10, to=150,
                                    orient='horizontal')
        self.edge_thresh.set(60)

        self.poster_lbl = tk.Label(ctrl_top, text='Posterize levels (Cartoon)',
                                   font=10, bg='#f0f0f0')
        self.poster = tk.Scale(ctrl_top, from_=2, to=16,
                               orient='horizontal')
        self.poster.set(6)

        self.update_controls()

        # -------- Hai nút đáy panel --------
        tk.Button(ctrl, text='Xem trước', command=self.preview,
                  bg='#4CAF50', fg='white', font=12, height=2)\
            .pack(side='bottom', fill='x', pady=10)

        tk.Button(ctrl, text='Lưu ảnh đã xử lý', command=self.save_processed,
                  bg='#2196F3', fg='white', font=12, height=2)\
            .pack(side='bottom', fill='x', pady=10)

        # ==================== RIGHT PANEL ====================
        right_frame = tk.Frame(self)
        right_frame.pack(side='right', expand=True, fill='both', padx=15, pady=15)

        self.canvas_orig = tk.Canvas(right_frame, bg='#333333')
        self.canvas_orig.pack(side='left', expand=True, fill='both')
        tk.Label(self.canvas_orig, text='Ảnh gốc', fg='white',
                 bg='#333333', font=14).place(x=15, y=15)

        sep = tk.Frame(right_frame, width=2, bg='gray')
        sep.pack(side='left', fill='y')

        self.canvas_proc = tk.Canvas(right_frame, bg='#333333')
        self.canvas_proc.pack(side='right', expand=True, fill='both')
        tk.Label(self.canvas_proc, text='Sau khi xử lý', fg='white',
                 bg='#333333', font=14).place(x=15, y=15)

        self.canvas_orig.bind('<Configure>', lambda e: self.show_both())
        self.canvas_proc.bind('<Configure>', lambda e: self.show_both())

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Quay về ảnh gốc", command=self.reset_preview)
        self.canvas_proc.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def update_controls(self):
        eff = self.effect.get()

        # Ẩn tất cả
        self.thresh_lbl.pack_forget()
        self.thresh.pack_forget()
        self.sigma_r_lbl.pack_forget()
        self.sigma_r.pack_forget()
        self.edge_thresh_lbl.pack_forget()
        self.edge_thresh.pack_forget()
        self.poster_lbl.pack_forget()
        self.poster.pack_forget()

        if eff == 'sketch':
            self.thresh_lbl.pack(anchor='w')
            self.thresh.pack(fill='x', pady=(0,10))
            self.sigma_r_lbl.pack(anchor='w')
            self.sigma_r.pack(fill='x', pady=(0,20))
        else:
            self.edge_thresh_lbl.pack(anchor='w')
            self.edge_thresh.pack(fill='x', pady=(0,5))
            self.poster_lbl.pack(anchor='w')
            self.poster.pack(fill='x', pady=(0,30))

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
        }
        if self.effect.get() == 'sketch':
            params['threshold_val'] = self.thresh.get()
            params['sigma_r'] = self.sigma_r.get()
        else:
            params['edge_thresh'] = self.edge_thresh.get()
            params['posterize_levels'] = self.poster.get()

        self.processed_img = apply_effect(self.orig_img, effect=self.effect.get(), params=params)
        self.show_both()

    def save_processed(self):
        if not self.processed_img:
            messagebox.showwarning('Chưa có ảnh xử lý', 'Vui lòng bấm "Xem trước" trước.')
            return
        outdir = filedialog.askdirectory()
        if not outdir: return
        name = os.path.basename(self.current_path)
        name, ext = os.path.splitext(name)
        save_path = os.path.join(outdir, f"{name}_{self.effect.get()}{ext}")
        self.processed_img.save(save_path)
        messagebox.showinfo('Thành công', f'Đã lưu:\n{save_path}')

    def reset_preview(self):
        if self.orig_img:
            self.processed_img = self.orig_img.copy()
            self.show_both()

if __name__ == '__main__':
    app = ConvertApp()
    app.mainloop()