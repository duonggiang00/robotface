import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor

from components import *
from emotions import EMOTIONS, Y_EYE
from engine import ComponentAnim

class FaceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Size is now dynamic, no more fixed size
        
        # Load the default Neutral state
        self.active_sequence = EMOTIONS["1_Listen-Neutral"]
        self.current_frame_idx = 0
        self.hold_counter = 0
        
        initial_state = self.active_sequence.frames[0]
        self.left_eye_anim = ComponentAnim(initial_state.left_eye)
        self.right_eye_anim = ComponentAnim(initial_state.right_eye)
        self.mouth_anim = ComponentAnim(initial_state.mouth)
        
        # Universal Transition Pipeline
        self.pending_sequence = None
        self.transition_progress = 1.0 # 1.0 means fully open
        
        # Start Engine Timer (Runs at 60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def set_emotion(self, emotion_name):
        if emotion_name in EMOTIONS and self.transition_progress >= 1.0:
            if EMOTIONS[emotion_name] != self.active_sequence:
                self.pending_sequence = EMOTIONS[emotion_name]
                self.transition_progress = 0.0 # Trigger the blink transition!

    def push_target_frame(self):
        state = self.active_sequence.frames[self.current_frame_idx]
        self.left_eye_anim.set_target(state.left_eye)
        self.right_eye_anim.set_target(state.right_eye)
        self.mouth_anim.set_target(state.mouth)

    def update_animation(self):
        # Handle Universal Blink Transition
        if self.transition_progress < 1.0:
            self.transition_progress += 0.06 # Transition speed
            
            # Exactly at the halfway point (eyes fully closed), swap the sequence!
            if self.transition_progress >= 0.5 and self.pending_sequence:
                self.active_sequence = self.pending_sequence
                self.pending_sequence = None
                self.current_frame_idx = 0
                self.hold_counter = 0
                self.push_target_frame()
                
                # Snap engine to the new targets immediately to prevent ghosting
                self.left_eye_anim.current = self.left_eye_anim.target
                self.right_eye_anim.current = self.right_eye_anim.target
                self.mouth_anim.current = self.mouth_anim.target
                self.left_eye_anim.fade_t = 1.0
                self.right_eye_anim.fade_t = 1.0
                self.mouth_anim.fade_t = 1.0

        lerp_speed = 0.35 # Fast chasing speed so shapes smoothly keep up with the timeline
        self.left_eye_anim.update(lerp_speed)
        self.right_eye_anim.update(lerp_speed)
        self.mouth_anim.update(lerp_speed)
        
        self.hold_counter += 1
        current_state = self.active_sequence.frames[self.current_frame_idx]
        
        if self.hold_counter >= current_state.hold_time:
            self.hold_counter = 0
            self.current_frame_idx += 1
            
            if self.current_frame_idx >= len(self.active_sequence.frames):
                if self.active_sequence.loop:
                    self.current_frame_idx = 0
                else:
                    self.current_frame_idx = len(self.active_sequence.frames) - 1
            
            self.push_target_frame()

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw Black Background
        painter.fillRect(self.rect(), QColor(5, 5, 5))
        
        # Center Coordinate for the face
        cx = self.width() / 2
        cy = self.height() / 2 - 50
        
        # Draw Mouth normally (doesn't squish during transition)
        self.mouth_anim.draw(painter, cx, cy)
        
        # Calculate Y-axis squish scale for the transition blink
        scale_y = 1.0
        if self.transition_progress < 0.5:
            scale_y = max(0.01, 1.0 - (self.transition_progress * 2))
        elif self.transition_progress < 1.0:
            scale_y = max(0.01, (self.transition_progress - 0.5) * 2)
            
        # Draw Eyes with procedural scaling applied
        painter.save()
        eye_center_y = cy + Y_EYE
        painter.translate(cx, eye_center_y)
        painter.scale(1.0, scale_y)
        painter.translate(-cx, -eye_center_y)
        
        self.left_eye_anim.draw(painter, cx, cy)
        self.right_eye_anim.draw(painter, cx, cy)
        
        painter.restore()

class FaceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procedural Robot Face - Keyframe Engine")
        self.face_widget = FaceWidget()
        self.setCentralWidget(self.face_widget)
        self.setStyleSheet("background-color: black;")
        
        # Setup and Detect Screens
        self.setup_screen()
        
    def setup_screen(self):
        screens = QApplication.screens()
        print(f"--- DETECTED {len(screens)} DISPLAY(S) ---")
        for i, screen in enumerate(screens):
            geom = screen.geometry()
            print(f"[{i}] {screen.name()} | Resolution: {geom.width()}x{geom.height()} | Pos: ({geom.x()}, {geom.y()})")
        
        # If there is more than 1 screen, usually screen 1 is the Robot's face monitor
        if len(screens) > 1:
            target_screen = screens[1]
            print(f"> Automatically moving face to secondary monitor: {target_screen.name()}")
            
            # Move the window to the target screen and maximize it fully!
            self.move(target_screen.geometry().x(), target_screen.geometry().y())
            self.showFullScreen()
        else:
            print("> Only 1 monitor detected. Running on primary screen.")
            self.resize(1024, 600) # Default size if no robot screen
        print("-----------------------------------")
        
    def set_emotion(self, emotion_name):
        self.face_widget.set_emotion(emotion_name)
        
    def keyPressEvent(self, event):
        key_map = {
            Qt.Key.Key_1: "1_Listen-Neutral",
            Qt.Key.Key_2: "2_Confirm",
            Qt.Key.Key_3: "3_Happy-when-sefile",
            Qt.Key.Key_4: "4_Happy-when-talking",
            Qt.Key.Key_5: "4_Apology",
            Qt.Key.Key_6: "5_Thinking",
            Qt.Key.Key_7: "6_Warning",
            Qt.Key.Key_8: "7_Welcome-when-sefile",
            Qt.Key.Key_9: "8_Suprise",
            Qt.Key.Key_0: "9_Unsure",
        }
        if event.key() in key_map:
            self.set_emotion(key_map[event.key()])
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

def main():
    app = QApplication(sys.argv)
    window = FaceWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
