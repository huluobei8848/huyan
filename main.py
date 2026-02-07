import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


from src.core.config import config_manager

from src.core.timer_service import TimerService
from src.ui.overlay import OverlayWindow
from src.ui.settings import SettingsDialog

class EyeProtectionApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Load Config
        self.config = config_manager
        
        # Service
        self.timer_service = TimerService()
        self.timer_service.work_finished.connect(self.show_overlay)
        self.timer_service.rest_finished.connect(self.timer_service.start_work) # Loop back
        
        # Windows
        self.overlays = []
        self.settings_dialog = None

        # Setup System Tray
        self.setup_tray()
        
        # Start
        self.timer_service.start_work()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setToolTip("护眼工具 - 运行中")
        
        # Use a standard icon for now if custom one missing
        style = self.app.style()
        icon = style.standardIcon(style.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        self.tray_icon.setVisible(True)

        # Tray Menu
        self.menu = QMenu()
        
        self.action_rest_now = QAction("立即休息")
        self.action_rest_now.triggered.connect(self.show_overlay)
        
        self.action_settings = QAction("设置")
        self.action_settings.triggered.connect(self.show_settings)
        
        self.action_exit = QAction("退出")
        self.action_exit.triggered.connect(self.exit_app)

        self.menu.addAction(self.action_rest_now)
        self.menu.addSeparator()
        self.menu.addAction(self.action_settings)
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)


        self.tray_icon.setContextMenu(self.menu)

        # Show settings on launch for better visibility
        self.show_settings()

    def show_settings(self):
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog()
        
        # Reload current settings in case they changed externally or were reset
        self.settings_dialog.load_settings()
        
        if self.settings_dialog.exec():
            # Settings saved. 
            # If timer duration changed, we might need to restart timer?
            # For simplicity, we just let the next cycle pick it up, 
            # or we could restart the timer service if the user wants immediate effect.
            # Let's restart the work timer to apply new interval immediately if in work mode.
            if not self.overlays: # In work mode
                self.timer_service.start_work()

    def show_overlay(self):
        print("Showing overlay...")
        # Clear existing overlays
        self.close_overlays()
        
        # Create an overlay for each screen
        screens = self.app.screens()
        for screen in screens:
            overlay = OverlayWindow(screen.geometry())
            overlay.finished.connect(self.on_overlay_finished)
            overlay.show()
            self.overlays.append(overlay)

    def close_overlays(self):
        for overlay in self.overlays:
            overlay.close()
            overlay.finished.disconnect(self.on_overlay_finished) # Disconnect to prevent double signals
        self.overlays.clear()

    def on_overlay_finished(self):
        # When one overlay finishes (e.g. user pressed ESC or time up), 
        # we should close all and restart work timer.
        # Check if we are already closing to avoid recursion
        if not self.overlays:
            return
            
        print("Rest over.")
        self.close_overlays()
        self.timer_service.on_rest_finished()

    def exit_app(self):
        self.timer_service.stop()
        self.close_overlays()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = EyeProtectionApp()
    app.run()
