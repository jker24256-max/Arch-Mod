import os
import sys
import random
import string
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget, QListWidget,
    QTextEdit, QMessageBox, QFileDialog, QTabWidget, QGroupBox,
    QFormLayout, QCheckBox, QSpinBox, QListWidgetItem, QInputDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette

from encryption import VaultEncryptor

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
QLineEdit, QTextEdit {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    border-radius: 4px;
    padding: 6px;
    color: #EDF2F4;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #D90429;
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
QListWidget {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    border-radius: 6px;
    padding: 5px;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #2B303A;
}
QListWidget::item:selected {
    background-color: #D90429;
    color: #0B0C10;
    font-weight: bold;
    border-radius: 4px;
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
"""

VAULT_DIR = os.path.expanduser("~/.config/jker")
os.makedirs(VAULT_DIR, exist_ok=True)
VAULT_PATH = os.path.join(VAULT_DIR, "vault.db")

class BlackVaultApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.encryptor = VaultEncryptor(VAULT_PATH)
        self.master_password = None
        self.vault_data = None
        
        self.setWindowTitle("BLACKVAULT // JKER OS SECURE")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(STYLE_SHEET)
        
        # Central widget and stacks (auth vs app dashboard)
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
        # Create UI states
        self.init_auth_ui()
        self.init_setup_ui()
        self.init_dashboard_ui()
        
        # Check vault existence
        if os.path.exists(VAULT_PATH):
            self.central_stack.setCurrentWidget(self.auth_widget)
        else:
            self.central_stack.setCurrentWidget(self.setup_widget)

    # --- Authentication and Setup Screens ---
    def init_auth_ui(self):
        self.auth_widget = QWidget()
        layout = QVBoxLayout(self.auth_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        container = QGroupBox("DECRYPT VAULT")
        container.setFixedWidth(400)
        form = QFormLayout(container)
        
        title = QLabel("JKER OS // BLACKVAULT v1.0")
        title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #D90429; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addRow(title)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Enter Master Password")
        form.addRow(QLabel("MASTER KEY:"), self.pwd_input)
        
        self.unlock_btn = QPushButton("UNLOCK")
        self.unlock_btn.clicked.connect(self.unlock_vault)
        self.pwd_input.returnPressed.connect(self.unlock_vault)
        form.addRow(self.unlock_btn)
        
        layout.addWidget(container)
        self.central_stack.addWidget(self.auth_widget)

    def init_setup_ui(self):
        # Setup UI for when vault.db doesn't exist
        self.setup_widget = QWidget()
        layout = QVBoxLayout(self.setup_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        container = QGroupBox("INITIALIZE SECURE VAULT")
        container.setFixedWidth(450)
        form = QFormLayout(container)
        
        title = QLabel("NEW VAULT SETUP")
        title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #D90429; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addRow(title)
        
        info = QLabel("Setup a strong Master Password. If lost, your encrypted vault cannot be recovered.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #8D99AE; margin-bottom: 15px;")
        form.addRow(info)
        
        self.new_pwd_input = QLineEdit()
        self.new_pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pwd_input.setPlaceholderText("New Master Password")
        form.addRow(QLabel("PASSWORD:"), self.new_pwd_input)
        
        self.new_pwd_confirm = QLineEdit()
        self.new_pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pwd_confirm.setPlaceholderText("Confirm Master Password")
        form.addRow(QLabel("CONFIRM:"), self.new_pwd_confirm)
        
        self.init_btn = QPushButton("INITIALIZE VAULT")
        self.init_btn.clicked.connect(self.setup_vault)
        form.addRow(self.init_btn)
        
        layout.addWidget(container)
        self.central_stack.addWidget(self.setup_widget)
        
    def setup_vault(self):
        pwd = self.new_pwd_input.text()
        confirm = self.new_pwd_confirm.text()
        if not pwd:
            QMessageBox.critical(self, "Error", "Password cannot be empty.")
            return
        if pwd != confirm:
            QMessageBox.critical(self, "Error", "Passwords do not match.")
            return
        
        success = self.encryptor.initialize_vault(pwd)
        if success:
            QMessageBox.information(self, "Success", "Vault initialized successfully!")
            self.master_password = pwd
            self.vault_data = self.encryptor.load_vault(pwd)
            self.central_stack.setCurrentWidget(self.dashboard_widget)
            self.refresh_all_lists()
        else:
            QMessageBox.critical(self, "Error", "Failed to initialize vault.")

    def unlock_vault(self):
        pwd = self.pwd_input.text()
        data = self.encryptor.load_vault(pwd)
        if data is not None:
            self.master_password = pwd
            self.vault_data = data
            self.central_stack.setCurrentWidget(self.dashboard_widget)
            self.refresh_all_lists()
        else:
            QMessageBox.critical(self, "Access Denied", "Invalid Master Password.")
            self.pwd_input.clear()

    # --- Main Application Dashboard ---
    def init_dashboard_ui(self):
        self.dashboard_widget = QWidget()
        main_layout = QHBoxLayout(self.dashboard_widget)
        
        # Tabs for categories
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Initialize different tabs
        self.create_passwords_tab()
        self.create_notes_tab()
        self.create_ssh_keys_tab()
        self.create_api_keys_tab()
        self.create_file_vault_tab()
        self.create_generator_tab()

    # Tab 1: Passwords
    def create_passwords_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left Side List
        list_pane = QVBoxLayout()
        self.pwd_search = QLineEdit()
        self.pwd_search.setPlaceholderText("Search passwords...")
        self.pwd_search.textChanged.connect(self.filter_passwords)
        list_pane.addWidget(self.pwd_search)
        
        self.pwd_list = QListWidget()
        self.pwd_list.itemClicked.connect(self.display_password_item)
        list_pane.addWidget(self.pwd_list)
        
        add_btn = QPushButton("+ ADD PASSWORD")
        add_btn.clicked.connect(self.add_password_dialog)
        list_pane.addWidget(add_btn)
        layout.addLayout(list_pane, 2)
        
        # Right Side Details Box
        self.pwd_details_box = QGroupBox("CREDENTIAL INFO")
        details_layout = QVBoxLayout(self.pwd_details_box)
        
        self.pwd_info_label = QLabel("Select an item to view")
        self.pwd_info_label.setWordWrap(True)
        details_layout.addWidget(self.pwd_info_label)
        
        btn_layout = QHBoxLayout()
        self.pwd_copy_btn = QPushButton("Copy Password")
        self.pwd_copy_btn.clicked.connect(self.copy_current_password)
        self.pwd_copy_btn.setEnabled(False)
        btn_layout.addWidget(self.pwd_copy_btn)
        
        self.pwd_delete_btn = QPushButton("Delete")
        self.pwd_delete_btn.clicked.connect(self.delete_current_password)
        self.pwd_delete_btn.setEnabled(False)
        self.pwd_delete_btn.setStyleSheet("border-color: #D90429; color: #D90429;")
        btn_layout.addWidget(self.pwd_delete_btn)
        
        details_layout.addLayout(btn_layout)
        layout.addWidget(self.pwd_details_box, 3)
        
        self.tabs.addTab(tab, "PASSWORDS")

    # Tab 2: Secure Notes
    def create_notes_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        list_pane = QVBoxLayout()
        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.display_note_item)
        list_pane.addWidget(self.notes_list)
        
        add_btn = QPushButton("+ ADD SECURE NOTE")
        add_btn.clicked.connect(self.add_note_dialog)
        list_pane.addWidget(add_btn)
        layout.addLayout(list_pane, 2)
        
        self.notes_details_box = QGroupBox("SECURE NOTE")
        details_layout = QVBoxLayout(self.notes_details_box)
        
        self.note_content_view = QTextEdit()
        self.note_content_view.setReadOnly(True)
        details_layout.addWidget(self.note_content_view)
        
        btn_layout = QHBoxLayout()
        self.note_save_btn = QPushButton("Save Changes")
        self.note_save_btn.clicked.connect(self.save_note_changes)
        self.note_save_btn.setEnabled(False)
        btn_layout.addWidget(self.note_save_btn)
        
        self.note_delete_btn = QPushButton("Delete")
        self.note_delete_btn.clicked.connect(self.delete_current_note)
        self.note_delete_btn.setEnabled(False)
        btn_layout.addWidget(self.note_delete_btn)
        
        details_layout.addLayout(btn_layout)
        layout.addWidget(self.notes_details_box, 3)
        
        self.tabs.addTab(tab, "SECURE NOTES")

    # Tab 3: SSH Keys
    def create_ssh_keys_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        list_pane = QVBoxLayout()
        self.ssh_list = QListWidget()
        self.ssh_list.itemClicked.connect(self.display_ssh_item)
        list_pane.addWidget(self.ssh_list)
        
        add_btn = QPushButton("+ ADD SSH KEY")
        add_btn.clicked.connect(self.add_ssh_dialog)
        list_pane.addWidget(add_btn)
        layout.addLayout(list_pane, 2)
        
        self.ssh_details_box = QGroupBox("SSH KEY DETAILS")
        details_layout = QVBoxLayout(self.ssh_details_box)
        
        self.ssh_info_label = QLabel("Select an SSH key")
        details_layout.addWidget(self.ssh_info_label)
        
        self.ssh_key_view = QTextEdit()
        self.ssh_key_view.setReadOnly(True)
        self.ssh_key_view.setPlaceholderText("SSH Key Content")
        details_layout.addWidget(self.ssh_key_view)
        
        btn_layout = QHBoxLayout()
        self.ssh_copy_btn = QPushButton("Copy Key")
        self.ssh_copy_btn.clicked.connect(self.copy_current_ssh)
        self.ssh_copy_btn.setEnabled(False)
        btn_layout.addWidget(self.ssh_copy_btn)
        
        self.ssh_delete_btn = QPushButton("Delete")
        self.ssh_delete_btn.clicked.connect(self.delete_current_ssh)
        self.ssh_delete_btn.setEnabled(False)
        btn_layout.addWidget(self.ssh_delete_btn)
        
        details_layout.addLayout(btn_layout)
        layout.addWidget(self.ssh_details_box, 3)
        
        self.tabs.addTab(tab, "SSH KEYS")

    # Tab 4: API Keys
    def create_api_keys_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        list_pane = QVBoxLayout()
        self.api_list = QListWidget()
        self.api_list.itemClicked.connect(self.display_api_item)
        list_pane.addWidget(self.api_list)
        
        add_btn = QPushButton("+ ADD API KEY")
        add_btn.clicked.connect(self.add_api_dialog)
        list_pane.addWidget(add_btn)
        layout.addLayout(list_pane, 2)
        
        self.api_details_box = QGroupBox("API KEY DETAILS")
        details_layout = QVBoxLayout(self.api_details_box)
        
        self.api_info_label = QLabel("Select an API key")
        details_layout.addWidget(self.api_info_label)
        
        btn_layout = QHBoxLayout()
        self.api_copy_btn = QPushButton("Copy Key")
        self.api_copy_btn.clicked.connect(self.copy_current_api)
        self.api_copy_btn.setEnabled(False)
        btn_layout.addWidget(self.api_copy_btn)
        
        self.api_delete_btn = QPushButton("Delete")
        self.api_delete_btn.clicked.connect(self.delete_current_api)
        self.api_delete_btn.setEnabled(False)
        btn_layout.addWidget(self.api_delete_btn)
        
        details_layout.addLayout(btn_layout)
        layout.addWidget(self.api_details_box, 3)
        
        self.tabs.addTab(tab, "API KEYS")

    # Tab 5: File Encrypter/Decrypter
    def create_file_vault_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        encryption_box = QGroupBox("FILE ENCRYPT / DECRYPT")
        box_layout = QVBoxLayout(encryption_box)
        
        desc = QLabel("Encrypt raw local files using BlackVault AES-256 standard.")
        desc.setStyleSheet("color: #8D99AE;")
        box_layout.addWidget(desc)
        
        form = QFormLayout()
        self.selected_file_input = QLineEdit()
        self.selected_file_input.setPlaceholderText("Select File...")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        
        file_selection = QHBoxLayout()
        file_selection.addWidget(self.selected_file_input)
        file_selection.addWidget(self.browse_btn)
        form.addRow(QLabel("TARGET FILE:"), file_selection)
        
        box_layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        self.encrypt_file_btn = QPushButton("ENCRYPT FILE")
        self.encrypt_file_btn.clicked.connect(self.encrypt_file)
        btn_layout.addWidget(self.encrypt_file_btn)
        
        self.decrypt_file_btn = QPushButton("DECRYPT FILE")
        self.decrypt_file_btn.clicked.connect(self.decrypt_file)
        btn_layout.addWidget(self.decrypt_file_btn)
        
        box_layout.addLayout(btn_layout)
        layout.addWidget(encryption_box)
        self.tabs.addTab(tab, "FILE ENCRYPTER")

    # Tab 6: Password Generator
    def create_generator_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        gen_box = QGroupBox("PASSCODE GENERATOR")
        box_layout = QFormLayout(gen_box)
        
        self.gen_len = QSpinBox()
        self.gen_len.setRange(8, 64)
        self.gen_len.setValue(16)
        box_layout.addRow(QLabel("LENGTH:"), self.gen_len)
        
        self.chk_upper = QCheckBox()
        self.chk_upper.setChecked(True)
        box_layout.addRow(QLabel("UPPERCASE (A-Z):"), self.chk_upper)
        
        self.chk_lower = QCheckBox()
        self.chk_lower.setChecked(True)
        box_layout.addRow(QLabel("LOWERCASE (a-z):"), self.chk_lower)
        
        self.chk_digits = QCheckBox()
        self.chk_digits.setChecked(True)
        box_layout.addRow(QLabel("DIGITS (0-9):"), self.chk_digits)
        
        self.chk_special = QCheckBox()
        self.chk_special.setChecked(True)
        box_layout.addRow(QLabel("SPECIAL SYMBOLS:"), self.chk_special)
        
        self.gen_btn = QPushButton("GENERATE STRONG KEY")
        self.gen_btn.clicked.connect(self.generate_passcode)
        box_layout.addRow(self.gen_btn)
        
        self.gen_output = QLineEdit()
        self.gen_output.setReadOnly(True)
        self.gen_copy_btn = QPushButton("Copy to Clipboard")
        self.gen_copy_btn.clicked.connect(self.copy_generated_pwd)
        
        out_layout = QHBoxLayout()
        out_layout.addWidget(self.gen_output)
        out_layout.addWidget(self.gen_copy_btn)
        box_layout.addRow(QLabel("RESULT:"), out_layout)
        
        layout.addWidget(gen_box)
        self.tabs.addTab(tab, "KEY GEN")

    # --- UI Logic & Actions ---
    def refresh_all_lists(self):
        # Refresh passwords
        self.pwd_list.clear()
        if "passwords" in self.vault_data:
            for item in self.vault_data["passwords"]:
                self.pwd_list.addItem(item.get("title", "Untitled"))
                
        # Refresh notes
        self.notes_list.clear()
        if "notes" in self.vault_data:
            for item in self.vault_data["notes"]:
                self.notes_list.addItem(item.get("title", "Untitled"))
                
        # Refresh SSH
        self.ssh_list.clear()
        if "ssh_keys" in self.vault_data:
            for item in self.vault_data["ssh_keys"]:
                self.ssh_list.addItem(item.get("title", "Untitled"))
                
        # Refresh API Keys
        self.api_list.clear()
        if "api_keys" in self.vault_data:
            for item in self.vault_data["api_keys"]:
                self.api_list.addItem(item.get("title", "Untitled"))

    def save_current_state(self):
        self.encryptor.save_vault(self.master_password, self.vault_data)

    # Password tab handlers
    def display_password_item(self, item):
        title = item.text()
        match = next((x for x in self.vault_data["passwords"] if x["title"] == title), None)
        if match:
            self.pwd_info_label.setText(
                f"TITLE: {match.get('title')}\n"
                f"USERNAME: {match.get('username')}\n"
                f"URL: {match.get('url')}\n"
                f"NOTES: {match.get('notes')}"
            )
            self.current_selected_password = match
            self.pwd_copy_btn.setEnabled(True)
            self.pwd_delete_btn.setEnabled(True)

    def filter_passwords(self, text):
        for i in range(self.pwd_list.count()):
            item = self.pwd_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def copy_current_password(self):
        if hasattr(self, 'current_selected_password'):
            QApplication.clipboard().setText(self.current_selected_password.get("password", ""))
            QMessageBox.information(self, "Clipboard", "Password copied!")

    def delete_current_password(self):
        if hasattr(self, 'current_selected_password'):
            self.vault_data["passwords"].remove(self.current_selected_password)
            self.save_current_state()
            self.pwd_info_label.setText("Select an item to view")
            self.pwd_copy_btn.setEnabled(False)
            self.pwd_delete_btn.setEnabled(False)
            self.refresh_all_lists()

    def add_password_dialog(self):
        title, ok1 = QInputDialog.getText(self, "BlackVault", "Enter Service Title:")
        if not ok1 or not title: return
        user, ok2 = QInputDialog.getText(self, "BlackVault", "Enter Username:")
        if not ok2: return
        pwd, ok3 = QInputDialog.getText(self, "BlackVault", "Enter Password:")
        if not ok3: return
        url, ok4 = QInputDialog.getText(self, "BlackVault", "Enter URL:")
        if not ok4: return
        notes, ok5 = QInputDialog.getText(self, "BlackVault", "Enter Notes:")
        if not ok5: return
        
        new_item = {
            "title": title,
            "username": user,
            "password": pwd,
            "url": url,
            "notes": notes
        }
        self.vault_data["passwords"].append(new_item)
        self.save_current_state()
        self.refresh_all_lists()

    # Notes handlers
    def display_note_item(self, item):
        title = item.text()
        match = next((x for x in self.vault_data["notes"] if x["title"] == title), None)
        if match:
            self.note_content_view.setPlainText(match.get("content", ""))
            self.note_content_view.setReadOnly(False)
            self.current_selected_note = match
            self.note_save_btn.setEnabled(True)
            self.note_delete_btn.setEnabled(True)

    def save_note_changes(self):
        if hasattr(self, 'current_selected_note'):
            self.current_selected_note["content"] = self.note_content_view.toPlainText()
            self.save_current_state()
            QMessageBox.information(self, "Success", "Note updated successfully!")

    def delete_current_note(self):
        if hasattr(self, 'current_selected_note'):
            self.vault_data["notes"].remove(self.current_selected_note)
            self.save_current_state()
            self.note_content_view.clear()
            self.note_content_view.setReadOnly(True)
            self.note_save_btn.setEnabled(False)
            self.note_delete_btn.setEnabled(False)
            self.refresh_all_lists()

    def add_note_dialog(self):
        title, ok = QInputDialog.getText(self, "BlackVault", "Enter Note Title:")
        if ok and title:
            new_item = {
                "title": title,
                "content": ""
            }
            self.vault_data["notes"].append(new_item)
            self.save_current_state()
            self.refresh_all_lists()

    # SSH key handlers
    def display_ssh_item(self, item):
        title = item.text()
        match = next((x for x in self.vault_data["ssh_keys"] if x["title"] == title), None)
        if match:
            self.ssh_key_view.setPlainText(match.get("private_key", ""))
            self.ssh_key_view.setReadOnly(False)
            self.ssh_info_label.setText(
                f"TITLE: {match.get('title')}\nPASSPHRASE: {match.get('passphrase')}"
            )
            self.current_selected_ssh = match
            self.ssh_copy_btn.setEnabled(True)
            self.ssh_delete_btn.setEnabled(True)

    def copy_current_ssh(self):
        if hasattr(self, 'current_selected_ssh'):
            QApplication.clipboard().setText(self.ssh_key_view.toPlainText())
            QMessageBox.information(self, "Clipboard", "SSH Private Key copied!")

    def delete_current_ssh(self):
        if hasattr(self, 'current_selected_ssh'):
            self.vault_data["ssh_keys"].remove(self.current_selected_ssh)
            self.save_current_state()
            self.ssh_key_view.clear()
            self.ssh_info_label.setText("Select an SSH key")
            self.ssh_copy_btn.setEnabled(False)
            self.ssh_delete_btn.setEnabled(False)
            self.refresh_all_lists()

    def add_ssh_dialog(self):
        title, ok1 = QInputDialog.getText(self, "BlackVault", "Enter Key Title:")
        if not ok1 or not title: return
        passphrase, ok2 = QInputDialog.getText(self, "BlackVault", "Enter Passphrase (optional):")
        if not ok2: return
        
        new_item = {
            "title": title,
            "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\n...\n-----END OPENSSH PRIVATE KEY-----",
            "passphrase": passphrase
        }
        self.vault_data["ssh_keys"].append(new_item)
        self.save_current_state()
        self.refresh_all_lists()

    # API keys handlers
    def display_api_item(self, item):
        title = item.text()
        match = next((x for x in self.vault_data["api_keys"] if x["title"] == title), None)
        if match:
            self.api_info_label.setText(
                f"SERVICE: {match.get('title')}\n"
                f"CLIENT ID: {match.get('client_id')}\n"
                f"API KEY: {match.get('key')}\n"
                f"NOTES: {match.get('notes')}"
            )
            self.current_selected_api = match
            self.api_copy_btn.setEnabled(True)
            self.api_delete_btn.setEnabled(True)

    def copy_current_api(self):
        if hasattr(self, 'current_selected_api'):
            QApplication.clipboard().setText(self.current_selected_api.get("key", ""))
            QMessageBox.information(self, "Clipboard", "API Key copied!")

    def delete_current_api(self):
        if hasattr(self, 'current_selected_api'):
            self.vault_data["api_keys"].remove(self.current_selected_api)
            self.save_current_state()
            self.api_info_label.setText("Select an API key")
            self.api_copy_btn.setEnabled(False)
            self.api_delete_btn.setEnabled(False)
            self.refresh_all_lists()

    def add_api_dialog(self):
        title, ok1 = QInputDialog.getText(self, "BlackVault", "Enter Service Name:")
        if not ok1 or not title: return
        client_id, ok2 = QInputDialog.getText(self, "BlackVault", "Enter Client ID/App ID:")
        if not ok2: return
        key, ok3 = QInputDialog.getText(self, "BlackVault", "Enter API Key:")
        if not ok3: return
        notes, ok4 = QInputDialog.getText(self, "BlackVault", "Enter Notes:")
        if not ok4: return
        
        new_item = {
            "title": title,
            "client_id": client_id,
            "key": key,
            "notes": notes
        }
        self.vault_data["api_keys"].append(new_item)
        self.save_current_state()
        self.refresh_all_lists()

    # File crypt handlers
    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Target File")
        if path:
            self.selected_file_input.setText(path)

    def encrypt_file(self):
        path = self.selected_file_input.text()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Warning", "Please select a valid file.")
            return
        
        dest_path = path + ".enc"
        success = self.encryptor.encrypt_external_file(self.master_password, path, dest_path)
        if success:
            QMessageBox.information(self, "Success", f"File encrypted to:\n{dest_path}")
            self.selected_file_input.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to encrypt file.")

    def decrypt_file(self):
        path = self.selected_file_input.text()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Warning", "Please select a valid file.")
            return
        
        if not path.endswith(".enc"):
            QMessageBox.warning(self, "Warning", "Target file does not appear to be encrypted (.enc).")
            
        dest_path = path[:-4] if path.endswith(".enc") else path + ".dec"
        success = self.encryptor.decrypt_external_file(self.master_password, path, dest_path)
        if success:
            QMessageBox.information(self, "Success", f"File decrypted to:\n{dest_path}")
            self.selected_file_input.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to decrypt file.")

    # Passcode generator handler
    def generate_passcode(self):
        length = self.gen_len.value()
        chars = ""
        if self.chk_upper.isChecked():
            chars += string.ascii_uppercase
        if self.chk_lower.isChecked():
            chars += string.ascii_lowercase
        if self.chk_digits.isChecked():
            chars += string.digits
        if self.chk_special.isChecked():
            chars += string.punctuation
            
        if not chars:
            QMessageBox.warning(self, "Warning", "Please select at least one character type.")
            return
            
        res = "".join(random.choice(chars) for _ in range(length))
        self.gen_output.setText(res)

    def copy_generated_pwd(self):
        val = self.gen_output.text()
        if val:
            QApplication.clipboard().setText(val)
            QMessageBox.information(self, "Clipboard", "Passcode copied!")

# Main Execution Entry
def main():
    app = QApplication(sys.argv)
    window = BlackVaultApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
