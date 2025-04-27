import customtkinter as ctk
from PIL import Image, ImageTk
from controller.user_controller import get_user_info
from animals_count import AnimalCounter
from animals import PetManagement
from work_shifts import ShiftManagement
from environment import EnvironmentManagement
from account import AccountManagement
from vaccination import VaccinationManagement
from employee_management import EmployeeManagement
import tkinter.messagebox as messagebox
import sys
import uuid
class Main:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.user_info = get_user_info(user_id)
        self.active_button = None  # Track active sidebar button

        # Giao diện customtkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root.title("Quản Lý Vật Nuôi")
        self.root.state('zoomed')
        self.root.protocol("WM_DELETE_WINDOW", self.logout)

        self.setup_ui()

    def setup_ui(self):
        # ========== HEADER ==========
        self.header = ctk.CTkFrame(self.root, height=140, fg_color="#e6f2f5")
        self.header.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(
            self.header, text="HỆ THỐNG QUẢN LÝ VẬT NUÔI", font=("Arial", 22, "bold"), text_color="#2e7a84"
        )
        self.title_label.pack(side="left", padx=20)

        self.user_info_frame = ctk.CTkFrame(self.header, fg_color="#e6f2f5")
        self.user_info_frame.pack(side="right", padx=20)

        welcome_text = f"Xin chào, {self.user_info['first_name']}"
        self.user_label = ctk.CTkLabel(self.user_info_frame, text=welcome_text, font=("Arial", 16), text_color="#2e7a84")
        self.user_label.pack(side="left", padx=(0, 10))

        self.logout_button = ctk.CTkButton(self.user_info_frame, text="Đăng xuất", fg_color="#db4437", hover_color="#c13b31",
                                           font=("Arial", 14, "bold"), command=self.logout, width=100)
        self.logout_button.pack(side="left")

        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(self.root, width=220, fg_color="#2e7a84")
        self.sidebar.pack(side="left", fill="y")

        button_config = {
            "font": ("Arial", 16),
            "fg_color": "#ffffff",
            "hover_color": "#cde6ec",
            "text_color": "#2e7a84",
            "width": 180,
            "height": 40
        }

        ctk.CTkLabel(self.sidebar, text="Chức năng", font=("Arial", 25, "bold"), text_color="white").pack(pady=(20, 10))

        def create_button(text, command):
            btn = ctk.CTkButton(self.sidebar, text=text, command=lambda: self.activate_button(btn, command), **button_config)
            btn.pack(pady=10)
            return btn

        self.buttons = [
            create_button("Nhận diện", self.start_detection),
            create_button("Quản lý ca", self.manage_shift),
            create_button("Quản lý vật nuôi", self.manage_pets),
            create_button("Môi trường", self.manage_environment),
            create_button("Tiêm phòng", self.tiemphong),
            create_button("Tài khoản", self.manage_accounts),
            create_button("Thống kê", self.show_statistics)
        ]

        # Add Employee Management button for admin role
        if self.user_info.get('role') == 'admin':
            self.buttons.append(create_button("Quản lý nhân viên", self.manage_employees))

        # ========== CONTENT ==========
        self.content = ctk.CTkFrame(self.root, fg_color="white")
        self.content.pack(side="left", expand=True, fill="both", padx=10, pady=10)

    def activate_button(self, button, command):
        # Reset previous active button
        if self.active_button:
            self.active_button.configure(fg_color="#ffffff")
        
        # Highlight current button
        button.configure(fg_color="#cde6ec")
        self.active_button = button
        
        # Execute command
        command()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def start_detection(self):
        self.clear_content()
        # self.animal_counter = AnimalCounter(self.content)
        # self.animal_counter.pack(expand=True, fill="both")
        # self.animal_counter.start_detection()

    def manage_shift(self):
        self.clear_content()
        shift_frame = ctk.CTkFrame(self.content)
        shift_frame.pack(expand=True, fill="both")
        self.shif = ShiftManagement(shift_frame)

    def manage_pets(self):
        self.clear_content()
        pet_frame = ctk.CTkFrame(self.content)
        pet_frame.pack(expand=True, fill="both")
        self.pet_management = PetManagement(pet_frame)

    def manage_environment(self):
        self.clear_content()
        env_frame = ctk.CTkFrame(self.content)
        env_frame.pack(expand=True, fill="both")
        self.env_management = EnvironmentManagement(env_frame)

    def tiemphong(self):
        self.clear_content()
        vacc_frame = ctk.CTkFrame(self.content)
        vacc_frame.pack(expand=True, fill="both")
        self.vacc_management = VaccinationManagement(vacc_frame)

    def manage_accounts(self):
        self.clear_content()
        account_frame = ctk.CTkFrame(self.content)
        account_frame.pack(expand=True, fill="both")
        self.manage_acc = AccountManagement(account_frame, self.user_id)

    def manage_employees(self):
        self.clear_content()
        emp_frame = ctk.CTkFrame(self.content)
        emp_frame.pack(expand=True, fill="both")
        self.emp_management = EmployeeManagement(emp_frame)

    def show_statistics(self):
        self.clear_content()
        stats_frame = ctk.CTkFrame(self.content)
        stats_frame.pack(expand=True, fill="both")
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 Thống kê hệ thống",
            font=("Arial", 22, "bold"),
            text_color="#2e7a84"
        ).pack(pady=20)
        
        stats_display = ctk.CTkFrame(stats_frame)
        stats_display.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(stats_display, text="Tổng số vật nuôi: Đang cập nhật", 
                     font=("Arial", 16)).pack(anchor="w", pady=5)
        ctk.CTkLabel(stats_display, text="Số ca làm việc: Đang cập nhật", 
                     font=("Arial", 16)).pack(anchor="w", pady=5)
        ctk.CTkLabel(stats_display, text="Tình trạng môi trường: Đang cập nhật", 
                     font=("Arial", 16)).pack(anchor="w", pady=5)

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất không?"):
            self.root.destroy()
            sys.exit()