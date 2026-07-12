import os
import sys
import subprocess
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QProgressBar, QTextEdit,
    QGroupBox, QStackedWidget, QMessageBox, QRadioButton, QButtonGroup,
    QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

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
    padding: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 10px;
    color: #D90429;
    font-weight: bold;
    font-size: 14px;
}
QLineEdit, QComboBox {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    border-radius: 4px;
    padding: 6px;
    color: #EDF2F4;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #D90429;
}
QPushButton {
    background-color: #1F2833;
    border: 1px solid #D90429;
    border-radius: 4px;
    color: #EDF2F4;
    padding: 10px 20px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #D90429;
    color: #0B0C10;
}
QPushButton:disabled {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    color: #8D99AE;
}
QProgressBar {
    border: 1px solid #8D99AE;
    border-radius: 5px;
    text-align: center;
    background-color: #151A21;
}
QProgressBar::chunk {
    background-color: #D90429;
}
QTextEdit {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    border-radius: 6px;
    color: #EDF2F4;
}
QRadioButton {
    color: #EDF2F4;
}
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #8D99AE;
    border-radius: 7px;
    background-color: #151A21;
}
QRadioButton::indicator:checked {
    background-color: #D90429;
    border: 1px solid #D90429;
}
"""

class InstallWorker(QThread):
    stdout_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(int)

    def __init__(self, env_vars):
        super().__init__()
        self.env_vars = env_vars

    def run(self):
        try:
            # We search for the install_helper.sh script path.
            # On the live ISO it will be in /usr/share/jker-apps/installer/install_helper.sh or /usr/bin/installer/install_helper.sh
            helper_path = "/usr/share/jker-apps/installer/install_helper.sh"
            if not os.path.exists(helper_path):
                # Fallback path inside current workspace for local testing
                helper_path = os.path.join(os.path.dirname(__file__), "install_helper.sh")
                helper_path = os.path.abspath(helper_path)
            
            # Ensure it is executable
            os.chmod(helper_path, 0o755)
            
            # Setup environment variables for child script
            env = os.environ.copy()
            env.update(self.env_vars)
            
            # Launch installation helper, executing it as root via pkexec if needed,
            # but since we run this app from the desktop terminal as root (sudo jker-install),
            # we execute it directly.
            self.stdout_signal.emit("[DEPLOY] Launching installation script: " + helper_path + "\n")
            
            proc = subprocess.Popen(
                ["bash", helper_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Simple progress heuristics based on log lines
            lines_counted = 0
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                self.stdout_signal.emit(line)
                lines_counted += 1
                
                # Progress bar updates
                if "Formatting partitions" in line:
                    self.progress_signal.emit(15)
                elif "Mounting target" in line:
                    self.progress_signal.emit(25)
                elif "Copying live environment" in line or "bootstrapping via pacstrap" in line:
                    self.progress_signal.emit(40)
                elif "Generating filesystem table" in line:
                    self.progress_signal.emit(70)
                elif "Initiating configuration phase" in line:
                    self.progress_signal.emit(80)
                elif "Syncing latest desktop themes" in line:
                    self.progress_signal.emit(90)
                    
            proc.wait()
            self.finished_signal.emit(proc.returncode)
        except Exception as e:
            self.stdout_signal.emit(f"[ERROR] Execution failure: {e}\n")
            self.finished_signal.emit(-1)

class JkerInstallerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JKER OS // GRAPHICAL DEPLOYMENT ENGINE")
        self.setMinimumSize(850, 580)
        self.setStyleSheet(STYLE_SHEET)
        
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
        # Installation setup data
        self.setup_data = {}
        
        self.init_welcome_ui()
        self.init_locale_ui()
        self.init_user_ui()
        self.init_disk_ui()
        self.init_summary_ui()
        self.init_progress_ui()
        
        self.central_stack.setCurrentWidget(self.welcome_widget)

    def go_next(self):
        current = self.central_stack.currentWidget()
        if current == self.welcome_widget:
            self.central_stack.setCurrentWidget(self.locale_widget)
        elif current == self.locale_widget:
            self.central_stack.setCurrentWidget(self.user_widget)
        elif current == self.user_widget:
            # Validate user account fields
            if not self.usr_input.text() or not self.pwd_input.text():
                QMessageBox.warning(self, "Validation Error", "Username and Password cannot be empty.")
                return
            if self.pwd_input.text() != self.confirm_pwd_input.text():
                QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
                return
            self.central_stack.setCurrentWidget(self.disk_widget)
            self.refresh_drives_list()
        elif current == self.disk_widget:
            # Validate partitions if manual
            if self.radio_manual.isChecked() and (not self.efi_input.text() or not self.root_input.text()):
                QMessageBox.warning(self, "Validation Error", "Manual partition fields cannot be empty.")
                return
            self.central_stack.setCurrentWidget(self.summary_widget)
            self.update_summary()
        elif current == self.summary_widget:
            self.central_stack.setCurrentWidget(self.progress_widget)
            self.start_installation()

    def go_back(self):
        current = self.central_stack.currentWidget()
        if current == self.locale_widget:
            self.central_stack.setCurrentWidget(self.welcome_widget)
        elif current == self.user_widget:
            self.central_stack.setCurrentWidget(self.locale_widget)
        elif current == self.disk_widget:
            self.central_stack.setCurrentWidget(self.user_widget)
        elif current == self.summary_widget:
            self.central_stack.setCurrentWidget(self.disk_widget)

    # --- Screen 1: Welcome & Setup mode ---
    def init_welcome_ui(self):
        self.welcome_widget = QWidget()
        layout = QVBoxLayout(self.welcome_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("JKER OS // SYSTEM INSTALLER")
        title.setFont(QFont("Courier New", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #D90429; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel("Welcome to the tactical installation deployment dashboard for JKER OS. This installer configures disk geometry, bootstrap dependencies, and user policies.")
        desc.setWordWrap(True)
        desc.setFixedWidth(550)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Options Box
        options_box = QGroupBox("INSTALLATION SPECIFICATIONS")
        options_box.setFixedWidth(550)
        form = QFormLayout(options_box)
        
        self.media_combo = QComboBox()
        self.media_combo.addItems(["Install to SSD (Trim Enabled, High Performance)", "Install to USB Flash Drive (Optimized Writeback)"])
        form.addRow(QLabel("TARGET HARDWARE:"), self.media_combo)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Offline Image Extraction (Fastest, Identical Replica)", "Online pacstrap Bootstrap (Requires Internet, Dynamic Sync)"])
        form.addRow(QLabel("INSTALLATION MODE:"), self.mode_combo)
        
        layout.addWidget(options_box)
        
        btn_layout = QHBoxLayout()
        next_btn = QPushButton("PROCEED")
        next_btn.clicked.connect(self.go_next)
        btn_layout.addStretch()
        btn_layout.addWidget(next_btn)
        
        layout.addLayout(btn_layout)
        self.central_stack.addWidget(self.welcome_widget)

    # --- Screen 2: Region & Keymap ---
    def init_locale_ui(self):
        self.locale_widget = QWidget()
        layout = QVBoxLayout(self.locale_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        box = QGroupBox("LOCALIZATION CONFIGURATION")
        box.setFixedWidth(550)
        form = QFormLayout(box)
        
        self.tz_combo = QComboBox()
        self.tz_combo.addItems(["UTC", "US/Eastern", "US/Pacific", "Europe/London", "Asia/Kolkata", "Australia/Sydney", "Asia/Tokyo"])
        self.tz_combo.setEditable(True)
        form.addRow(QLabel("SYSTEM TIMEZONE:"), self.tz_combo)
        
        self.locale_combo = QComboBox()
        self.locale_combo.addItems(["en_US.UTF-8", "en_GB.UTF-8", "de_DE.UTF-8", "fr_FR.UTF-8", "es_ES.UTF-8"])
        self.locale_combo.setEditable(True)
        form.addRow(QLabel("SYSTEM LOCALE:"), self.locale_combo)
        
        self.key_combo = QComboBox()
        self.key_combo.addItems(["us", "uk", "de", "fr", "es"])
        self.key_combo.setEditable(True)
        form.addRow(QLabel("KEYBOARD LAYOUT:"), self.key_combo)
        
        layout.addWidget(box)
        
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("BACK")
        back_btn.clicked.connect(self.go_back)
        next_btn = QPushButton("NEXT")
        next_btn.clicked.connect(self.go_next)
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(next_btn)
        
        layout.addLayout(btn_layout)
        self.central_stack.addWidget(self.locale_widget)

    # --- Screen 3: User Details ---
    def init_user_ui(self):
        self.user_widget = QWidget()
        layout = QVBoxLayout(self.user_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        box = QGroupBox("USER ACCOUNT CREDENTIALS")
        box.setFixedWidth(550)
        form = QFormLayout(box)
        
        self.host_input = QLineEdit("jker-host")
        form.addRow(QLabel("SYSTEM HOSTNAME:"), self.host_input)
        
        self.usr_input = QLineEdit("jker-user")
        form.addRow(QLabel("USERNAME:"), self.usr_input)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Enter Password")
        form.addRow(QLabel("PASSWORD:"), self.pwd_input)
        
        self.confirm_pwd_input = QLineEdit()
        self.confirm_pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pwd_input.setPlaceholderText("Confirm Password")
        form.addRow(QLabel("CONFIRM PASSWORD:"), self.confirm_pwd_input)
        
        layout.addWidget(box)
        
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("BACK")
        back_btn.clicked.connect(self.go_back)
        next_btn = QPushButton("NEXT")
        next_btn.clicked.connect(self.go_next)
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(next_btn)
        
        layout.addLayout(btn_layout)
        self.central_stack.addWidget(self.user_widget)

    # --- Screen 4: Disk Partitioning ---
    def init_disk_ui(self):
        self.disk_widget = QWidget()
        layout = QVBoxLayout(self.disk_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        box = QGroupBox("TARGET SYSTEM PARTITIONING")
        box.setFixedWidth(580)
        form = QFormLayout(box)
        
        self.drive_combo = QComboBox()
        form.addRow(QLabel("TARGET STORAGE DISK:"), self.drive_combo)
        
        # Partitioning Options
        self.radio_auto = QRadioButton("AUTOMATIC (GPT, erases drive, 512M EFI, rest ext4 ROOT)")
        self.radio_auto.setChecked(True)
        self.radio_manual = QRadioButton("MANUAL (Install to existing configured partitions)")
        
        btn_group = QButtonGroup(self.disk_widget)
        btn_group.addButton(self.radio_auto)
        btn_group.addButton(self.radio_manual)
        
        form.addRow(self.radio_auto)
        form.addRow(self.radio_manual)
        
        # Manual partitions panel
        self.manual_group = QWidget()
        m_layout = QFormLayout(self.manual_group)
        self.efi_input = QLineEdit()
        self.efi_input.setPlaceholderText("e.g. /dev/sda1")
        m_layout.addRow(QLabel("EFI ESP PARTITION:"), self.efi_input)
        
        self.root_input = QLineEdit()
        self.root_input.setPlaceholderText("e.g. /dev/sda2")
        m_layout.addRow(QLabel("ROOT (/) PARTITION:"), self.root_input)
        
        self.manual_group.setVisible(False)
        self.radio_manual.toggled.connect(self.manual_group.setVisible)
        
        form.addRow(self.manual_group)
        layout.addWidget(box)
        
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("BACK")
        back_btn.clicked.connect(self.go_back)
        next_btn = QPushButton("NEXT")
        next_btn.clicked.connect(self.go_next)
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(next_btn)
        
        layout.addLayout(btn_layout)
        self.central_stack.addWidget(self.disk_widget)

    def refresh_drives_list(self):
        self.drive_combo.clear()
        try:
            # Probe available block devices
            output = subprocess.check_output("lsblk -d -n -o NAME,SIZE,MODEL", shell=True).decode()
            for line in output.strip().split("\n"):
                if line:
                    self.drive_combo.addItem(line.strip())
        except Exception:
            # Fallback for offline testing
            self.drive_combo.addItems(["sda (256.0G, SSD Emulator)", "nvme0n1 (512.0G, SSD Emulator)", "sdb (32.0G, USB Stick)"])

    # --- Screen 5: Confirmation Summary ---
    def init_summary_ui(self):
        self.summary_widget = QWidget()
        layout = QVBoxLayout(self.summary_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        box = QGroupBox("INSTALLATION DEPLOYMENT PROFILE")
        box.setFixedWidth(580)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Courier New", 12))
        
        v_layout = QVBoxLayout(box)
        v_layout.addWidget(self.summary_text)
        
        warning = QLabel("[WARNING] Proceeding will format partitions and erase data on the target storage disk persistently.")
        warning.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
        warning.setStyleSheet("color: #D90429;")
        warning.setWordWrap(True)
        v_layout.addWidget(warning)
        
        layout.addWidget(box)
        
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("BACK")
        back_btn.clicked.connect(self.go_back)
        install_btn = QPushButton("DEPLOY JKER OS")
        install_btn.setStyleSheet("border-color: #D90429; color: #D90429; font-weight: bold;")
        install_btn.clicked.connect(self.go_next)
        
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(install_btn)
        
        layout.addLayout(btn_layout)
        self.central_stack.addWidget(self.summary_widget)

    def update_summary(self):
        drive = self.drive_combo.currentText().split()[0]
        mode = "Offline (Live SquashFS Clone)" if "Offline" in self.mode_combo.currentText() else "Online (Pacstrap Bootstrap)"
        media = "SSD" if "SSD" in self.media_combo.currentText() else "USB"
        part_mode = "Automatic Partitioning" if self.radio_auto.isChecked() else "Manual Target Partitioning"
        
        summary = f"""========================================
