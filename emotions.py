from components import *
import math

# =========================================================
# GLOBAL LAYOUT CONFIGURATION
# Chỉnh sửa các thông số này để tự động thay đổi trên TẤT CẢ các frame!
# =========================================================
EYE_SPREAD = 400       # Khoảng cách mắt (Tăng số này để 2 mắt xa nhau ra, VD: 220)
Y_EYE = -100           # Độ cao của mắt (Số âm là nằm bên trên tâm)
Y_MOUTH = 200          # Độ cao của miệng (Số dương là nằm bên dưới tâm)

L_X = -EYE_SPREAD      # Tọa độ X chuẩn cho Mắt Trái
R_X = EYE_SPREAD       # Tọa độ X chuẩn cho Mắt Phải
# =========================================================
class FaceState:
    def __init__(self, left_eye, right_eye, mouth, hold_time=1):
        self.left_eye = left_eye
        self.right_eye = right_eye
        self.mouth = mouth
        self.hold_time = hold_time

class FaceSequence:
    def __init__(self, frames, loop=True):
        self.frames = frames
        self.loop = loop

# ---------------------------------------------------------
# The 7-Frame Listen-Neutral Sequence (Replicated exactly)
# ---------------------------------------------------------
NEUTRAL_FRAMES = [
    # Frame 1: Holding open eyes (Long pause)
    FaceState(left_eye=NeutralEye(h=220, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=220, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=150),
    
    # Closing sequence (Squishing down progressively, centered)
    FaceState(left_eye=NeutralEye(h=200, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=200, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=3),
    FaceState(left_eye=NeutralEye(h=180, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=180, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=150, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=150, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=120, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=120, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=90, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=90, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=60, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=60, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=40, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=40, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=20, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=20, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    
    # Fully closed blink (BlinkEye curve, perfectly centered)
    FaceState(left_eye=BlinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=BlinkEye(x_offset=R_X, y_offset=Y_EYE), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=3),
    FaceState(left_eye=BlinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=BlinkEye(x_offset=R_X, y_offset=Y_EYE), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=3),
    FaceState(left_eye=BlinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=BlinkEye(x_offset=R_X, y_offset=Y_EYE), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=3),
    
    # Opening sequence (Expanding back up, centered)
    FaceState(left_eye=NeutralEye(h=20, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=20, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=40, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=40, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=60, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=60, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=90, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=90, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=120, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=120, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=150, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=150, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=180, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=180, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=NeutralEye(h=200, y_offset=Y_EYE, x_offset=L_X), right_eye=NeutralEye(h=200, y_offset=Y_EYE, x_offset=R_X), mouth=SmileMouth(y_offset=Y_MOUTH), hold_time=3),
]

# ---------------------------------------------------------
# ANIMATION SEQUENCES (CONFIRM)
# ---------------------------------------------------------
CONFIRM_FRAMES = [
    # Phase 1: Sparkle pulsing up and holding (Frames 1-4)
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=250, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.5), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=4),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=250, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=1.0), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=4),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=250, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=1.4), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=40),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=250, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=1.0), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=4),
    
    # Phase 2: Slowly closing the SparkleEye (Squishing down h) (Frames 5-11)
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=220, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.8), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=180, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.6), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=140, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.4), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=100, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.2), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=60, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.1), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=30, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.0), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=10, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.0), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    
    # Phase 3: Hold Double Wink (Frames 12-14)
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=WinkEye(x_offset=R_X, y_offset=Y_EYE), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=15),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=WinkEye(x_offset=R_X, y_offset=Y_EYE), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=15),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=WinkEye(x_offset=R_X, y_offset=Y_EYE), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=15),
    
    # Phase 4: Slowly opening back to SparkleEye (Frames 15-20)
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=30, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.0), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=60, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.1), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=100, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.2), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=140, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.4), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=180, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.6), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
    FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=SparkleEye(h=220, x_offset=R_X, y_offset=Y_EYE, sparkle_scale=0.8), mouth=BowlMouth(y_offset=Y_MOUTH), hold_time=2),
]

