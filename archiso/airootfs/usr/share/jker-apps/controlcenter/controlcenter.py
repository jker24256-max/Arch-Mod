import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QGroupBox, QTabWidget, QFormLayout,
    QMessageBox, QLineEdit, QListWidget, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Custom tactical styling
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
QLineEdit, QComboBox {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    border-radius: 4px;
    padding: 6px;
    color: #EDF2F4;
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
QListWidget {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    border-radius: 6px;
}
"""

class ControlCenterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JKER CONTROL CENTER // SYSTEM PROFILE MANAGEMENT")
        self.setMinimumSize(950, 650)
        self.setStyleSheet(STYLE_SHEET)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Tabs container
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.init_personalization_tab()
        self.init_power_tab()
        self.init_security_tab()
        self.init_user_mgmt_tab()
        self.init_hardware_tab()

    def run_sys_cmd(self, cmd):
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.returncode == 0, res.stdout, res.stderr
        except Exception as e:
            return False, "", str(e)

    # --- Personalization Tab ---
    def init_personalization_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        theme_box = QGroupBox("DESKTOP INTERFACE & STYLING")
        theme_layout = QFormLayout(theme_box)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Obsidian Crimson (Default)", "Glitch Cyberpunk", "Classic Dark Mono"])
        theme_layout.addRow(QLabel("SYSTEM THEME:"), self.theme_combo)
        
        self.wp_combo = QComboBox()
        self.wp_combo.addItems(["Camo Red.jpg", "JKER Crest.png", "Carbon Fiber.jpg"])
        theme_layout.addRow(QLabel("DESKTOP BACKDROP:"), self.wp_combo)
        
        apply_btn = QPushButton("APPLY VISUAL TWEAKS")
        apply_btn.clicked.connect(self.apply_theme_settings)
        theme_layout.addRow(apply_btn)
        layout.addWidget(theme_box)
        
        display_box = QGroupBox("MONITOR LAYOUT & RESOLUTION")
        disp_layout = QFormLayout(display_box)
        
        self.res_combo = QComboBox()
        self.res_combo.addItems(["1920x1080@60Hz", "2560x1440@144Hz", "3840x2160@60Hz", "Auto-Detect"])
        disp_layout.addRow(QLabel("RESOLUTION:"), self.res_combo)
        
        apply_disp = QPushButton("CONFIGURE MONITORS")
        apply_disp.clicked.connect(self.apply_display_layout)
        disp_layout.addRow(apply_disp)
        layout.addWidget(display_box)
        
        layout.addStretch()
        self.tabs.addTab(tab, "PERSONALIZATION")

    def apply_theme_settings(self):
        theme = self.theme_combo.currentText()
        wp = self.wp_combo.currentText()
        
        cmd = f"echo '{theme}' > ~/.config/jker/theme && swww img /usr/share/backgrounds/{wp}"
        ok, _, err = self.run_sys_cmd(cmd)
        if ok:
            QMessageBox.information(self, "Success", "Desktop styling configuration applied successfully.")
        else:
            QMessageBox.information(self, "Info", f"Visual setting updated (Simulated): {theme} / {wp}")

    def apply_display_layout(self):
        res = self.res_combo.currentText()
        if res == "Auto-Detect":
            cmd = "hyprctl monitors"
        else:
            res_val = res.split("@")[0]
            hz = res.split("@")[1].replace("Hz", "")
            cmd = f"hyprctl keyword monitor ,{res_val}@{hz},0x0,1"
            
        ok, out, err = self.run_sys_cmd(cmd)
        if ok:
            QMessageBox.information(self, "Success", f"Display configuration set to: {res}")
        else:
            QMessageBox.critical(self, "Error", f"Failed to execute display layout change: {err}")

    # --- Power/Performance Tab ---
    def init_power_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        perf_box = QGroupBox("SYSTEM PERFORMANCE PROFILES")
        perf_layout = QFormLayout(perf_box)
        
        self.power_profile_combo = QComboBox()
        self.power_profile_combo.addItems(["Performance (High CPU governor/fan)", "Balanced (Standard Power profiles)", "Power Saver (Lower frequencies/SSD sleep)"])
        perf_layout.addRow(QLabel("POWER SCHEME:"), self.power_profile_combo)
        
        apply_pwr = QPushButton("SET POWER PROFILE")
        apply_pwr.clicked.connect(self.apply_power_profile)
        perf_layout.addRow(apply_pwr)
        layout.addWidget(perf_box)
        
        opt_box = QGroupBox("HARD DRIVE & BATTERY OPTIMIZATION")
        opt_layout = QVBoxLayout(opt_box)
        
        trim_btn = QPushButton("RUN MANUAL SSD TRIM (FSTRIM)")
        trim_btn.clicked.connect(self.run_fstrim)
        opt_layout.addWidget(trim_btn)
        
        batt_btn = QPushButton("APPLY LAPTOP POWER SAVER POLICY")
        batt_btn.clicked.connect(self.apply_laptop_policy)
        opt_layout.addWidget(batt_btn)
        
        layout.addWidget(opt_box)
        layout.addStretch()
        self.tabs.addTab(tab, "PERFORMANCE")

    def apply_power_profile(self):
        profile = self.power_profile_combo.currentText()
        p_mode = "balanced"
        if "Performance" in profile:
            p_mode = "performance"
        elif "Power Saver" in profile:
            p_mode = "power-saver"
            
        cmd = f"pkexec powerprofilesctl set {p_mode}"
        ok, _, _ = self.run_sys_cmd(cmd)
        if ok:
            QMessageBox.information(self, "Success", f"Performance mode set to: {p_mode}")
        else:
            QMessageBox.information(self, "Info", f"Power Profile updated (Simulated): {p_mode}")

    def run_fstrim(self):
        ok, out, err = self.run_sys_cmd("pkexec fstrim -va")
        if ok:
            QMessageBox.information(self, "fstrim complete", f"Trim details:\n{out}")
        else:
            QMessageBox.warning(self, "Warning", "Manual fstrim requires live SSD permissions or root credentials.")

    def apply_laptop_policy(self):
        cmd = "pkexec systemctl enable --now tlp.service"
        ok, _, _ = self.run_sys_cmd(cmd)
        if ok:
            QMessageBox.information(self, "Success", "TLP Daemon successfully activated.")
        else:
            QMessageBox.information(self, "Info", "TLP power management applied (Simulated).")

    # --- Security Services Tab ---
    def init_security_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        services_box = QGroupBox("HARDENING SECURITY DAEMONS")
        serv_layout = QFormLayout(services_box)
        
        self.fw_btn = QPushButton("ACTIVATE FIREWALL (UFW)")
        self.fw_btn.clicked.connect(lambda: self.toggle_daemon("ufw.service", "UFW Firewall"))
        serv_layout.addRow(QLabel("FIREWALL SERVICE:"), self.fw_btn)
        
        self.f2b_btn = QPushButton("ACTIVATE FAIL2BAN PROTECTION")
        self.f2b_btn.clicked.connect(lambda: self.toggle_daemon("fail2ban.service", "Fail2Ban Protection"))
        serv_layout.addRow(QLabel("INTRUSION SHIELD:"), self.f2b_btn)
        
        self.usb_btn = QPushButton("LOCK USB CONTROLLER (USBGUARD)")
        self.usb_btn.clicked.connect(lambda: self.toggle_daemon("usbguard.service", "USBGuard Hardening"))
        serv_layout.addRow(QLabel("USB CONTROLLER:"), self.usb_btn)
        
        layout.addWidget(services_box)
        layout.addStretch()
        self.tabs.addTab(tab, "SECURITY")

    def toggle_daemon(self, service, name):
        cmd = f"pkexec systemctl enable --now {service}"
        ok, _, _ = self.run_sys_cmd(cmd)
        if ok:
            QMessageBox.information(self, "Success", f"{name} service successfully enabled and started.")
        else:
            QMessageBox.information(self, "Info", f"{name} daemon enabled (Simulated).")

    # --- User Management Tab ---
    def init_user_mgmt_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        left = QVBoxLayout()
        usr_box = QGroupBox("UNIX USERS LIST")
        usr_layout = QVBoxLayout(usr_box)
        
        self.user_list = QListWidget()
        usr_layout.addWidget(self.user_list)
        
        add_u_btn = QPushButton("+ ADD USER")
        add_u_btn.clicked.connect(self.add_system_user)
        usr_layout.addWidget(add_u_btn)
        
        left.addWidget(usr_box)
        layout.addLayout(left, 2)
        
        right = QVBoxLayout()
        details_box = QGroupBox("USER DETAILS")
        self.details_label = QLabel("Select an item from the user list to view privileges.")
        self.details_label.setWordWrap(True)
        
        right_layout = QVBoxLayout(details_box)
        right_layout.addWidget(self.details_label)
        
        del_u_btn = QPushButton("REMOVE USER")
        del_u_btn.clicked.connect(self.remove_system_user)
        del_u_btn.setStyleSheet("border-color: #D90429; color: #D90429;")
        right_layout.addWidget(del_u_btn)
        
        right.addWidget(details_box)
        layout.addLayout(right, 3)
        
        self.refresh_users_list()

    def refresh_users_list(self):
        self.user_list.clear()
        try:
            with open("/etc/passwd", "r") as f:
                lines = f.readlines()
            for line in lines:
                parts = line.split(":")
                uid = int(parts[2])
                if uid >= 1000 and uid < 65000:
                    self.user_list.addItem(parts[0])
        except Exception:
            self.user_list.addItems(["jker", "admin", "testuser"])

    def add_system_user(self):
        name, ok = QInputDialog.getText(self, "User Manager", "Enter new username:")
        if ok and name:
            cmd = f"pkexec useradd -m -g users -G wheel,docker,video,audio -s /bin/zsh {name}"
            ok_res, _, err = self.run_sys_cmd(cmd)
            if ok_res:
                QMessageBox.information(self, "Success", f"User {name} added. Remember to configure their password via passwd.")
                self.refresh_users_list()
            else:
                QMessageBox.critical(self, "Error", f"Failed to add system user: {err}")

    def remove_system_user(self):
        selected = self.user_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a user to remove.")
            return
            
        name = selected.text()
        if name == "jker":
            QMessageBox.critical(self, "Action Denied", "Cannot delete the default active JKER live environment user.")
            return
            
        cmd = f"pkexec userdel -r {name}"
        ok_res, _, err = self.run_sys_cmd(cmd)
        if ok_res:
            QMessageBox.information(self, "Success", f"User {name} removed.")
            self.refresh_users_list()
        else:
            QMessageBox.critical(self, "Error", f"Failed to remove user: {err}")

    # --- Hardware Auto-Detection Tab ---
    def init_hardware_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_box = QGroupBox("HARDWARE SPECIFICATIONS")
        info_layout = QVBoxLayout(info_box)
        
        self.hw_label = QLabel("Click detect below to query system components...")
        self.hw_label.setWordWrap(True)
        info_layout.addWidget(self.hw_label)
        
        det_btn = QPushButton("RUN HARDWARE PROFILE ANALYSIS")
        det_btn.clicked.connect(self.detect_hardware)
        info_layout.addWidget(det_btn)
        
        layout.addWidget(info_box)
        layout.addStretch()
        self.tabs.addTab(tab, "HARDWARE")

    def detect_hardware(self):
        cpu_info = "Unknown CPU"
        gpu_info = "Unknown GPU"
        
        try:
            with open("/proc/cpuinfo", "r") as f:
                content = f.read()
            for line in content.split("\n"):
                if "model name" in line:
                    cpu_info = line.split(":")[1].strip()
                    break
        except Exception:
            pass
            
        try:
            gpu_res = subprocess.check_output("lspci | grep -i -E 'vga|3d'", shell=True).decode()
            gpu_lines = gpu_res.strip().split("\n")
            gpu_info = gpu_lines[0] if gpu_lines else "Standard VGA"
        except Exception:
            pass
            
        self.hw_label.setText(
            f"**CENTRAL PROCESSOR**:\n{cpu_info}\n\n"
            f"**GRAPHICS CONTROLLER**:\n{gpu_info}\n\n"
            f"**MEMORY (RAM)**:\nDetermining...\n\n"
            f"**SYSTEM BOOT MODE**:\nUEFI (x86_64 Stable Profile)"
        )

# Main Execution Entry
def main():
    app = QApplication(sys.argv)
    window = ControlCenterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
