import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap

# ==========================================
# CẤU HÌNH THAM SỐ TỪNG FRAME TẠI ĐÂY
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Danh sách các frame: (Đường dẫn ảnh, Thời gian chờ tính bằng mili-giây)
# Chỉnh sửa con số ở cuối mỗi dòng để thay đổi tốc độ chuyển cho ĐÚNG frame đó.
FRAMES_CONFIG = [
    (os.path.join(BASE_DIR, "../Happy-when-talking", "happy-when-talking-1.jpg"), 250),
    (os.path.join(BASE_DIR, "../Happy-when-talking", "happy-when-talking-2.jpg"), 250),
    (os.path.join(BASE_DIR, "../Happy-when-talking", "happy-when-talking-3.jpg"), 250),
    (os.path.join(BASE_DIR, "../Happy-when-talking", "happy-when-talking-4.jpg"), 250),
]
# ==========================================

class AnimationDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RobotFace Animation Demo - Happy-when-talking")
        self.setFixedSize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.image_label)

        self.current_frame_index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        
        if FRAMES_CONFIG:
            self.show_frame()
        else:
            self.image_label.setText("Không tìm thấy cấu hình ảnh.")
            self.image_label.setStyleSheet("color: white; background-color: black; font-size: 20px;")

    def show_frame(self):
        if not FRAMES_CONFIG:
            return
        
        image_path, delay_ms = FRAMES_CONFIG[self.current_frame_index]
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText(f"Lỗi: Không tìm thấy ảnh\n{image_path}")
            self.image_label.setStyleSheet("color: red; background-color: black; font-size: 16px;")

        # Set timer for the current frame's specific delay
        self.timer.start(delay_ms)

    def next_frame(self):
        if not FRAMES_CONFIG:
            return
            
        self.current_frame_index += 1
        if self.current_frame_index >= len(FRAMES_CONFIG):
            self.current_frame_index = 0
            
        self.show_frame()

    def resizeEvent(self, event):
        self.show_frame()
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimationDemo()
    
    # Tự động nhận diện màn hình phụ
    screens = app.screens()
    if len(screens) > 1:
        # Nếu có nhiều hơn 1 màn hình, chọn màn hình thứ 2 (external monitor)
        external_screen = screens[1]
        print(f"Chạy trên màn hình phụ: {external_screen.name()}")
        
        # Di chuyển cửa sổ sang góc trên cùng bên trái của màn hình phụ
        window.move(external_screen.geometry().topLeft())
        
        # Hiển thị toàn màn hình
        window.showFullScreen()
    else:
        print("Không tìm thấy màn hình phụ, chạy trên màn hình chính.")
        window.show()
        
    sys.exit(app.exec())