# ---------------------------------------------------------
# ANIMATION SEQUENCES (HAPPY)
# ---------------------------------------------------------
HAPPY_FRAMES = [
    # Happy eyes are spread slightly wider than normal (+40) and have a heartbeat pulse
    FaceState(left_eye=HeartEye(x_offset=L_X - 40, y_offset=Y_EYE, heart_scale=1.0), right_eye=HeartEye(x_offset=R_X + 40, y_offset=Y_EYE, heart_scale=1.0), mouth=BowlMouth(w=250, h=120, y_offset=Y_MOUTH), hold_time=5),
    FaceState(left_eye=HeartEye(x_offset=L_X - 40, y_offset=Y_EYE, heart_scale=1.2), right_eye=HeartEye(x_offset=R_X + 40, y_offset=Y_EYE, heart_scale=1.2), mouth=BowlMouth(w=250, h=120, y_offset=Y_MOUTH), hold_time=5),
    FaceState(left_eye=HeartEye(x_offset=L_X - 40, y_offset=Y_EYE, heart_scale=1.4), right_eye=HeartEye(x_offset=R_X + 40, y_offset=Y_EYE, heart_scale=1.4), mouth=BowlMouth(w=250, h=120, y_offset=Y_MOUTH), hold_time=15),
    FaceState(left_eye=HeartEye(x_offset=L_X - 40, y_offset=Y_EYE, heart_scale=1.2), right_eye=HeartEye(x_offset=R_X + 40, y_offset=Y_EYE, heart_scale=1.2), mouth=BowlMouth(w=250, h=120, y_offset=Y_MOUTH), hold_time=5),
    FaceState(left_eye=HeartEye(x_offset=L_X - 40, y_offset=Y_EYE, heart_scale=1.0), right_eye=HeartEye(x_offset=R_X + 40, y_offset=Y_EYE, heart_scale=1.0), mouth=BowlMouth(w=250, h=120, y_offset=Y_MOUTH), hold_time=20),
]

# ---------------------------------------------------------
# ANIMATION SEQUENCES (HAPPY TALKING)
# ---------------------------------------------------------
# Chỉnh sửa blush_scale, blush_y, và blush_gap ở ĐÂY (chỉ 1 dòng duy nhất) để áp dụng cho toàn bộ 4 frame!
def get_talking_eye(is_right=False):
    x_pos = (R_X + 40) if is_right else (L_X - 40)
    return HeartEye(x_offset=x_pos, y_offset=Y_EYE, heart_scale=1.1, show_blush=True, blush_scale=1.0, blush_y=180, blush_gap=50)

HAPPY_TALKING_FRAMES = [
    # Talking sequence with moving lips (cheeks are static now, attached to eyes)
    FaceState(left_eye=get_talking_eye(False), right_eye=get_talking_eye(True), mouth=TalkingMouth(w=250, h=100, top_curve=0, y_offset=Y_MOUTH), hold_time=10),
    FaceState(left_eye=get_talking_eye(False), right_eye=get_talking_eye(True), mouth=TalkingMouth(w=230, h=70, top_curve=40, y_offset=Y_MOUTH), hold_time=10),
    FaceState(left_eye=get_talking_eye(False), right_eye=get_talking_eye(True), mouth=TalkingMouth(w=200, h=50, top_curve=70, y_offset=Y_MOUTH), hold_time=10),
    FaceState(left_eye=get_talking_eye(False), right_eye=get_talking_eye(True), mouth=TalkingMouth(w=230, h=80, top_curve=30, y_offset=Y_MOUTH), hold_time=10),
]

# ---------------------------------------------------------
# ANIMATION SEQUENCES (APOLOGY)
# ---------------------------------------------------------
# Chỉnh sửa giọt nước mắt ở đây nếu cần!
# - tear_x_offset: Đẩy nước mắt sang trái (số âm) hoặc phải (số dương) so với tâm con mắt
# - tear_y_offset: Kéo dòng nước mắt thấp xuống (số dương) hoặc cao lên (số âm)
def get_crying_eye(is_right=False):
    x_pos = R_X if is_right else L_X
    return SadEye(x_offset=x_pos, y_offset=Y_EYE, is_right=is_right, show_tears=True, tear_x_offset=20, tear_y_offset=0)

APOLOGY_FRAMES = [
    # Frame 1: Pendulum start (Mouth at 0 phase)
    FaceState(
        left_eye=get_crying_eye(False), 
        right_eye=get_crying_eye(True), 
        mouth=SquigglyMouth(y_offset=Y_MOUTH, phase=0.0), 
        hold_time=20
    ),
    # Frame 2: Pendulum end (Mouth flips completely)
    FaceState(
        left_eye=get_crying_eye(False), 
        right_eye=get_crying_eye(True), 
        mouth=SquigglyMouth(y_offset=Y_MOUTH, phase=math.pi), 
        hold_time=20
    ),
]

