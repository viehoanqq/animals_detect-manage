from ultralytics import YOLO
import cv2

# 1. Tải mô hình đã huấn luyện
model = YOLO('runs/detect/train5/weights/best.pt')  # Thay thế đường dẫn đúng nếu cần

# 2. Đọc ảnh mới để dự đoán
image_path = 'dataset/test/images/test4.jpg'  # Thay thế bằng đường dẫn của ảnh cần nhận diện
img = cv2.imread(image_path)

# 3. Dự đoán đối tượng trong ảnh
results = model.predict(img)  # Dự đoán đối tượng trong ảnh

# 4. Kết quả trả về là một list, bạn cần lấy đối tượng đầu tiên (nếu có nhiều ảnh) để hiển thị
result = results[0]  # Lấy kết quả từ ảnh đầu tiên trong danh sách

# 5. Hiển thị kết quả
result.show()  # Hiển thị ảnh với các hộp dự đoán

# 6. (Tuỳ chọn) Lưu kết quả vào file mới
result.save()  # Lưu kết quả vào thư mục 'runs/detect/predict'

# 7. Lấy thông tin chi tiết về dự đoán (ví dụ: các lớp và độ chính xác)

# 7. Lấy thông tin chi tiết về dự đoán (ví dụ: các lớp và các bounding boxes)
print(f"Predicted labels: {result.names}")  # Các lớp dự đoán
print(f"Predicted boxes: {result.boxes.xywh}")  # Các bounding boxes (vị trí và kích thước)