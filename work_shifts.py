import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controller.work_shifts_controller import work_shifts_controller
from controller.shift_details_controller import shift_details_controller
from datetime import datetime

class ShiftManagement:
    def __init__(self, parent):
        self.parent = parent
        self.shift_controller = work_shifts_controller()
        self.detail_controller = shift_details_controller()
        self.selected_shift_id = None
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện người dùng cho quản lý ca làm việc"""
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tiêu đề
        ctk.CTkLabel(main_frame, text="QUẢN LÝ CA LÀM VIỆC", font=("Arial", 20, "bold"), text_color="#2e7a84").pack(pady=10)

        # Split frame into left (shifts) and right (details)
        split_frame = ctk.CTkFrame(main_frame)
        split_frame.pack(fill="both", expand=True)

        # Left panel: Work Shifts
        left_panel = ctk.CTkFrame(split_frame, width=500)
        left_panel.pack(side="left", fill="both", padx=5, expand=False)

        # Search for shifts
        shift_search_frame = ctk.CTkFrame(left_panel)
        shift_search_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(shift_search_frame, text="Tìm ca:", font=("Arial", 12)).pack(side="left")
        self.shift_search_entry = ctk.CTkEntry(shift_search_frame, width=200, placeholder_text="Số ca hoặc username")
        self.shift_search_entry.pack(side="left", padx=5)
        self.shift_search_entry.bind("<KeyRelease>", self.search_shifts)

        # Shift table
        shift_table_frame = ctk.CTkFrame(left_panel)
        shift_table_frame.pack(fill="both", expand=True, pady=10)

        shift_columns = ("ID", "Số ca", "Bắt đầu", "Kết thúc", "Số lượng", "Username")
        self.shift_tree = ttk.Treeview(shift_table_frame, columns=shift_columns, show="headings")
        for col in shift_columns:
            self.shift_tree.heading(col, text=col)
            self.shift_tree.column(col, width=100)
        self.shift_tree.pack(fill="both", expand=True)

        shift_scrollbar = ttk.Scrollbar(shift_table_frame, orient="vertical", command=self.shift_tree.yview)
        shift_scrollbar.pack(side="right", fill="y")
        self.shift_tree.configure(yscrollcommand=shift_scrollbar.set)

        # Bind selection event
        self.shift_tree.bind("<<TreeviewSelect>>", self.on_shift_select)

        # Shift buttons
        shift_button_frame = ctk.CTkFrame(left_panel)
        shift_button_frame.pack(fill="x", pady=10)
        ctk.CTkButton(
            shift_button_frame,
            text="Thêm ca",
            command=self.open_add_shift_window,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            shift_button_frame,
            text="Sửa ca",
            command=self.open_edit_shift_window,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            shift_button_frame,
            text="Xóa ca",
            command=self.delete_shift,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=100
        ).pack(side="left", padx=5)

        # Right panel: Shift Details
        right_panel = ctk.CTkFrame(split_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=5)

        # Search for details
        detail_search_frame = ctk.CTkFrame(right_panel)
        detail_search_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(detail_search_frame, text="Tìm chi tiết:", font=("Arial", 12)).pack(side="left")
        self.detail_search_entry = ctk.CTkEntry(detail_search_frame, width=200, placeholder_text="Shift ID hoặc Animal ID")
        self.detail_search_entry.pack(side="left", padx=5)
        self.detail_search_entry.bind("<KeyRelease>", self.search_details)

        # Detail table
        detail_table_frame = ctk.CTkFrame(right_panel)
        detail_table_frame.pack(fill="both", expand=True, pady=10)

        detail_columns = ("ID", "Shift ID", "Animal ID", "Loài", "Số lượng")
        self.detail_tree = ttk.Treeview(detail_table_frame, columns=detail_columns, show="headings")
        for col in detail_columns:
            self.detail_tree.heading(col, text=col)
            self.detail_tree.column(col, width=100)
        self.detail_tree.pack(fill="both", expand=True)

        detail_scrollbar = ttk.Scrollbar(detail_table_frame, orient="vertical", command=self.detail_tree.yview)
        detail_scrollbar.pack(side="right", fill="y")
        self.detail_tree.configure(yscrollcommand=detail_scrollbar.set)

        # Detail buttons
        detail_button_frame = ctk.CTkFrame(right_panel)
        detail_button_frame.pack(fill="x", pady=10)
        ctk.CTkButton(
            detail_button_frame,
            text="Thêm chi tiết",
            command=self.open_add_detail_window,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            detail_button_frame,
            text="Sửa chi tiết",
            command=self.open_edit_detail_window,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            detail_button_frame,
            text="Xóa chi tiết",
            command=self.delete_detail,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=100
        ).pack(side="left", padx=5)

        # Load initial shift data
        self.load_shifts()

    def load_shifts(self, shifts=None):
        """Tải danh sách ca làm việc"""
        for item in self.shift_tree.get_children():
            self.shift_tree.delete(item)

        if shifts is None:
            shifts = self.shift_controller.get_list()

        for shift in shifts:
            self.shift_tree.insert("", "end", values=(
                shift['id'],
                shift['shift_number'],
                shift['start_time'],
                shift['end_time'],
                shift['total_animals'],
                shift['username']
            ))

    def load_details(self, shift_id=None):
        """Tải chi tiết ca làm việc"""
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

        if shift_id:
            details = [d for d in self.detail_controller.get_list() if d['shift_id'] == shift_id]
            for detail in details:
                self.detail_tree.insert("", "end", values=(
                    detail['id'],
                    detail['shift_id'],
                    detail['animal_id'],
                    detail['type_name'],
                    detail['quantity']
                ))

    def search_shifts(self, event):
        """Tìm kiếm ca làm việc"""
        search_term = self.shift_search_entry.get().strip()
        shifts = self.shift_controller.search_shifts(search_term)
        self.load_shifts(shifts)

    def search_details(self, event):
        """Tìm kiếm chi tiết ca làm việc"""
        search_term = self.detail_search_entry.get().strip()
        details = self.detail_controller.search_shift_details(search_term)
        if self.selected_shift_id:
            details = [d for d in details if d['shift_id'] == self.selected_shift_id]
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        for detail in details:
            self.detail_tree.insert("", "end", values=(
                detail['id'],
                detail['shift_id'],
                detail['animal_id'],
                detail['type_name'],
                detail['quantity']
            ))

    def on_shift_select(self, event):
        """Xử lý khi chọn một ca làm việc"""
        selected_item = self.shift_tree.selection()
        if selected_item:
            item = self.shift_tree.item(selected_item)
            self.selected_shift_id = int(item["values"][0])
            self.load_details(self.selected_shift_id)

    def open_add_shift_window(self):
        """Mở cửa sổ thêm ca làm việc"""
        window = ctk.CTkToplevel(self.parent)
        window.title("Thêm ca làm việc")
        window.geometry("400x400")

        fields = [
            ("Số ca:", "shift_number"),
            ("Giờ bắt đầu (HH:MM:SS):", "start_time"),
            ("Giờ kết thúc (HH:MM:SS):", "end_time"),
            ("Tổng số vật nuôi:", "total_animals"),
            ("Username:", "username")
        ]

        entries = {}
        for label_text, field in fields:
            ctk.CTkLabel(window, text=label_text).pack()
            entry = ctk.CTkEntry(window)
            entry.pack()
            entries[field] = entry

        def save_shift():
            try:
                shift_number = entries["shift_number"].get()
                start_time = entries["start_time"].get()
                end_time = entries["end_time"].get()
                total_animals = int(entries["total_animals"].get())
                username = entries["username"].get()

                if not all([shift_number, start_time, end_time, entries["total_animals"].get(), username]):
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                    return

                self.shift_controller.add_shift(shift_number, start_time, end_time, total_animals, username)
                self.load_shifts()
                window.destroy()
                messagebox.showinfo("Thành công", "Đã thêm ca làm việc!")
            except ValueError:
                messagebox.showerror("Lỗi", "Tổng số vật nuôi phải là số nguyên!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")

        ctk.CTkButton(window, text="Lưu", command=save_shift, fg_color="#2e7a84").pack(pady=20)

    def open_edit_shift_window(self):
        """Mở cửa sổ sửa ca làm việc"""
        selected_item = self.shift_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một ca để sửa!")
            return

        item = self.shift_tree.item(selected_item)
        values = item["values"]
        shift_id = values[0]

        window = ctk.CTkToplevel(self.parent)
        window.title("Sửa ca làm việc")
        window.geometry("400x400")

        fields = [
            ("Số ca:", "shift_number", values[1]),
            ("Giờ bắt đầu (HH:MM:SS):", "start_time", values[2]),
            ("Giờ kết thúc (HH:MM:SS):", "end_time", values[3]),
            ("Tổng số vật nuôi:", "total_animals", values[4]),
            ("Username:", "username", values[5])
        ]

        entries = {}
        for label_text, field, value in fields:
            ctk.CTkLabel(window, text=label_text).pack()
            entry = ctk.CTkEntry(window)
            entry.insert(0, value)
            entry.pack()
            entries[field] = entry

        def update_shift():
            try:
                shift_number = entries["shift_number"].get()
                start_time = entries["start_time"].get()
                end_time = entries["end_time"].get()
                total_animals = int(entries["total_animals"].get())
                username = entries["username"].get()

                if not all([shift_number, start_time, end_time, entries["total_animals"].get(), username]):
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                    return

                self.shift_controller.update_shift(shift_id, shift_number, start_time, end_time, total_animals, username)
                self.load_shifts()
                window.destroy()
                messagebox.showinfo("Thành công", "Đã cập nhật ca làm việc!")
            except ValueError:
                messagebox.showerror("Lỗi", "Tổng số vật nuôi phải là số nguyên!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

        ctk.CTkButton(window, text="Cập nhật", command=update_shift, fg_color="#2e7a84").pack(pady=20)

    def delete_shift(self):
        """Xóa ca làm việc đã chọn"""
        selected_item = self.shift_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một ca để xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa ca này?"):
            item = self.shift_tree.item(selected_item)
            shift_id = item["values"][0]
            try:
                self.shift_controller.delete_shift(shift_id)
                self.load_shifts()
                self.load_details(None)  # Clear details
                self.selected_shift_id = None
                messagebox.showinfo("Thành công", "Đã xóa ca làm việc!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")

    def open_add_detail_window(self):
        """Mở cửa sổ thêm chi tiết ca làm việc"""
        if not self.selected_shift_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một ca làm việc trước!")
            return

        window = ctk.CTkToplevel(self.parent)
        window.title("Thêm chi tiết ca làm việc")
        window.geometry("400x300")

        fields = [
            ("Shift ID:", "shift_id", str(self.selected_shift_id), True),
            ("Animal ID:", "animal_id"),
            ("Số lượng:", "quantity")
        ]

        entries = {}
        for label_text, field, *args in fields:
            ctk.CTkLabel(window, text=label_text).pack()
            entry = ctk.CTkEntry(window)
            if args:
                entry.insert(0, args[0])
                entry.configure(state="readonly")
            entry.pack()
            entries[field] = entry

        def save_detail():
            try:
                shift_id = int(entries["shift_id"].get())
                animal_id = int(entries["animal_id"].get())
                quantity = int(entries["quantity"].get())

                if not all([entries["animal_id"].get(), entries["quantity"].get()]):
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                    return

                self.detail_controller.add_shift_detail(shift_id, animal_id, quantity)
                self.load_details(shift_id)
                window.destroy()
                messagebox.showinfo("Thành công", "Đã thêm chi tiết ca làm việc!")
            except ValueError:
                messagebox.showerror("Lỗi", "Animal ID và số lượng phải là số nguyên!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")

        ctk.CTkButton(window, text="Lưu", command=save_detail, fg_color="#2e7a84").pack(pady=20)

    def open_edit_detail_window(self):
        """Mở cửa sổ sửa chi tiết ca làm việc"""
        selected_item = self.detail_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một chi tiết để sửa!")
            return

        item = self.detail_tree.item(selected_item)
        values = item["values"]
        detail_id = values[0]

        window = ctk.CTkToplevel(self.parent)
        window.title("Sửa chi tiết ca làm việc")
        window.geometry("400x300")

        fields = [
            ("Shift ID:", "shift_id", str(values[1]), True),
            ("Animal ID:", "animal_id", str(values[2])),
            ("Số lượng:", "quantity", str(values[4]))
        ]

        entries = {}
        for label_text, field, value in fields:
            ctk.CTkLabel(window, text=label_text).pack()
            entry = ctk.CTkEntry(window)
            entry.insert(0, value)
            if field == "shift_id":
                entry.configure(state="readonly")
            entry.pack()
            entries[field] = entry

        def update_detail():
            try:
                shift_id = int(entries["shift_id"].get())
                animal_id = int(entries["animal_id"].get())
                quantity = int(entries["quantity"].get())

                if not all([entries["animal_id"].get(), entries["quantity"].get()]):
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                    return

                self.detail_controller.update_shift_detail(detail_id, shift_id, animal_id, quantity)
                self.load_details(shift_id)
                window.destroy()
                messagebox.showinfo("Thành công", "Đã cập nhật chi tiết ca làm việc!")
            except ValueError:
                messagebox.showerror("Lỗi", "Animal ID và số lượng phải là số nguyên!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

        ctk.CTkButton(window, text="Cập nhật", command=update_detail, fg_color="#2e7a84").pack(pady=20)

    def delete_detail(self):
        """Xóa chi tiết ca làm việc đã chọn"""
        selected_item = self.detail_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một chi tiết để xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa chi tiết này?"):
            item = self.detail_tree.item(selected_item)
            detail_id = item["values"][0]
            shift_id = item["values"][1]
            try:
                self.detail_controller.delete_shift_detail(detail_id)
                self.load_details(shift_id)
                messagebox.showinfo("Thành công", "Đã xóa chi tiết ca làm việc!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")