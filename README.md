<div align="center">

# 🏝️ Dynamic Island for Windows

**A sleek, fluid, and modern multitasking experience brought to the Windows desktop.**

[![Website](https://img.shields.io/badge/Website-denisdev.online-8A2BE2?style=for-the-badge&logo=googlechrome&logoColor=white)](https://denisdev.online/projects/dynamic_island/index.html)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/)
[![Built with](https://img.shields.io/badge/Python-CustomTkinter-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

<p align="center">
  <b>Seamlessly docks at the top of your screen, morphing dynamically based on what you're doing.</b>
</p>

[Explore Website](https://denisdev.online/projects/dynamic_island/index.html) • [Download Setup](#-quick-install-installer) • [Run Script (.pyw)](#-run-standalone-script-pyw) • [Features](#-core-features)

---

</div>

## 🌟 Overview

**Dynamic Island for Windows** bridges the gap between clean aesthetics and practical desktop utilities. Built to deliver native-feeling responsiveness, it stays docked unobtrusively at the top of your display, dynamically expanding to reveal media controls, weather updates, and quick settings without interrupting your workflow.

---

## ⚡ Core Features

<div align="center">
  <table>
    <tr>
      <td width="50%" align="center">
        <img src="https://denisdev.online/projects/dynamic_island/media.png" alt="Media Player" width="100%"/>
        <br/><b>🎵 Smart Media Controller</b><br/>
        <i>Track titles, artist info, progress bar, and media controls.</i>
      </td>
      <td width="50%" align="center">
        <img src="https://denisdev.online/projects/dynamic_island/weather.png" alt="Weather Widget" width="100%"/>
        <br/><b>🌦️ Live Weather</b><br/>
        <i>Real-time temperature and forecast glance directly from your desktop.</i>
      </td>
    </tr>
    <tr>
      <td width="50%" align="center">
        <img src="https://denisdev.online/projects/dynamic_island/settings.png" alt="Quick Settings" width="100%"/>
        <br/><b>📶 Quick Toggles</b><br/>
        <i>Fast switches for Wi-Fi and Bluetooth connectivity.</i>
      </td>
      <td width="50%" align="center">
        <img src="https://denisdev.online/projects/dynamic_island/hud.png" alt="Brightness and Volume" width="100%"/>
        <br/><b>☀️ Volume & Brightness HUD</b><br/>
        <i>Minimalist floating controls to adjust audio and screen brightness smoothly.</i>
      </td>
    </tr>
  </table>
</div>

### 🎨 Visual & Performance Highlights
- **Dark Mode & Glassmorphic UI:** Translucent acrylic blur with dynamic gradients that adapt cleanly over any wallpaper.
- **Micro-Animations:** Smooth expansion, morphing physics, and responsive hover transitions.
- **Resource Efficient:** Built to sit dormant in background threads without chewing clock cycles.
- **Background Tray Integration:** Auto-minimizes to the Windows system tray with quick-access settings and launch-on-boot support.

---

## 🚀 Quick Install (Installer)

Download the official preconfigured setup directly from the website:

👉 **[Download Dynamic Island Setup](https://denisdev.online/projects/dynamic_island/index.html)**

1. Download the executable **`DynamicIsland-Setup.exe`**.
2. Run the guided installer (installs files, creates desktop and Start Menu shortcuts).
3. Check the **"Start with Windows"** option if you want it to launch automatically upon startup.
4. Hit finish and enjoy your Dynamic Island!

---

## 🐍 Run Standalone Script (.pyw)

If you prefer not to use the installer and want a lightweight folder containing only the Python script without a console window:

1. **Create a folder** (e.g., `DynamicIsland`) and place the **`dynamic_island.pyw`** script inside (downloadable from the `/src` folder or releases).
2. Make sure you have **Python 3.10+** installed with the *"Add python.exe to PATH"* option checked.
3. Open your terminal (Command Prompt or PowerShell) inside the folder and install the required packages:

```bash
pip install customtkinter pillow psutil
