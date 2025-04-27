import torch
from ultralytics import YOLO

# 1. Load pre-trained model (hoặc bạn tự chọn yolov8n, yolov8s, ...). 'yolov8n.pt' là mô hình nhẹ.
model = YOLO('yolov8n.pt')  # Nếu bạn có mô hình khác, thay thế 'yolov8n.pt'

# 2. Train (Đảm bảo rằng data.yaml và ảnh đã được cấu trúc chính xác)
model.train(
    data='D:/python/dataset/data.yaml',  # Đảm bảo đường dẫn đúng đến file data.yaml
    epochs=50,                                    # Số epoch (tùy theo tài nguyên máy tính của bạn)
    imgsz=640,                                    # Kích thước ảnh đưa vào mô hình
    batch=16,                                     # Số lượng ảnh trong một batch (có thể điều chỉnh tùy tài nguyên)
    device='cuda' if torch.cuda.is_available() else 'cpu',  # Chạy trên GPU nếu có
)
