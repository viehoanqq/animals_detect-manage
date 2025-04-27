import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controller.environment_controller import environment_controller
from datetime import datetime
import requests


class EnvironmentManagement:
    def __init__(self, parent):
        self.parent = parent
        self.controller = environment_controller()
        self.env_data = []  # Store environment data for sorting/filtering
        self.sort_column = "record_date"  # Default sort column
        self.sort_order = "desc"  # Default sort order
        self.setup_ui()
        print(environment_controller.get_info_env())

    def setup_ui(self):
        """Thiết lập giao diện người dùng cho quản lý môi trường"""
        main_frame = ctk.CTkFrame(self.parent) 
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tiêu đề
        ctk.CTkLabel(main_frame, text="QUẢN LÝ MÔI TRƯỜNG", font=("Arial", 20, "bold"), text_color="#2e7a84").pack(pady=10)

        # Header frame for search and sort
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=5)

        # Search and sort controls
        controls_frame = ctk.CTkFrame(header_frame)
        controls_frame.pack(side="right", padx=10)
        
        lable_frame = ctk.CTkFrame(header_frame)
        lable_frame.pack(side="left",padx= 5)
        ctk.CTkLabel(lable_frame,text=""+environment_controller.get_info_env()[0], font=("Arial", 19, "bold"), text_color="#2e7a84").pack(padx=5)
        ctk.CTkLabel(lable_frame,text="Trạng thái: "+environment_controller.get_info_env()[3],font=("Arial", 12, "bold"),text_color="#2e7a84").pack(padx=5)
        

        # Search by date
        search_frame = ctk.CTkFrame(controls_frame)
        search_frame.pack(side="left", padx=5)
        ctk.CTkLabel(search_frame, text="Tìm theo ngày:", font=("Arial", 12)).pack()
        self.search_entry = ctk.CTkEntry(search_frame, width=150, placeholder_text="YYYY-MM-DD")
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_by_date)

        # Sort options
        sort_frame = ctk.CTkFrame(controls_frame)
        sort_frame.pack(side="left", padx=5)
        ctk.CTkLabel(sort_frame, text="Sắp xếp:", font=("Arial", 12)).pack()

        sort_subframe = ctk.CTkFrame(sort_frame)
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
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=10, padx=10)

        # Current date and time
        current_time = datetime.now()
        date_str = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")

        # Input fields
        fields = [
            ("Ngày:", date_str, "date", True),
            ("Giờ:", time_str, "time", True),
            ("Nhiệt độ (°C):", environment_controller.get_info_env()[1], "temperature", True),
            ("Độ ẩm (%):", environment_controller.get_info_env()[2] , "humidity", True),
            ("Lượng mưa (mm):", environment_controller.get_info_env()[4], "rainfall", True)
        ]

        self.entries = {}
        for label_text, default_value, field, readonly in fields:
            field_frame = ctk.CTkFrame(input_frame)
            field_frame.pack(side="left", padx=5)
            
            ctk.CTkLabel(field_frame, text=label_text, font=("Arial", 12)).pack()
            entry = ctk.CTkEntry(field_frame, width=120)
            entry.insert(0, default_value)
            if readonly:
                entry.configure(state="readonly")
            entry.pack()
            self.entries[field] = entry

        # Buttons frame
        buttons_frame = ctk.CTkFrame(input_frame)
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
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)

        # Create table
        columns = ("Ngày", "Giờ", "Nhiệt độ (°C)", "Độ ẩm (%)", "Lượng mưa (mm)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Load existing data
        self.load_environment_data()

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
            
            for field in ["temperature", "humidity", "rainfall"]:
                self.entries[field].delete(0, "end")

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