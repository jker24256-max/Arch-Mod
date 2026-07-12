import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox, QGroupBox,
    QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap

# Tactical Color Scheme
STYLE_SHEET = """
QMainWindow {
    background-color: #0B0C10;
}
QWidget {
    background-color: #0B0C10;
    color: #EDF2F4;
    font-family: 'Courier New', monospace;
    font-size: 13px;
}
QGroupBox {
    background-color: #1F2833;
    border: 1px solid #8D99AE;
    border-radius: 8px;
    margin-top: 10px;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 10px;
    color: #D90429;
    font-weight: bold;
}
QPushButton {
    background-color: #1F2833;
    border: 1px solid #D90429;
    border-radius: 4px;
    color: #EDF2F4;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #D90429;
    color: #0B0C10;
}
QPushButton:pressed {
    background-color: #EF233C;
}
QScrollArea {
    border: 1px solid #8D99AE;
    border-radius: 6px;
    background-color: #151A21;
}
"""

DEFAULT_WALLPAPERS_DIR = "/usr/share/backgrounds"
CONFIG_DIR = os.path.expanduser("~/.config/jker")
os.makedirs(CONFIG_DIR, exist_ok=True)
WALLPAPER_CONFIG_PATH = os.path.join(CONFIG_DIR, "wallpaper")

class WallpaperTile(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Image preview
        self.img_label = QLabel()
        self.img_label.setFixedSize(160, 100)
        self.img_label.setScaledContents(True)
        
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.img_label.setText("No Image")
            self.img_label.setStyleSheet("border: 1px solid #8D99AE; background-color: #151A21; color: #8D99AE;")
        else:
            self.img_label.setPixmap(pixmap.scaled(QSize(160, 100), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        
        self.layout.addWidget(self.img_label)

        # Name label
        name = os.path.basename(file_path)
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("color: #EDF2F4; font-size: 11px;")
        self.layout.addWidget(self.name_label)

        self.setStyleSheet("border: 1px solid #1F2833; border-radius: 4px; padding: 5px;")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parentWidget().parentWidget().parentWidget().parentWidget().select_wallpaper(self)

    def set_selected(self, selected):
        if selected:
            self.setStyleSheet("border: 2px solid #D90429; border-radius: 4px; padding: 5px; background-color: #1F2833;")
        else:
            self.setStyleSheet("border: 1px solid #1F2833; border-radius: 4px; padding: 5px;")


class WallpaperManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_tile = None
        self.wallpapers_dir = DEFAULT_WALLPAPERS_DIR
        if not os.path.exists(self.wallpapers_dir):
            # Fallback path if running locally outside Arch environment
            self.wallpapers_dir = os.path.join(os.path.dirname(__file__), "../../branding/backgrounds")
            self.wallpapers_dir = os.path.abspath(self.wallpapers_dir)
            os.makedirs(self.wallpapers_dir, exist_ok=True)
            
        self.setWindowTitle("WALLPAPER MANAGER // JKER OS DESKTOP CUSTOMIZATION")
        self.setMinimumSize(850, 550)
        self.setStyleSheet(STYLE_SHEET)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Heading
        title = QLabel("JKER OS // WALLPAPER CONFIGURATION")
        title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #D90429; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Scrollable grid of wallpapers
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15)
        
        scroll_area.setWidget(self.grid_widget)
        main_layout.addWidget(scroll_area)
        
        # Selected wallpaper details pane
        self.info_box = QGroupBox("ACTIVE WORKSPACE WALLPAPER")
        info_layout = QHBoxLayout(self.info_box)
        
        self.selected_label = QLabel("No wallpaper selected. Click a preview above.")
        self.selected_label.setWordWrap(True)
        info_layout.addWidget(self.selected_label, 3)
        
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("APPLY WALLPAPER")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.apply_wallpaper)
        btn_layout.addWidget(self.apply_btn)
        
        self.browse_btn = QPushButton("BROWSE CUSTOM...")
        self.browse_btn.clicked.connect(self.browse_custom_wallpaper)
        btn_layout.addWidget(self.browse_btn)
        
        info_layout.addLayout(btn_layout, 2)
        main_layout.addWidget(self.info_box)
        
        self.load_wallpapers()

    def load_wallpapers(self):
        # Clear existing grid items
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                
        # Scan folder for wallpapers
        supported_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
        wallpapers = []
        if os.path.exists(self.wallpapers_dir):
            for filename in os.listdir(self.wallpapers_dir):
                if filename.lower().endswith(supported_exts):
                    wallpapers.append(os.path.join(self.wallpapers_dir, filename))
                    
        # Populate grid layout
        columns = 4
        for idx, path in enumerate(wallpapers):
            tile = WallpaperTile(path, self.grid_widget)
            row = idx // columns
            col = idx % columns
            self.grid_layout.addWidget(tile, row, col)
            
            # Auto-select currently configured wallpaper if match
            if os.path.exists(WALLPAPER_CONFIG_PATH):
                try:
                    with open(WALLPAPER_CONFIG_PATH, "r") as f:
                        current_wp = f.read().strip()
                    if current_wp == path:
                        self.select_wallpaper(tile)
                except Exception:
                    pass

    def select_wallpaper(self, tile):
        if self.selected_tile:
            self.selected_tile.set_selected(False)
            
        self.selected_tile = tile
        self.selected_tile.set_selected(True)
        self.selected_label.setText(f"SELECTED: {os.path.basename(tile.file_path)}")
        self.apply_btn.setEnabled(True)

    def browse_custom_wallpaper(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Custom Image Wallpaper", "", "Images (*.jpg *.jpeg *.png *.bmp *.webp)")
        if path:
            # Copy to wallpapers directory
            dest = os.path.join(self.wallpapers_dir, os.path.basename(path))
            try:
                import shutil
                shutil.copy(path, dest)
                self.load_wallpapers()
                # Find the tile matching the newly added destination and select it
                for i in range(self.grid_layout.count()):
                    widget = self.grid_layout.itemAt(i).widget()
                    if isinstance(widget, WallpaperTile) and widget.file_path == dest:
                        self.select_wallpaper(widget)
                        break
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import wallpaper: {e}")

    def apply_wallpaper(self):
        if not self.selected_tile:
            return
            
        path = self.selected_tile.file_path
        
        # Save selection persistently
        try:
            with open(WALLPAPER_CONFIG_PATH, "w") as f:
                f.write(path)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not write wallpaper config: {e}")
            
        # Apply using swww
        try:
            # swww is standard wallpaper tool on Hyprland/Wayland
            cmd = f"swww img {path} --transition-type outer --transition-pos 0.85,0.85"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                QMessageBox.information(self, "Success", "Wallpaper applied to live session successfully.")
            else:
                # If swww daemon is not running, try to initialize it first
                subprocess.run("swww init", shell=True)
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if res.returncode == 0:
                    QMessageBox.information(self, "Success", "Wallpaper applied after initializing swww daemon.")
                else:
                    QMessageBox.information(self, "Wallpaper Set", f"Selection saved persistently. (Note: swww was not active to apply it dynamically: {res.stderr})")
        except Exception as e:
            QMessageBox.information(self, "Wallpaper Set", f"Selection saved persistently. (Command exec failed: {e})")

def main():
    app = QApplication(sys.argv)
    window = WallpaperManagerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
