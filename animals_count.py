import cv2
import torch
from ultralytics import YOLO
import numpy as np
import tkinter as tk
from threading import Thread
from collections import defaultdict
from tkinter import ttk
from PIL import Image, ImageTk
import time

class AnimalCounter(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F4F4F4")
        self.model = YOLO("yolov8n.pt")  # Model YOLOv8
        self.line_position = 250  
        self.animal_counts = defaultdict(int)  
        self.crossed_ids = set()
        self.cap = None
        self.running = False
        self.start_time = None
        self.end_time = None
        
        # Main layout
        self.pack(fill=tk.BOTH, expand=True)

        # Camera Frame (Smaller size)
        self.canvas = tk.Canvas(self, width=500, height=300, bg="black")
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Table Frame (Full width)
        table_frame = tk.Frame(self, bg="#F4F4F4")
        table_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Table (Treeview) - 750px width
        self.tree = ttk.Treeview(table_frame, columns=("Animal", "Count"), show="headings", height=10)
        self.tree.heading("Animal", text="Loài")
        self.tree.heading("Count", text="Số lượng")
        self.tree.column("Animal", width=600)
        self.tree.column("Count", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Button Frame (Bottom Right Corner)
        button_frame = tk.Frame(self, bg="#F4F4F4")
        button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

        # Start Button
        self.btn_start = tk.Button(button_frame, text="Bắt đầu Nhận Diện", command=self.start_detection, font=("Arial", 12), bg="green", fg="white")
        self.btn_start.pack(pady=5, fill=tk.X)

        # Stop Button
        self.btn_stop = tk.Button(button_frame, text="Dừng Nhận Diện", command=self.stop_detection, font=("Arial", 12), bg="red", fg="white")
        self.btn_stop.pack(pady=5, fill=tk.X)

        # Time Labels
        self.start_time_label = tk.Label(button_frame, text="Bắt đầu: --:--:--", font=("Arial", 10), bg="#F4F4F4")
        self.start_time_label.pack(pady=2)
        
        self.end_time_label = tk.Label(button_frame, text="Kết thúc: --:--:--", font=("Arial", 10), bg="#F4F4F4")
        self.end_time_label.pack(pady=2)

    def start_detection(self):
        if not self.running:
            self.running = True
            self.cap = cv2.VideoCapture(0)  
            self.thread = Thread(target=self.detect_and_count, daemon=True)
            self.thread.start()
            self.start_time = time.strftime("%H:%M:%S")
            self.start_time_label.config(text=f"Bắt đầu: {self.start_time}")
            self.end_time_label.config(text="Kết thúc: --:--:--")

    def stop_detection(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.end_time = time.strftime("%H:%M:%S")
        self.end_time_label.config(text=f"Kết thúc: {self.end_time}")

    def detect_and_count(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.resize(frame, (500, 300))
            frame_height, frame_width, _ = frame.shape
            cv2.line(frame, (0, self.line_position), (frame_width, self.line_position), (0, 255, 255), 2)

            results = self.model(frame)
            for r in results:
                boxes = r.boxes.xyxy
                names = self.model.names
                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = map(int, box[:4])
                    class_id = int(r.boxes.cls[i])
                    label_text = names[class_id]
                    obj_id = f"{x1}-{y1}-{x2}-{y2}"
                    
                    if y1 < self.line_position < y2 and obj_id not in self.crossed_ids:
                        self.animal_counts[label_text] += 1
                        self.crossed_ids.add(obj_id)
                        self.update_table()
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            self.display_frame(frame)

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.canvas.image = imgtk  

    def update_table(self):
        # Xóa bảng cũ
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Thêm dữ liệu mới
        for animal, count in self.animal_counts.items():
            self.tree.insert("", "end", values=(animal, count))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Animal Counter")
    root.geometry("1000x600")  # Set kích thước cửa sổ
    app = AnimalCounter(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
