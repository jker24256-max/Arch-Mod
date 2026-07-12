import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
    QProgressBar, QGroupBox, QFileDialog, QMessageBox, QTabWidget,
    QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from scanner import NetworkScanner

# Theme Styling
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
QProgressBar {
    border: 1px solid #8D99AE;
    border-radius: 5px;
    text-align: center;
    background-color: #151A21;
}
QProgressBar::chunk {
    background-color: #D90429;
}
QTableWidget {
    background-color: #151A21;
    border: 1px solid #8D99AE;
    gridline-color: #2B303A;
    color: #EDF2F4;
}
QHeaderView::section {
    background-color: #1F2833;
    color: #D90429;
    padding: 6px;
    border: 1px solid #8D99AE;
    font-weight: bold;
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

class ScanWorker(QThread):
    host_found = pyqtSignal(dict)
    finished_scan = pyqtSignal(list)

    def __init__(self, scanner):
        super().__init__()
        self.scanner = scanner

    def run(self):
        hosts = self.scanner.scan_subnet(self.host_found.emit)
        self.finished_scan.emit(hosts)

class SentryOpsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scanner = NetworkScanner()
        self.scanned_hosts = []
        
        self.setWindowTitle("SENTRYOPS // NETWORK DIAGNOSTIC & HARDENING")
        self.setMinimumSize(950, 650)
        self.setStyleSheet(STYLE_SHEET)
        
        # Central Layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Top banner info
        self.net_info_label = QLabel("INITIALIZING SENTRYOPS STACK...")
        self.net_info_label.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        self.net_info_label.setStyleSheet("color: #D90429;")
        main_layout.addWidget(self.net_info_label)
        
        # Tabs container
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.init_dashboard_tab()
        self.init_wifi_tab()
        self.init_logs_tab()
        
        # Actions layout at bottom
        btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("RUN SUBNET SCAN")
        self.scan_btn.clicked.connect(self.start_subnet_scan)
        btn_layout.addWidget(self.scan_btn)
        
        self.report_btn = QPushButton("GENERATE THREAT REPORT")
        self.report_btn.clicked.connect(self.export_report)
        self.report_btn.setEnabled(False)
        btn_layout.addWidget(self.report_btn)
        
        main_layout.addLayout(btn_layout)
        
        # Pull initial info
        self.refresh_network_details()

    def refresh_network_details(self):
        details = self.scanner.get_network_details()
        self.net_info_label.setText(
            f"SSID: {details['ssid']} // GATEWAY: {details['gateway_ip']} // LOCAL IP: {details['local_ip']} // SUBNET: {details['subnet']}"
        )
        self.current_network_details = details

    def init_dashboard_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Subnet hosts table
        left_layout = QVBoxLayout()
        hosts_box = QGroupBox("SUBNET ALIVE HOSTS")
        hosts_layout = QVBoxLayout(hosts_box)
        
        self.hosts_table = QTableWidget()
        self.hosts_table.setColumnCount(4)
        self.hosts_table.setHorizontalHeaderLabels(["IP Address", "Hostname", "Role", "Open Ports"])
        self.hosts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hosts_layout.addWidget(self.hosts_table)
        
        left_layout.addWidget(hosts_box)
        layout.addLayout(left_layout, 3)
        
        # Security Rating Panel
        right_layout = QVBoxLayout()
        rating_box = QGroupBox("SECURITY POSTURE SCORE")
        rating_layout = QVBoxLayout(rating_box)
        
        self.score_label = QLabel("SCORE: 10/100")
        self.score_label.setFont(QFont("Courier New", 18, QFont.Weight.Bold))
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rating_layout.addWidget(self.score_label)
        
        self.score_bar = QProgressBar()
        self.score_bar.setValue(10)
        rating_layout.addWidget(self.score_bar)
        
        self.rating_label = QLabel("RATING: SECURE")
        self.rating_label.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        self.rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rating_label.setStyleSheet("color: #00FF00;")
        rating_layout.addWidget(self.rating_label)
        
        right_layout.addWidget(rating_box)
        
        # Vulnerabilities box
        vuln_box = QGroupBox("DETECTED SECURITY ISSUES")
        vuln_layout = QVBoxLayout(vuln_box)
        self.vuln_view = QTextEdit()
        self.vuln_view.setReadOnly(True)
        self.vuln_view.setPlaceholderText("No critical subnet/wifi vulnerabilities discovered.")
        vuln_layout.addWidget(self.vuln_view)
        
        right_layout.addWidget(vuln_box)
        layout.addLayout(right_layout, 2)
        
        self.tabs.addTab(tab, "DASHBOARD")

    def init_wifi_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        wifi_box = QGroupBox("WIRELESS SURVEY (AP SCANNER)")
        wifi_layout = QVBoxLayout(wifi_box)
        
        self.wifi_table = QTableWidget()
        self.wifi_table.setColumnCount(4)
        self.wifi_table.setHorizontalHeaderLabels(["SSID", "BSSID", "Signal", "Security"])
        self.wifi_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        wifi_layout.addWidget(self.wifi_table)
        
        wifi_btn = QPushButton("SURVEY WIRELESS BANDS")
        wifi_btn.clicked.connect(self.survey_wifi)
        wifi_layout.addWidget(wifi_btn)
        
        layout.addWidget(wifi_box)
        self.tabs.addTab(tab, "WIFI ANALYZER")

    def init_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        logs_box = QGroupBox("SENTRYOPS DIAGNOSTIC CONSOLE")
        logs_layout = QVBoxLayout(logs_box)
        
        self.console_log = QTextEdit()
        self.console_log.setReadOnly(True)
        logs_layout.addWidget(self.console_log)
        
        layout.addWidget(logs_box)
        self.tabs.addTab(tab, "CONSOLE LOGS")

    # --- Scanning Controllers ---
    def log_message(self, message):
        self.console_log.append(f"[SENTRYOPS] >> {message}")

    def start_subnet_scan(self):
        self.refresh_network_details()
        self.hosts_table.setRowCount(0)
        self.scanned_hosts = []
        self.log_message(f"Starting active host detection on subnet: {self.current_network_details['subnet']}...")
        self.scan_btn.setEnabled(False)
        self.report_btn.setEnabled(False)
        
        self.worker = ScanWorker(self.scanner)
        self.worker.host_found.connect(self.add_host_to_table)
        self.worker.finished_scan.connect(self.subnet_scan_complete)
        self.worker.start()

    def add_host_to_table(self, host):
        self.scanned_hosts.append(host)
        row = self.hosts_table.rowCount()
        self.hosts_table.insertRow(row)
        
        self.hosts_table.setItem(row, 0, QTableWidgetItem(host["ip"]))
        self.hosts_table.setItem(row, 1, QTableWidgetItem(host["hostname"]))
        self.hosts_table.setItem(row, 2, QTableWidgetItem(host["role"]))
        
        ports_str = ", ".join(map(str, host["ports"])) if host["ports"] else "None"
        self.hosts_table.setItem(row, 3, QTableWidgetItem(ports_str))
        
        self.log_message(f"Discovered active host: {host['ip']} ({host['hostname']})")

    def subnet_scan_complete(self, hosts):
        self.scan_btn.setEnabled(True)
        self.report_btn.setEnabled(True)
        self.log_message(f"Subnet scan completed. Found {len(hosts)} active devices.")
        
        score, rating, vulns = self.scanner.calculate_threat_score(self.scanner.wifi_networks, hosts)
        self.score_label.setText(f"SCORE: {score}/100")
        self.score_bar.setValue(score)
        self.rating_label.setText(f"RATING: {rating}")
        
        if score > 75:
            self.rating_label.setStyleSheet("color: #D90429;")
        elif score > 45:
            self.rating_label.setStyleSheet("color: #FF8C00;")
        else:
            self.rating_label.setStyleSheet("color: #00FF00;")
            
        self.vuln_view.clear()
        if vulns:
            self.vuln_view.setPlainText("\n\n".join(f"[!] {v}" for v in vulns))
        else:
            self.vuln_view.setPlainText("All checked criteria comply with JKER OS security hardening recommendations.")

    def survey_wifi(self):
        self.log_message("Initiating 802.11 wireless bands survey...")
        self.wifi_table.setRowCount(0)
        networks = self.scanner.scan_wifi()
        
        for net in networks:
            row = self.wifi_table.rowCount()
            self.wifi_table.insertRow(row)
            self.wifi_table.setItem(row, 0, QTableWidgetItem(net["ssid"]))
            self.wifi_table.setItem(row, 1, QTableWidgetItem(net["bssid"]))
            self.wifi_table.setItem(row, 2, QTableWidgetItem(net["signal"] + "%"))
            self.wifi_table.setItem(row, 3, QTableWidgetItem(net["security"]))
            
        self.log_message(f"Wireless bands survey complete. Discovered {len(networks)} Access Points.")

    def export_report(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Threat Assessment Report", "", "Markdown Files (*.md);;HTML Files (*.html)")
        if not path:
            return
            
        score, rating, vulns = self.scanner.calculate_threat_score(self.scanner.wifi_networks, self.scanned_hosts)
        
        report_content = f"""# JKER OS // SentryOps Network Security Audit Report
Generated automatically by SentryOps security analyzer engine.

## Network Context
* **Active SSID**: {self.current_network_details['ssid']}
* **Wi-Fi Security**: {self.current_network_details['security']}
* **Gateway IP**: {self.current_network_details['gateway_ip']}
* **Local Assignment**: {self.current_network_details['local_ip']}
* **Subnet Boundary**: {self.current_network_details['subnet']}

## Risk posture Summary
* **Threat Score**: {score} / 100
* **Rating**: {rating}

## Discovered Active Hosts
"""
        for host in self.scanned_hosts:
            ports_str = ", ".join(map(str, host["ports"])) if host["ports"] else "None"
            report_content += f"* **Host**: {host['ip']} ({host['hostname']}) | Role: {host['role']} | Open Ports: {ports_str}\n"

        report_content += "\n## Identified Vulnerabilities & Hardening Advisories\n"
        if vulns:
            for v in vulns:
                report_content += f"* [VULNERABILITY] {v}\n"
        else:
            report_content += "* No vulnerabilities discovered during subnet and AP audit.\n"
            
        report_content += "\n---\nReport compiled by JKER OS Tactical Security Suite.\n"

        try:
            with open(path, "w") as f:
                f.write(report_content)
            QMessageBox.information(self, "Success", f"Report saved successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save report: {e}")

# Entry point
def main():
    app = QApplication(sys.argv)
    window = SentryOpsApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
