import os
import sys
import customtkinter as ctk
from PIL import Image
import tkinter.messagebox as messagebox
import controller.login_controller as LoginController
import re
from datetime import datetime

class Login:
    def __init__(self, root, on_login_success=None):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Đăng nhập hệ thống")
        
        # Đặt kích thước cửa sổ đăng nhập
        window_width = 900
        window_height = 550
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.configure(fg_color="#2e7a84")
        self.root.resizable(False, False)
        self.after_ids = []
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root, width=800, height=450, fg_color="white", corner_radius=20)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.left_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=20)
        self.left_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.left_frame, text="Đăng nhập", text_color="#2e7a84", font=("Arial", 24, "bold")).pack(pady=(10, 20))

        self.entry_user = ctk.CTkEntry(self.left_frame, placeholder_text="Tên đăng nhập", font=("Arial", 12), corner_radius=20)
        self.entry_user.pack(pady=10, fill="x")

        self.entry_pass = ctk.CTkEntry(self.left_frame, placeholder_text="Mật khẩu", font=("Arial", 12), show="*", corner_radius=20)
        self.entry_pass.pack(pady=10, fill="x")

        ctk.CTkButton(self.left_frame, text="Đăng nhập", fg_color="#2e7a84", hover_color="#255a5f",
                      font=("Arial", 12, "bold"), corner_radius=20,
                      command=lambda: self.login(self.entry_user.get(), self.entry_pass.get())).pack(pady=(20, 10), fill="x")

        ctk.CTkButton(self.left_frame, text="Đăng ký", fg_color="#ff0000", hover_color="#c13b31",
                      font=("Arial", 12, "bold"), corner_radius=20, command=self.register).pack(pady=(0, 10), fill="x")

        change_pass_label = ctk.CTkLabel(self.left_frame, text="Bạn quên mật khẩu? Lấy lại mật khẩu",
                                        text_color="green", font=("Arial", 12), cursor="hand2")
        change_pass_label.pack(pady=(0, 10), fill="x")
        change_pass_label.bind("<Button-1>", lambda event: self.open_forgot_password_window())

        self.right_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=20)
        self.right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(self.right_frame, text="HỆ THỐNG QUẢN LÝ VẬT NUÔI", text_color="#2e7a84",
                     font=("Arial", 16, "bold")).pack(pady=(30, 10))

        try:
            banner_img = ctk.CTkImage(
                light_image=Image.open(self.resource_path("img/banner.png")).resize((350, 250), Image.Resampling.LANCZOS),
                size=(350, 250)
            )
            ctk.CTkLabel(self.right_frame, image=banner_img, text="").pack(pady=10)
        except Exception as e:
            print(f"Không thể load ảnh: {e}")
            ctk.CTkLabel(self.right_frame, text="").pack(pady=10)

    def resource_path(self, relative_path):
        """Trả về đường dẫn tuyệt đối đến tài nguyên, hoạt động với cả script và .exe"""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def login(self, username, password):
        login_controller = LoginController.LoginController()
        if login_controller.check_login(username, password):
            messagebox.showinfo("Đăng nhập", "Đăng nhập thành công!")
            user_id = login_controller.check_id(username)
            self.open_main(user_id)
        else:
            messagebox.showerror("Lỗi đăng nhập", "Sai tài khoản hoặc mật khẩu! Hoặc tài khoản chưa được duyệt!")

    def register(self):
        self.open_reg_window()

    def validate_inputs(self, first_name, last_name, gender, phone_number, email, birth_year, username, password, confirm_password):
        if not all([first_name, last_name, gender, phone_number, email, birth_year, username, password, confirm_password]):
            return "Vui lòng nhập đầy đủ thông tin"
        if not first_name.isalpha() or not last_name.isalpha():
            return "Họ và tên chỉ được chứa chữ cái!"
        try:
            birth_year = int(birth_year)
            current_year = datetime.now().year
            if birth_year < 1900 or birth_year > current_year:
                return "Năm sinh không hợp lệ!"
        except ValueError:
            return "Năm sinh phải là số!"
        if gender not in ["MALE", "FEMALE"]:
            return "Giới tính không hợp lệ!"
        if not re.match(r"^\d{10,11}$", phone_number):
            return "Số điện thoại phải là số và có 10-11 chữ số!"
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return "Email không hợp lệ!"
        if not re.match(r"^[a-zA-Z0-9_]{3,50}$", username):
            return "Tên đăng nhập chỉ chứa chữ cái, số, dấu gạch dưới, độ dài 3-50 ký tự!"
        if len(password) < 6:
            return "Mật khẩu phải có ít nhất 6 ký tự!"
        if password != confirm_password:
            return "Mật khẩu xác nhận không khớp!"
        return None

    def open_reg_window(self):
        reg_window = ctk.CTkToplevel(self.root)
        reg_window.title("Đăng ký tài khoản")
        # Căn giữa cửa sổ đăng ký
        window_width = 600
        window_height = 600
        screen_width = reg_window.winfo_screenwidth()
        screen_height = reg_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        reg_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        reg_window.resizable(False, False)
        reg_window.transient(self.root)
        reg_window.grab_set()

        frame = ctk.CTkFrame(reg_window, corner_radius=15, fg_color="#f5f6f5")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Đăng ký tài khoản", font=("Helvetica", 24, "bold"), text_color="#2e7a84").pack(pady=(10, 20))

        form_frame = ctk.CTkFrame(frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20)

        ctk.CTkLabel(form_frame, text="Họ:", font=("Arial", 14), text_color="#333", width=100).grid(row=0, column=0, sticky="w", pady=5)
        first_name_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập họ", font=("Arial", 12), corner_radius=10)
        first_name_entry.grid(row=0, column=1, pady=5)

        ctk.CTkLabel(form_frame, text="Tên:", font=("Arial", 14), text_color="#333", width=100).grid(row=1, column=0, sticky="w", pady=5)
        last_name_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập tên", font=("Arial", 12), corner_radius=10)
        last_name_entry.grid(row=1, column=1, pady=5)

        ctk.CTkLabel(form_frame, text="Giới tính:", font=("Arial", 14), text_color="#333", width=100).grid(row=2, column=0, sticky="w", pady=5)
        gender_var = ctk.StringVar(value="MALE")
        gender_menu = ctk.CTkOptionMenu(form_frame, values=["MALE", "FEMALE"], variable=gender_var, width=300, font=("Arial", 12), corner_radius=10)
        gender_menu.grid(row=2, column=1, pady=5)

        ctk.CTkLabel(form_frame, text="Năm sinh:", font=("Arial", 14), text_color="#333", width=100).grid(row=3, column=0, sticky="w", pady=5)
        birth_year_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập năm sinh (VD: 1990)", font=("Arial", 12), corner_radius=10)
        birth_year_entry.grid(row=3, column=1, pady=5)

        ctk.CTkLabel(form_frame, text="Số điện thoại:", font=("Arial", 14), text_color="#333", width=100).grid(row=4, column=0, sticky="w", pady=5)
        phone_number_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập số điện thoại", font=("Arial", 12), corner_radius=10)
        phone_number_entry.grid(row=4, column=1, pady=5)

        ctk.CTkLabel(form_frame, text="Email:", font=("Arial", 14), text_color="#333", width=100).grid(row=5, column=0, sticky="w", pady=5)
        email_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập email", font=("Arial", 12), corner_radius=10)
        email_entry.grid(row=5, column=1, pady=5)

        ctk.CTkLabel(form_frame, text="Tên đăng nhập:", font=("Arial", 14), text_color="#333", width=100).grid(row=6, column=0, sticky="w", pady=5)
        username_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập tên đăng nhập", font=("Arial", 12), corner_radius=10)
        username_entry.grid(row=6, column=1, pady=5)

        ctk.CTkLabel(form_frame, text="Mật khẩu:", font=("Arial", 14), text_color="#333", width=100).grid(row=7, column=0, sticky="w", pady=5)
        password_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập mật khẩu", show="*", font=("Arial", 12), corner_radius=10)
        password_entry.grid(row=7, column=1, pady=5)

        ctk.CTkLabel(form_frame, text="Xác nhận mật khẩu:", font=("Arial", 14), text_color="#333", width=100).grid(row=8, column=0, sticky="w", pady=5)
        confirm_password_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập lại mật khẩu", show="*", font=("Arial", 12), corner_radius=10)
        confirm_password_entry.grid(row=8, column=1, pady=5)

        ctk.CTkButton(frame, text="Đăng ký", fg_color="#2e7a84", hover_color="#1b5e6b", font=("Arial", 14, "bold"), corner_radius=10,
                      command=lambda: self.info_save(
                          first_name_entry.get(), last_name_entry.get(), gender_var.get(),
                          phone_number_entry.get(), email_entry.get(), birth_year_entry.get(),
                          username_entry.get(), password_entry.get(), confirm_password_entry.get(), reg_window
                      )).pack(pady=20)

    def info_save(self, first_name, last_name, gender, phone_number, email, birth_year, username, password, confirm_password, reg_window):
        validation_error = self.validate_inputs(first_name, last_name, gender, phone_number, email, birth_year, username, password, confirm_password)
        if validation_error:
            messagebox.showerror("Lỗi", validation_error)
            return
        login_controller = LoginController.LoginController()
        success = login_controller.register_user(first_name, last_name, gender, phone_number, email, int(birth_year), "Employee", username, password)
        if success:
            messagebox.showinfo("Thành công", "Đăng ký thành công! Vui lòng chờ quản trị viên duyệt tài khoản.")
            reg_window.destroy()
        else:
            messagebox.showerror("Lỗi", "Đăng ký thất bại! Tên đăng nhập đã tồn tại hoặc có lỗi hệ thống.")

    def open_forgot_password_window(self):
        forgot_window = ctk.CTkToplevel(self.root)
        forgot_window.title("Khôi phục mật khẩu")
        # Căn giữa cửa sổ quên mật khẩu
        window_width = 500
        window_height = 500
        screen_width = forgot_window.winfo_screenwidth()
        screen_height = forgot_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        forgot_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        forgot_window.resizable(False, False)
        forgot_window.transient(self.root)
        forgot_window.grab_set()

        frame = ctk.CTkFrame(forgot_window, corner_radius=15, fg_color="#f5f6f5")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Khôi phục mật khẩu", font=("Helvetica", 20, "bold"), text_color="#2e7a84").pack(pady=(10, 20))

        form_frame = ctk.CTkFrame(frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20)

        # Trường nhập username
        ctk.CTkLabel(form_frame, text="Tên đăng nhập:", font=("Arial", 14), text_color="#333", width=150).grid(row=0, column=0, sticky="w", pady=5)
        username_entry = ctk.CTkEntry(form_frame, width=250, placeholder_text="Nhập tên đăng nhập", font=("Arial", 12), corner_radius=10)
        username_entry.grid(row=0, column=1, pady=5)

        # Trường nhập email
        ctk.CTkLabel(form_frame, text="Email:", font=("Arial", 14), text_color="#333", width=150).grid(row=1, column=0, sticky="w", pady=5)
        email_entry = ctk.CTkEntry(form_frame, width=250, placeholder_text="Nhập email", font=("Arial", 12), corner_radius=10)
        email_entry.grid(row=1, column=1, pady=5)

        # Trường nhập số điện thoại
        ctk.CTkLabel(form_frame, text="Số điện thoại:", font=("Arial", 14), text_color="#333", width=150).grid(row=2, column=0, sticky="w", pady=5)
        phone_number_entry = ctk.CTkEntry(form_frame, width=250, placeholder_text="Nhập số điện thoại", font=("Arial", 12), corner_radius=10)
        phone_number_entry.grid(row=2, column=1, pady=5)

        # Trường nhập mật khẩu mới
        ctk.CTkLabel(form_frame, text="Mật khẩu mới:", font=("Arial", 14), text_color="#333", width=150).grid(row=3, column=0, sticky="w", pady=5)
        new_password_entry = ctk.CTkEntry(form_frame, width=250, placeholder_text="Nhập mật khẩu mới", show="*", font=("Arial", 12), corner_radius=10)
        new_password_entry.grid(row=3, column=1, pady=5)

        # Trường nhập xác nhận mật khẩu
        ctk.CTkLabel(form_frame, text="Xác nhận mật khẩu:", font=("Arial", 14), text_color="#333", width=150).grid(row=4, column=0, sticky="w", pady=5)
        confirm_password_entry = ctk.CTkEntry(form_frame, width=250, placeholder_text="Xác nhận mật khẩu", show="*", font=("Arial", 12), corner_radius=10)
        confirm_password_entry.grid(row=4, column=1, pady=5)

        ctk.CTkButton(frame, text="Xác nhận", fg_color="#2e7a84", hover_color="#1b5e6b", font=("Arial", 14, "bold"), corner_radius=10,
                      command=lambda: self.request_password_reset(
                          username_entry.get(), email_entry.get(), phone_number_entry.get(),
                          new_password_entry.get(), confirm_password_entry.get(), forgot_window
                      )).pack(pady=20)

    def request_password_reset(self, username, email, phone_number, new_password, confirm_password, forgot_window):
        # Kiểm tra các trường nhập liệu
        if not all([username, email, phone_number, new_password, confirm_password]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            messagebox.showerror("Lỗi", "Email không hợp lệ!")
            return
        if not re.match(r"^\d{9,11}$", phone_number):
            messagebox.showerror("Lỗi", "Số điện thoại phải là số và có 10-11 chữ số!")
            return
        if not re.match(r"^[a-zA-Z0-9_]{3,50}$", username):
            messagebox.showerror("Lỗi", "Tên đăng nhập chỉ chứa chữ cái, số, dấu gạch dưới, độ dài 3-50 ký tự!")
            return
        if len(new_password) < 6:
            messagebox.showerror("Lỗi", "Mật khẩu mới phải có ít nhất 6 ký tự!")
            return
        if new_password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        # Kiểm tra thông tin người dùng
        login_controller = LoginController.LoginController()
        if login_controller.verify_user_for_reset(username, email, phone_number):
            # Cập nhật mật khẩu
            success = login_controller.update_password(username, new_password)
            if success:
                messagebox.showinfo("Thành công", "Mật khẩu đã được cập nhật thành công!")
                forgot_window.destroy()
            else:
                messagebox.showerror("Lỗi", "Cập nhật mật khẩu thất bại! Vui lòng thử lại.")
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập, email hoặc số điện thoại không đúng!")

    def open_main(self, user_id):
        for after_id in self.after_ids:
            self.root.after_cancel(after_id)
        self.after_ids.clear()
        self.root.destroy()
        if self.on_login_success:
            self.on_login_success(user_id)

    def __del__(self):
        for after_id in self.after_ids:
            self.root.after_cancel(after_id)
        self.after_ids.clear()