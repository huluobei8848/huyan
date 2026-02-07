
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QLineEdit, QPushButton, QFileDialog, 
                             QSlider, QFormLayout, QListWidget, QRadioButton, 
                             QButtonGroup, QTabWidget, QWidget, QListWidgetItem,
                             QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from src.core.config import config_manager
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("护眼工具设置")
        self.setFixedSize(700, 500) # Slightly larger for cards
        self.setup_style()
        self.init_ui()
        self.load_settings()

    def setup_style(self):
        # A simple modern dark-ish style
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #dcdcdc;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #e1e4e8;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                font-weight: bold;
                border-bottom: 2px solid #0078d4;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton#danger {
                background-color: #d13438;
            }
            QPushButton#danger:hover {
                background-color: #a80000;
            }
            QLineEdit, QSpinBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background: white;
            }
            QListWidget {
                border: 1px solid #ccc;
                background-color: #f9f9f9;
            }
            QListWidget::item {
                border-radius: 5px;
                padding: 5px;
                color: #333;
            }
            QListWidget::item:selected {
                background-color: #e6f7ff;
                border: 1px solid #1890ff;
                color: #333;
            }
        """)

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_general_tab(), "常规设置")
        self.tabs.addTab(self.create_wallpaper_tab(), "壁纸管理")
        
        main_layout.addWidget(self.tabs)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存配置")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setMinimumHeight(35)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet("background-color: #888; color: white;")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def create_general_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Work Interval
        self.work_interval_spin = QSpinBox()
        self.work_interval_spin.setRange(1, 120)
        self.work_interval_spin.setSuffix(" 分钟")
        layout.addRow("💼 工作时长:", self.work_interval_spin)

        # Rest Duration
        self.rest_duration_spin = QSpinBox()
        self.rest_duration_spin.setRange(5, 300)
        self.rest_duration_spin.setSuffix(" 秒")
        layout.addRow("☕ 休息时长:", self.rest_duration_spin)

        # Blur Radius
        self.blur_radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_radius_slider.setRange(0, 50)
        layout.addRow("🌫️ 背景模糊度:", self.blur_radius_slider)

        widget.setLayout(layout)
        return widget

    def create_wallpaper_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Mode Selection
        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup()
        
        self.radio_single = QRadioButton("单张固定")
        self.radio_cycle = QRadioButton("多图轮播")
        self.mode_group.addButton(self.radio_single)
        self.mode_group.addButton(self.radio_cycle)
        
        mode_layout.addWidget(QLabel("展示模式:"))
        mode_layout.addWidget(self.radio_single)
        mode_layout.addWidget(self.radio_cycle)
        mode_layout.addStretch()
        
        layout.addLayout(mode_layout)

        # Cycle Settings
        cycle_layout = QHBoxLayout()
        self.cycle_spin = QSpinBox()
        self.cycle_spin.setRange(1, 600)
        self.cycle_spin.setSuffix(" 秒")
        cycle_layout.addWidget(QLabel("轮播间隔:"))
        cycle_layout.addWidget(self.cycle_spin)
        cycle_layout.addStretch()
        layout.addLayout(cycle_layout)

        # List Management
        layout.addWidget(QLabel("壁纸列表 (拖入或点击添加):"))
        self.wallpaper_list = QListWidget()
        self.wallpaper_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        # Card View Settings
        self.wallpaper_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.wallpaper_list.setIconSize(QSize(160, 100))
        self.wallpaper_list.setGridSize(QSize(180, 140))
        self.wallpaper_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.wallpaper_list.setMovement(QListWidget.Movement.Static)
        self.wallpaper_list.setSpacing(10)
        
        layout.addWidget(self.wallpaper_list)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加壁纸...")
        self.add_btn.clicked.connect(self.add_wallpapers)
        
        self.remove_btn = QPushButton("移除选中")
        self.remove_btn.setObjectName("danger")
        self.remove_btn.clicked.connect(self.remove_wallpaper)
        
        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.setStyleSheet("background-color: #d13438;")
        self.clear_btn.clicked.connect(self.clear_wallpapers)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        return widget

    def create_wallpaper_item(self, path):
        item = QListWidgetItem()
        item.setText(os.path.basename(path))
        item.setToolTip(path)
        item.setData(Qt.ItemDataRole.UserRole, path)
        
        # Create thumbnail
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            # Scale to icon size, keeping aspect ratio, making it cover the square slightly or fit
            # We want a nice thumbnail.
            scaled = pixmap.scaled(160, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            item.setIcon(QIcon(scaled))
        else:
            # Placeholder or broken image icon
            pass 
            
        return item

    def load_settings(self):
        # General
        self.work_interval_spin.setValue(config_manager.get("work_interval_minutes", 45))
        self.rest_duration_spin.setValue(config_manager.get("rest_duration_seconds", 20))
        self.blur_radius_slider.setValue(config_manager.get("blur_radius", 15))

        # Wallpaper
        wallpapers = config_manager.get("wallpapers", [])
        self.wallpaper_list.clear()
        
        # Find current selection to highlight it
        current_wallpaper = config_manager.get("current_wallpaper", "")
        
        for path in wallpapers:
            if os.path.exists(path):
                item = self.create_wallpaper_item(path)
                self.wallpaper_list.addItem(item)
                if path == current_wallpaper:
                    self.wallpaper_list.setCurrentItem(item)

        mode = config_manager.get("wallpaper_mode", "cycle")
        if mode == "single":
            self.radio_single.setChecked(True)
        else:
            self.radio_cycle.setChecked(True)
            
        self.cycle_spin.setValue(config_manager.get("cycle_interval_seconds", 5))

    def add_wallpapers(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "选择壁纸", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if files:
            # Check existing to avoid duplicates
            existing = []
            for i in range(self.wallpaper_list.count()):
                 existing.append(self.wallpaper_list.item(i).data(Qt.ItemDataRole.UserRole))
            
            for f in files:
                if f not in existing:
                    item = self.create_wallpaper_item(f)
                    self.wallpaper_list.addItem(item)

    def remove_wallpaper(self):
        row = self.wallpaper_list.currentRow()
        if row >= 0:
            self.wallpaper_list.takeItem(row)

    def clear_wallpapers(self):
        self.wallpaper_list.clear()

    def save_settings(self):
        # General
        config_manager.set("work_interval_minutes", self.work_interval_spin.value())
        config_manager.set("rest_duration_seconds", self.rest_duration_spin.value())
        config_manager.set("blur_radius", self.blur_radius_slider.value())

        # Wallpaper
        wallpapers = []
        for i in range(self.wallpaper_list.count()):
            path = self.wallpaper_list.item(i).data(Qt.ItemDataRole.UserRole)
            wallpapers.append(path)
            
        config_manager.set("wallpapers", wallpapers)
        
        mode = "single" if self.radio_single.isChecked() else "cycle"
        config_manager.set("wallpaper_mode", mode)
        config_manager.set("cycle_interval_seconds", self.cycle_spin.value())
        
        if mode == "single":
            current_item = self.wallpaper_list.currentItem()
            if current_item:
                config_manager.set("current_wallpaper", current_item.data(Qt.ItemDataRole.UserRole))
            elif wallpapers:
                config_manager.set("current_wallpaper", wallpapers[0])
                QMessageBox.information(self, "提示", "单张模式下未选中壁纸，默认使用第一张。")
        
        self.accept()
