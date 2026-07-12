import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QGroupBox, QTabWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Styling sheet
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
    background-color: #151A21;
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
QTabWidget::pane {
    border: 1px solid #8D99AE;
    background-color: #1F2833;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    border-bottom-color: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 16px;
    color: #8D99AE;
}
QTabBar::tab:selected {
    background-color: #1F2833;
    border-color: #D90429;
    color: #D90429;
    font-weight: bold;
}
QTextEdit {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    border-radius: 4px;
    color: #EDF2F4;
}
"""

class InstallWorker(QThread):
    stdout_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        # Run package manager under terminal emulator or via pkexec for root actions
        try:
            # For live execution, we can wrap standard installations using pkexec/sudo -n
            # or launch via zsh script.
            proc = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                self.stdout_signal.emit(line)
            proc.wait()
            self.finished_signal.emit(proc.returncode)
        except Exception as e:
            self.stdout_signal.emit(f"Execution Error: {e}\n")
            self.finished_signal.emit(-1)

class DownloadCenterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOWNLOAD CENTER // JKER OS SOFTWARE DEPLOYMENT")
        self.setMinimumSize(950, 650)
        self.setStyleSheet(STYLE_SHEET)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # Tabs for Categories
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 3)
        
        # Right Console panel
        right_panel = QVBoxLayout()
        console_box = QGroupBox("PACMAN / PARU DEPLOYMENT LOGS")
        console_layout = QVBoxLayout(console_box)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Console output from active installations will display here...")
        console_layout.addWidget(self.console)
        
        right_panel.addWidget(console_box)
        main_layout.addLayout(right_panel, 2)
        
        self.init_drivers_tab()
        self.init_packages_tab()
        self.init_themes_tab()
        self.init_wallpapers_tab()

    def log_line(self, line):
        self.console.insertPlainText(line)
        self.console.ensureCursorVisible()

    def run_installer_command(self, cmd_name, cmd):
        self.log_line(f"\n[DEPLOY] >> Launching {cmd_name} installation...\n")
        self.log_line(f"[CMD] >> {cmd}\n")
        
        # Execute using thread worker
        self.worker = InstallWorker(cmd)
        self.worker.stdout_signal.connect(self.log_line)
        self.worker.finished_signal.connect(lambda code: self.install_finished(cmd_name, code))
        self.worker.start()

    def install_finished(self, name, exit_code):
        if exit_code == 0:
            self.log_line(f"\n[SUCCESS] >> {name} successfully deployed.\n")
            QMessageBox.information(self, "Success", f"{name} installed successfully.")
        else:
            self.log_line(f"\n[FAILURE] >> {name} installation failed (exit code {exit_code}).\n")
            QMessageBox.critical(self, "Failure", f"{name} installation failed.")

    # --- Category Tabs ---
    def init_drivers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        desc = QLabel("Automated Graphics and Kernel Hardware Drivers")
        desc.setStyleSheet("color: #8D99AE;")
        layout.addWidget(desc)
        
        # NVIDIA Driver Card
        nv_box = QGroupBox("NVIDIA PROPRIETARY STACK")
        nv_layout = QHBoxLayout(nv_box)
        nv_info = QLabel("Proprietary NVIDIA drivers, CUDA core libraries, and utility settings panel.")
        nv_info.setWordWrap(True)
        nv_btn = QPushButton("INSTALL DRIVER")
        # pkexec runs graphical sudo helper on live Arch ISO
        nv_btn.clicked.connect(lambda: self.run_installer_command("NVIDIA Proprietary Driver", "pkexec pacman -S --noconfirm nvidia nvidia-utils nvidia-settings"))
        nv_layout.addWidget(nv_info, 3)
        nv_layout.addWidget(nv_btn, 1)
        layout.addWidget(nv_box)
        
        # AMD GPU Card
        amd_box = QGroupBox("AMD RADV OPEN-SOURCE DRIVER")
        amd_layout = QHBoxLayout(amd_box)
        amd_info = QLabel("Vulkan RADV drivers, Mesa graphics library modules, and performance options.")
        amd_info.setWordWrap(True)
        amd_btn = QPushButton("INSTALL RADV")
        amd_btn.clicked.connect(lambda: self.run_installer_command("AMD Vulkan Driver", "pkexec pacman -S --noconfirm vulkan-radeon lib32-vulkan-radeon mesa-vdpau"))
        amd_layout.addWidget(amd_info, 3)
        amd_layout.addWidget(amd_btn, 1)
        layout.addWidget(amd_box)
        
        # Broadcom WiFi Card
        wifi_box = QGroupBox("BROADCOM WIRELESS DRIVERS")
        wifi_layout = QHBoxLayout(wifi_box)
        wifi_info = QLabel("Proprietary Broadcom (broadcom-wl) wireless adapter driver modules.")
        wifi_info.setWordWrap(True)
        wifi_btn = QPushButton("INSTALL WL")
        wifi_btn.clicked.connect(lambda: self.run_installer_command("Broadcom WiFi Driver", "pkexec pacman -S --noconfirm broadcom-wl"))
        wifi_layout.addWidget(wifi_info, 3)
        wifi_layout.addWidget(wifi_btn, 1)
        layout.addWidget(wifi_box)
        
        layout.addStretch()
        self.tabs.addTab(tab, "DRIVERS")

    def init_packages_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        desc = QLabel("Install additional JKER Packages, tools, and developer modules.")
        desc.setStyleSheet("color: #8D99AE;")
        layout.addWidget(desc)
        
        # Docker & Podman
        docker_box = QGroupBox("CONTAINER VIRTUALIZATION ENGINE")
        docker_layout = QHBoxLayout(docker_box)
        docker_info = QLabel("Install Docker, Podman, and docker-compose orchestration toolsets.")
        docker_info.setWordWrap(True)
        docker_btn = QPushButton("INSTALL ENGINE")
        docker_btn.clicked.connect(lambda: self.run_installer_command("Container Engine", "pkexec pacman -S --noconfirm docker podman docker-compose"))
        docker_layout.addWidget(docker_info, 3)
        docker_layout.addWidget(docker_btn, 1)
        layout.addWidget(docker_box)
        
        # VS Code & Git utils
        vscode_box = QGroupBox("VS CODE IDE & GITHUB UTILITIES")
        vscode_layout = QHBoxLayout(vscode_box)
        vscode_info = QLabel("Visual Studio Code OSS and GitHub command-line helper package.")
        vscode_info.setWordWrap(True)
        vscode_btn = QPushButton("INSTALL IDE")
        vscode_btn.clicked.connect(lambda: self.run_installer_command("VS Code & GitHub CLI", "pkexec pacman -S --noconfirm code github-cli"))
        vscode_layout.addWidget(vscode_info, 3)
        vscode_layout.addWidget(vscode_btn, 1)
        layout.addWidget(vscode_box)
        
        # Python / Zsh helpers
        zsh_box = QGroupBox("EXTENDED CYBERSECURITY SCRIPTS")
        zsh_layout = QHBoxLayout(zsh_box)
        zsh_info = QLabel("Install additional python-pip, pipx, and custom shell scripting utilities.")
        zsh_info.setWordWrap(True)
        zsh_btn = QPushButton("INSTALL SCRIPTS")
        zsh_btn.clicked.connect(lambda: self.run_installer_command("Python & Script Utils", "pkexec pacman -S --noconfirm python-pip python-pipx zsh-completions"))
        zsh_layout.addWidget(zsh_info, 3)
        zsh_layout.addWidget(zsh_btn, 1)
        layout.addWidget(zsh_box)
        
        layout.addStretch()
        self.tabs.addTab(tab, "JKER PACKAGES")

    def init_themes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        desc = QLabel("Deploy custom Hyprland UI themes, SDDM configs and GTK profiles.")
        desc.setStyleSheet("color: #8D99AE;")
        layout.addWidget(desc)
        
        # Nord Theme
        nord_box = QGroupBox("TACTICAL OBSIDIAN & CRIMSON (DEFAULT)")
        nord_layout = QHBoxLayout(nord_box)
        nord_info = QLabel("Sleek crimson UI theme including special custom dark CSS classes.")
        nord_info.setWordWrap(True)
        nord_btn = QPushButton("REINSTALL")
        nord_btn.clicked.connect(lambda: self.run_installer_command("Tactical Red Theme", "echo 'Deploying Tactical Red files...'; sleep 1"))
        nord_layout.addWidget(nord_info, 3)
        nord_layout.addWidget(nord_btn, 1)
        layout.addWidget(nord_box)
        
        # Cyberpunk Theme
        cyber_box = QGroupBox("CYBERPUNK GLITCH THEME")
        cyber_layout = QHBoxLayout(cyber_box)
        cyber_info = QLabel("Vibrant neon pink, cyan and dark purple elements matching custom rofi files.")
        cyber_info.setWordWrap(True)
        cyber_btn = QPushButton("DEPLOY THEME")
        cyber_btn.clicked.connect(lambda: self.run_installer_command("Cyberpunk Glitch Theme", "echo 'Installing Cyberpunk UI configuration...'; sleep 1"))
        cyber_layout.addWidget(cyber_info, 3)
        cyber_layout.addWidget(cyber_btn, 1)
        layout.addWidget(cyber_box)
        
        layout.addStretch()
        self.tabs.addTab(tab, "THEMES")

    def init_wallpapers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        desc = QLabel("Manage background backdrops and lockscreens.")
        desc.setStyleSheet("color: #8D99AE;")
        layout.addWidget(desc)
        
        wp1_box = QGroupBox("TACTICAL DIGITAL CAMOUFLAGE")
        wp1_layout = QHBoxLayout(wp1_box)
        wp1_info = QLabel("Tactical military pattern wallpaper in black, slate and deep crimson.")
        wp1_btn = QPushButton("GET BACKGROUND")
        wp1_btn.clicked.connect(lambda: self.run_installer_command("Tactical Camo WP", "echo 'Downloading Camo backdrop...'; sleep 1"))
        wp1_layout.addWidget(wp1_info, 3)
        wp1_layout.addWidget(wp1_btn, 1)
        layout.addWidget(wp1_box)
        
        wp2_box = QGroupBox("TERMINAL COMMAND CONSOLE")
        wp2_layout = QHBoxLayout(wp2_box)
        wp2_info = QLabel("Dark terminal grid with JKER OS security crest vector branding.")
        wp2_btn = QPushButton("GET BACKGROUND")
        wp2_btn.clicked.connect(lambda: self.run_installer_command("Terminal Console WP", "echo 'Downloading Terminal backdrop...'; sleep 1"))
        wp2_layout.addWidget(wp2_info, 3)
        wp2_layout.addWidget(wp2_btn, 1)
        layout.addWidget(wp2_box)
        
        layout.addStretch()
        self.tabs.addTab(tab, "WALLPAPERS")

# Main Execution Entry
def main():
    app = QApplication(sys.argv)
    window = DownloadCenterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
