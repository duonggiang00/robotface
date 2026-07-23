import math
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainterPath, QColor, QLinearGradient, QPen, QGradient

# ---------------------------------------------------------
# Colors
# ---------------------------------------------------------
CYAN_MAIN = QColor(0, 217, 255)
CYAN_GLOW = QColor(0, 255, 255)
BLUE_GRAD = QColor(87, 153, 245)
WHITE_SPARKLE = QColor(220, 250, 255)

ORANGE_MAIN = QColor(255, 140, 60)
ORANGE_GLOW = QColor(255, 100, 0)
ORANGE_GRAD = QColor(255, 80, 50)

# ---------------------------------------------------------
# Base Component Class
# ---------------------------------------------------------
class FaceComponent:
    def draw(self, painter, cx, cy, opacity=1.0): pass
    def lerp(self, target, t): return self

# ---------------------------------------------------------
# Base Eye Components (Template Pattern)
# ---------------------------------------------------------
class BaseEye(FaceComponent):
    def __init__(self, w=180, h=220, x_offset=-180, y_offset=-100):
        self.w = w; self.h = h; self.x_offset = x_offset; self.y_offset = y_offset
        self.glow_color = CYAN_GLOW; self.main_color = CYAN_MAIN

    def get_frame_path(self, base_x, base_y): return QPainterPath()
    def draw_background(self, painter, base_x, base_y, opacity): pass
    def draw_inner(self, painter, base_x, base_y, opacity): pass
    def draw_foreground(self, painter, base_x, base_y, opacity): pass

    def draw_glow(self, painter, path, opacity):
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(1, 16):
            glow_pen = QPen(self.glow_color)
            glow_pen.setWidth(int(10 + i * 4))
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            glow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(glow_pen)
            painter.setOpacity(opacity * (0.12 / i))
            painter.drawPath(path)

    def draw_main_frame(self, painter, path, opacity):
        painter.setOpacity(opacity); painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.main_color); painter.drawPath(path)

    def draw(self, painter, cx, cy, opacity=1.0):
        base_x = cx + self.x_offset; base_y = cy + self.y_offset
        self.draw_background(painter, base_x, base_y, opacity)
        path = self.get_frame_path(base_x, base_y)
        self.draw_glow(painter, path, opacity)
        self.draw_main_frame(painter, path, opacity)
        painter.save()
        painter.setClipPath(path)
        self.draw_inner(painter, base_x, base_y, opacity)
        painter.restore()
        self.draw_foreground(painter, base_x, base_y, opacity)

class RoundedEyeFrame(BaseEye):
    def __init__(self, w=180, h=220, x_offset=-180, y_offset=-100, radius=80):
        super().__init__(w, h, x_offset, y_offset); self.radius = radius

    def get_frame_path(self, base_x, base_y):
        path = QPainterPath()
        path.addRoundedRect(base_x - self.w/2, base_y - self.h/2, self.w, self.h, self.radius, self.radius)
        return path

    def draw_glow(self, painter, path, opacity):
        painter.setBrush(self.glow_color); painter.setPen(Qt.PenStyle.NoPen)
        for i in range(1, 16):
            painter.setOpacity(opacity * (0.12 / i))
            expand = i * 2.5
            painter.drawRoundedRect(int(self.base_x_memo - self.w/2 - expand), 
                                    int(self.base_y_memo - self.h/2 - expand), 
                                    int(self.w + expand*2), int(self.h + expand*2), 
                                    int(self.radius + expand), int(self.radius + expand))
                                    
    def draw(self, painter, cx, cy, opacity=1.0):
        self.base_x_memo = cx + self.x_offset; self.base_y_memo = cy + self.y_offset
        super().draw(painter, cx, cy, opacity)

# ---------------------------------------------------------
# Modular Eye Components
# ---------------------------------------------------------
class NeutralEye(RoundedEyeFrame):
    def __init__(self, w=180, h=220, x_offset=-180, y_offset=-100, highlights=True):
        super().__init__(w, h, x_offset, y_offset, radius=80); self.highlights = highlights
    def lerp(self, target, t):
        return NeutralEye(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t, self.highlights)
    def draw_inner(self, painter, base_x, base_y, opacity):
        if self.highlights:
            painter.setBrush(WHITE_SPARKLE); painter.setPen(Qt.PenStyle.NoPen)
            h1_w = self.w * 0.35; h2_w = self.w * 0.15
            if self.x_offset > 0:
                x1 = base_x - 45; x2 = base_x + 18
            else:
                x1 = base_x - 18; x2 = base_x - 45
            painter.drawEllipse(int(x1), int(base_y - 66), int(h1_w), int(h1_w))
            painter.drawEllipse(int(x2), int(base_y + 33), int(h2_w), int(h2_w))

