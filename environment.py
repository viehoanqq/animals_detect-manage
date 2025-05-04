import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controller.environment_controller import environment_controller
from datetime import datetime
import schedule
import time
import threading

class EnvironmentManagement:
    def __init__(self, parent):
        self.parent = parent
        self.controller = environment_controller()
        self.env_data = []  # Store environment data for sorting/filtering
        self.sort_column = "record_date"  # Default sort column
        self.sort_order = "desc"  # Default sort order
        self.setup_ui()
        self.start_scheduler()

    def setup_ui(self):
        """Thiết lập giao diện người dùng cho quản lý môi trường"""
        main_frame = ctk.CTkFrame(self.parent, fg_color="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tiêu đề
        ctk.CTkLabel(
            main_frame,
            text="QUẢN LÝ MÔI TRƯỜNG",
            font=("Arial", 20, "bold"),
            text_color="#2e7a84"
        ).pack(pady=10)

        # Header frame for search and sort
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=5)

        # Search and sort controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=10)

        # Location and status labels
        label_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        label_frame.pack(side="left", padx=5)
        try:
            env_info = self.controller.get_info_env()
            ctk.CTkLabel(
                label_frame,
                text=env_info[0],
                font=("Arial", 19, "bold"),
                text_color="#2e7a84"
            ).pack(padx=5)
            ctk.CTkLabel(
                label_frame,
                text="Trạng thái: " + env_info[3],
                font=("Arial", 12, "bold"),
                text_color="#2e7a84"
            ).pack(padx=5)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy thông tin môi trường: {str(e)}")

        # Search by date
        search_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=5)
        ctk.CTkLabel(search_frame, text="Tìm theo ngày:", font=("Arial", 12)).pack()
        self.search_entry = ctk.CTkEntry(search_frame, width=150, placeholder_text="YYYY-MM-DD")
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_by_date)

        # Sort options
        sort_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        sort_frame.pack(side="left", padx=5)
        ctk.CTkLabel(sort_frame, text="Sắp xếp:", font=("Arial", 12)).pack()

        sort_subframe = ctk.CTkFrame(sort_frame, fg_color="transparent")
        sort_subframe.pack(pady=5)

        # Combobox for column selection
        self.sort_column_combobox = ctk.CTkComboBox(
            sort_subframe,
            values=["Ngày", "Nhiệt độ", "Độ ẩm", "Lượng mưa"],
            command=self.update_sort_column,
            width=120
        )
        self.sort_column_combobox.pack(side="left", padx=2)

        # Combobox for sort order
        self.sort_order_combobox = ctk.CTkComboBox(
            sort_subframe,
            values=["Giảm dần", "Tăng dần"],
            command=self.update_sort_order,
            width=100
        )
        self.sort_order_combobox.pack(side="left", padx=2)

        # Input and button frame
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=10, padx=10)

        # Current date and time
        current_time = datetime.now()
        date_str = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")

        # Input fields
        fields = [
            ("Ngày:", date_str, "date", True),
            ("Giờ:", time_str, "time", True),
            ("Nhiệt độ (°C):", "", "temperature", True),
            ("Độ ẩm (%):", "", "humidity", True),
            ("Lượng mưa (mm):", "", "rainfall", True)
        ]

        self.entries = {}
        try:
            env_info = self.controller.get_info_env()
            fields[2] = ("Nhiệt độ (°C):", env_info[1], "temperature", True)
            fields[3] = ("Độ ẩm (%):", env_info[2], "humidity", True)
            fields[4] = ("Lượng mưa (mm):", env_info[4], "rainfall", True)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy thông tin môi trường: {str(e)}")

        for label_text, default_value, field, readonly in fields:
            field_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
            field_frame.pack(side="left", padx=5)
            ctk.CTkLabel(field_frame, text=label_text, font=("Arial", 12)).pack()
            entry = ctk.CTkEntry(field_frame, width=120)
            entry.insert(0, default_value)
            if readonly:
                entry.configure(state="readonly")
            entry.pack()
            self.entries[field] = entry

        # Buttons frame
        buttons_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        buttons_frame.pack(side="left", padx=10)

        # Update button
        ctk.CTkButton(
            buttons_frame,
            text="Cập nhật",
            command=self.update_environment,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(pady=5)

        # Delete button
        ctk.CTkButton(
            buttons_frame,
            text="Xóa",
            command=self.delete_selected,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=100
        ).pack(pady=5)

        # Table frame
        table_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Treeview styling
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background="#ffffff",
                        foreground="black",
                        rowheight=32,
                        fieldbackground="#ffffff",
                        font=("Arial", 12))
        style.configure("Custom.Treeview.Heading",
                        background="#1a5f7a",
                        foreground="black",
                        font=("Arial", 13, "bold"),
                        borderwidth=1,
                        relief="flat")
        style.map("Custom.Treeview",
                  background=[('selected', 'black')],
                  foreground=[('selected', 'white')])
        style.map("Custom.Treeview.Heading",
                  background=[('active', 'black')])

        # Treeview setup
        columns = ("Ngày", "Giờ", "Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Set column headings and widths
        column_widths = {
            "Ngày": 120,
            "Giờ": 100,
            "Nhiệt độ (°C)": 100,
            "Độ ẩm (%)": 100,
            "Lượng mưa (mm)": 100
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Load existing data
        self.load_environment_data()

    def start_scheduler(self):
        """Khởi động scheduler để tự động cập nhật thời tiết lúc 12:00 PM hàng ngày"""
        def run_scheduler():
            schedule.every().day.at("12:00").do(self.auto_update_weather)
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        # Run scheduler in a separate thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

    def auto_update_weather(self):
        """Tự động cập nhật dữ liệu thời tiết lúc 12:00 PM"""
        try:
            env_info = self.controller.get_info_env()
            current_time = datetime.now()
            record_date = current_time.strftime("%Y-%m-%d")
            record_time = current_time.strftime("%H:%M:%S")
            temperature = float(env_info[1])
            humidity = float(env_info[2])
            rainfall = float(env_info[4])

            self.controller.add_enviroment(record_date, record_time, temperature, humidity, rainfall)
            self.load_environment_data()
        except Exception as e:
            print(f"Lỗi khi tự động cập nhật thời tiết: {str(e)}")

    def load_environment_data(self, data=None):
        """Tải danh sách dữ liệu môi trường vào bảng"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if data is None:
            self.env_data = self.controller.get_list()
            data = self.env_data

        for record in data:
            self.tree.insert("", "end", values=(
                record['record_date'],
                record['record_time'],
                record['temperature'],
                record['humidity'],
                record['rainfall']
            ))

    def search_by_date(self, event):
        """Tìm kiếm bản ghi theo ngày"""
        search_term = self.search_entry.get().strip()
        filtered_data = [
            record for record in self.env_data
            if search_term in str(record['record_date'])
        ]
        self.load_environment_data(filtered_data)

    def update_sort_column(self, choice):
        """Cập nhật cột sắp xếp"""
        column_map = {
            "Ngày": "record_date",
            "Nhiệt độ": "temperature",
            "Độ ẩm": "humidity",
            "Lượng mưa": "rainfall"
        }
        self.sort_column = column_map[choice]
        self.sort_data()

    def update_sort_order(self, choice):
        """Cập nhật thứ tự sắp xếp"""
        self.sort_order = "asc" if choice == "Tăng dần" else "desc"
        self.sort_data()

    def sort_data(self):
        """Sắp xếp dữ liệu theo cột và thứ tự đã chọn"""
        self.env_data.sort(
            key=lambda x: x[self.sort_column],
            reverse=(self.sort_order == "desc")
        )
        self.load_environment_data(self.env_data)

    def update_environment(self):
        """Lưu dữ liệu môi trường mới và cập nhật bảng"""
        try:
            record_date = self.entries["date"].get()
            record_time = self.entries["time"].get()
            temperature = float(self.entries["temperature"].get())
            humidity = float(self.entries["humidity"].get())
            rainfall = float(self.entries["rainfall"].get())

            if not all([record_date, record_time, self.entries["temperature"].get(),
                       self.entries["humidity"].get(), self.entries["rainfall"].get()]):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                return

            self.controller.add_enviroment(record_date, record_time, temperature, humidity, rainfall)
            self.load_environment_data()

            # Reset input fields (keep date and time as current)
            current_time = datetime.now()
            self.entries["date"].configure(state="normal")
            self.entries["date"].delete(0, "end")
            self.entries["date"].insert(0, current_time.strftime("%Y-%m-%d"))
            self.entries["date"].configure(state="readonly")

            self.entries["time"].configure(state="normal")
            self.entries["time"].delete(0, "end")
            self.entries["time"].insert(0, current_time.strftime("%H:%M:%S"))
            self.entries["time"].configure(state="readonly")

            env_info = self.controller.get_info_env()
            for field, value in [("temperature", env_info[1]), ("humidity", env_info[2]), ("rainfall", env_info[4])]:
                self.entries[field].configure(state="normal")
                self.entries[field].delete(0, "end")
                self.entries[field].insert(0, value)
                self.entries[field].configure(state="readonly")

            messagebox.showinfo("Thành công", "Đã cập nhật dữ liệu môi trường!")

        except ValueError:
            messagebox.showerror("Lỗi", "Nhiệt độ, độ ẩm và lượng mưa phải là số!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

    def delete_selected(self):
        """Xóa bản ghi môi trường đã chọn"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa thông tin này?"):
            item = self.tree.item(selected_item)
            values = item["values"]
            record_date, record_time = values[0], values[1]
            try:
                self.controller.delete_enviroment(record_date, record_time)
                self.load_environment_data()
                messagebox.showinfo("Thành công", "Đã xóa!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")