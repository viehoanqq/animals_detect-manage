import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controller.animals_controller import AnimalsController
from datetime import datetime

class PetManagement:
    def __init__(self, parent):
        self.parent = parent
        self.controller = AnimalsController()
        self.animals_data = []  # Store animals data
        self.batches_data = []  # Store batches data
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện người dùng cho quản lý vật nuôi và đàn"""
        # Main frame
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(
            main_frame,
            text="QUẢN LÝ VẬT NUÔI",
            font=("Arial", 24, "bold"),
            text_color="#2e7a84"
        ).pack(pady=20)

        # Split main frame into two panels
        left_panel = ctk.CTkFrame(main_frame, width=450, fg_color="#f5f5f5")
        left_panel.pack(side="left", fill="both", padx=15, pady=15, expand=True)

        right_panel = ctk.CTkFrame(main_frame, fg_color="#f5f5f5")
        right_panel.pack(side="right", fill="both", padx=15, pady=15, expand=True)

        # Left panel: Animals management
        # Title
        ctk.CTkLabel(
            left_panel,
            text="Danh sách vật nuôi",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        ).pack(pady=10)

        # Controls for animals
        animals_controls = ctk.CTkFrame(left_panel, fg_color="transparent")
        animals_controls.pack(fill="x", pady=10)

        button_config = {
            "fg_color": "#2e7a84",
            "hover_color": "#256b73",
            "width": 150,
            "height": 35,
            "font": ("Arial", 13)
        }

        ctk.CTkButton(
            animals_controls,
            text="Thêm loài",
            command=self.open_add_animal_window,
            **button_config
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            animals_controls,
            text="Xóa loài",
            command=self.delete_selected_animal,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=150,
            height=35,
            font=("Arial", 13)
        ).pack(side="left", padx=10)

        # Animals table
        animals_table_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        animals_table_frame.pack(fill="both", expand=True, pady=15)

        animals_columns = ("ID", "Loài", "Tổng số lượng", "Mô tả")
        self.animals_tree = ttk.Treeview(animals_table_frame, columns=animals_columns, show="headings", style="Treeview")
        for col in animals_columns:
            self.animals_tree.heading(col, text=col)
            self.animals_tree.column(col, width=120)
        self.animals_tree.pack(fill="both", expand=True)

        # Style for Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

        # Scrollbar for animals
        animals_scrollbar = ttk.Scrollbar(animals_table_frame, orient="vertical", command=self.animals_tree.yview)
        animals_scrollbar.pack(side="right", fill="y")
        self.animals_tree.configure(yscrollcommand=animals_scrollbar.set)

        # Bind selection event
        self.animals_tree.bind("<<TreeviewSelect>>", self.on_animal_select)

        # Right panel: Batches management
        # Title
        ctk.CTkLabel(
            right_panel,
            text="Danh sách đàn",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        ).pack(pady=10)

        # Controls for batches
        batches_controls = ctk.CTkFrame(right_panel, fg_color="transparent")
        batches_controls.pack(fill="x", pady=10)

        ctk.CTkButton(
            batches_controls,
            text="Thêm đàn",
            command=self.open_add_batch_window,
            **button_config
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            batches_controls,
            text="Chỉnh sửa",
            command=self.open_edit_batch_window,
            **button_config
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            batches_controls,
            text="Xuất chuồng",
            command=self.export_batch,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=150,
            height=35,
            font=("Arial", 13)
        ).pack(side="left", padx=10)

        # Batches table
        batches_table_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        batches_table_frame.pack(fill="both", expand=True, pady=5)

        batches_columns = ("ID", "Loài", "Ngày nhập", "Số lượng", "Cân nặng TB")
        self.batches_tree = ttk.Treeview(batches_table_frame, columns=batches_columns, show="headings", style="Treeview")
        for col in batches_columns:
            self.batches_tree.heading(col, text=col)
            self.batches_tree.column(col, width=120)
        self.batches_tree.pack(fill="both", expand=True)

        # Scrollbar for batches
        batches_scrollbar = ttk.Scrollbar(batches_table_frame, orient="vertical", command=self.batches_tree.yview)
        batches_scrollbar.pack(side="right", fill="y")
        self.batches_tree.configure(yscrollcommand=batches_scrollbar.set)

        # Export history table
        export_history_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        export_history_frame.pack(fill="both", expand=True, pady=5)

        ctk.CTkLabel(
            export_history_frame,
            text="Lịch sử xuất chuồng",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        ).pack(pady=10)

        export_columns = ("ID", "Loài", "Ngày nhập", "Ngày xuất", "Số lượng", "Cân nặng TB")
        self.export_tree = ttk.Treeview(export_history_frame, columns=export_columns, show="headings", style="Treeview")
        for col in export_columns:
            self.export_tree.heading(col, text=col)
            self.export_tree.column(col, width=120)
        self.export_tree.pack(fill="both", expand=True)

        # Scrollbar for export history
        export_scrollbar = ttk.Scrollbar(export_history_frame, orient="vertical", command=self.export_tree.yview)
        export_scrollbar.pack(side="right", fill="y")
        self.export_tree.configure(yscrollcommand=export_scrollbar.set)

        # Load initial data
        self.load_animals()

    def load_animals(self):
        """Tải danh sách loài và tổng số lượng"""
        for item in self.animals_tree.get_children():
            self.animals_tree.delete(item)

        self.animals_data = self.controller.get_species_list()
        self.batches_data = self.controller.get_batches_list()

        for animal in self.animals_data:
            total_quantity = sum(
                batch['quantity'] for batch in self.batches_data
                if batch['animal_id'] == animal['animal_id'] and not batch['export_date']
            )
            self.animals_tree.insert("", "end", values=(
                animal['animal_id'],
                animal['species'],
                total_quantity,
                animal['description'] or ""
            ))

    def load_batches(self, animal_id):
        """Tải danh sách đàn chưa xuất chuồng cho loài được chọn"""
        for item in self.batches_tree.get_children():
            self.batches_tree.delete(item)

        batches = [batch for batch in self.batches_data if batch['animal_id'] == animal_id and not batch['export_date']]
        for batch in batches:
            self.batches_tree.insert("", "end", values=(
                batch['batch_id'],
                batch['species'],
                batch['import_date'],
                batch['quantity'],
                batch['average_weight']
            ))

    def load_export_history(self, animal_id):
        """Tải danh sách đàn đã xuất chuồng cho loài được chọn"""
        for item in self.export_tree.get_children():
            self.export_tree.delete(item)

        exported_batches = [batch for batch in self.batches_data if batch['animal_id'] == animal_id and batch['export_date']]
        for batch in exported_batches:
            self.export_tree.insert("", "end", values=(
                batch['batch_id'],
                batch['species'],
                batch['import_date'],
                batch['export_date'],
                batch['quantity'],
                batch['average_weight']
            ))

    def on_animal_select(self, event):
        """Xử lý khi chọn một loài"""
        selected_item = self.animals_tree.selection()
        if selected_item:
            item = self.animals_tree.item(selected_item)
            animal_id = item["values"][0]
            self.load_batches(animal_id)
            self.load_export_history(animal_id)

    def create_animal_form(self, window, title, values=None):
        """Tạo form nhập liệu cho loài"""
        window.title(title)
        window.geometry("400x300")

        entries = {}
        fields = [
            ("Loài:", "species"),
            ("Mô tả:", "description")
        ]

        for label_text, field in fields:
            ctk.CTkLabel(window, text=label_text, font=("Arial", 14)).pack(pady=5)
            entry = ctk.CTkEntry(window, width=300, font=("Arial", 12))
            if values and field in values:
                entry.insert(0, values[field])
            entry.pack(pady=5)
            entries[field] = entry

        return entries

    def create_batch_form(self, window, title, animal_id, values=None):
        """Tạo form nhập liệu cho đàn"""
        window.title(title)
        window.geometry("400x400")

        entries = {}
        fields = [
            ("Ngày nhập (YYYY-MM-DD):", "import_date"),
            ("Số lượng:", "quantity"),
            ("Cân nặng trung bình:", "average_weight"),
            ("Ngày xuất (YYYY-MM-DD, để trống nếu chưa có):", "export_date")
        ]

        for label_text, field in fields:
            ctk.CTkLabel(window, text=label_text, font=("Arial", 14)).pack(pady=5)
            entry = ctk.CTkEntry(window, width=300, font=("Arial", 12))
            if field == "import_date" and not values:
                entry.insert(0, datetime.now().strftime('%Y-%m-%d'))  # Default to current date
            elif values and field in values:
                entry.insert(0, values[field])
            entry.pack(pady=5)
            entries[field] = entry

        return entries

    def open_add_animal_window(self):
        """Mở cửa sổ thêm loài"""
        add_window = ctk.CTkToplevel(self.parent)
        entries = self.create_animal_form(add_window, "Thêm loài")

        def save_animal():
            try:
                species = entries["species"].get()
                description = entries["description"].get()

                if not species:
                    messagebox.showerror("Lỗi", "Vui lòng nhập tên loài!")
                    return

                self.controller.add_species(species, description)
                self.load_animals()
                add_window.destroy()
                messagebox.showinfo("Thành công", "Đã thêm loài!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")

        ctk.CTkButton(
            add_window,
            text="Lưu",
            command=save_animal,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=150,
            height=35,
            font=("Arial", 13)
        ).pack(pady=20)

    def open_add_batch_window(self):
        """Mở cửa sổ thêm đàn"""
        selected_item = self.animals_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một loài trước!")
            return

        item = self.animals_tree.item(selected_item)
        animal_id = item["values"][0]

        add_window = ctk.CTkToplevel(self.parent)
        entries = self.create_batch_form(add_window, "Thêm đàn", animal_id)

        def save_batch():
            try:
                import_date = entries["import_date"].get()
                quantity = int(entries["quantity"].get())
                average_weight = float(entries["average_weight"].get())
                export_date = entries["export_date"].get() or None

                if not import_date or not quantity or not average_weight:
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                    return

                self.controller.add_batch(animal_id, import_date, quantity, average_weight, export_date)
                self.load_animals()
                self.load_batches(animal_id)
                self.load_export_history(animal_id)
                add_window.destroy()
                messagebox.showinfo("Thành công", "Đã thêm đàn!")
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng và cân nặng phải là số!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")

        ctk.CTkButton(
            add_window,
            text="Lưu",
            command=save_batch,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=150,
            height=35,
            font=("Arial", 13)
        ).pack(pady=20)

    def open_edit_batch_window(self):
        """Mở cửa sổ chỉnh sửa đàn"""
        selected_item = self.batches_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một đàn để chỉnh sửa!")
            return

        item = self.batches_tree.item(selected_item)
        values = item["values"]
        animal_id = next(batch['animal_id'] for batch in self.batches_data if batch['batch_id'] == values[0])
        form_values = {
            "import_date": values[2],
            "quantity": values[3],
            "average_weight": values[4],
            "export_date": ""
        }

        edit_window = ctk.CTkToplevel(self.parent)
        entries = self.create_batch_form(edit_window, "Chỉnh sửa đàn", animal_id, form_values)

        def update_batch():
            try:
                import_date = entries["import_date"].get()
                quantity = int(entries["quantity"].get())
                average_weight = float(entries["average_weight"].get())
                export_date = entries["export_date"].get() or None

                if not import_date or not quantity or not average_weight:
                    messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                    return

                self.controller.update_batch(values[0], import_date, quantity, average_weight, export_date)
                self.load_animals()
                self.load_batches(animal_id)
                self.load_export_history(animal_id)
                edit_window.destroy()
                messagebox.showinfo("Thành công", "Đã cập nhật đàn!")
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng và cân nặng phải là số!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

        ctk.CTkButton(
            edit_window,
            text="Cập nhật",
            command=update_batch,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=150,
            height=35,
            font=("Arial", 13)
        ).pack(pady=20)

    def export_batch(self):
        """Xuất chuồng đàn đã chọn"""
        selected_item = self.batches_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một đàn để xuất chuồng!")
            return

        item = self.batches_tree.item(selected_item)
        batch_id = item["values"][0]
        animal_id = next(batch['animal_id'] for batch in self.batches_data if batch['batch_id'] == batch_id)

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xuất chuồng đàn này?"):
            try:
                # Get current batch data
                current_batch = next(batch for batch in self.batches_data if batch['batch_id'] == batch_id)
                import_date = current_batch['import_date']
                quantity = current_batch['quantity']
                average_weight = current_batch['average_weight']
                export_date = datetime.now().strftime('%Y-%m-%d')  # Set export date to current date

                self.controller.update_batch(batch_id, import_date, quantity, average_weight, export_date)
                self.load_animals()  # Update total quantity in animals table
                self.load_batches(animal_id)  # Reload non-exported batches
                self.load_export_history(animal_id)  # Update export history
                messagebox.showinfo("Thành công", "Đã xuất chuồng đàn!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xuất chuồng: {str(e)}")

    def delete_selected_animal(self):
        """Xóa loài đã chọn"""
        selected_item = self.animals_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một loài để xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa loài này? (Sẽ xóa tất cả đàn liên quan)"):
            item = self.animals_tree.item(selected_item)
            animal_id = item["values"][0]
            try:
                # Delete all batches for this animal
                for batch in [b for b in self.batches_data if b['animal_id'] == animal_id]:
                    self.controller.delete_batch(batch['batch_id'])
                # Then delete the animal
                self.controller.delete_animal(animal_id)
                self.load_animals()
                self.batches_tree.delete(*self.batches_tree.get_children())
                self.export_tree.delete(*self.export_tree.get_children())
                messagebox.showinfo("Thành công", "Đã xóa loài!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")