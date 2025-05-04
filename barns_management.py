import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as messagebox
from controller.barns_controller import BarnsController

class BarnManagement:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.controller = BarnsController()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.setup_ui()
        self.load_barns()

    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent_frame, fg_color="#ffffff", corner_radius=12)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header frame
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="#ffffff", corner_radius=8)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 20))

        # Title
        ctk.CTkLabel(
            self.header_frame,
            text="Quản lý chuồng nuôi",
            font=("Arial", 26, "bold"),
            text_color="#1a5f7a"
        ).pack(side="left", padx=15, pady=10)

        # Content frame (split layout)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # Left frame (inputs and buttons) - fixed width at 400
        self.left_frame = ctk.CTkFrame(self.content_frame, fg_color="#f8f9fa", corner_radius=10, border_width=1, border_color="#e9ecef", width=400)
        self.left_frame.pack(side="left", fill="y", padx=(0, 15), pady=10, ipadx=10, ipady=10)
        self.left_frame.pack_propagate(False)

        # Right frame (barn list)
        self.right_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(15, 0), pady=10)

        # Input fields frame
        self.inputs_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.inputs_frame.pack(pady=15, padx=15, fill="x")

        # Input fields configuration
        self.barns_name_entry = ctk.CTkEntry(self.inputs_frame, width=220, font=("Arial", 13), placeholder_text="Tên chuồng", corner_radius=6)
        self.batch_id_combo = ctk.CTkComboBox(self.inputs_frame, width=220, font=("Arial", 13), corner_radius=6, state="readonly")

        # Populate batch_id dropdown
        try:
            batch_ids = self.controller.get_batch_ids_for_dropdown()
            self.batch_id_combo.configure(values=batch_ids)
            self.batch_id_combo.set("")  # Default to empty
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy danh sách ID đàn: {str(e)}")

        input_fields = [
            ("Tên chuồng:", self.barns_name_entry),
            ("ID đàn vật nuôi:", self.batch_id_combo),
        ]

        for label_text, widget in input_fields:
            ctk.CTkLabel(self.inputs_frame, text=label_text, font=("Arial", 14, "bold"), text_color="#343a40").pack(anchor="w", padx=5, pady=3)
            widget.pack(pady=6, padx=5, fill="x")

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=20, padx=15, fill="x")

        # Action buttons
        self.add_button = ctk.CTkButton(
            self.buttons_frame,
            text="Thêm",
            command=self.add_barn,
            fg_color="#1a5f7a",
            hover_color="#134b60",
            width=120,
            height=36,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#134b60"
        )
        self.add_button.pack(side="left", padx=5)

        self.update_button = ctk.CTkButton(
            self.buttons_frame,
            text="Cập nhật",
            command=self.update_barn,
            fg_color="#17a2b8",
            hover_color="#138496",
            width=120,
            height=36,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#117a8b"
        )
        self.update_button.pack(side="left", padx=5)

        self.delete_button = ctk.CTkButton(
            self.buttons_frame,
            text="Xóa",
            command=self.delete_barn,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=120,
            height=36,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#bd2130"
        )
        self.delete_button.pack(side="left", padx=5)

        # Barn list frame
        self.barn_list_frame = ctk.CTkFrame(self.right_frame, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#e9ecef")
        self.barn_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header table and search
        self.header_table_frame = ctk.CTkFrame(self.barn_list_frame, fg_color="transparent")
        self.header_table_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.header_table_text = ctk.CTkLabel(
            self.header_table_frame,
            text="Danh sách chuồng nuôi",
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
            placeholder_text="Tìm theo ID hoặc tên chuồng...",
            corner_radius=6,
            border_width=1,
            border_color="#ced4da"
        )
        self.search_entry.pack(side="left", padx=(0, 5))

        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Tìm kiếm",
            command=self.search_barn,
            fg_color="#1a5f7a",
            hover_color="#134b60",
            width=120,
            height=36,
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
            width=120,
            height=36,
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
        columns = ("ID", "Tên chuồng", "ID đàn", "ID Con vật", "Số lượng")
        self.tree = ttk.Treeview(self.barn_list_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Set column headings and widths
        column_widths = {"ID": 80, "Tên chuồng": 200, "ID đàn": 100, "ID Con vật": 100, "Số lượng": 100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.barn_list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_barn_select)

    def load_barns(self):
        """Load barn data into the Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            barns = self.controller.get_all_barns()
            for barn in barns:
                self.tree.insert("", "end", values=(
                    barn['barn_id'],
                    barn['barns_name'],
                    barn['batch_id'] or '',
                    barn['animal_id'] or '',
                    barn['quantity'] or ''
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải danh sách chuồng: {str(e)}")

    def on_barn_select(self, event):
        """Populate input fields when a barn is selected"""
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            values = item['values']
            self.clear_inputs()
            self.barns_name_entry.insert(0, values[1])
            batch_id = str(values[2]) if values[2] else ""
            if batch_id:
                for option in self.batch_id_combo._values:
                    if option.startswith(f"{batch_id} - "):
                        self.batch_id_combo.set(option)
                        break
                else:
                    self.batch_id_combo.set("")
            else:
                self.batch_id_combo.set("")

    def search_barn(self):
        """Search barns by ID or name"""
        search_term = self.search_entry.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            barns = self.controller.get_all_barns()
            for barn in barns:
                barn_id = str(barn['barn_id']).lower()
                barns_name = barn['barns_name'].lower()
                if search_term in barn_id or search_term in barns_name:
                    self.tree.insert("", "end", values=(
                        barn['barn_id'],
                        barn['barns_name'],
                        barn['batch_id'] or '',
                        barn['animal_id'] or '',
                        barn['quantity'] or ''
                    ))
            if not self.tree.get_children():
                messagebox.showinfo("Kết quả", "Không tìm thấy chuồng phù hợp.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tìm kiếm: {str(e)}")

    def clear_search(self):
        """Clear search entry and reload all barns"""
        self.search_entry.delete(0, "end")
        self.load_barns()

    def add_barn(self):
        """Add a new barn"""
        barns_name = self.barns_name_entry.get().strip()
        batch_display = self.batch_id_combo.get().strip()

        if not barns_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên chuồng!")
            return

        try:
            batch_id = int(batch_display.split(" - ")[0]) if batch_display else None
            self.controller.add_barn(barns_name, batch_id)
            messagebox.showinfo("Thành công", "Thêm chuồng nuôi thành công")
            self.load_barns()
            self.clear_inputs()
            batch_ids = self.controller.get_batch_ids_for_dropdown()
            self.batch_id_combo.configure(values=batch_ids)
            self.batch_id_combo.set("")
        except ValueError:
            messagebox.showerror("Lỗi", "ID đàn không hợp lệ")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")

    def update_barn(self):
        """Update selected barn's information"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn chuồng để cập nhật")
            return

        barns_name = self.barns_name_entry.get().strip()
        batch_display = self.batch_id_combo.get().strip()

        if not barns_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên chuồng!")
            return

        try:
            barn_id = self.tree.item(selected_item)['values'][0]
            batch_id = int(batch_display.split(" - ")[0]) if batch_display else None
            self.controller.update_barn(barn_id, barns_name, batch_id)
            messagebox.showinfo("Thành công", "Cập nhật chuồng nuôi thành công")
            self.load_barns()
            self.clear_inputs()
            batch_ids = self.controller.get_batch_ids_for_dropdown()
            self.batch_id_combo.configure(values=batch_ids)
            self.batch_id_combo.set("")
        except ValueError:
            messagebox.showerror("Lỗi", "ID đàn không hợp lệ")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

    def delete_barn(self):
        """Delete selected barn"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn chuồng để xóa")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa chuồng này?"):
            try:
                barn_id = self.tree.item(selected_item)['values'][0]
                self.controller.delete_barn(barn_id)
                messagebox.showinfo("Thành công", "Xóa chuồng nuôi thành công")
                self.load_barns()
                self.clear_inputs()
                batch_ids = self.controller.get_batch_ids_for_dropdown()
                self.batch_id_combo.configure(values=batch_ids)
                self.batch_id_combo.set("")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")

    def clear_inputs(self):
        """Clear all input fields"""
        self.barns_name_entry.delete(0, "end")
        self.batch_id_combo.set("")