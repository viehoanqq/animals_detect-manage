import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
import controller.login_controller as LoginController
import main as mainMenu
import re
from datetime import datetime

# ===== SETUP CƠ BẢN =====
ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue") 

root = ctk.CTk()
root.title("Đăng nhập hệ thống")
root.geometry("900x550")
root.configure(fg_color="#2e7a84")

def setup_ui():
    # ===== FRAME CHÍNH =====
    main_frame = ctk.CTkFrame(root, width=800, height=450, fg_color="white", corner_radius=20)
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    # ===== TRÁI: FORM =====
    left_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=20)
    left_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

    ctk.CTkLabel(left_frame, text="Đăng nhập", text_color="#2e7a84", font=("Arial", 24, "bold")).pack(pady=(10, 20))

    # Username
    entry_user = ctk.CTkEntry(left_frame, placeholder_text="Tên đăng nhập", font=("Arial", 12), corner_radius=20)
    entry_user.pack(pady=10, fill="x")

    # Password
    entry_pass = ctk.CTkEntry(left_frame, placeholder_text="Mật khẩu", font=("Arial", 12), show="*", corner_radius=20)
    entry_pass.pack(pady=10, fill="x")

    # Nút đăng nhập
    login_btn = ctk.CTkButton(left_frame, text="Đăng nhập", fg_color="#2e7a84", hover_color="#255a5f",
                              font=("Arial", 12, "bold"), corner_radius=20, command=lambda: login(entry_user.get(), entry_pass.get()))
    login_btn.pack(pady=(20, 10), fill="x")

    # Nút đăng ký
    reg_btn = ctk.CTkButton(left_frame, text="Đăng ký", fg_color="#2e7a84", hover_color="#c13b31",
                            font=("Arial", 12, "bold"), corner_radius=20, command=lambda: register())
    reg_btn.pack(pady=(0, 10), fill="x")
    
    # Label quên mật khẩu với sự kiện click
    change_pass_label = ctk.CTkLabel(left_frame, text="Bạn quên mật khẩu? Lấy lại mật khẩu", 
                                   text_color="green", font=("Arial", 12), cursor="hand2")
    change_pass_label.pack(pady=(0, 10), fill="x")
    change_pass_label.bind("<Button-1>", lambda event: open_forgot_password_window())

    # ===== PHẢI: TIÊU ĐỀ + ẢNH =====
    right_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=20)
    right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

    ctk.CTkLabel(right_frame, text="HỆ THỐNG QUẢN LÝ VẬT NUÔI", text_color="#2e7a84",
                 font=("Arial", 16, "bold")).pack(pady=(30, 10))

    # Load ảnh banner
    try:
        banner_img = Image.open("img/banner.png")
        banner_img = banner_img.resize((350, 250), Image.Resampling.LANCZOS)
        banner_photo = ImageTk.PhotoImage(banner_img)
        banner_label = ctk.CTkLabel(right_frame, image=banner_photo, text="")
        banner_label.image = banner_photo
        banner_label.pack(pady=10)
    except Exception as e:
        print("Không thể load ảnh:", e)

def login(username, password):
    """Handles login validation."""
    login = LoginController.LoginController()
    if login.check_login(username, password):
        messagebox.showinfo("Đăng nhập", "Đăng nhập thành công!")
        user_id= login.check_id(username)
        open_main(user_id)
    else:
        messagebox.showerror("Lỗi đăng nhập", "Sai tài khoản hoặc mật khẩu! Hoặc tài khoản chưa được duyệt!")

def register():
    open_reg_window()

def validate_inputs(first_name, last_name, gender, phone_number, email, birth_year, username, password, confirm_password):
    """Kiểm tra dữ liệu đầu vào"""
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
    
    # Validate phone number (e.g., must be digits and 10-11 characters long)
    if not re.match(r"^\d{10,11}$", phone_number):
        return "Số điện thoại phải là số và có 10-11 chữ số!"
    
    # Validate email format
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return "Email không hợp lệ!"
    
    if not re.match(r"^[a-zA-Z0-9_]{3,50}$", username):
        return "Tên đăng nhập chỉ chứa chữ cái, số, dấu gạch dưới, độ dài 3-50 ký tự!"
    
    if len(password) < 6:
        return "Mật khẩu phải có ít nhất 6 ký tự!"
    
    if password != confirm_password:
        return "Mật khẩu xác nhận không khớp!"
    
    return None

