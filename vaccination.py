import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controller.vaccination_controller import VaccinationController
from controller.animals_controller import AnimalsController
from datetime import datetime

class VaccinationManagement:
    def __init__(self, parent):
        self.parent = parent
        self.vacc_controller = VaccinationController()
        self.animals_controller = AnimalsController()
        self.vaccinations_data = []  # Store vaccination records
        self.batches_data = []  # Store batch data for ComboBox
        self.batch_id_map = {}  # Map display strings to batch_id
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện cho quản lý tiêm phòng"""
        # Main frame
        main_frame = ctk.CTkFrame(self.parent, fg_color="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_frame,
            text="QUẢN LÝ TIÊM PHÒNG",
            font=("Arial", 24, "bold"),
            text_color="#2e7a84"
        ).pack(pady=20)

        # Controls frame
        controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=10)

        button_config = {
            "fg_color": "#2e7a84",
            "hover_color": "#256b73",
            "width": 150,
            "height": 35,
            "font": ("Arial", 13)
        }

        ctk.CTkButton(
            controls_frame,
            text="Thêm tiêm phòng",
            command=self.open_add_vaccination_window,
            **button_config
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            controls_frame,
            text="Sửa tiêm phòng",
            command=self.open_edit_vaccination_window,
            **button_config
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            controls_frame,
            text="Xóa tiêm phòng",
            command=self.delete_selected_vaccination,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=150,
            height=35,
            font=("Arial", 13)
        ).pack(side="left", padx=10)

        # Vaccinations table
        table_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, pady=15)

        ctk.CTkLabel(
            table_frame,
            text="Danh sách tiêm phòng",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        ).pack(pady=10)

        columns = ("ID", "ID Vật nuôi", "Loại vaccine", "Ngày tiêm", "Ghi chú")
        self.vaccinations_tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.vaccinations_tree.heading(col, text=col)
            self.vaccinations_tree.column(col, width=120)
        self.vaccinations_tree.pack(fill="both", expand=True)

        # Style for Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.vaccinations_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.vaccinations_tree.configure(yscrollcommand=scrollbar.set)

        # Load initial data
        self.load_vaccinations()

    def load_vaccinations(self):
        """Tải danh sách tiêm phòng"""
        for item in self.vaccinations_tree.get_children():
            self.vaccinations_tree.delete(item)

        self.vaccinations_data = self.vacc_controller.get_vaccinations_list()
        for vacc in self.vaccinations_data:
            self.vaccinations_tree.insert("", "end", values=(
                vacc['vaccination_id'],
                vacc['batch_id'],
                vacc['vaccine_type'],
                vacc['vaccination_date'],
                vacc['notes'] or ""
            ))

    def get_batch_ids(self):
        """Lấy danh sách ID bầy chưa xuất chuồng với định dạng batch_id - species - import_date"""
        self.batches_data = self.animals_controller.get_batches_list()
        self.batch_id_map = {}
        display_list = []
        for batch in self.batches_data:
            if not batch['export_date']:
                display_str = f"{batch['batch_id']} - {batch['species']} - {batch['import_date']}"
                self.batch_id_map[display_str] = str(batch['batch_id'])
                display_list.append(display_str)
        return display_list if display_list else [""]

    def create_vaccination_form(self, window, title, values=None):
        """Tạo form nhập liệu cho tiêm phòng với layout ngang"""
        window.title(title)
        window.geometry("450x300")

        entries = {}
        fields = [
            ("ID Vật nuôi:", "batch_id"),
            ("Loại vaccine:", "vaccine_type"),
            ("Ngày tiêm:", "vaccination_date"),
            ("Ghi chú:", "notes")
        ]

        form_frame = ctk.CTkFrame(window, fg_color="transparent")
        form_frame.pack(pady=20, padx=20, fill="x")

        for label_text, field in fields:
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)

            label = ctk.CTkLabel(
                row_frame,
                text=label_text,
                font=("Arial", 14),
                width=150,
                anchor="w"
            )
            label.pack(side="left")

            if field == "batch_id":
                entry = ctk.CTkComboBox(
                    row_frame,
                    values=self.get_batch_ids(),
                    width=250,
                    font=("Arial", 12)
                )
                if values and field in values:
                    # Find the display string for the batch_id
                    selected_batch_id = str(values[field])
                    for display_str, batch_id in self.batch_id_map.items():
                        if batch_id == selected_batch_id:
                            entry.set(display_str)
                            break
                    else:
                        entry.set("")
                elif entry.get() == "":
                    entry.set("")  # Default to empty if no batches
            else:
                entry = ctk.CTkEntry(row_frame, width=200, font=("Arial", 12))
                if field == "vaccination_date" and not values:
                    entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
                elif values and field in values:
                    entry.insert(0, values[field] or "")
            entry.pack(side="left")
            entries[field] = entry

        return entries

    def open_add_vaccination_window(self):
        """Mở cửa sổ thêm tiêm phòng"""
        add_window = ctk.CTkToplevel(self.parent)
        entries = self.create_vaccination_form(add_window, "Thêm tiêm phòng")

        def save_vaccination():
            try:
                batch_display = entries["batch_id"].get()
                vaccine_type = entries["vaccine_type"].get().strip()
                vaccination_date = entries["vaccination_date"].get()
                notes = entries["notes"].get()

                if not batch_display or not vaccine_type or not vaccination_date:
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                    return
                if batch_display == "":
                    messagebox.showerror("Lỗi", "Không có bầy nào để chọn!")
                    return
                if len(vaccine_type) > 100:
                    messagebox.showerror("Lỗi", "Loại vaccine không được vượt quá 100 ký tự!")
                    return

                batch_id = self.batch_id_map.get(batch_display)
                if not batch_id:
                    messagebox.showerror("Lỗi", "ID bầy không hợp lệ!")
                    return

                self.vacc_controller.add_vaccination(batch_id, vaccine_type, vaccination_date, notes)
                self.load_vaccinations()
                add_window.destroy()
                messagebox.showinfo("Thành công", "Đã thêm lịch sử tiêm phòng!")
            except ValueError as ve:
                messagebox.showerror("Lỗi", f"Lỗi giá trị: {str(ve)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")

        ctk.CTkButton(
            add_window,
            text="Lưu",
            command=save_vaccination,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=150,
            height=35,
            font=("Arial", 13)
        ).pack(pady=20)

    def open_edit_vaccination_window(self):
        """Mở cửa sổ chỉnh sửa tiêm phòng"""
        selected_item = self.vaccinations_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một lịch sử tiêm phòng để chỉnh sửa!")
            return

        item = self.vaccinations_tree.item(selected_item)
        values = item["values"]
        form_values = {
            "batch_id": values[1],
            "vaccine_type": values[2],
            "vaccination_date": values[3],
            "notes": values[4]
        }

        edit_window = ctk.CTkToplevel(self.parent)
        entries = self.create_vaccination_form(edit_window, "Sửa tiêm phòng", form_values)

        def update_vaccination():
            try:
                batch_display = entries["batch_id"].get()
                vaccine_type = entries["vaccine_type"].get().strip()
                vaccination_date = entries["vaccination_date"].get()
                notes = entries["notes"].get()

                if not batch_display or not vaccine_type or not vaccination_date:
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                    return
                if batch_display == "":
                    messagebox.showerror("Lỗi", "Không có bầy nào để chọn!")
                    return
                if len(vaccine_type) > 100:
                    messagebox.showerror("Lỗi", "Loại vaccine không được vượt quá 100 ký tự!")
                    return

                batch_id = self.batch_id_map.get(batch_display)
                if not batch_id:
                    messagebox.showerror("Lỗi", "ID bầy không hợp lệ!")
                    return

                self.vacc_controller.update_vaccination(values[0], batch_id, vaccine_type, vaccination_date, notes)
                self.load_vaccinations()
                edit_window.destroy()
                messagebox.showinfo("Thành công", "Đã cập nhật lịch sử tiêm phòng!")
            except ValueError as ve:
                messagebox.showerror("Lỗi", f"Lỗi giá trị: {str(ve)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

        ctk.CTkButton(
            edit_window,
            text="Cập nhật",
            command=update_vaccination,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=150,
            height=35,
            font=("Arial", 13)
        ).pack(pady=20)

    def delete_selected_vaccination(self):
        """Xóa lịch sử tiêm phòng đã chọn"""
        selected_item = self.vaccinations_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một lịch sử tiêm phòng để xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lịch sử tiêm phòng này?"):
            item = self.vaccinations_tree.item(selected_item)
            vaccination_id = item["values"][0]
            try:
                self.vacc_controller.delete_vaccination(vaccination_id)
                self.load_vaccinations()
                messagebox.showinfo("Thành công", "Đã xóa lịch sử tiêm phòng!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")