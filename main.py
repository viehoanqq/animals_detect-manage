import os
import customtkinter as ctk
from PIL import Image
from controller.user_controller import get_user_info
from animals_count import AnimalCounter
from animals_count_2 import AnimalCounter2
from animals import PetManagement
from work_shifts import ShiftManagement
from environment import EnvironmentManagement
from account import AccountManagement
from vaccination import VaccinationManagement
from employee_management import EmployeeManagement
from barns_management import BarnManagement
from statistics_p import Statistics
import tkinter.messagebox as messagebox
import sys
import uuid
from login import Login

class Main:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.user_info = get_user_info(user_id)
        self.active_button = None
        self.after_ids = []

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root.title("Quản Lý Vật Nuôi")
        # Loại bỏ geometry thủ công, thay bằng tối đa hóa
        self.root.state('zoomed')  # Tối đa hóa cửa sổ trên Windows
        self.root.attributes('-fullscreen', False)  # Đảm bảo không ở chế độ toàn màn hình thực sự
        self.root.focus_force()
        self.root.protocol("WM_DELETE_WINDOW", self.logout)

        # Thêm phím tắt Esc để thoát chế độ tối đa hóa (tùy chọn)
        self.root.bind('<Escape>', lambda event: self.root.state('normal'))

        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header = ctk.CTkFrame(self.root, height=100, fg_color="#e6f2f5")
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open(self.resource_path("img/logo.png")),
                size=(75, 75)
            )
            self.logo_label = ctk.CTkLabel(self.header, image=logo_image, text="")
            self.logo_label.pack(side="left", padx=0, pady=10)
        except FileNotFoundError:
            print("Warning: logo.png not found, skipping logo display")
            self.logo_label = ctk.CTkLabel(self.header, text="")
            self.logo_label.pack(side="left", padx=10, pady=10)

        self.title_label = ctk.CTkLabel(
            self.header,
            text="HỆ THỐNG QUẢN LÝ VẬT NUÔI",
            font=("Arial", 24, "bold"),
            text_color="#2e7a84"
        )
        self.title_label.pack(side="left", padx=20, pady=10)

        self.user_info_frame = ctk.CTkFrame(self.header, fg_color="#e6f2f5")
        self.user_info_frame.pack(side="right", padx=20, pady=10)

        self.image_avatar = ctk.CTkImage(light_image=Image.open(self.resource_path("img/avatar-icon.png")), size=(25, 25))
        self.image_avatar_label = ctk.CTkLabel(self.user_info_frame, image=self.image_avatar, text="")
        self.image_avatar_label.pack(side="left", padx=(5, 0))

        welcome_text = f"Xin chào, {self.user_info['last_name']}"
        self.user_label = ctk.CTkLabel(
            self.user_info_frame,
            text=welcome_text,
            font=("Arial", 16, "bold"),
            text_color="#2e7a84"
        )
        self.user_label.pack(side="left", padx=(0, 10))

        self.logout_button = ctk.CTkButton(
            self.user_info_frame,
            text="Đăng xuất",
            fg_color="#db4437",
            hover_color="#c13b31",
            font=("Arial", 14, "bold"),
            command=self.logout,
            width=100
        )
        self.logout_button.pack(side="left")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=220, fg_color="#2e7a84")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        button_config = {
            "font": ("Arial", 16),
            "fg_color": "#ffffff",
            "hover_color": "#cde6ec",
            "text_color": "#2e7a84",
            "width": 180,
            "height": 40
        }

        ctk.CTkLabel(
            self.sidebar,
            text="Chức năng",
            font=("Arial", 25, "bold"),
            text_color="white"
        ).pack(pady=(20, 10))

        def create_button(text, command):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda: self.activate_button(btn, command),
                **button_config
            )
            btn.pack(pady=10, padx=10)
            return btn

        standard_buttons = [
            ("Nhận diện", self.start_detection),
            ("Nhận diện 2", self.start_detection_2),
            ("Quản lý ca", self.manage_shift),
            ("Quản lý vật nuôi", self.manage_pets),
            ("Môi trường", self.manage_environment),
            ("Tiêm phòng", self.tiemphong),
            ("Quản lý chuồng nuôi", self.manage_barns)
        ]
        admin_buttons = [
            ("Quản lý nhân viên", self.manage_employees)
        ] if self.user_info.get('role') == 'admin' else []
        bottom_buttons = [
            ("Thống kê", self.show_statistics),
            ("Tài khoản", self.manage_accounts)
        ]

        self.buttons = []

        for text, command in standard_buttons + admin_buttons:
            self.buttons.append(create_button(text, command))

        ctk.CTkLabel(self.sidebar, text="", height=20).pack(pady=10)

        for text, command in bottom_buttons:
            self.buttons.append(create_button(text, command))

        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)

        # Content area
        self.content = ctk.CTkFrame(self.root, fg_color="white")
        self.content.pack(side="left", expand=True, fill="both", padx=10, pady=10)

    def activate_button(self, button, command):
        if self.active_button:
            self.active_button.configure(fg_color="#ffffff")
        button.configure(fg_color="#cde6ec")
        self.active_button = button
        command()

    def clear_content(self):
        for after_id in self.after_ids:
            self.root.after_cancel(after_id)
        self.after_ids.clear()
        for widget in self.content.winfo_children():
            widget.destroy()

    def start_detection(self):
        self.clear_content()
        self.animal_counter = AnimalCounter(self.content, self.user_id)

    def start_detection_2(self):
        self.clear_content()
        self.animal_counter_2 = AnimalCounter2(self.content, self.user_id)

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

    def manage_barns(self):
        self.clear_content()
        barn_frame = ctk.CTkFrame(self.content)
        barn_frame.pack(expand=True, fill="both")
        self.barn_management = BarnManagement(barn_frame)

    def show_statistics(self):
        self.clear_content()
        stats_frame = ctk.CTkFrame(self.content)
        stats_frame.pack(expand=True, fill="both")
        self.stats_management = Statistics(stats_frame)

    def resource_path(self, relative_path):
        """Trả về đường dẫn tuyệt đối đến tài nguyên, hoạt động với cả script và .exe"""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất không?"):
            for after_id in self.after_ids:
                self.root.after_cancel(after_id)
            self.after_ids.clear()
            self.root.destroy()
            try:
                new_root = ctk.CTk()
                login_app = Login(new_root, self.run_main)
                new_root.mainloop()
            except ImportError as e:
                messagebox.showerror("Lỗi", f"Không thể tải giao diện đăng nhập: {str(e)}")
                sys.exit()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi khởi động đăng nhập: {str(e)}")
                sys.exit()

    @staticmethod
    def run_main(user_id):
        """Run the Main interface with the given user_id."""
        main_root = ctk.CTk()
        main_root.state('zoomed')  # Tối đa hóa cửa sổ
        main_root.attributes('-fullscreen', False)
        main_root.focus_force()
        app = Main(main_root, user_id)
        main_root.update()
        main_root.mainloop()

def run():
    """Application entry point."""
    root = ctk.CTk()
    login_app = Login(root, Main.run_main)
    root.mainloop()

if __name__ == "__main__":
    run()