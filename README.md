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

[Explore Website](https://denisdev.online/projects/dynamic_island/index.html) • [Download Setup](#-quick-install-installer) • [Run Script (.pyw)](#-run-standalone-script-pyw) • [Features](#-core-features)

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

## 🚀 Quick Install (Installer)

Scarica il setup preconfigurato ufficiale direttamente dal sito:

👉 **[Scarica Dynamic Island Setup](https://denisdev.online/projects/dynamic_island/index.html)**

1. Scarica l'eseguibile **`DynamicIsland-Setup.exe`**.
2. Avvia l'installer guidato (installa i file, crea i collegamenti sul desktop e nel menu Start).
3. Spunta l'opzione **"Start with Windows"** se vuoi avviarlo automaticamente a ogni accensione.
4. Premi fine e goditi la tua Dynamic Island!

---

## 🐍 Run Standalone Script (.pyw)

Se non vuoi usare l'installer e preferisci avere una cartella leggera con solo lo script Python senza finestra di console:

1. **Crea una cartella** (es. `DynamicIsland`) e inserisci all'interno lo script **`dynamic_island.pyw`** (scaricabile dalla cartella `/src` o dalle release).
2. Assicurati di avere installato **Python 3.10+** con l'opzione *"Add python.exe to PATH"* spuntata.
3. Apri il terminale (Prompt dei comandi o PowerShell) all'interno della cartella e installa i pacchetti necessari:

```bash
pip install customtkinter pillow psutil