def open_reg_window():
    """Mở cửa sổ đăng ký với giao diện đẹp và tiện lợi"""
    # Tạo cửa sổ mới
    reg_window = ctk.CTkToplevel(root)
    reg_window.title("Đăng ký tài khoản")
    reg_window.geometry("600x600")
    reg_window.resizable(False, False)
    reg_window.transient(root)
    reg_window.grab_set()

    # Frame chính với gradient background
    frame = ctk.CTkFrame(reg_window, corner_radius=15, fg_color="#f5f6f5")
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Tiêu đề
    ctk.CTkLabel(frame, text="Đăng ký tài khoản", font=("Helvetica", 24, "bold"), text_color="#2e7a84").pack(pady=(10, 20))

    # Form frame để căn chỉnh label và entry trên cùng hàng
    form_frame = ctk.CTkFrame(frame, fg_color="transparent")
    form_frame.pack(fill="x", padx=20)

    # Họ
    ctk.CTkLabel(form_frame, text="Họ:", font=("Arial", 14), text_color="#333", width=100).grid(row=0, column=0, sticky="w", pady=5)
    first_name_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập họ", font=("Arial", 12), corner_radius=10)
    first_name_entry.grid(row=0, column=1, pady=5)

    # Tên
    ctk.CTkLabel(form_frame, text="Tên:", font=("Arial", 14), text_color="#333", width=100).grid(row=1, column=0, sticky="w", pady=5)
    last_name_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập tên", font=("Arial", 12), corner_radius=10)
    last_name_entry.grid(row=1, column=1, pady=5)

    # Giới tính
    ctk.CTkLabel(form_frame, text="Giới tính:", font=("Arial", 14), text_color="#333", width=100).grid(row=2, column=0, sticky="w", pady=5)
    gender_var = ctk.StringVar(value="MALE")
    gender_menu = ctk.CTkOptionMenu(form_frame, values=["MALE", "FEMALE"], variable=gender_var, width=300, font=("Arial", 12), corner_radius=10)
    gender_menu.grid(row=2, column=1, pady=5)

    # Năm sinh
    ctk.CTkLabel(form_frame, text="Năm sinh:", font=("Arial", 14), text_color="#333", width=100).grid(row=3, column=0, sticky="w", pady=5)
    birth_year_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập năm sinh (VD: 1990)", font=("Arial", 12), corner_radius=10)
    birth_year_entry.grid(row=3, column=1, pady=5)

    # Số điện thoại
    ctk.CTkLabel(form_frame, text="Số điện thoại:", font=("Arial", 14), text_color="#333", width=100).grid(row=4, column=0, sticky="w", pady=5)
    phone_number_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập số điện thoại", font=("Arial", 12), corner_radius=10)
    phone_number_entry.grid(row=4, column=1, pady=5)

    # Email
    ctk.CTkLabel(form_frame, text="Email:", font=("Arial", 14), text_color="#333", width=100).grid(row=5, column=0, sticky="w", pady=5)
    email_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập email", font=("Arial", 12), corner_radius=10)
    email_entry.grid(row=5, column=1, pady=5)

    # Tên đăng nhập
    ctk.CTkLabel(form_frame, text="Tên đăng nhập:", font=("Arial", 14), text_color="#333", width=100).grid(row=6, column=0, sticky="w", pady=5)
    username_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập tên đăng nhập", font=("Arial", 12), corner_radius=10)
    username_entry.grid(row=6, column=1, pady=5)

    # Mật khẩu
    ctk.CTkLabel(form_frame, text="Mật khẩu:", font=("Arial", 14), text_color="#333", width=100).grid(row=7, column=0, sticky="w", pady=5)
    password_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập mật khẩu", show="*", font=("Arial", 12), corner_radius=10)
    password_entry.grid(row=7, column=1, pady=5)

    # Xác nhận mật khẩu
    ctk.CTkLabel(form_frame, text="Xác nhận mật khẩu:", font=("Arial", 14), text_color="#333", width=100).grid(row=8, column=0, sticky="w", pady=5)
    confirm_password_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="Nhập lại mật khẩu", show="*", font=("Arial", 12), corner_radius=10)
    confirm_password_entry.grid(row=8, column=1, pady=5)

    # Nút xác nhận
    ctk.CTkButton(frame, text="Đăng ký", fg_color="#2e7a84", hover_color="#1b5e6b", font=("Arial", 14, "bold"), corner_radius=10,
                  command=lambda: info_save(
                      first_name_entry.get(), last_name_entry.get(), gender_var.get(),
                      phone_number_entry.get(), email_entry.get(), birth_year_entry.get(),
                      username_entry.get(), password_entry.get(), confirm_password_entry.get(), reg_window
                  )).pack(pady=20)