class BlinkEye(BaseEye):
    def __init__(self, w=180, x_offset=-180, y_offset=-100):
        super().__init__(w, 0, x_offset, y_offset)
    def lerp(self, target, t):
        return BlinkEye(self.w + (target.w - self.w)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def get_frame_path(self, base_x, base_y):
        path = QPainterPath()
        path.moveTo(base_x - self.w/2, base_y)
        path.quadTo(base_x, base_y - 40, base_x + self.w/2, base_y)
        return path
    def draw_main_frame(self, painter, path, opacity):
        painter.setOpacity(opacity)
        pen = QPen(CYAN_MAIN); pen.setWidth(40); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

class HeartEye(RoundedEyeFrame):
    def __init__(self, w=220, h=270, x_offset=-220, y_offset=-100, heart_scale=1.0, show_blush=False, blush_scale=1.0, blush_y=40, blush_gap=40):
        super().__init__(w, h, x_offset, y_offset, radius=100)
        self.heart_scale = heart_scale; self.show_blush = show_blush
        self.blush_scale = blush_scale; self.blush_y = blush_y; self.blush_gap = blush_gap
    def lerp(self, target, t):
        return HeartEye(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t, self.heart_scale + (target.heart_scale - self.heart_scale)*t, self.show_blush, self.blush_scale + (target.blush_scale - self.blush_scale)*t, self.blush_y + (target.blush_y - self.blush_y)*t, self.blush_gap + (target.blush_gap - self.blush_gap)*t)
    def draw_main_frame(self, painter, path, opacity):
        painter.setOpacity(opacity); pen = QPen(CYAN_MAIN); pen.setWidth(18)
        painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
    def draw_glow(self, painter, path, opacity):
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(1, 10):
            glow_pen = QPen(CYAN_GLOW); glow_pen.setWidth(18 + i*3)
            painter.setPen(glow_pen); painter.setOpacity(opacity * (0.08 / i))
            painter.drawPath(path)
    def draw_inner(self, painter, base_x, base_y, opacity):
        painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(CYAN_MAIN)
        def draw_heart(hx, hy, size):
            path = QPainterPath()
            path.moveTo(hx, hy + size/4)
            path.cubicTo(hx - size, hy - size, hx - size/2, hy - size*1.5, hx, hy - size/2)
            path.cubicTo(hx + size/2, hy - size*1.5, hx + size, hy - size, hx, hy + size/4)
            painter.drawPath(path)
        sc = self.heart_scale
        draw_heart(base_x, base_y + self.h*0.1, 80 * sc)
        draw_heart(base_x - self.w*0.25, base_y + self.h*0.3, 25 * sc)
        draw_heart(base_x + self.w*0.15, base_y + self.h*0.4, 30 * sc)
    def draw_foreground(self, painter, base_x, base_y, opacity):
        if self.show_blush:
            bar_w = 12 * self.blush_scale; gap = self.blush_gap * self.blush_scale
            base_heights = [15, 35, 60, 75, 60, 35, 15]
            painter.setBrush(CYAN_GLOW); painter.setPen(Qt.PenStyle.NoPen)
            total_width = gap * 6; start_x = base_x - total_width / 2
            for i in range(7):
                bh = base_heights[i] * self.blush_scale
                bx = start_x + (i * gap)
                by = base_y + self.h/2 + self.blush_y - bh/2 
                painter.drawRoundedRect(int(bx - bar_w/2), int(by), int(bar_w), int(bh), int(bar_w/2), int(bar_w/2))

class WinkEye(BaseEye):
    def __init__(self, size=180, x_offset=-180, y_offset=-100):
        super().__init__(size, size, x_offset, y_offset); self.size = size
    def lerp(self, target, t):
        return WinkEye(self.size + (target.size - self.size)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def get_frame_path(self, base_x, base_y):
        s = self.size / 2; path = QPainterPath()
        flip = -1 if self.x_offset > 0 else 1
        path.moveTo(base_x + (-s/2)*flip, base_y - s/1.5)
        path.lineTo(base_x + (s/2)*flip, base_y)
        path.lineTo(base_x + (-s/2)*flip, base_y + s/1.5)
        path.moveTo(base_x + (-s/1.5)*flip, base_y)
        path.lineTo(base_x + (s/2)*flip, base_y)
        return path
    def draw_main_frame(self, painter, path, opacity):
        painter.setOpacity(opacity)
        pen = QPen(CYAN_MAIN); pen.setWidth(28)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

class SparkleEye(RoundedEyeFrame):
    def __init__(self, w=200, h=250, x_offset=180, y_offset=-100, sparkle_scale=1.0):
        super().__init__(w, h, x_offset, y_offset, radius=90); self.sparkle_scale = sparkle_scale
    def lerp(self, target, t):
        return SparkleEye(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t, self.sparkle_scale + (target.sparkle_scale - self.sparkle_scale)*t)
    def draw_inner(self, painter, base_x, base_y, opacity):
        painter.setBrush(WHITE_SPARKLE); painter.setPen(Qt.PenStyle.NoPen)
        sc = self.sparkle_scale; star_size = 40 * sc
        sx = base_x - self.w/2 + self.w*0.35; sy = base_y - self.h/2 + self.h*0.35
        path = QPainterPath()
        path.moveTo(sx, sy - star_size)
        path.quadTo(sx, sy, sx + star_size, sy)
        path.quadTo(sx, sy, sx, sy + star_size)
        path.quadTo(sx, sy, sx - star_size, sy)
        path.quadTo(sx, sy, sx, sy - star_size)
        painter.drawPath(path)
        c1_w = self.w*0.25*sc; c2_w = self.w*0.12*sc
        painter.drawEllipse(int(base_x - self.w/2 + self.w*0.7 - c1_w/2), int(base_y - self.h/2 + self.h*0.55 - c1_w/2), int(c1_w), int(c1_w)) 
        painter.drawEllipse(int(base_x - self.w/2 + self.w*0.45 - c2_w/2), int(base_y - self.h/2 + self.h*0.8 - c2_w/2), int(c2_w), int(c2_w)) 

class SadEye(BaseEye):
    def __init__(self, w=150, h=220, x_offset=-220, y_offset=-100, is_right=False, show_tears=True, tear_x_offset=0, tear_y_offset=0):
        super().__init__(w, h, x_offset, y_offset)
        self.is_right = is_right; self.show_tears = show_tears
        self.tear_x_offset = tear_x_offset; self.tear_y_offset = tear_y_offset
    def lerp(self, target, t):
        return SadEye(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t, self.is_right, self.show_tears, self.tear_x_offset + (target.tear_x_offset - self.tear_x_offset)*t, self.tear_y_offset + (target.tear_y_offset - self.tear_y_offset)*t)
    def draw_background(self, painter, base_x, base_y, opacity):
        if not self.show_tears: return
        import time; flow = (time.time() * 2.0) % 1.0
        tear_x = base_x + self.tear_x_offset; tear_y = base_y + self.tear_y_offset
        grad = QLinearGradient(0, tear_y + flow * 150, 0, tear_y + flow * 150 + 150)
        grad.setSpread(QGradient.Spread.RepeatSpread)
        grad.setColorAt(0.0, QColor(0, 100, 150))
        grad.setColorAt(0.5, CYAN_GLOW)
        grad.setColorAt(1.0, QColor(0, 100, 150))
        painter.setBrush(grad); painter.setPen(Qt.PenStyle.NoPen)
        r1 = math.sin(time.time() * 5.0) * 12; r2 = math.cos(time.time() * 4.2) * 18
        tw_top = 15; tw_bot = 55; th = 350
        t_path = QPainterPath()
        t_path.moveTo(tear_x - tw_top, tear_y)
        t_path.cubicTo(tear_x - tw_top + r1, tear_y + th*0.3, tear_x - tw_bot + r2, tear_y + th*0.7, tear_x - tw_bot, tear_y + th)
        t_path.lineTo(tear_x + tw_bot, tear_y + th)
        t_path.cubicTo(tear_x + tw_bot + r2, tear_y + th*0.7, tear_x + tw_top + r1, tear_y + th*0.3, tear_x + tw_top, tear_y)
        painter.drawPath(t_path)
    def draw(self, painter, cx, cy, opacity=1.0):
        base_x = cx + self.x_offset; base_y = cy + self.y_offset
        self.draw_background(painter, base_x, base_y, opacity)
        start_angle = -20 if self.is_right else 20; span_angle = -180
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(1, 10):
            glow_pen = QPen(CYAN_GLOW); glow_pen.setWidth(18 + i*3)
            painter.setPen(glow_pen); painter.setOpacity(opacity * (0.08 / i))
            painter.drawChord(int(base_x - self.w/2), int(base_y - self.h/2), int(self.w), int(self.h), start_angle * 16, span_angle * 16)
        painter.setOpacity(opacity)
        pen = QPen(CYAN_MAIN); pen.setWidth(18); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen); painter.setBrush(CYAN_MAIN)
        painter.drawChord(int(base_x - self.w/2), int(base_y - self.h/2), int(self.w), int(self.h), start_angle * 16, span_angle * 16)
        painter.setBrush(WHITE_SPARKLE); painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(base_x - 10), int(base_y - 20), int(self.w*0.35), int(self.w*0.35))
        painter.drawEllipse(int(base_x - self.w*0.3), int(base_y + 40), int(self.w*0.15), int(self.w*0.15))

