import sys
import os
import importlib.util
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap

def load_config_from_file(file_name):
    """
    Tải động mảng FRAMES_CONFIG từ một file .py (hỗ trợ cả tên file có dấu gạch ngang)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, file_name)
    if not os.path.exists(file_path):
        print(f"Cảnh báo: Không tìm thấy file {file_name}")
        return []
        
    module_name = file_name.replace(".py", "").replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            return module.FRAMES_CONFIG
        except Exception as e:
            print(f"Lỗi khi tải cấu hình từ {file_name}: {e}")
            return []
    return []

# Bảng ánh xạ Phím tắt -> Cấu hình frames của từng cảm xúc
KEY_MAPPING = {
    Qt.Key.Key_1: load_config_from_file("demo_Apology.py"),
    Qt.Key.Key_2: load_config_from_file("demo_Confirm.py"),
    Qt.Key.Key_3: load_config_from_file("demo_Happy-when-sefile.py"),
    Qt.Key.Key_4: load_config_from_file("demo_Happy-when-talking.py"),
    Qt.Key.Key_5: load_config_from_file("demo_Listen-Neutral.py"),
    Qt.Key.Key_6: load_config_from_file("demo_Suprise.py"),
    Qt.Key.Key_7: load_config_from_file("demo_Thinking.py"),
    Qt.Key.Key_8: load_config_from_file("demo_Unsure.py"),
    Qt.Key.Key_9: load_config_from_file("demo_Warning.py"),
    Qt.Key.Key_0: load_config_from_file("demo_Welcome-when-sefile.py"),
    Qt.Key.Key_Q: load_config_from_file("demo_talking-when-normal.py"),
    Qt.Key.Key_W: load_config_from_file("demo_welcome-when-talking.py"),
}

class MasterAnimationDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RobotFace Master Animation Demo")
        self.setFixedSize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Label hiển thị ảnh
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.image_label)

        # Cấu hình hiện tại
        self.current_frames_config = []
        self.current_frame_index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        
        # Mặc định load phím số 5 (Listen-Neutral) nếu có
        default_config = KEY_MAPPING.get(Qt.Key.Key_5, [])
        if not default_config:
            # Nếu không có phím 5, tìm cái đầu tiên có data
            for cfg in KEY_MAPPING.values():
                if cfg:
                    default_config = cfg
                    break
                    
        if default_config:
            self.set_active_config(default_config)
        else:
            self.image_label.setText("Chưa tải được bất kỳ cấu hình nào.\nHãy kiểm tra lại các file demo_*.py")
            self.image_label.setStyleSheet("color: white; background-color: black; font-size: 20px;")

    def set_active_config(self, config):
        if not config:
            return
            
        self.current_frames_config = config
        self.current_frame_index = 0
        self.show_frame()

    def show_frame(self):
        if not self.current_frames_config:
            return
        
        image_path, delay_ms = self.current_frames_config[self.current_frame_index]
        
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

        # Chạy timer với thời gian của đúng frame hiện tại
        self.timer.start(delay_ms)

    def next_frame(self):
        if not self.current_frames_config:
            return
            
        self.current_frame_index += 1
        if self.current_frame_index >= len(self.current_frames_config):
            self.current_frame_index = 0
            
        self.show_frame()

    def resizeEvent(self, event):
        self.show_frame()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        # Kiểm tra xem phím bấm có nằm trong danh sách ánh xạ không
        key = event.key()
        if key in KEY_MAPPING:
            config = KEY_MAPPING[key]
            if config:
                self.set_active_config(config)
            else:
                print(f"Cảm xúc ở phím này hiện không có file ảnh hoặc chưa được cấu hình!")
        elif key == Qt.Key.Key_Escape:
            # Bấm Esc để thoát chương trình nhanh
            self.close()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterAnimationDemo()
    
    # Tự động nhận diện màn hình phụ
    screens = app.screens()
    if len(screens) > 1:
        external_screen = screens[1]
        print(f"Chạy trên màn hình phụ: {external_screen.name()}")
        window.move(external_screen.geometry().topLeft())
        window.showFullScreen()
    else:
        print("Không tìm thấy màn hình phụ, chạy trên màn hình chính.")
        window.show()
        
    sys.exit(app.exec())
