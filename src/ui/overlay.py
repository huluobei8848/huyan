import sys
import os
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import QPixmap, QImage, QKeyEvent, QAction
from PIL import Image, ImageFilter, ImageEnhance

# Ensure src is in path for imports if run directly
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.core.config import config_manager

class OverlayWindow(QWidget):
    finished = pyqtSignal()  # Signal when rest is over or exited

    def __init__(self, screen_geometry=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Determine geometry
        if screen_geometry:
            self.setGeometry(screen_geometry)
        else:
            self.showFullScreen()


        self.esc_start_time = 0
        self.esc_timer = QTimer()
        self.esc_timer.setInterval(100) # Check every 100ms
        self.esc_timer.timeout.connect(self.check_esc_long_press)
        
        self.rest_duration = config_manager.get("rest_duration_seconds", 20)
        self.time_left = self.rest_duration
        
        self.init_ui()
        self.setup_timer()
        
        # Load and blur image
        self.set_background_image()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.timer_label = QLabel(f"休息一下: {self.time_left}s")
        self.timer_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 100);
                padding: 20px;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.timer_label)
        
        self.hint_label = QLabel("长按 ESC 5秒可紧急退出")
        self.hint_label.setStyleSheet("color: rgba(255, 255, 255, 150); font-size: 16px; margin-top: 20px;")
        layout.addWidget(self.hint_label)

        self.setLayout(layout)


    def set_background_image(self):
        wallpapers = config_manager.get("wallpapers", [])
        mode = config_manager.get("wallpaper_mode", "cycle")
        
        self.image_queue = []
        
        if not wallpapers:
            # Fallback to default color if no wallpapers
            self.create_placeholder_bg()
            return

        if mode == "single":
            selected = config_manager.get("current_wallpaper", "")
            if selected and selected in wallpapers:
                self.image_queue = [selected]
            else:
                self.image_queue = [wallpapers[0]] # Fallback
        else: # cycle
            self.image_queue = wallpapers.copy()
            # Random shuffle maybe? User asked for "cycle", usually implies order.
            # But "轮回" serves well in order.

        self.current_image_index = 0
        self.update_background()
        
        if mode == "cycle" and len(self.image_queue) > 1:
            interval = config_manager.get("cycle_interval_seconds", 5)
            self.cycle_timer = QTimer()
            self.cycle_timer.timeout.connect(self.next_background)
            self.cycle_timer.start(interval * 1000)

    def next_background(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_queue)
        self.update_background()

    def update_background(self):
        if not self.image_queue:
            return

        path = self.image_queue[self.current_image_index]
        try:
            img = Image.open(path)
            # Resize logic to cover screen? 
            # Pillow resize might be slow for large images on main thread, 
            # but usually fine for a few mb.
            # For better performance, we can just let Qt scale using aspect ratio.
            # But we need to blur it.
            
            # Simple resize to screen size to save blur performance
            img = img.resize((self.width(), self.height()))
            
            blur_radius = config_manager.get("blur_radius", 15)
            if blur_radius > 0:
                img = img.filter(ImageFilter.GaussianBlur(blur_radius))
            
            data = img.tobytes("raw", "RGB")
            qim = QImage(data, img.size[0], img.size[1], QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qim)
            
            if not hasattr(self, 'bg_label'):
                self.bg_label = QLabel(self)
                self.bg_label.setScaledContents(True)
                self.bg_label.resize(self.width(), self.height())
                self.bg_label.lower()

            self.bg_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            self.create_placeholder_bg()

    def create_placeholder_bg(self):
        # Fallback background
        try:
            img = Image.new('RGB', (self.width(), self.height()), color = (73, 109, 137))
            blur_radius = config_manager.get("blur_radius", 15)
            if blur_radius > 0:
                img = img.filter(ImageFilter.GaussianBlur(blur_radius))
            data = img.tobytes("raw", "RGB")
            qim = QImage(data, img.size[0], img.size[1], QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qim)
            
            if not hasattr(self, 'bg_label'):
                self.bg_label = QLabel(self)
                self.bg_label.setScaledContents(True)
                self.bg_label.resize(self.width(), self.height())
                self.bg_label.lower()

            self.bg_label.setPixmap(pixmap)
        except:
             self.setStyleSheet("background-color: rgba(50, 50, 50, 200);")

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        
        # Focus enforcement timer
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self.enforce_focus)
        self.focus_timer.start(500) # Every 500ms

    def enforce_focus(self):
        self.raise_()
        self.activateWindow()

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.setText(f"休息一下: {self.time_left}s")
        if self.time_left <= 0:
            self.finish_rest()


    def finish_rest(self):
        self.timer.stop()
        self.focus_timer.stop()
        if hasattr(self, 'cycle_timer'):
            self.cycle_timer.stop()
        self.close()
        self.finished.emit()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            if not event.isAutoRepeat():
                import time
                self.esc_start_time = time.time()
                self.esc_timer.start()
                print("ESC pressed")
        # Block other keys
        # return super().keyPressEvent(event) 

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            if not event.isAutoRepeat():
                self.esc_timer.stop()
                self.hint_label.setText("长按 ESC 5秒可紧急退出")
                print("ESC released")

    def check_esc_long_press(self):
        import time
        elapsed = time.time() - self.esc_start_time
        if elapsed >= 5:
            print("Emergency exit triggered")
            self.finish_rest()
        else:
            remaining = 5.0 - elapsed
            self.hint_label.setText(f"紧急退出: {remaining:.1f}s")
    
    # Block mouse events
    def mousePressEvent(self, event):
        pass

    def resizeEvent(self, event):
        if hasattr(self, 'bg_label'):
            self.bg_label.resize(self.width(), self.height())
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    sys.exit(app.exec())