class CryingEye(BaseEye):
    def __init__(self, w=220, h=160, tear_flow=0.0, x_offset=-190, y_offset=-100, tear_x_offset=0, tear_y_offset=0, tear_scale=1.0):
        super().__init__(w, h, x_offset, y_offset)
        self.tear_flow = tear_flow; self.tear_x_offset = tear_x_offset
        self.tear_y_offset = tear_y_offset; self.tear_scale = tear_scale
    def lerp(self, target, t):
        return CryingEye(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.tear_flow + (target.tear_flow - self.tear_flow)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t, self.tear_x_offset + (target.tear_x_offset - self.tear_x_offset)*t, self.tear_y_offset + (target.tear_y_offset - self.tear_y_offset)*t, self.tear_scale + (target.tear_scale - self.tear_scale)*t)
    def draw(self, painter, cx, cy, opacity=1.0):
        painter.setOpacity(opacity); painter.setPen(Qt.PenStyle.NoPen)
        base_x = cx + self.x_offset; base_y = cy + self.y_offset
        tear_start_x = base_x + self.tear_x_offset; tear_start_y = base_y + self.tear_y_offset
        grad = QLinearGradient(tear_start_x, tear_start_y, tear_start_x, tear_start_y + 400 * self.tear_scale)
        grad.setColorAt(0, CYAN_MAIN); grad.setColorAt(1, QColor(0, 217, 255, 0)) 
        painter.setBrush(grad)
        ripple_1 = math.sin(self.tear_flow * math.pi * 2) * 20 * self.tear_scale
        ripple_2 = math.cos(self.tear_flow * math.pi * 2) * 20 * self.tear_scale
        ts = self.tear_scale
        t_path = QPainterPath()
        t_path.moveTo(tear_start_x - self.w*0.4*ts, tear_start_y)
        t_path.cubicTo(tear_start_x - self.w*0.25*ts + ripple_1, tear_start_y + 200*ts, tear_start_x - self.w*0.45*ts + ripple_2, tear_start_y + 400*ts, tear_start_x - self.w*0.15*ts, tear_start_y + 500*ts)
        t_path.lineTo(tear_start_x + self.w*0.45*ts, tear_start_y + 500*ts)
        t_path.cubicTo(tear_start_x + self.w*0.35*ts + ripple_2, tear_start_y + 300*ts, tear_start_x + self.w*0.15*ts + ripple_1, tear_start_y + 100*ts, tear_start_x + self.w*0.4*ts, tear_start_y)
        painter.drawPath(t_path)
        painter.setBrush(CYAN_MAIN)
        painter.drawPie(int(base_x - self.w/2), int(base_y - self.h/2), int(self.w), int(self.h*2), 0, -180 * 16)
        painter.setBrush(WHITE_SPARKLE)
        painter.drawEllipse(int(base_x), int(base_y + self.h*0.2), int(self.w*0.35), int(self.w*0.35))
        painter.drawEllipse(int(base_x - self.w*0.3), int(base_y + self.h*0.65), int(self.w*0.15), int(self.w*0.15))