JKER OS DEPLOYMENT TARGET PROFILE
========================================
HOST CONFIGURATION:
* Hostname     : {self.host_input.text()}
* User Account : {self.usr_input.text()}

LOCALIZATION CONFIGURATION:
* Timezone     : {self.tz_combo.currentText()}
* System Locale: {self.locale_combo.currentText()}
* Keyboard     : {self.key_combo.currentText()}

STORAGE CONFIGURATION:
* Mode         : {part_mode}
* Target Drive : /dev/{drive}
"""
        if self.radio_manual.isChecked():
            summary += f"* EFI Partition: {self.efi_input.text()}\n* ROOT Partition: {self.root_input.text()}\n"
            
        summary += f"""
INSTALLATION ENGINE:
* Method       : {mode}
* Hardware Opt : {media} Optimization Policy
========================================
"""
        self.summary_text.setPlainText(summary)

    # --- Screen 6: Progress Bar and logs console ---
    def init_progress_ui(self):
        self.progress_widget = QWidget()
        layout = QVBoxLayout(self.progress_widget)
        
        title = QLabel("JKER SYSTEM DEPLOYMENT IN PROGRESS...")
        title.setFont(QFont("Courier New", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #D90429;")
        layout.addWidget(title)
        
        self.pbar = QProgressBar()
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        layout.addWidget(self.pbar)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setPlaceholderText("Low-level filesystem logs will display here...")
        layout.addWidget(self.log_console)
        
        self.central_stack.addWidget(self.progress_widget)

    def log_progress(self, line):
        self.log_console.insertPlainText(line)
        self.log_console.ensureCursorVisible()

    def update_pbar(self, value):
        self.pbar.setValue(value)

    def start_installation(self):
        # Gather environmental parameters for child script
        drive = self.drive_combo.currentText().split()[0]
        mode = "offline" if "Offline" in self.mode_combo.currentText() else "online"
        part_mode = "auto" if self.radio_auto.isChecked() else "manual"
        
        env_vars = {
            "TARGET_DISK": drive,
            "INSTALL_MODE": mode,
            "HOSTNAME": self.host_input.text(),
            "USERNAME": self.usr_input.text(),
            "PASSWORD": self.pwd_input.text(),
            "TIMEZONE": self.tz_combo.currentText(),
            "LOCALE": self.locale_combo.currentText(),
            "KEYMAP": self.key_combo.currentText(),
            "PARTITION_MODE": part_mode,
            "EFI_PART": self.efi_input.text(),
            "ROOT_PART": self.root_input.text()
        }
        
        self.worker = InstallWorker(env_vars)
        self.worker.stdout_signal.connect(self.log_progress)
        self.worker.progress_signal.connect(self.update_pbar)
        self.worker.finished_signal.connect(self.installation_finished)
        self.worker.start()

    def installation_finished(self, exit_code):
        if exit_code == 0:
            self.pbar.setValue(100)
            QMessageBox.information(
                self, 
                "Success", 
                "JKER OS has been successfully installed onto your hardware!\n"
                "Please close this window, unmount your install media, and reboot."
            )
        else:
            QMessageBox.critical(
                self, 
                "Failure", 
                f"Installation process failed with exit code: {exit_code}\n"
                "Please review the console logs for debugging information."
            )

def main():
    app = QApplication(sys.argv)
    window = JkerInstallerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