# ---------------------------------------------------------
# ANIMATION SEQUENCES (SURPRISE)
# ---------------------------------------------------------
SURPRISE_FRAMES = [
    # Static base frame (Animation is now purely procedural rotation inside the eyes)
    FaceState(
        left_eye=StarEye(w=220, h=270, x_offset=L_X - 40, y_offset=Y_EYE), 
        right_eye=StarEye(w=220, h=270, x_offset=R_X + 40, y_offset=Y_EYE), 
        # ĐIỀU CHỈNH VỊ TRÍ MIỆNG Ở ĐÂY:
        # y_offset: Tăng để miệng hạ thấp xuống, Giảm để nhích lên cao
        # x_offset: Chỉnh để dịch miệng sang trái/phải nếu cần (Mặc định 0 là chính giữa)
        mouth=RectMouth(w=150, h=170, y_offset=Y_MOUTH, radius=25), 
        hold_time=20
    )
]

# ---------------------------------------------------------
# Global Dictionary mapping Folder Names to Sequences
# ---------------------------------------------------------
# Chỉnh sửa blush_scale, blush_y, và blush_gap ở ĐÂY cho biểu cảm Confusing
def get_confusing_eye(is_right=False):
    x_pos = R_X if is_right else L_X
    return SpiralEye(x_offset=x_pos, y_offset=Y_EYE, continuous_spin=True, show_blush=True, blush_scale=1.0, blush_y=180, blush_gap=50)

EMOTIONS = {
    "1_Listen-Neutral": FaceSequence(frames=NEUTRAL_FRAMES, loop=True),
    "2_Confirm": FaceSequence(frames=CONFIRM_FRAMES, loop=True),
    "3_Happy-when-sefile": FaceSequence(frames=HAPPY_FRAMES, loop=True),
    "4_Happy-when-talking": FaceSequence(frames=HAPPY_TALKING_FRAMES, loop=True),
    "4_Apology": FaceSequence(frames=APOLOGY_FRAMES, loop=True),
    "5_Thinking": FaceSequence(frames=[
        # Look Left (Shift entire eye assembly to the left by 40px)
        FaceState(left_eye=NeutralEye(x_offset=L_X - 40, y_offset=Y_EYE, highlights=False), right_eye=NeutralEye(x_offset=R_X - 40, y_offset=Y_EYE, highlights=False), mouth=CapsuleMouth(y_offset=Y_MOUTH), hold_time=40),
        # Look Right (Shift entire eye assembly to the right by 40px)
        FaceState(left_eye=NeutralEye(x_offset=L_X + 40, y_offset=Y_EYE, highlights=False), right_eye=NeutralEye(x_offset=R_X + 40, y_offset=Y_EYE, highlights=False), mouth=CapsuleMouth(y_offset=Y_MOUTH), hold_time=40)
    ], loop=True),
    "6_Warning": FaceSequence(frames=[
        # Confusing/Warning emotion: Spiral runs a full infinite circle, with orange blush!
        FaceState(
            left_eye=get_confusing_eye(False), 
            right_eye=get_confusing_eye(True), 
            mouth=VerticalMouth(y_offset=Y_MOUTH), 
            hold_time=20
        )
    ], loop=True),
    "7_Welcome-when-sefile": FaceSequence(frames=[
        FaceState(left_eye=WelcomeEye(x_offset=L_X, y_offset=Y_EYE), right_eye=WelcomeEye(x_offset=R_X, y_offset=Y_EYE), mouth=BowlMouth(w=300, h=150, y_offset=Y_MOUTH))
    ], loop=True),
    "8_Suprise": FaceSequence(frames=SURPRISE_FRAMES, loop=True),
    "9_Unsure": FaceSequence(frames=[
        FaceState(left_eye=WinkEye(x_offset=L_X, y_offset=Y_EYE), right_eye=NeutralEye(x_offset=R_X, y_offset=Y_EYE), mouth=SquigglyMouth(y_offset=Y_MOUTH)) # Placeholder
    ], loop=True),
}
