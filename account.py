import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from controller.account_controller import AccountController
from datetime import datetime

class AccountManagement:
    def __init__(self, parent, user_id):
        self.parent = parent
        self.user_id = user_id
        self.controller = AccountController(user_id)
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện người dùng cho quản lý thông tin tài khoản"""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Nền chính với màu nhạt
        self.parent.configure(fg_color="#f5f7fa")

        # Frame chính với bo góc, đặt giữa
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15, fg_color="white", width=600)
        main_frame.pack(pady=40, padx=40, expand=True)

        # Tiêu đề
        ctk.CTkLabel(main_frame, text="THÔNG TIN TÀI KHOẢN",
                     font=("Helvetica", 24, "bold"), text_color="#2e7a84").grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

        # Frame cho logo
        logo_frame = ctk.CTkFrame(main_frame, corner_radius=75, fg_color="#ffffff", width=100, height=100)
        logo_frame.grid(row=1, column=0, columnspan=2, pady=10)
        logo_frame.grid_propagate(False)  # Ngăn frame thay đổi kích thước

        # Logo tròn
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("img/banner.png"),
                                   dark_image=Image.open("img/banner.png"),
                                   size=(90, 90))
            ctk.CTkLabel(logo_frame, image=logo_img, text="").place(relx=0.5, rely=0.5, anchor="center")
        except FileNotFoundError:
            ctk.CTkLabel(logo_frame, text="Không tìm thấy logo",
                         font=("Arial", 14), text_color="red").place(relx=0.5, rely=0.5, anchor="center")

        # Lấy thông tin người dùng
        user_info = self.controller.get_user_info()
        if not user_info:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin tài khoản!")
            return

        # Chuyển đổi giới tính và vai trò
        gender_display = {"MALE": "Nam", "FEMALE": "Nữ"}.get(user_info.get("gender", ""), user_info.get("gender", ""))
        role_display = {"ADMIN": "Quản trị viên", "USER": "Người dùng"}.get(user_info.get("role", ""), user_info.get("role", ""))

        # Frame chứa các trường nhập
        fields_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#ffffff")
        fields_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        # Các trường nhập liệu
        self.entries = {}
        fields = [
            ("ID", "id", True),
            ("Tên", "first_name", False),
            ("Họ", "last_name", False),
            ("Giới tính", "gender", False, gender_display),
            ("Năm sinh", "birth_year", False),
            ("Số điện thoại", "phone_number", False),
            ("Email", "email", False),
            ("Vai trò", "role", False, role_display),
            ("Ngày tham gia", "joined_date", True),
        ]

        for i, field in enumerate(fields):
            label_text, key, readonly = field[:3]
            display_value = field[3] if len(field) > 3 else user_info.get(key, "")
            
            ctk.CTkLabel(fields_frame, text=f"{label_text}:",
                         font=("Arial", 14), width=120, anchor="e").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            entry = ctk.CTkEntry(fields_frame, width=300, font=("Arial", 14))
            entry.insert(0, str(display_value))
            if readonly:
                entry.configure(state="readonly", fg_color="#f0f0f0")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.entries[key] = entry

        # Frame cho các nút
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        # Nút cập nhật
        ctk.CTkButton(button_frame, text="Cập nhật",
                      fg_color="#2e7a84", hover_color="#1b5e6b",
                      font=("Arial", 14, "bold"), corner_radius=10,
                      command=self.update_account, width=150).pack(side="left", padx=10)

        # Nút đổi mật khẩu
        ctk.CTkButton(button_frame, text="Đổi mật khẩu",
                      fg_color="#db4437", hover_color="#c13b31",
                      font=("Arial", 14, "bold"), corner_radius=10,
                      command=self.open_change_password_window, width=150).pack(side="left", padx=10)

    def update_account(self):
        """Cập nhật thông tin tài khoản"""
        try:
            first_name = self.entries['first_name'].get()
            last_name = self.entries['last_name'].get()
            gender = self.entries['gender'].get()
            if gender=="Nam":
                gender="MALE"
            else:
                gender = "FEMALE"                
            birth_year = self.entries['birth_year'].get()
            phone_number = self.entries['phone_number'].get()
            email = self.entries['email'].get()

            if not all([first_name, last_name, gender,birth_year, phone_number, email]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return

            try:
                birth_year = int(birth_year)
                if birth_year < 1900 or birth_year > datetime.now().year:
                    messagebox.showerror("Lỗi", "Năm sinh không hợp lệ!")
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Năm sinh phải là số!")
                return

            self.controller.update_account(first_name, last_name, gender, birth_year, phone_number, email)
            messagebox.showinfo("Thành công", "Cập nhật thông tin tài khoản thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật tài khoản: {str(e)}")

    def open_change_password_window(self):
        """Mở cửa sổ đổi mật khẩu"""
        self.password_window = ctk.CTkToplevel(self.parent)
        self.password_window.title("Đổi mật khẩu")
        self.password_window.geometry("400x300")
        self.password_window.resizable(False, False)
        self.password_window.transient(self.parent)
        self.password_window.grab_set()

        frame = ctk.CTkFrame(self.password_window, corner_radius=10, fg_color="#ffffff")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="ĐỔI MẬT KHẨU",
                     font=("Helvetica", 20, "bold"), text_color="#2e7a84").pack(pady=10)

        ctk.CTkLabel(frame, text="Mật khẩu mới:", font=("Arial", 14)).pack(pady=5)
        self.new_password_entry = ctk.CTkEntry(frame, width=250, show="*", placeholder_text="Nhập mật khẩu mới")
        self.new_password_entry.pack(pady=5)

        ctk.CTkLabel(frame, text="Xác nhận mật khẩu:", font=("Arial", 14)).pack(pady=5)
        self.confirm_password_entry = ctk.CTkEntry(frame, width=250, show="*", placeholder_text="Xác nhận mật khẩu")
        self.confirm_password_entry.pack(pady=5)

        ctk.CTkButton(frame, text="Xác nhận",
                      fg_color="#2e7a84", hover_color="#1b5e6b",
                      font=("Arial", 14, "bold"), corner_radius=10,
                      command=self.change_password).pack(pady=20)

    def change_password(self):
        """Xử lý đổi mật khẩu"""
        try:
            new_password = self.new_password_entry.get()
            confirm_password = self.confirm_password_entry.get()

            if not new_password or not confirm_password:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return

            if new_password != confirm_password:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
                return

            if len(new_password) < 6:
                messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
                return

            self.controller.change_password(new_password)
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!")
            self.password_window.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi đổi mật khẩu: {str(e)}")