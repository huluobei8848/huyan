from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.core.config import config_manager

class TimerService(QObject):
    work_finished = pyqtSignal() # Time to rest
    rest_finished = pyqtSignal() # Time to work

    def __init__(self):
        super().__init__()
        self.work_timer = QTimer()
        self.work_timer.setSingleShot(True)
        self.work_timer.timeout.connect(self.on_work_finished)

        # Rest timer is handled by the OverlayWindow logic usually, 
        # but the centralized manager should know when it ends.
        # Actually, if OverlayWindow handles the rest countdown, 
        # TimerService just needs to trigger the start of rest 
        # and wait for a signal that rest is over.
        
    def start_work(self):
        minutes = config_manager.get("work_interval_minutes", 45)
        print(f"Starting work timer for {minutes} minutes.")
        self.work_timer.start(minutes * 60 * 1000) 

    def on_work_finished(self):
        print("Work finished, triggering rest.")
        self.work_finished.emit()

    def on_rest_finished(self):
        print("Rest finished, restarting work timer.")
        self.rest_finished.emit()
        self.start_work()

    def stop(self):
        self.work_timer.stop()
