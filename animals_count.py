import os
import sys
import customtkinter as ctk
from tkinter import ttk
from PIL import Image
import cv2
import numpy as np
from ultralytics import YOLO
import tkinter.messagebox as messagebox
from controller.barns_controller import BarnsController
from controller.animals_controller import AnimalsController
from controller.work_shifts_controller import WorkShiftsController
from datetime import datetime

class AnimalCounter:
    def __init__(self, parent_frame, user_id):
        self.parent_frame = parent_frame
        self.user_id = user_id
        self.model = YOLO(self.resource_path("runs/detect/train19/weights/best.pt"))
        self.barns_controller = BarnsController()
        self.animals_controller = AnimalsController()
        self.work_shifts_controller = WorkShiftsController()
        self.cow_count = 0
        self.pig_count = 0
        self.recognition_ratio = "N/A"
        self.cap = None  # Webcam capture object
        self.webcam_running = False  # Flag to control webcam loop
        self.tracks = {}  # Dictionary to store tracks of center points (ID -> list of (x, y))
        self.previous_centers = {}  # Store previous frame centers for tracking
        self.crossed_ids = set()  # Track IDs that have already crossed the line
        self.detected_count = 0  # Total detected count for animals crossing the line
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.setup_data()
        self.setup_ui()
    def resource_path(self,relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    def setup_data(self):
        try:
            self.barns = self.barns_controller.get_all_barns()
            self.batches = self.animals_controller.get_batches_list()
            self.shifts = self.work_shifts_controller.get_list()
            self.shift_options = ["Tạo ca mới"] + [f"Ca {shift['id']} - {shift['date']}" for shift in self.shifts]
            self.shift_id_map = {f"Ca {shift['id']} - {shift['date']}": shift['id'] for shift in self.shifts}
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {str(e)}")
            self.barns = []
            self.batches = []
            self.shifts = []
            self.shift_options = ["Tạo ca mới"]
            self.shift_id_map = {}

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
            text="Nhận diện và Lưu Ca Làm Việc (Webcam)",
            font=("Arial", 26, "bold"),
            text_color="#1a5f7a"
        ).pack(side="left", padx=15, pady=10)

        # Content frame (split layout)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # Left frame (inputs and buttons) - fixed width at 400
        self.left_frame = ctk.CTkFrame(self.content_frame, fg_color="#f8f9fa", corner_radius=10, border_width=1, border_color="#e9ecef", width=400)
        self.left_frame.pack(side="left", fill="y", padx=(0, 15), pady=10, ipadx=15, ipady=15)
        self.left_frame.pack_propagate(False)

        # Right frame (video and results)
        self.right_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(15, 0), pady=10)

        # Input fields frame
        self.inputs_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.inputs_frame.pack(pady=0, padx=0)

        # Input fields configuration
        now = datetime.now()
        self.shift_combo = ctk.CTkComboBox(self.inputs_frame, values=self.shift_options, width=220, font=("Arial", 13), corner_radius=6, state="readonly")
        self.shift_combo.set("Tạo ca mới")
        self.shift_combo.bind("<<ComboboxSelected>>", lambda e: self.update_shift_date(self.shift_combo.get()))

        self.shift_date_entry = ctk.CTkEntry(self.inputs_frame, width=220, font=("Arial", 13), placeholder_text="YYYY-MM-DD", corner_radius=6)
        self.shift_date_entry.insert(0, now.strftime("%Y-%m-%d"))

        barn_names = [barn['barns_name'] for barn in self.barns] if self.barns else ["Không có chuồng"]
        self.barn_combo = ctk.CTkComboBox(self.inputs_frame, values=barn_names, width=220, font=("Arial", 13), corner_radius=6, state="readonly")
        self.barn_combo.set(barn_names[0] if barn_names else "Không có chuồng")

        self.quantity_entry = ctk.CTkEntry(self.inputs_frame, width=220, font=("Arial", 13), placeholder_text="Số lượng nhận diện", corner_radius=6)

        input_fields = [
            ("Chọn ca:", self.shift_combo),
            ("Ngày ca:", self.shift_date_entry),
            ("Chuồng:", self.barn_combo),
            ("Số lượng nhận diện:", self.quantity_entry),
        ]

        for label_text, widget in input_fields:
            ctk.CTkLabel(self.inputs_frame, text=label_text, font=("Arial", 14, "bold"), text_color="#343a40").pack(anchor="w", padx=5, pady=3)
            widget.pack(pady=6, padx=5, fill="x")

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=(20, 10), padx=15, fill="x")

        # Action buttons
        self.start_button = ctk.CTkButton(
            self.buttons_frame,
            text="Bắt đầu webcam",
            command=self.start_webcam,
            fg_color="#1a5f7a",
            hover_color="#134b60",
            width=120,
            height=36,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#134b60"
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(
            self.buttons_frame,
            text="Dừng webcam",
            command=self.stop_webcam,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=120,
            height=36,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#bd2130"
        )
        self.stop_button.pack(side="left", padx=5)

        self.save_button = ctk.CTkButton(
            self.buttons_frame,
            text="Lưu ca",
            command=self.save_shift,
            fg_color="#17a2b8",
            hover_color="#138496",
            width=120,
            height=36,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            border_width=1,
            border_color="#117a8b"
        )
        self.save_button.pack(side="left", padx=5)

        # Right frame: Video and results
        self.image_frame = ctk.CTkFrame(self.right_frame, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#e9ecef")
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header for image section
        self.image_header_frame = ctk.CTkFrame(self.image_frame, fg_color="transparent")
        self.image_header_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            self.image_header_frame,
            text="Kết quả nhận diện",
            font=("Arial", 16, "bold"),
            text_color="#343a40"
        ).pack(side="left", padx=10)

        # Video display
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="Chưa có video từ webcam",
            font=("Arial", 16),
            text_color="#343a40",
            fg_color="#f0f0f0",
            corner_radius=8
        )
        self.image_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Result label
        self.result_label = ctk.CTkLabel(
            self.image_frame,
            text="Số lượng phát hiện: 0 bò, 0 heo / Số lượng trong bầy: 0",
            font=("Arial", 14, "bold"),
            text_color="#1a5f7a"
        )
        self.result_label.pack(pady=10)

    def start_webcam(self):
        if self.webcam_running:
            return

        try:
            self.cap = cv2.VideoCapture(0)  # Access default webcam (ID 0)
            if not self.cap.isOpened():
                raise Exception("Không thể mở webcam")

            self.webcam_running = True
            self.tracks = {}
            self.previous_centers = {}
            self.crossed_ids = set()
            self.detected_count = 0
            self.cow_count = 0
            self.pig_count = 0
            self.update_frame()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi mở webcam: {str(e)}")
            self.webcam_running = False
            if self.cap:
                self.cap.release()

    def stop_webcam(self):
        self.webcam_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.image_label.configure(image=None, text="Chưa có video từ webcam")
        self.cow_count = 0
        self.pig_count = 0
        self.detected_count = 0
        self.tracks = {}
        self.previous_centers = {}
        self.crossed_ids = set()
        self.result_label.configure(text="Số lượng phát hiện: 0 bò, 0 heo / Số lượng trong bầy: 0")
        self.quantity_entry.delete(0, "end")

    def update_frame(self):
        if not self.webcam_running:
            return

        try:
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Không thể đọc khung hình từ webcam")

            # Get frame dimensions
            height, width = frame.shape[:2]
            mid_line_y = height // 2

            # Draw the middle line
            cv2.line(frame, (0, mid_line_y), (width, mid_line_y), (255, 255, 0), 2)

            # Process frame with YOLO
            results = self.model(frame, conf=0.5)  # Only take boxes with confidence > 50%
            self.cow_count = 0
            self.pig_count = 0
            confidence_scores = []

            # Current frame centers for tracking
            current_centers = []
            current_boxes = []

            for result in results:
                for box in result.boxes:
                    class_name = result.names[int(box.cls)].lower()
                    confidence = float(box.conf)
                    confidence_scores.append(confidence)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    current_centers.append((center_x, center_y))
                    current_boxes.append((x1, y1, x2, y2, class_name, confidence))

                    if class_name == "cow":
                        self.cow_count += 1
                    elif class_name == "pig":
                        self.pig_count += 1

            # Simple tracking: Match current centers to previous centers
            new_tracks = {}
            next_id = max(self.tracks.keys(), default=0) + 1 if self.tracks else 0

            for i, (center_x, center_y) in enumerate(current_centers):
                x1, y1, x2, y2, class_name, confidence = current_boxes[i]
                label = f"{class_name.upper()}: {confidence:.2f}"

                # Find the closest previous center
                matched_id = None
                min_dist = float('inf')
                for track_id, prev_center in self.previous_centers.items():
                    dist = ((center_x - prev_center[0]) ** 2 + (center_y - prev_center[1]) ** 2) ** 0.5
                    if dist < min_dist and dist < 50:  # Threshold for matching
                        min_dist = dist
                        matched_id = track_id

                if matched_id is None:
                    matched_id = next_id
                    next_id += 1

                # Update track
                if matched_id not in self.tracks:
                    self.tracks[matched_id] = []
                self.tracks[matched_id].append((center_x, center_y))
                new_tracks[matched_id] = (center_x, center_y)

                # Draw box and label
                if class_name == "cow":
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA
                    )
                elif class_name == "pig":
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        2,
                        cv2.LINE_AA
                    )

                # Draw center point
                cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)

                # Draw track (path of center point)
                if len(self.tracks[matched_id]) > 1:
                    for j in range(len(self.tracks[matched_id]) - 1):
                        pt1 = self.tracks[matched_id][j]
                        pt2 = self.tracks[matched_id][j + 1]
                        cv2.line(frame, pt1, pt2, (255, 165, 0), 2)

                # Check if the center point crosses the middle line (from top to bottom)
                if matched_id not in self.crossed_ids:
                    if matched_id in self.previous_centers:
                        prev_y = self.previous_centers[matched_id][1]
                        if prev_y <= mid_line_y and center_y > mid_line_y:  # Top to bottom
                            self.detected_count += 1
                            self.crossed_ids.add(matched_id)

            # Update previous centers
            self.previous_centers = new_tracks

            # Clean up old tracks
            active_ids = set(new_tracks.keys())
            self.tracks = {track_id: points for track_id, points in self.tracks.items() if track_id in active_ids}

            self.recognition_ratio = f"{sum(confidence_scores) / len(confidence_scores):.4f}" if confidence_scores else "N/A"

            selected_barn_name = self.barn_combo.get()
            selected_barn = next((barn for barn in self.barns if barn['barns_name'] == selected_barn_name), None)
            batch_quantity = 0
            species = "unknown"
            if selected_barn and selected_barn['batch_id']:
                batch = next((batch for batch in self.batches if batch['batch_id'] == selected_barn['batch_id']), None)
                if batch:
                    batch_quantity = batch['quantity']
                    species = batch['species'].lower()

            # Update detected count in quantity entry
            self.quantity_entry.delete(0, "end")
            self.quantity_entry.insert(0, str(self.detected_count))
            result_text = f"Số lượng phát hiện: {self.cow_count} bò, {self.pig_count} heo / Số lượng trong bầy: {batch_quantity}"
            self.result_label.configure(text=result_text)

            # Convert frame to CTkImage for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            max_size = (800, 600)
            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)

            ctk_image = ctk.CTkImage(light_image=pil_image, size=pil_image.size)
            self.image_label.configure(image=ctk_image, text="")
            self.image_label.image = ctk_image

            # Schedule the next frame update
            if self.webcam_running:
                self.image_label.after(30, self.update_frame)  # Update every 30ms (~33 FPS)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xử lý khung hình: {str(e)}")
            self.stop_webcam()

    def update_shift_date(self, shift_selection):
        if shift_selection == "Tạo ca mới":
            self.shift_date_entry.delete(0, "end")
            self.shift_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        else:
            shift_id = self.shift_id_map.get(shift_selection)
            shift = next((s for s in self.shifts if s['id'] == shift_id), None)
            if shift and shift['date']:
                self.shift_date_entry.delete(0, "end")
                self.shift_date_entry.insert(0, shift['date'].strftime("%Y-%m-%d"))

    def save_shift(self):
        if self.detected_count == 0:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả nhận diện để lưu!")
            return

        try:
            shift_selection = self.shift_combo.get()
            shift_date_str = self.shift_date_entry.get().strip()
            quantity_str = self.quantity_entry.get().strip()

            try:
                shift_date = datetime.strptime(shift_date_str, "%Y-%m-%d").date()
                quantity = int(quantity_str)
            except ValueError:
                messagebox.showerror("Lỗi", "Định dạng ngày hoặc số lượng không hợp lệ!")
                return

            if shift_selection == "Tạo ca mới":
                shift_id = self.work_shifts_controller.add_shift(self.user_id, shift_date)
            else:
                shift_id = self.shift_id_map.get(shift_selection)
                if not shift_id:
                    messagebox.showerror("Lỗi", "Không tìm thấy ca làm việc được chọn!")
                    return

            selected_barn_name = self.barn_combo.get()
            selected_barn = next((barn for barn in self.barns if barn['barns_name'] == selected_barn_name), None)
            if not selected_barn:
                messagebox.showerror("Lỗi", "Không tìm thấy chuồng được chọn!")
                return

            batch = None
            species = "unknown"
            if selected_barn['batch_id']:
                batch = next((batch for batch in self.batches if batch['batch_id'] == selected_barn['batch_id']), None)
                if batch:
                    species = batch['species'].lower()

            if quantity == 0:
                messagebox.showwarning("Cảnh báo", "Số lượng nhận diện phải lớn hơn 0!")
                return

            barn_id = selected_barn['barn_id']
            if not barn_id:
                messagebox.showerror("Lỗi", "Không tìm thấy ID của chuồng!")
                return

            self.work_shifts_controller.add_shift_details(shift_id, barn_id, quantity)
            messagebox.showinfo("Thành công", f"Đã lưu chi tiết nhận diện cho ca làm việc ID {shift_id}!")
            self.quantity_entry.delete(0, "end")
            self.stop_webcam()
            self.cow_count = 0
            self.pig_count = 0
            self.detected_count = 0
            self.recognition_ratio = "N/A"

            self.setup_data()
            self.shift_combo.configure(values=self.shift_options)
            self.shift_combo.set("Tạo ca mới")
            self.update_shift_date("Tạo ca mới")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lưu ca làm việc: {str(e)}")

    def destroy(self):
        self.stop_webcam()  # Ensure webcam is stopped before destroying
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()