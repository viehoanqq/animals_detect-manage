import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as messagebox
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os

class EmployeeManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        # Main title
        ctk.CTkLabel(
            self.parent_frame,
            text="Quản lý nhân viên",
            font=("Arial", 22, "bold"),
            text_color="#2e7a84"
        ).pack(pady=20)

        # Employee controls frame (input fields)
        self.controls_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.controls_frame.pack(pady=10, padx=10, fill="x")

        # Input fields
        self.first_name_entry = ctk.CTkEntry(self.controls_frame, width=150, font=("Arial", 12))
        self.last_name_entry = ctk.CTkEntry(self.controls_frame, width=150, font=("Arial", 12))
        self.gender_combo = ctk.CTkComboBox(self.controls_frame, values=["MALE", "FEMALE"], width=100, font=("Arial", 12))
        self.birth_year_entry = ctk.CTkEntry(self.controls_frame, width=100, font=("Arial", 12))
        self.phone_entry = ctk.CTkEntry(self.controls_frame, width=150, font=("Arial", 12))
        self.email_entry = ctk.CTkEntry(self.controls_frame, width=150, font=("Arial", 12))
        self.role_combo = ctk.CTkComboBox(self.controls_frame, values=["Employee", "Admin"], width=150, font=("Arial", 12))
        self.username_entry = ctk.CTkEntry(self.controls_frame, width=150, font=("Arial", 12))
        self.password_entry = ctk.CTkEntry(self.controls_frame, width=150, font=("Arial", 12), show="*")

        input_fields = [
            ("Tên:", self.first_name_entry),
            ("Họ:", self.last_name_entry),
            ("Giới tính:", self.gender_combo),
            ("Năm sinh:", self.birth_year_entry),
            ("SĐT:", self.phone_entry),
            ("Email:", self.email_entry),
            ("Vai trò:", self.role_combo),
            ("Tên đăng nhập:", self.username_entry),
            ("Mật khẩu:", self.password_entry)
        ]

        for label_text, widget in input_fields:
            ctk.CTkLabel(self.controls_frame, text=label_text, font=("Arial", 16)).pack(side="left", padx=5)
            widget.pack(side="left", padx=5)

        # Approval and action buttons frame
        self.actions_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.actions_frame.pack(pady=10, padx=10, fill="x")

        # Approval section (left)
        self.approval_subframe = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        self.approval_subframe.pack(side="left")

        ctk.CTkLabel(
            self.approval_subframe,
            text="Duyệt tài khoản:",
            font=("Arial", 16),
            text_color="#333333"
        ).pack(side="left", padx=5)

        self.approve_button = ctk.CTkButton(
            self.approval_subframe,
            text="Duyệt",
            command=self.approve_account,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100,
            height=35,
            font=("Arial", 13)
        )
        self.approve_button.pack(side="left", padx=5)

        self.reject_button = ctk.CTkButton(
            self.approval_subframe,
            text="Từ chối",
            command=self.reject_account,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=100,
            height=35,
            font=("Arial", 13)
        )
        self.reject_button.pack(side="left", padx=5)

        # Action buttons (right)
        self.buttons_subframe = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        self.buttons_subframe.pack(side="right")

        self.add_button = ctk.CTkButton(
            self.buttons_subframe,
            text="Thêm nhân viên",
            command=self.add_employee,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=150,
            height=35,
            font=("Arial", 13)
        )
        self.add_button.pack(side="left", padx=5)

        self.update_button = ctk.CTkButton(
            self.buttons_subframe,
            text="Cập nhật",
            command=self.update_employee,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=150,
            height=35,
            font=("Arial", 13)
        )
        self.update_button.pack(side="left", padx=5)

        self.delete_button = ctk.CTkButton(
            self.buttons_subframe,
            text="Xóa",
            command=self.delete_employee,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=150,
            height=35,
            font=("Arial", 13)
        )
        self.delete_button.pack(side="left", padx=5)

        # Employee list frame
        self.employee_list_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.employee_list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Treeview setup
        columns = ("ID", "Họ tên", "Giới tính", "Năm sinh", "SĐT", "Email", "Vai trò", "Tên đăng nhập", "Trạng thái")
        self.tree = ttk.Treeview(self.employee_list_frame, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True)

        # Set column headings and widths
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.employee_list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_employee_select)

    def load_employees(self):
        """Load employee data into the Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            from controller.account_controller import AccountController
            controller = AccountController(user_id=0)  # Temporary user_id for fetching data
            employees = controller.get_all_accounts()
            for emp in employees:
                full_name = f"{emp['first_name']} {emp['last_name']}"
                self.tree.insert("", "end", values=(
                    emp['id'], full_name, emp['gender'], emp['birth_year'],
                    emp['phone_number'], emp['email'], emp['role'].capitalize(),
                    emp['username'], emp['activity']
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
            self.username_entry.insert(0, values[7])

    def add_employee(self):
        """Add a new employee"""
        try:
            from controller.account_controller import AccountController
            first_name = self.first_name_entry.get().strip()
            last_name = self.last_name_entry.get().strip()
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()

            if not all([first_name, last_name, username, password]):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ Tên, Họ, Tên đăng nhập và Mật khẩu!")
                return

            controller = AccountController(user_id=0)
            controller.add_account(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                gender=self.gender_combo.get(),
                phone_number=self.phone_entry.get().strip(),
                email=self.email_entry.get().strip(),
                birth_year=int(self.birth_year_entry.get()) if self.birth_year_entry.get().strip() else 0,
                role=self.role_combo.get().lower(),
                activity="pending"
            )
            messagebox.showinfo("Thành công", "Thêm nhân viên thành công")
            self.load_employees()
            self.clear_inputs()
        except ValueError:
            messagebox.showerror("Lỗi", "Năm sinh phải là số nguyên")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm nhân viên: {str(e)}")

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
            # Update role separately
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
            messagebox.showinfo("Thành công", "Đã duyệt tài khoản")
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
            messagebox.showinfo("Thành công", "Đã từ chối tài khoản")
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
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.gender_combo.set("MALE")
        self.role_combo.set("Employee")