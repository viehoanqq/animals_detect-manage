import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as messagebox
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os
import uuid

class EmployeeManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent_frame, fg_color="#ffffff", corner_radius=12)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header frame
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="#ffffff", corner_radius=8)
        self.header_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Title
        ctk.CTkLabel(
            self.header_frame,
            text="Quản lý nhân viên",
            font=("Arial", 26, "bold"),
            text_color="#1a5f7a"
        ).pack(side="left", padx=15, pady=5)

        # Content frame (split layout)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # Left frame (inputs and buttons) - fixed width and height
        self.left_frame = ctk.CTkFrame(self.content_frame, fg_color="#f8f9fa", corner_radius=10, border_width=1, border_color="#e9ecef", width=500, height=600)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10), pady=5)
        self.left_frame.pack_propagate(False)

        # Right frame (employee list)
        self.right_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)

        # Input fields frame
        self.inputs_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.inputs_frame.pack(pady=10, padx=10, fill="x")

        # Input fields configuration
        self.first_name_entry = ctk.CTkEntry(self.inputs_frame, width=220, font=("Arial", 13), placeholder_text="Tên", corner_radius=6)
        self.last_name_entry = ctk.CTkEntry(self.inputs_frame, width=220, font=("Arial", 13), placeholder_text="Họ", corner_radius=6)
        self.gender_combo = ctk.CTkComboBox(self.inputs_frame, values=["MALE", "FEMALE"], width=220, font=("Arial", 13), corner_radius=6)
        self.birth_year_entry = ctk.CTkEntry(self.inputs_frame, width=220, font=("Arial", 13), placeholder_text="Năm sinh", corner_radius=6)
        self.phone_entry = ctk.CTkEntry(self.inputs_frame, width=220, font=("Arial", 13), placeholder_text="SĐT", corner_radius=6)
        self.email_entry = ctk.CTkEntry(self.inputs_frame, width=220, font=("Arial", 13), placeholder_text="Email", corner_radius=6)
        self.role_combo = ctk.CTkComboBox(self.inputs_frame, values=["Employee", "Admin"], width=220, font=("Arial", 13), corner_radius=6)

        input_fields = [
            ("Tên:", self.first_name_entry),
            ("Họ:", self.last_name_entry),
            ("Giới tính:", self.gender_combo),
            ("Năm sinh:", self.birth_year_entry),
            ("SĐT:", self.phone_entry),
            ("Email:", self.email_entry),
            ("Vai trò:", self.role_combo),
        ]

        # Grid layout for label:entry
        for i, (label_text, widget) in enumerate(input_fields):
            label = ctk.CTkLabel(self.inputs_frame, text=f"{label_text}", font=("Arial", 14, "bold"), text_color="#343a40", width=80)
            label.grid(row=i, column=0, padx=(5, 0), pady=3, sticky="w")
            widget.grid(row=i, column=1, padx=(0, 5), pady=3, sticky="ew")
        self.inputs_frame.grid_columnconfigure(1, weight=1)

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=10, padx=10, fill="x")

        # Approval buttons
        self.approve_button = ctk.CTkButton(
            self.buttons_frame,
            text="Kích hoạt",
            command=self.approve_account,
            fg_color="#1a5f7a",
            hover_color="#134b60",
            width=100,
            height=32,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
        )
        self.approve_button.pack(side="left", padx=3)

        self.reject_button = ctk.CTkButton(
            self.buttons_frame,
            text="Khóa tài khoản",
            command=self.reject_account,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=100,
            height=32,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#bd2130"
        )
        self.reject_button.pack(side="left", padx=3)

        # Action buttons
        self.update_button = ctk.CTkButton(
            self.buttons_frame,
            text="Cập nhật",
            command=self.update_employee,
            fg_color="#17a2b8",
            hover_color="#138496",
            width=100,
            height=32,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#117a8b"
        )
        self.update_button.pack(side="left", padx=3)

        self.delete_button = ctk.CTkButton(
            self.buttons_frame,
            text="Xóa",
            command=self.delete_employee,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=100,
            height=32,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#5a6268"
        )
        self.delete_button.pack(side="left", padx=3)

        # Employee list frame
        self.employee_list_frame = ctk.CTkFrame(self.right_frame, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#e9ecef")
        self.employee_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Header table and search
        self.header_table_frame = ctk.CTkFrame(self.employee_list_frame, fg_color="transparent")
        self.header_table_frame.pack(fill="x", padx=10, pady=(5, 5))

        self.header_table_text = ctk.CTkLabel(
            self.header_table_frame,
            text="Danh sách nhân viên",
            font=("Arial", 16, "bold"),
            text_color="#343a40"
        )
        self.header_table_text.pack(side="left", padx=10)

        self.search_frame = ctk.CTkFrame(self.header_table_frame, fg_color="transparent")
        self.search_frame.pack(side="right", padx=10)

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            width=200,
            font=("Arial", 13),
            placeholder_text="Tìm theo ID hoặc tên...",
            corner_radius=6,
            border_width=1,
            border_color="#ced4da"
        )
        self.search_entry.pack(side="left", padx=(0, 5))

        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Tìm kiếm",
            command=self.search_employee,
            fg_color="#1a5f7a",
            hover_color="#134b60",
            width=100,
            height=32,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#134b60"
        )
        self.search_button.pack(side="left")

        self.clear_search_button = ctk.CTkButton(
            self.search_frame,
            text="Cài lại",
            command=self.clear_search,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=100,
            height=32,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#5a6268"
        )
        self.clear_search_button.pack(side="left", padx=(5, 0))

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
        columns = ("ID", "Họ tên", "Giới tính", "Năm sinh", "SĐT", "Email", "Vai trò", "Trạng thái")
        self.tree = ttk.Treeview(self.employee_list_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Set column headings and widths
        column_widths = {"ID": 60, "Họ tên": 130, "Giới tính": 80, "Năm sinh": 60, "SĐT": 100, "Email": 120, "Vai trò": 120, "Trạng thái": 80}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.employee_list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_employee_select)

    def search_employee(self):
        """Search employees by ID or name"""
        search_term = self.search_entry.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            from controller.account_controller import AccountController
            controller = AccountController(user_id=0)
            employees = controller.get_all_accounts()
            for emp in employees:
                full_name = f"{emp['first_name']} {emp['last_name']}".lower()
                emp_id = str(emp['id'])
                if search_term in full_name or search_term in emp_id:
                    self.tree.insert("", "end", values=(
                        emp['id'], full_name.title(), emp['gender'], emp['birth_year'],
                        emp['phone_number'], emp['email'], emp['role'].capitalize(),
                        emp['activity']
                    ))
            if not self.tree.get_children():
                messagebox.showinfo("Kết quả", "Không tìm thấy nhân viên phù hợp.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tìm kiếm: {str(e)}")

    def clear_search(self):
        """Clear search entry and reload all employees"""
        self.search_entry.delete(0, "end")
        self.load_employees()

    def load_employees(self):
        """Load employee data into the Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            from controller.account_controller import AccountController
            controller = AccountController(user_id=0)
            employees = controller.get_all_accounts()
            for emp in employees:
                full_name = f"{emp['first_name']} {emp['last_name']}"
                self.tree.insert("", "end", values=(
                    emp['id'], full_name, emp['gender'], emp['birth_year'],
                    emp['phone_number'], emp['email'], emp['role'].capitalize(),
                    emp['activity']
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải danh sách nhân viên: {str(e)}")

    def on_employee_select(self, event):
        """Populate input fields when an employee is selected"""
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            values = item['values']
            self.clear_inputs()
            name_parts = values[1].split()
            if len(name_parts) > 1:
                self.first_name_entry.insert(0, name_parts[0])
                self.last_name_entry.insert(0, " ".join(name_parts[1:]))
            else:
                self.first_name_entry.insert(0, name_parts[0])
            self.gender_combo.set(values[2])
            self.birth_year_entry.insert(0, values[3])
            self.phone_entry.insert(0, values[4])
            self.email_entry.insert(0, values[5])
            self.role_combo.set(values[6])

    def update_employee(self):
        """Update selected employee's information"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên để cập nhật")
            return

        try:
            from controller.account_controller import AccountController
            emp_id = self.tree.item(selected_item)['values'][0]
            first_name = self.first_name_entry.get().strip()
            last_name = self.last_name_entry.get().strip()

            if not all([first_name, last_name]):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ Tên và Họ!")
                return

            controller = AccountController(user_id=emp_id)
            controller.update_account(
                first_name=first_name,
                last_name=last_name,
                gender=self.gender_combo.get(),
                birth_year=int(self.birth_year_entry.get()) if self.birth_year_entry.get().strip() else 0,
                phone_number=self.phone_entry.get().strip(),
                email=self.email_entry.get().strip()
            )
            conn = controller._get_connection()
            cursor = conn.cursor()
            query = "UPDATE users SET role = %s WHERE id = %s"
            cursor.execute(query, (self.role_combo.get().lower(), emp_id))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Thành công", "Cập nhật nhân viên thành công")
            self.load_employees()
            self.clear_inputs()
        except ValueError:
            messagebox.showerror("Lỗi", "Năm sinh phải là số nguyên")
        except mysql.connector.Error as db_err:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {str(db_err)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

    def delete_employee(self):
        """Delete selected employee"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên để xóa")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa nhân viên này?"):
            try:
                from controller.account_controller import AccountController
                emp_id = self.tree.item(selected_item)['values'][0]
                controller = AccountController(user_id=emp_id)
                controller.delete_account()
                messagebox.showinfo("Thành công", "Xóa nhân viên thành công")
                self.load_employees()
                self.clear_inputs()
            except mysql.connector.Error as db_err:
                messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {str(db_err)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")

    def approve_account(self):
        """Approve selected employee's account"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản để duyệt")
            return

        try:
            from controller.account_controller import AccountController
            emp_id = self.tree.item(selected_item)['values'][0]
            controller = AccountController(user_id=emp_id)
            conn = controller._get_connection()
            cursor = conn.cursor()
            query = "UPDATE accounts SET activity = %s WHERE user_id = %s"
            cursor.execute(query, (1, emp_id))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Thành công", "Đã kích hoạt thành công!")
            self.load_employees()
        except mysql.connector.Error as db_err:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {str(db_err)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi duyệt tài khoản: {str(e)}")

    def reject_account(self):
        """Reject selected employee's account"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản để từ chối")
            return

        try:
            from controller.account_controller import AccountController
            emp_id = self.tree.item(selected_item)['values'][0]
            controller = AccountController(user_id=emp_id)
            conn = controller._get_connection()
            cursor = conn.cursor()
            query = "UPDATE accounts SET activity = %s WHERE user_id = %s"
            cursor.execute(query, ("rejected", emp_id))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Thành công", "Đã hủy kích hoạt tài khoản!")
            self.load_employees()
        except mysql.connector.Error as db_err:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {str(db_err)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi từ chối tài khoản: {str(e)}")

    def clear_inputs(self):
        """Clear all input fields"""
        self.first_name_entry.delete(0, "end")
        self.last_name_entry.delete(0, "end")
        self.birth_year_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.gender_combo.set("MALE")
        self.role_combo.set("Employee")