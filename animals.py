import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from controller.animals_controller import AnimalsController
from datetime import datetime, date

class PetManagement:
    def __init__(self, parent):
        self.parent = parent
        self.controller = AnimalsController()
        self.animals_data = []  # Store animals data
        self.batches_data = []  # Store batches data
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập giao diện người dùng cho quản lý vật nuôi và đàn"""
        main_frame = ctk.CTkFrame(self.parent, fg_color="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Title (aligned to the left)
        ctk.CTkLabel(
            main_frame,
            text="QUẢN LÝ VẬT NUÔI VÀ ĐÀN",
            font=("Arial", 20, "bold"),
            text_color="#2e7a84",
            anchor="w"
        ).pack(fill="x", padx=10, pady=5)

        # Container for side-by-side sections
        container_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        container_frame.pack(fill="both", expand=True)

        # Left section: Animals
        animals_frame = ctk.CTkFrame(container_frame, fg_color="#ffffff")
        animals_frame.pack(side="left", fill="both", expand=True, padx=5)

        # Right section: Batches and Export History
        batches_frame = ctk.CTkFrame(container_frame, fg_color="#ffffff")
        batches_frame.pack(side="left", fill="both", expand=True, padx=5)

        # Setup UI for each section
        self.setup_animals_section(animals_frame)
        self.setup_batches_section(batches_frame)

    def setup_animals_section(self, frame):
        """Thiết lập giao diện cho phần Quản Lý Vật Nuôi"""
        # Search frame
        search_frame = ctk.CTkFrame(frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5, padx=10)
        ctk.CTkLabel(search_frame, text="Tìm theo loài:", font=("Arial", 12)).pack(side="left")
        self.animals_search_entry = ctk.CTkEntry(search_frame, width=150, placeholder_text="Tên loài hoặc ID")
        self.animals_search_entry.pack(side="left", padx=5)
        self.animals_search_entry.bind("<KeyRelease>", self.search_animals)

        # Buttons frame (horizontal, aligned right)
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=5, anchor="e")

        ctk.CTkButton(
            buttons_frame,
            text="Thêm",
            command=self.add_animal_directly,  # Thay đổi để sử dụng trực tiếp Entry
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Sửa",
            command=self.edit_animal_directly,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Xóa",
            command=self.delete_selected_animal,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=100
        ).pack(side="left", padx=5)

        # Input frame
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=5, padx=10)

        fields = [
            ("Loài:", "", "species", False),
            ("Mô tả:", "", "description", False)
        ]

        self.animals_entries = {}
        for label_text, default_value, field, readonly in fields:
            field_frame = ctk.CTkFrame(input_frame)
            field_frame.pack(side="left", padx=5)
            ctk.CTkLabel(field_frame, text=label_text, font=("Arial", 12)).pack()
            entry = ctk.CTkEntry(field_frame, width=150)
            entry.insert(0, default_value)
            if readonly:
                entry.configure(state="readonly")
            entry.pack()
            self.animals_entries[field] = entry

        # Table frame
        table_frame = ctk.CTkFrame(frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, pady=5, padx=10)

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
        columns = ("ID", "Loài", "Tổng số lượng", "Mô tả")
        self.animals_tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.animals_tree.pack(fill="both", expand=True, padx=10, pady=5)

        column_widths = {"ID": 80, "Loài": 150, "Tổng số lượng": 100, "Mô tả": 150}
        for col in columns:
            self.animals_tree.heading(col, text=col)
            self.animals_tree.column(col, width=column_widths.get(col, 100), anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.animals_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.animals_tree.configure(yscrollcommand=scrollbar.set)

        # Bind selection event
        self.animals_tree.bind("<<TreeviewSelect>>", self.on_animal_select)

        # Load initial data
        self.load_animals()

    def setup_batches_section(self, frame):
        """Thiết lập giao diện cho phần Quản Lý Đàn và Lịch Sử Xuất Chuồng"""
        # Batches section
        batches_frame = ctk.CTkFrame(frame, fg_color="#ffffff")
        batches_frame.pack(fill="both", expand=False, padx=10, pady=5)  # Limit expansion

        # Search frame
        search_frame = ctk.CTkFrame(batches_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=5, padx=10)

        # Import date search
        ctk.CTkLabel(search_frame, text="Ngày nhập:", font=("Arial", 12)).pack(side="left")
        self.batches_date_search = ctk.CTkEntry(search_frame, width=150, placeholder_text="YYYY-MM-DD")
        self.batches_date_search.pack(side="left", padx=5)
        self.batches_date_search.bind("<KeyRelease>", self.search_batches)

        # Buttons frame (horizontal, aligned right)
        buttons_frame = ctk.CTkFrame(batches_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=5, anchor="e")

        ctk.CTkButton(
            buttons_frame,
            text="Thêm",
            command=self.add_batch_directly,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Sửa",
            command=self.edit_batch_directly,
            fg_color="#2e7a84",
            hover_color="#256b73",
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Xuất chuồng",
            command=self.export_batch,
            fg_color="#db4437",
            hover_color="#c13b31",
            width=100
        ).pack(side="left", padx=5)

        # Input frame
        input_frame = ctk.CTkFrame(batches_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=5, padx=10)

        fields = [
            ("Loài:", "", "animal_id", False),
            ("Ngày nhập:", datetime.now().strftime("%Y-%m-%d"), "import_date", False),
            ("Số lượng:", "", "quantity", False),
            ("Cân nặng TB:", "", "average_weight", False)
        ]

        self.batches_entries = {}
        for label_text, default_value, field, readonly in fields:
            field_frame = ctk.CTkFrame(input_frame)
            field_frame.pack(side="left", padx=5)
            ctk.CTkLabel(field_frame, text=label_text, font=("Arial", 12)).pack()
            if field == "animal_id":
                entry = ctk.CTkComboBox(
                    field_frame,
                    values=self.get_species(),
                    width=150,
                    state="readonly"
                )
                entry.set("")
            else:
                entry = ctk.CTkEntry(field_frame, width=150)
                entry.insert(0, default_value)
                if readonly:
                    entry.configure(state="readonly")
            entry.pack()
            self.batches_entries[field] = entry

        # Batches table frame
        batches_table_frame = ctk.CTkFrame(batches_frame, fg_color="transparent")
        batches_table_frame.pack(fill="both", expand=True, pady=5, padx=10)

        # Treeview setup
        batches_columns = ("ID", "Loài", "Ngày nhập", "Số lượng", "Cân nặng TB")
        self.batches_tree = ttk.Treeview(batches_table_frame, columns=batches_columns, show="headings", style="Custom.Treeview")
        self.batches_tree.pack(fill="both", expand=True, padx=10, pady=5)

        batches_column_widths = {"ID": 80, "Loài": 150, "Ngày nhập": 120, "Số lượng": 100, "Cân nặng TB": 100}
        for col in batches_columns:
            self.batches_tree.heading(col, text=col)
            self.batches_tree.column(col, width=batches_column_widths.get(col, 100), anchor="center")

        # Scrollbar
        batches_scrollbar = ttk.Scrollbar(batches_table_frame, orient="vertical", command=self.batches_tree.yview)
        batches_scrollbar.pack(side="right", fill="y")
        self.batches_tree.configure(yscrollcommand=batches_scrollbar.set)

        # Bind selection event
        self.batches_tree.bind("<<TreeviewSelect>>", self.on_batch_select)

        # Export history section
        export_frame = ctk.CTkFrame(frame, fg_color="#ffffff")
        export_frame.pack(fill="both", expand=True, padx=10, pady=0)  # Reduced pady

        ctk.CTkLabel(
            export_frame,
            text="Lịch sử xuất chuồng",
            font=("Arial", 16, "bold"),
            text_color="#343a40"
        ).pack(anchor="w", padx=10, pady=5)

        # Export table frame
        export_table_frame = ctk.CTkFrame(export_frame, fg_color="transparent")
        export_table_frame.pack(fill="both", expand=True, pady=5, padx=10)

        # Treeview setup
        export_columns = ("ID", "Loài", "Ngày nhập", "Ngày xuất", "Số lượng", "Cân nặng TB")
        self.export_tree = ttk.Treeview(export_table_frame, columns=export_columns, show="headings", style="Custom.Treeview")
        self.export_tree.pack(fill="both", expand=True, padx=10, pady=5)

        export_column_widths = {"ID": 80, "Loài": 150, "Ngày nhập": 120, "Ngày xuất": 120, "Số lượng": 100, "Cân nặng TB": 100}
        for col in export_columns:
            self.export_tree.heading(col, text=col)
            self.export_tree.column(col, width=export_column_widths.get(col, 100), anchor="center")

        # Scrollbar
        export_scrollbar = ttk.Scrollbar(export_table_frame, orient="vertical", command=self.export_tree.yview)
        export_scrollbar.pack(side="right", fill="y")
        self.export_tree.configure(yscrollcommand=export_scrollbar.set)

    def load_animals(self, data=None):
        """Tải danh sách loài và tổng số lượng"""
        for item in self.animals_tree.get_children():
            self.animals_tree.delete(item)

        if data is None:
            self.animals_data = self.controller.get_species_list()
            self.batches_data = self.controller.get_batches_list()
            data = self.animals_data

        for animal in data:
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

        # Refresh species dropdowns
        species_values = self.get_species()
        if hasattr(self, 'batches_entries'):
            self.batches_entries["animal_id"].configure(values=species_values)
        if hasattr(self, 'batches_species_search'):
            self.batches_species_search.configure(values=species_values)

    def load_batches(self, animal_id, data=None):
        """Tải danh sách đàn chưa xuất chuồng cho loài được chọn"""
        for item in self.batches_tree.get_children():
            self.batches_tree.delete(item)

        if data is None:
            batches = [batch for batch in self.batches_data if batch['animal_id'] == animal_id and not batch['export_date']]
        else:
            batches = data

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
            species = item["values"][1]
            description = item["values"][3]
            self.animals_entries["species"].delete(0, "end")
            self.animals_entries["species"].insert(0, species)
            self.animals_entries["description"].delete(0, "end")
            self.animals_entries["description"].insert(0, description)
            self.load_batches(animal_id)
            self.load_export_history(animal_id)
            # Clear batch entries and selection
            if hasattr(self, 'batches_entries'):
                self.batches_entries["animal_id"].set("")
                self.batches_entries["import_date"].delete(0, "end")
                self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
                self.batches_entries["quantity"].delete(0, "end")
                self.batches_entries["average_weight"].delete(0, "end")
            self.batches_tree.selection_remove(self.batches_tree.selection())
        else:
            self.animals_entries["species"].delete(0, "end")
            self.animals_entries["description"].delete(0, "end")
            if hasattr(self, 'batches_entries'):
                self.batches_entries["animal_id"].set("")
                self.batches_entries["import_date"].delete(0, "end")
                self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
                self.batches_entries["quantity"].delete(0, "end")
                self.batches_entries["average_weight"].delete(0, "end")
            self.batches_tree.delete(*self.batches_tree.get_children())
            self.export_tree.delete(*self.export_tree.get_children())
            self.batches_tree.selection_remove(self.batches_tree.selection())

    def on_batch_select(self, event):
        """Xử lý khi chọn một đàn"""
        selected_item = self.batches_tree.selection()
        if selected_item:
            item = self.batches_tree.item(selected_item)
            values = item["values"]
            batch_id = values[0]
            batch = next((b for b in self.batches_data if b['batch_id'] == batch_id), None)
            if batch:
                self.batches_entries["animal_id"].set(f"{batch['animal_id']} - {batch['species']}")
                self.batches_entries["import_date"].delete(0, "end")
                self.batches_entries["import_date"].insert(0, batch['import_date'])
                self.batches_entries["quantity"].delete(0, "end")
                self.batches_entries["quantity"].insert(0, batch['quantity'])
                self.batches_entries["average_weight"].delete(0, "end")
                self.batches_entries["average_weight"].insert(0, batch['average_weight'])
        else:
            self.batches_entries["animal_id"].set("")
            self.batches_entries["import_date"].delete(0, "end")
            self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.batches_entries["quantity"].delete(0, "end")
            self.batches_entries["average_weight"].delete(0, "end")

    def search_animals(self, event):
        """Tìm kiếm loài theo ID hoặc tên loài"""
        search_term = self.animals_search_entry.get().strip().lower()
        filtered_data = [
            animal for animal in self.animals_data
            if search_term in str(animal['animal_id']).lower() or search_term in animal['species'].lower()
        ]
        self.load_animals(filtered_data)

    def search_batches(self, event):
        """Tìm kiếm đàn theo ngày nhập"""
        selected_item = self.animals_tree.selection()
        if not selected_item:
            return

        item = self.animals_tree.item(selected_item)
        animal_id = item["values"][0]
        date_search = self.batches_date_search.get().strip().lower()

        filtered_data = [
            batch for batch in self.batches_data
            if batch['animal_id'] == animal_id and not batch['export_date']
        ]

        if date_search:
            filtered_data = [
                batch for batch in filtered_data
                if date_search in str(batch['import_date']).lower()
            ]

        self.load_batches(animal_id, filtered_data)

    def get_species(self):
        """Lấy danh sách loài cho dropdown"""
        try:
            species_list = [f"{animal['animal_id']} - {animal['species']}" for animal in self.animals_data]
            return species_list if species_list else [""]
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy danh sách loài: {str(e)}")
            return [""]

    def add_animal_directly(self):
        """Thêm loài trực tiếp từ các trường nhập liệu"""
        try:
            species = self.animals_entries["species"].get().strip()
            description = self.animals_entries["description"].get().strip()

            if not species:
                messagebox.showerror("Lỗi", "Vui lòng nhập tên loài!")
                return
            if len(species) > 100:
                messagebox.showerror("Lỗi", "Tên loài không được vượt quá 100 ký tự!")
                return

            self.controller.add_species(species, description)
            self.load_animals()
            self.animals_entries["species"].delete(0, "end")
            self.animals_entries["description"].delete(0, "end")
            self.batches_tree.delete(*self.batches_tree.get_children())
            self.export_tree.delete(*self.export_tree.get_children())
            self.batches_entries["animal_id"].set("")
            self.batches_entries["import_date"].delete(0, "end")
            self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.batches_entries["quantity"].delete(0, "end")
            self.batches_entries["average_weight"].delete(0, "end")
            self.batches_tree.selection_remove(self.batches_tree.selection())
            messagebox.showinfo("Thành công", "Đã thêm loài!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")

    def edit_animal_directly(self):
        """Chỉnh sửa loài trực tiếp từ các trường nhập liệu"""
        selected_item = self.animals_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một loài để chỉnh sửa!")
            return

        item = self.animals_tree.item(selected_item)
        animal_id = item["values"][0]
        try:
            species = self.animals_entries["species"].get().strip()
            description = self.animals_entries["description"].get().strip()

            if not species:
                messagebox.showerror("Lỗi", "Vui lòng nhập tên loài!")
                return
            if len(species) > 100:
                messagebox.showerror("Lỗi", "Tên loài không được vượt quá 100 ký tự!")
                return

            self.controller.update_animal(animal_id, species, description)
            self.load_animals()
            self.animals_entries["species"].delete(0, "end")
            self.animals_entries["description"].delete(0, "end")
            self.batches_tree.delete(*self.batches_tree.get_children())
            self.export_tree.delete(*self.export_tree.get_children())
            self.batches_entries["animal_id"].set("")
            self.batches_entries["import_date"].delete(0, "end")
            self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.batches_entries["quantity"].delete(0, "end")
            self.batches_entries["average_weight"].delete(0, "end")
            self.batches_tree.selection_remove(self.batches_tree.selection())
            messagebox.showinfo("Thành công", "Đã cập nhật loài!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

    def add_batch_directly(self):
        """Thêm đàn trực tiếp từ các trường nhập liệu"""
        try:
            animal_display = self.batches_entries["animal_id"].get()
            import_date_str = self.batches_entries["import_date"].get().strip()
            quantity = self.batches_entries["quantity"].get().strip()
            average_weight = self.batches_entries["average_weight"].get().strip()

            if not animal_display or not import_date_str or not quantity or not average_weight:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                return
            if animal_display == "":
                messagebox.showerror("Lỗi", "Không có loài nào để chọn!")
                return

            animal_id = int(animal_display.split(" - ")[0])
            import_date = date.fromisoformat(import_date_str)
            quantity = int(quantity)
            average_weight = float(average_weight)

            if quantity <= 0:
                messagebox.showerror("Lỗi", "Số lượng phải lớn hơn 0!")
                return
            if average_weight < 0:
                messagebox.showerror("Lỗi", "Cân nặng trung bình không được âm!")
                return
            if import_date > datetime.now().date():
                messagebox.showerror("Lỗi", "Ngày nhập không được trong tương lai!")
                return

            self.controller.add_batch(animal_id, import_date, quantity, average_weight, None)
            self.load_animals()
            self.load_batches(animal_id)
            self.load_export_history(animal_id)
            self.batches_entries["animal_id"].set("")
            self.batches_entries["import_date"].delete(0, "end")
            self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.batches_entries["quantity"].delete(0, "end")
            self.batches_entries["average_weight"].delete(0, "end")
            self.batches_tree.selection_remove(self.batches_tree.selection())
            messagebox.showinfo("Thành công", "Đã thêm đàn!")
        except ValueError as ve:
            if "invalid literal" in str(ve):
                messagebox.showerror("Lỗi", "Số lượng và cân nặng phải là số!")
            else:
                messagebox.showerror("Lỗi", "Ngày nhập không hợp lệ (định dạng: YYYY-MM-DD)!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")

    def edit_batch_directly(self):
        """Chỉnh sửa đàn trực tiếp từ các trường nhập liệu"""
        selected_item = self.batches_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một đàn để chỉnh sửa!")
            return

        item = self.batches_tree.item(selected_item)
        batch_id = item["values"][0]
        current_batch = next((batch for batch in self.batches_data if batch['batch_id'] == batch_id), None)
        if not current_batch:
            messagebox.showerror("Lỗi", "Không tìm thấy đàn được chọn!")
            return

        animal_id = current_batch['animal_id']
        try:
            animal_display = self.batches_entries["animal_id"].get()
            import_date_str = self.batches_entries["import_date"].get().strip()
            quantity = self.batches_entries["quantity"].get().strip()
            average_weight = self.batches_entries["average_weight"].get().strip()

            if not animal_display or not import_date_str or not quantity or not average_weight:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin bắt buộc!")
                return
            if animal_display == "":
                messagebox.showerror("Lỗi", "Không có loài nào để chọn!")
                return

            animal_id_new = int(animal_display.split(" - ")[0])
            import_date = date.fromisoformat(import_date_str)
            quantity = int(quantity)
            average_weight = float(average_weight)

            if quantity <= 0:
                messagebox.showerror("Lỗi", "Số lượng phải lớn hơn 0!")
                return
            if average_weight < 0:
                messagebox.showerror("Lỗi", "Cân nặng trung bình không được âm!")
                return
            if import_date > datetime.now().date():
                messagebox.showerror("Lỗi", "Ngày nhập không được trong tương lai!")
                return

            self.controller.update_batch(batch_id, import_date, quantity, average_weight, None)
            self.load_animals()
            self.load_batches(animal_id_new)
            self.load_export_history(animal_id_new)
            self.batches_entries["animal_id"].set("")
            self.batches_entries["import_date"].delete(0, "end")
            self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.batches_entries["quantity"].delete(0, "end")
            self.batches_entries["average_weight"].delete(0, "end")
            self.batches_tree.selection_remove(self.batches_tree.selection())
            messagebox.showinfo("Thành công", "Đã cập nhật đàn!")
        except ValueError as ve:
            if "invalid literal" in str(ve):
                messagebox.showerror("Lỗi", "Số lượng và cân nặng phải là số!")
            else:
                messagebox.showerror("Lỗi", "Ngày nhập không hợp lệ (định dạng: YYYY-MM-DD)!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

    def export_batch(self):
        """Xuất chuồng đàn đã chọn"""
        selected_item = self.batches_tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một đàn để xuất chuồng!")
            return

        item = self.batches_tree.item(selected_item)
        batch_id = item["values"][0]
        current_batch = next((batch for batch in self.batches_data if batch['batch_id'] == batch_id), None)
        if not current_batch:
            messagebox.showerror("Lỗi", "Không tìm thấy đàn được chọn!")
            return

        animal_id = current_batch['animal_id']
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xuất chuồng đàn này?"):
            try:
                import_date = current_batch['import_date']
                quantity = current_batch['quantity']
                average_weight = current_batch['average_weight']
                export_date = datetime.now().strftime('%Y-%m-%d')

                self.controller.update_batch(batch_id, import_date, quantity, average_weight, export_date)
                self.load_animals()
                self.load_batches(animal_id)
                self.load_export_history(animal_id)
                self.batches_entries["animal_id"].set("")
                self.batches_entries["import_date"].delete(0, "end")
                self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
                self.batches_entries["quantity"].delete(0, "end")
                self.batches_entries["average_weight"].delete(0, "end")
                self.batches_tree.selection_remove(self.batches_tree.selection())
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
                self.controller.delete_animal(animal_id)
                self.load_animals()
                self.batches_tree.delete(*self.batches_tree.get_children())
                self.export_tree.delete(*self.export_tree.get_children())
                self.animals_entries["species"].delete(0, "end")
                self.animals_entries["description"].delete(0, "end")
                self.batches_entries["animal_id"].set("")
                self.batches_entries["import_date"].delete(0, "end")
                self.batches_entries["import_date"].insert(0, datetime.now().strftime("%Y-%m-%d"))
                self.batches_entries["quantity"].delete(0, "end")
                self.batches_entries["average_weight"].delete(0, "end")
                self.batches_tree.selection_remove(self.batches_tree.selection())
                messagebox.showinfo("Thành công", "Đã xóa loài!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")