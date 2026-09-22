<div align="center">

# 🏝️ Dynamic Island for Windows

**A sleek, fluid, and modern multitasking experience brought to the Windows desktop.**

[![Website](https://img.shields.io/badge/Website-denisdev.online-8A2BE2?style=for-the-badge&logo=googlechrome&logoColor=white)](https://denisdev.online/projects/dynamic_island/index.html)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/)
[![Built with](https://img.shields.io/badge/Python-CustomTkinter-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

<!-- Hero Banner / Showcase Preview -->
<img src="https://denisdev.online/projects/dynamic_island/preview.png" alt="Dynamic Island Showcase" width="850px" style="border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.5);" />

<p align="center">
  <b>Seamlessly docks at the top of your screen, morphing dynamically based on what you're doing.</b>
</p>

[Explore Website](https://denisdev.online/projects/dynamic_island/index.html) • [Download Setup](#-quick-install) • [Features](#-core-features) • [Manual Setup](#-manual-development)

---

</div>

## 🌟 Overview

**Dynamic Island for Windows** bridges the gap between clean aesthetics and practical desktop utilities. Built to deliver native-feeling responsiveness, it stays docked unobtrusively at the top of your display, dynamically expanding to reveal interactive widgets, hardware telemetry, and controls without interrupting your workflow.

---

## ⚡ Core Features

<div align="center">
  <table>
    <tr>
      <td width="50%" align="center">
        <img src="https://denisdev.online/projects/dynamic_island/media.png" alt="Media Player" width="100%"/>
        <br/><b>🎵 Smart Media Controller</b><br/>
        <i>Real-time track titles, album artwork, progress bars, and playback gestures.</i>
      </td>
      <td width="50%" align="center">
        <img src="https://denisdev.online/projects/dynamic_island/stats.png" alt="Hardware Telemetry" width="100%"/>
        <br/><b>📊 System HUD & Telemetry</b><br/>
        <i>Live CPU, GPU, and RAM telemetry with discreet status alerts.</i>
      </td>
    </tr>
    <tr>
      <td width="50%" align="center">
        <img src="https://denisdev.online/projects/dynamic_island/battery.png" alt="Battery & Power" width="100%"/>
        <br/><b>🔋 Power & Hardware Alerts</b><br/>
        <i>Fluid popups for charging states, low power warnings, and device plug/unplug.</i>
      </td>
      <td width="50%" align="center">
        <img src="https://denisdev.online/projects/dynamic_island/hud.png" alt="Volume HUD" width="100%"/>
        <br/><b>🔊 Modern Volume & Brightness HUD</b><br/>
        <i>Minimalist floating bars that replace bulky default Windows on-screen displays.</i>
      </td>
    </tr>
  </table>
</div>

### 🎨 Visual & Performance Highlights
- **Dark Mode & Glassmorphic UI:** Translucent acrylic blur with dynamic gradients that adapt cleanly over any wallpaper.
- **Micro-Animations:** Smooth expansion, morphing physics, and responsive hover transitions.
- **Resource Efficient:** Built to sit dormant in background threads without chewing clock cycles or battery.
- **Background Tray Integration:** Auto-minimizes to the Windows system tray with quick-access settings and launch-on-boot support.

---

## 🚀 Quick Install (Windows Setup Wizard)

Grab the pre-compiled installer from the **[Releases](../../releases)** section:

1. Download **`DynamicIsland-Setup.exe`**.
2. Run the installer wizard (installs to `Program Files`, adds Start Menu and Desktop shortcuts).
3. Check **"Start with Windows"** if you want it ready every time you boot.
4. Launch and enjoy!

---

## 🛠️ Manual Development

If you prefer building from the raw Python source:

```bash
# 1. Clone the repository
git clone [https://github.com/your-username/dynamic-island-windows.git](https://github.com/your-username/dynamic-island-windows.git)
cd dynamic-island-windows

# 2. Set up environment
python -m venv venv
venv\Scripts\activate

# 3. Install required libraries
pip install -r requirements.txt

# 4. Launch the application
python main.py
