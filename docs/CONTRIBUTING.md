# JKER OS // Developer Contribution Guide

Welcome to the JKER OS distribution developer guide! This document outlines code standards, package manifests structures, and contribution guidelines.

---

## 1. Development Guidelines

### Adding Custom Applications
All native JKER applications are written in Python 3 and use the PyQt6 GUI framework. To add a new application:
1.  Place code in a subdirectory under `applications/` (e.g. `applications/myapp/`).
2.  Follow the **Tactical Minimalist Dashboard** style sheet definitions. Use fonts, colors, and layout borders matching [ARCHITECTURE.md](ARCHITECTURE.md#design-system-standards).
3.  Add an entry in `packages/installer.list` or similar manifests for any new python module dependencies (e.g. `python-requests`).
4.  Create a shell script wrapper under `archiso/airootfs/usr/bin/` so the live environment can launch it:
    ```sh
    #!/bin/sh
    exec python3 /usr/share/jker-apps/myapp/myapp.py "$@"
    ```
5.  Add permissions to the wrapper in `archiso/profiledef.sh` under `file_permissions`:
    ```bash
    ["/usr/bin/myapp"]="0:0:0755"
    ```
6.  Register your application launch class in [scripts/test_apps.py](file:///c:/Users/abdul/Documents/Arch-Mod/scripts/test_apps.py) so it is validated during the test verification phase.

### Editing Package manifests
Do not write hardcoded installation package strings in build files. All packages must be listed inside files under `packages/`:
*   `base.list`: Essential boot systems, microcodes, core network.
*   `desktop.list`: Compositor window managers, bars, font styles, panels, audio.
*   `security.list`: Hardening daemons and security audit scripts.
*   `developer.list`: Programming languages and compiler runtimes.
*   `gaming.list`: Wine, Steam, multilib gaming dependency drivers.
*   `installer.list`: Libraries required to execute the system installer.

To add new distribution editions, create or modify lists and update the conditional matrices in `build.sh`.

---

## 2. Style Sheet & Coding Standards

*   **Monospace Fonts**: Use `'Courier New', monospace` for user interface panels to match the tactical theme.
*   **Shell Scripting**: All bash scripts must be formatted and declare `set -euo pipefail` for error propagation.
*   **Python**: Follow PEP 8 style conventions. Keep event loop threads responsive by offloading heavy system/network processes onto separate worker threads inheriting from `QThread`.

---

## 3. Pull Request Guidelines

Before submitting pull requests:
1.  **Test Custom Applications**: Run the test runner script to ensure zero UI crashes:
    ```bash
    ./test.sh
    ```
2.  **Verify the Build**: Verify the ISO build compiles cleanly. Run locally or in Docker using:
    ```bash
    ./build.sh --edition desktop
    ```
3.  **Run release checks**: Ensure the ISO can be successfully processed using `release.sh`.