def info_save(first_name, last_name, gender, phone_number, email, birth_year, username, password, confirm_password, reg_window):
    """Lưu thông tin đăng ký và hiển thị thông báo chờ duyệt"""
    # Kiểm tra dữ liệu đầu vào
    validation_error = validate_inputs(first_name, last_name, gender, phone_number, email, birth_year, username, password, confirm_password)
    if validation_error:
        messagebox.showerror("Lỗi", validation_error)
        return

    # Lưu thông tin vào cơ sở dữ liệu với role mặc định là "Employee"
    login = LoginController.LoginController()
    success = login.register_user(first_name, last_name, gender, phone_number, email, int(birth_year), "Employee", username, password)
    
    if success:
        messagebox.showinfo("Thành công", "Đăng ký thành công! Vui lòng chờ quản trị viên duyệt tài khoản.")
        reg_window.destroy()
    else:
        messagebox.showerror("Lỗi", "Đăng ký thất bại! Tên đăng nhập đã tồn tại hoặc có lỗi hệ thống.")

def open_forgot_password_window():
    """Mở cửa sổ quên mật khẩu"""
    forgot_window = ctk.CTkToplevel(root)
    forgot_window.title("Quên mật khẩu")
    forgot_window.geometry("400x300")
    forgot_window.resizable(False, False)
    forgot_window.transient(root)
    forgot_window.grab_set()

    # Frame chính
    frame = ctk.CTkFrame(forgot_window, corner_radius=15, fg_color="#f5f6f5")
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Tiêu đề
    ctk.CTkLabel(frame, text="Khôi phục mật khẩu", font=("Helvetica", 20, "bold"), text_color="#2e7a84").pack(pady=(10, 20))

    # Form frame
    form_frame = ctk.CTkFrame(frame, fg_color="transparent")
    form_frame.pack(fill="x", padx=20)

    # Tên đăng nhập
    ctk.CTkLabel(form_frame, text="Tên đăng nhập:", font=("Arial", 14), text_color="#333", width=100).grid(row=0, column=0, sticky="w", pady=5)
    username_entry = ctk.CTkEntry(form_frame, width=200, placeholder_text="Nhập tên đăng nhập", font=("Arial", 12), corner_radius=10)
    username_entry.grid(row=0, column=1, pady=5)

    # Email
    ctk.CTkLabel(form_frame, text="Email:", font=("Arial", 14), text_color="#333", width=100).grid(row=1, column=0, sticky="w", pady=5)
    email_entry = ctk.CTkEntry(form_frame, width=200, placeholder_text="Nhập email", font=("Arial", 12), corner_radius=10)
    email_entry.grid(row=1, column=1, pady=5)

    # Nút gửi yêu cầu
    ctk.CTkButton(frame, text="Gửi yêu cầu", fg_color="#2e7a84", hover_color="#1b5e6b", font=("Arial", 14, "bold"), corner_radius=10,
                  command=lambda: request_password_reset(username_entry.get(), email_entry.get(), forgot_window)).pack(pady=20)
def request_password_reset(username, email, forgot_window):
    """Xử lý yêu cầu khôi phục mật khẩu"""
    if not username or not email:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ tên đăng nhập và email!")
        return

    # Validate email format
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        messagebox.showerror("Lỗi", "Email không hợp lệ!")
        return

    # Kiểm tra thông tin với controller
    login = LoginController.LoginController()
    if login.verify_user_for_reset(username, email):
        messagebox.showinfo("Thành công", "Yêu cầu khôi phục mật khẩu đã được gửi! Vui lòng kiểm tra email để đặt lại mật khẩu.")
        forgot_window.destroy()
    else:
        messagebox.showerror("Lỗi", "Tên đăng nhập hoặc email không đúng!")

def open_main(user_id):
    """Hiển thị giao diện chính sau khi đăng nhập thành công."""
    root.destroy()
    main_root = ctk.CTk()
    test = mainMenu.Main(main_root, user_id)

# Setup the UI
setup_ui()
root.mainloop()