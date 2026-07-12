#!/usr/bin/env python3
# ==============================================================================
# JKER OS Application Compilation & UI Verification Script
# Verifies that PyQt6 and cryptographic/network dependencies load without error.
# Instantiates each custom application and cycles their GUI event loop.
# ==============================================================================

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add application directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "applications", "blackvault"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "applications", "sentryops"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "applications", "downloadcenter"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "applications", "controlcenter"))

def test_application(app_class, name):
    print(f"[TEST] Verifying load status for: {name}...")
    try:
        # Create standard Qt Application context
        qt_app = QApplication.instance()
        if not qt_app:
            qt_app = QApplication(sys.argv)
            
        # Instantiate window
        window = app_class()
        
        # Schedule close after 500ms to verify loop loads and doesn't block indefinitely
        QTimer.singleShot(500, window.close)
        QTimer.singleShot(600, qt_app.quit)
        
        # Execute event loop briefly
        qt_app.exec()
        print(f"[SUCCESS] {name} initialized and closed successfully.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to compile or run {name}: {e}")
        return False

def main():
    print("=== STARTING JKER OS NATIVE APPLICATIONS VERIFICATION ===")
    
    # Imports
    try:
        from blackvault import BlackVaultApp
        from sentryops import SentryOpsApp
        from downloadcenter import DownloadCenterApp
        from controlcenter import ControlCenterApp
    except ImportError as e:
        print(f"[CRITICAL] Import error encountered. Are all application paths valid? {e}")
        sys.exit(1)

    tests = [
        (BlackVaultApp, "BlackVault Password Manager"),
        (SentryOpsApp, "SentryOps Threat Dashboard"),
        (DownloadCenterApp, "Download Center Store"),
        (ControlCenterApp, "JKER Control Center")
    ]
    
    failures = 0
    for app_cls, name in tests:
        if not test_application(app_cls, name):
            failures += 1
            
    print("=========================================================")
    if failures == 0:
        print("[SUCCESS] All JKER OS custom applications passed compilation tests.")
        sys.exit(0)
    else:
        print(f"[CRITICAL] {failures} application compilation checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