class SpiralEye(RoundedEyeFrame):
    def __init__(self, w=220, h=180, rot=0, x_offset=-180, y_offset=-100):
        super().__init__(w, h, x_offset, y_offset, radius=80)
        self.rot = rot; self.glow_color = ORANGE_GLOW; self.main_color = ORANGE_MAIN
    def lerp(self, target, t):
        return SpiralEye(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.rot + (target.rot - self.rot)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def draw_glow(self, painter, path, opacity):
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(1, 8):
            glow = QPen(self.glow_color); glow.setWidth(int(10 + i*4)); painter.setPen(glow); painter.setOpacity(opacity * (0.1/i))
            painter.drawPath(path)
    def draw_main_frame(self, painter, path, opacity):
        painter.setOpacity(opacity)
        pen = QPen(self.main_color); pen.setWidth(12); painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
    def draw_inner(self, painter, base_x, base_y, opacity):
        painter.translate(base_x, base_y); painter.rotate(self.rot)
        spiral_path = QPainterPath()
        for i in range(100):
            r = i * 0.6; angle = i * 0.2
            x = r * math.cos(angle); y = r * math.sin(angle)
            if i == 0: spiral_path.moveTo(x, y)
            else: spiral_path.lineTo(x, y)
        pen = QPen(self.main_color)
        pen.setWidth(10); pen.setCapStyle(Qt.PenCapStyle.RoundCap); painter.setPen(pen)
        painter.drawPath(spiral_path)

class StarEye(RoundedEyeFrame):
    def __init__(self, w=200, h=250, x_offset=-180, y_offset=-100):
        super().__init__(w, h, x_offset, y_offset, radius=80)
    def lerp(self, target, t):
        return StarEye(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.x_offset + (target.x_offset - self.x_offset)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def draw_inner(self, painter, base_x, base_y, opacity):
        painter.setBrush(WHITE_SPARKLE); painter.setPen(Qt.PenStyle.NoPen)
        def draw_star(sx, sy, size):
            path = QPainterPath()
            path.moveTo(sx, sy - size)
            path.quadTo(sx, sy, sx + size, sy)
            path.quadTo(sx, sy, sx, sy + size)
            path.quadTo(sx, sy, sx - size, sy)
            path.quadTo(sx, sy, sx, sy - size)
            painter.drawPath(path)
        draw_star(base_x - self.w/2 + self.w*0.35, base_y - self.h/2 + self.h*0.3, 40)
        draw_star(base_x - self.w/2 + self.w*0.7, base_y - self.h/2 + self.h*0.7, 20)
        painter.drawEllipse(int(base_x - self.w/2 + self.w*0.2), int(base_y - self.h/2 + self.h*0.6), 30, 30)

# ---------------------------------------------------------
# Modular Mouth Components
# ---------------------------------------------------------
class SmileMouth(FaceComponent):
    def __init__(self, w=150, curve=30, y_offset=280):
        self.w = w; self.curve = curve; self.y_offset = y_offset
    def lerp(self, target, t):
        return SmileMouth(self.w + (target.w - self.w)*t, self.curve + (target.curve - self.curve)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def draw(self, painter, cx, cy, opacity=1.0):
        painter.setOpacity(opacity)
        pen = QPen(CYAN_MAIN); pen.setWidth(20); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
        mouth_y = cy + self.y_offset
        path = QPainterPath()
        path.moveTo(cx - self.w/2, mouth_y)
        path.quadTo(cx, mouth_y + self.curve, cx + self.w/2, mouth_y)
        painter.drawPath(path)

class CapsuleMouth(FaceComponent):
    def __init__(self, w=150, h=30, y_offset=280):
        self.w = w; self.h = h; self.y_offset = y_offset
    def lerp(self, target, t):
        return CapsuleMouth(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def draw(self, painter, cx, cy, opacity=1.0):
        painter.setOpacity(opacity); painter.setPen(Qt.PenStyle.NoPen)
        mouth_y = cy + self.y_offset
        grad = QLinearGradient(cx, mouth_y, cx, mouth_y + self.h)
        grad.setColorAt(0, CYAN_MAIN); grad.setColorAt(1, BLUE_GRAD)
        painter.setBrush(grad)
        painter.drawRoundedRect(int(cx - self.w/2), int(mouth_y), int(self.w), int(self.h), int(self.h/2), int(self.h/2))

class SquigglyMouth(FaceComponent):
    def __init__(self, w=150, phase=0.0, y_offset=280):
        self.w = w; self.phase = phase; self.y_offset = y_offset
    def lerp(self, target, t):
        return SquigglyMouth(self.w + (target.w - self.w)*t, self.phase + (target.phase - self.phase)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def draw(self, painter, cx, cy, opacity=1.0):
        painter.setOpacity(opacity)
        pen = QPen(CYAN_MAIN); pen.setWidth(18); pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
        mouth_y = cy + self.y_offset
        
        # Calculate procedural lip wobble using cosine phase
        wobble_1 = -25 * math.cos(self.phase)
        wobble_2 = 25 * math.cos(self.phase)
        wobble_3 = 10 * math.cos(self.phase)
        
        path = QPainterPath()
        path.moveTo(cx - self.w/2, mouth_y)
        path.cubicTo(cx - self.w/4, mouth_y + wobble_1, cx, mouth_y + wobble_2, cx + self.w/4, mouth_y)
        path.lineTo(cx + self.w/2, mouth_y + wobble_3)
        painter.drawPath(path)

class BowlMouth(FaceComponent):
    def __init__(self, w=220, h=110, y_offset=280):
        self.w = w; self.h = h; self.y_offset = y_offset
    def lerp(self, target, t):
        return BowlMouth(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def draw(self, painter, cx, cy, opacity=1.0):
        painter.setOpacity(opacity); painter.setPen(Qt.PenStyle.NoPen)
        mouth_y = cy + self.y_offset
        grad = QLinearGradient(cx, mouth_y, cx, mouth_y + self.h)
        grad.setColorAt(0, CYAN_MAIN); grad.setColorAt(1, BLUE_GRAD)
        painter.setBrush(grad)
        path = QPainterPath()
        path.moveTo(cx - self.w/2, mouth_y); path.lineTo(cx + self.w/2, mouth_y)
        path.quadTo(cx, mouth_y + self.h * 1.5, cx - self.w/2, mouth_y)
        painter.drawPath(path)

class TalkingMouth(FaceComponent):
    def __init__(self, w=250, h=100, top_curve=0, y_offset=280):
        self.w = w; self.h = h; self.top_curve = top_curve; self.y_offset = y_offset
    def lerp(self, target, t):
        return TalkingMouth(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.top_curve + (target.top_curve - self.top_curve)*t, self.y_offset + (target.y_offset - self.y_offset)*t)
    def draw(self, painter, cx, cy, opacity=1.0):
        painter.setOpacity(opacity); painter.setPen(Qt.PenStyle.NoPen)
        mouth_y = cy + self.y_offset
        grad = QLinearGradient(cx, mouth_y, cx, mouth_y + self.h)
        grad.setColorAt(0, CYAN_MAIN); grad.setColorAt(1, BLUE_GRAD)
        painter.setBrush(grad)
        
        # 1. Draw the parametric mouth curve
        path = QPainterPath()
        path.moveTo(cx - self.w/2, mouth_y)
        path.quadTo(cx, mouth_y + self.top_curve, cx + self.w/2, mouth_y)
        path.quadTo(cx, mouth_y + self.h * 1.5, cx - self.w/2, mouth_y)
        painter.drawPath(path)

class VerticalMouth(FaceComponent):
    def __init__(self, w=100, h=140, y_offset=280, color_main=ORANGE_MAIN, color_grad=ORANGE_GRAD):
        self.w = w; self.h = h; self.y_offset = y_offset; self.color_main = color_main; self.color_grad = color_grad
    def lerp(self, target, t):
        return VerticalMouth(self.w + (target.w - self.w)*t, self.h + (target.h - self.h)*t, self.y_offset + (target.y_offset - self.y_offset)*t, self.color_main, self.color_grad)
    def draw(self, painter, cx, cy, opacity=1.0):
        painter.setOpacity(opacity); painter.setPen(Qt.PenStyle.NoPen)
        mouth_y = cy + self.y_offset
        grad = QLinearGradient(cx, mouth_y - self.h/2, cx, mouth_y + self.h/2)
        grad.setColorAt(0, self.color_main); grad.setColorAt(1, self.color_grad)
        painter.setBrush(grad)
        painter.drawRoundedRect(int(cx - self.w/2), int(mouth_y - self.h/2), int(self.w), int(self.h), 40, 40)
