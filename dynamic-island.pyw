#Current Version v2.0.0
import sys
import asyncio
import requests
import random
import threading
import os
import ctypes
from ctypes import wintypes
import psutil
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QHBoxLayout, QStackedWidget, QPushButton, QSlider, QProgressBar,
                             QDialog, QTabWidget, QColorDialog, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer, QTime, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPixmap

user32 = ctypes.windll.user32
class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

def is_fullscreen():
    hwnd = user32.GetForegroundWindow()
    if not hwnd: return False
    class_name = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_name, 256)
    if class_name.value in ("Progman", "WorkerW"): return False

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    hMonitor = user32.MonitorFromWindow(hwnd, 2)
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi))
    
    return (rect.right - rect.left) >= (mi.rcMonitor.right - mi.rcMonitor.left) and (rect.bottom - rect.top) >= (mi.rcMonitor.bottom - mi.rcMonitor.top)

try:
    import screen_brightness_control as sbc
except Exception:
    sbc = None

def get_system_brightness():
    if sbc:
        try:
            val = sbc.get_brightness()
            return val[0] if isinstance(val, list) else val
        except: pass
    return 70

def set_system_brightness(val):
    if sbc:
        try: threading.Thread(target=lambda: sbc.set_brightness(val), daemon=True).start()
        except: pass

class MiniVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(16, 12)
        self.is_playing = False
        self.current_bars = [2.0, 2.0, 2.0, 2.0]
        self.target_bars = [2.0, 2.0, 2.0, 2.0]
        self.color = QColor("#ffffff")
        
        self.logic_timer = QTimer()
        self.logic_timer.timeout.connect(self.update_targets)
        self.logic_timer.start(200)
        
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.smooth_render)
        self.render_timer.start(16)

    def set_color(self, hex_color):
        self.color = QColor(hex_color)

    def update_targets(self):
        if self.is_playing: self.target_bars = [random.uniform(3, 11) for _ in range(4)]
        else: self.target_bars = [1.5, 1.5, 1.5, 1.5]

    def smooth_render(self):
        for i in range(4): self.current_bars[i] += (self.target_bars[i] - self.current_bars[i]) * 0.2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.color) 
        painter.setPen(Qt.PenStyle.NoPen)
        for i, h in enumerate(self.current_bars):
            painter.drawRoundedRect(i * 4, int(12 - h), 2, int(h), 1, 1)

class NotificationWorker(QThread):
    notification_received = pyqtSignal(str, str)

    def run(self):
        try:
            from winsdk.windows.ui.notifications.management import UserNotificationListener
            from winsdk.windows.ui.notifications import NotificationKinds
            
            async def listen():
                listener = UserNotificationListener.get_current()
                known_ids = set()
                while True:
                    try:
                        notifs = await listener.get_notifications_async(NotificationKinds.TOAST)
                        for n in notifs:
                            if n.id not in known_ids:
                                known_ids.add(n.id)
                                binding = n.notification.visual.get_binding("ToastGeneric")
                                if binding:
                                    texts = binding.get_text_elements()
                                    title = texts[0].text if len(texts) > 0 else "Notification"
                                    body = texts[1].text if len(texts) > 1 else "New Message Received"
                                    self.notification_received.emit(title, body)
                    except: pass
                    await asyncio.sleep(1)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(listen())
        except: pass

class DataWorker(QThread):
    media_updated = pyqtSignal(str, str, bytes, bool, int, int)
    weather_updated = pyqtSignal(str, int)
    sys_stats_updated = pyqtSignal(int, int, int) 

    def run(self):
        try:
            from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
            from winsdk.windows.storage.streams import DataReader
        except ImportError:
            MediaManager = None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        weather_counter = 0
        last_title = None
        cached_thumb = b""

        while True:
            if MediaManager:
                try:
                    async def get_media():
                        sessions = await MediaManager.request_async()
                        current = sessions.get_current_session()
                        if not current: return None, "", "", False, 0, 0
                        info = await current.try_get_media_properties_async()
                        playback = current.get_playback_info()
                        timeline = current.get_timeline_properties()
                        pos = int(timeline.position.total_seconds()) if timeline else 0
                        tot = int(timeline.end_time.total_seconds()) if timeline else 0
                        is_play = (playback.playback_status == 4)
                        return info, info.title, info.artist, is_play, pos, tot
                    
                    info, title, artist, is_play, pos, tot = loop.run_until_complete(get_media())
                    
                    if title:
                        if title != last_title:
                            cached_thumb = b""
                            if info.thumbnail:
                                try:
                                    async def get_thumb():
                                        stream = await info.thumbnail.open_read_async()
                                        reader = DataReader(stream)
                                        await reader.load_async(stream.size)
                                        buf = bytearray(stream.size)
                                        reader.read_bytes(buf)
                                        return bytes(buf)
                                    cached_thumb = loop.run_until_complete(get_thumb())
                                except: pass
                            last_title = title
                        self.media_updated.emit(title, artist, cached_thumb, is_play, pos, tot)
                    else:
                        self.media_updated.emit("", "", b"", False, 0, 0)
                        last_title = None
                except: 
                    self.media_updated.emit("", "", b"", False, 0, 0)
                    last_title = None

            if weather_counter % 600 == 0:
                try:
                    url = "https://api.open-meteo.com/v1/forecast?latitude=45.96&longitude=12.65&current_weather=true"
                    res = requests.get(url).json()
                    temp_val = int(res['current_weather']['temperature'])
                    self.weather_updated.emit(f"{temp_val}°C", temp_val)
                except: pass
            weather_counter += 1

            try:
                cpu = int(psutil.cpu_percent())
                ram = int(psutil.virtual_memory().percent)
                batt = psutil.sensors_battery()
                batt_val = int(batt.percent) if batt else 100
                self.sys_stats_updated.emit(cpu, ram, batt_val)
            except: pass

            QThread.sleep(1)

def media_control(action):
    def fire_and_forget():
        try:
            from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
            async def do_action():
                sessions = await MediaManager.request_async()
                current = sessions.get_current_session()
                if current:
                    if action == "play_pause": await current.try_toggle_play_pause_async()
                    elif action == "next": await current.try_skip_next_async()
                    elif action == "prev": await current.try_skip_previous_async()
            asyncio.run(do_action())
        except: pass
    threading.Thread(target=fire_and_forget, daemon=True).start()

class ControlPanelDialog(QDialog):
    def __init__(self, main_island):
        super().__init__()
        self.island = main_island
        self.setWindowTitle("Dynamic Island Control Panel")
        self.resize(400, 480)
        self.setStyleSheet("QDialog { background-color: #121212; color: #ffffff; font-family: 'Segoe UI Variable Display'; } QLabel { color: #ffffff; } QPushButton { background-color: #222; color: #fff; border: 1px solid #444; border-radius: 6px; padding: 6px; } QPushButton:hover { background-color: #333; } QSlider::groove:horizontal { background: #333; height: 6px; border-radius: 3px; } QSlider::sub-page:horizontal { background: #0a84ff; height: 6px; border-radius: 3px; } QSlider::handle:horizontal { background: #ffffff; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; } QComboBox { background: #222; color: #fff; border: 1px solid #444; border-radius: 6px; padding: 4px; }")

        tabs = QTabWidget(self)
        tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #333; } QTabBar::tab { background: #1c1c1c; color: #888; padding: 8px 12px; } QTabBar::tab:selected { background: #2c2c2c; color: #fff; }")

        tab_pos = QWidget()
        l_pos = QVBoxLayout(tab_pos)
        l_pos.setSpacing(12)
        
        l_pos.addWidget(QLabel("Island Width Offset:"))
        self.slider_w = QSlider(Qt.Orientation.Horizontal)
        self.slider_w.setRange(250, 500)
        self.slider_w.setValue(self.island.large_rect.width())
        self.slider_w.valueChanged.connect(self.update_dimensions)
        l_pos.addWidget(self.slider_w)

        l_pos.addWidget(QLabel("Island Height Offset:"))
        self.slider_h = QSlider(Qt.Orientation.Horizontal)
        self.slider_h.setRange(180, 400)
        self.slider_h.setValue(self.island.large_rect.height())
        self.slider_h.valueChanged.connect(self.update_dimensions)
        l_pos.addWidget(self.slider_h)

        l_pos.addWidget(QLabel("Vertical Position Offset:"))
        self.slider_y = QSlider(Qt.Orientation.Horizontal)
        self.slider_y.setRange(-20, 50)
        self.slider_y.setValue(self.island.small_rect.top())
        self.slider_y.valueChanged.connect(self.update_dimensions)
        l_pos.addWidget(self.slider_y)
        l_pos.addStretch()

        tab_color = QWidget()
        l_col = QVBoxLayout(tab_color)
        l_col.setSpacing(12)

        self.btn_bg_color = QPushButton("Choose Custom Color")
        self.btn_bg_color.clicked.connect(self.pick_bg_color)
        l_col.addWidget(self.btn_bg_color)

        l_col.addWidget(QLabel("Background Opacity:"))
        self.slider_alpha = QSlider(Qt.Orientation.Horizontal)
        self.slider_alpha.setRange(50, 255)
        self.slider_alpha.setValue(self.island.bg_alpha)
        self.slider_alpha.valueChanged.connect(self.update_colors)
        l_col.addWidget(self.slider_alpha)
        l_col.addStretch()

        tab_theme = QWidget()
        l_thm = QVBoxLayout(tab_theme)
        l_thm.setSpacing(12)

        l_thm.addWidget(QLabel("Preset Themes:"))
        self.combo_presets = QComboBox()
        self.combo_presets.addItems(["Default Total Black", "Apple Glass", "Dark Neon", "Midnight Blue", "Sunset Gold"])
        self.combo_presets.currentIndexChanged.connect(self.apply_preset)
        l_thm.addWidget(self.combo_presets)

        self.chk_glass = QCheckBox("Enable Glass Style Alpha")
        self.chk_glass.setStyleSheet("color: white;")
        self.chk_glass.setChecked(self.island.glass_theme)
        self.chk_glass.toggled.connect(self.toggle_glass)
        l_thm.addWidget(self.chk_glass)
        l_thm.addStretch()

        tab_widgets = QWidget()
        l_wid = QVBoxLayout(tab_widgets)
        l_wid.setSpacing(12)

        l_wid.addWidget(QLabel("Compact Island Right Widget:"))
        self.combo_widget = QComboBox()
        self.combo_widget.addItems(["Weather", "CPU Usage", "RAM Usage", "Battery"])
        self.combo_widget.setCurrentText(self.island.mini_widget_selection)
        self.combo_widget.currentTextChanged.connect(self.update_widget_selection)
        l_wid.addWidget(self.combo_widget)
        l_wid.addStretch()

        tabs.addTab(tab_pos, "Position")
        tabs.addTab(tab_color, "Colors")
        tabs.addTab(tab_theme, "Themes")
        tabs.addTab(tab_widgets, "Widgets")

        bottom_lay = QHBoxLayout()
        self.btn_reset = QPushButton("Reset Default")
        self.btn_reset.clicked.connect(self.reset_defaults)
        self.btn_save = QPushButton("Apply Settings")
        self.btn_save.setStyleSheet("background-color: #0a84ff; font-weight: bold;")
        self.btn_save.clicked.connect(self.apply_changes)

        bottom_lay.addWidget(self.btn_reset)
        bottom_lay.addStretch()
        bottom_lay.addWidget(self.btn_save)

        main_lay = QVBoxLayout(self)
        main_lay.addWidget(tabs)
        main_lay.addLayout(bottom_lay)

    def update_dimensions(self):
        w = self.slider_w.value()
        h = self.slider_h.value()
        y = self.slider_y.value()
        
        self.island.small_rect = QRect(self.island.screen_w // 2 - (w // 3), y, w // 1.5, 36)
        self.island.large_rect = QRect(self.island.screen_w // 2 - (w // 2), y, w, h)
        self.island.hidden_rect = QRect(self.island.screen_w // 2 - (w // 3), -40, w // 1.5, 36)
        
        if self.island.stack.isVisible():
            self.island.setGeometry(self.island.large_rect)
        else:
            self.island.setGeometry(self.island.small_rect)

    def pick_bg_color(self):
        col = QColorDialog.getColor(self.island.bg_color, self, "Select Island Background")
        if col.isValid():
            self.island.bg_color = col
            self.update_colors()

    def update_colors(self):
        self.island.bg_alpha = self.slider_alpha.value()
        self.island.apply_theme()

    def toggle_glass(self, checked):
        self.island.glass_theme = checked
        self.island.apply_theme()

    def apply_preset(self, index):
        if index == 0:
            self.island.bg_color = QColor("#000000")
            self.island.bg_alpha = 255
            self.island.glass_theme = False
        elif index == 1:
            self.island.bg_color = QColor("#121212")
            self.island.bg_alpha = 180
            self.island.glass_theme = True
        elif index == 2:
            self.island.bg_color = QColor("#0d001a")
            self.island.bg_alpha = 230
            self.island.glass_theme = True
        elif index == 3:
            self.island.bg_color = QColor("#021024")
            self.island.bg_alpha = 240
            self.island.glass_theme = False
        elif index == 4:
            self.island.bg_color = QColor("#2b1e00")
            self.island.bg_alpha = 230
            self.island.glass_theme = True

        self.slider_alpha.setValue(self.island.bg_alpha)
        self.chk_glass.setChecked(self.island.glass_theme)
        self.island.apply_theme()

    def update_widget_selection(self, text):
        self.island.mini_widget_selection = text
        self.island.refresh_mini_widget()

    def apply_changes(self):
        self.island.apply_theme()

    def reset_defaults(self):
        self.combo_presets.setCurrentIndex(0)
        self.combo_widget.setCurrentIndex(0)
        self.slider_w.setValue(380)
        self.slider_h.setValue(275)
        self.slider_y.setValue(-2)
        self.update_dimensions()
        self.island.apply_theme()

class DynamicIsland(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.screen_w = QApplication.primaryScreen().geometry().width()
        
        self.bg_color = QColor("#000000")
        self.bg_alpha = 255
        self.glass_theme = False

        self.current_temp = "--°C"
        self.current_cpu = 0
        self.current_ram = 0
        self.current_batt = 100
        self.mini_widget_selection = "Weather"

        self.hidden_rect = QRect(self.screen_w // 2 - 110, -40, 220, 36)
        self.small_rect = QRect(self.screen_w // 2 - 120, -2, 240, 36)
        self.large_rect = QRect(self.screen_w // 2 - 190, -2, 380, 275)

        self.setGeometry(self.small_rect)
        self.is_hidden_by_fs = False 
        
        self.mode_state = 0 
        self.auto_hide_enabled = False
        self.force_fullscreen = False

        self.inactivity_timer = QTimer()
        self.inactivity_timer.timeout.connect(self.hide_island_completely)
        
        self.notif_timer = QTimer()
        self.notif_timer.setSingleShot(True)
        self.notif_timer.timeout.connect(self.clear_notification)

        self.init_ui()
        self.start_worker()
        self.apply_theme()

    def init_ui(self):
        self.container = QWidget(self)
        self.container.setObjectName("MainContainer")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(14, 4, 14, 4)
        self.layout.setSpacing(2)

        self.header_layout = QHBoxLayout()
        self.mini_art = QLabel()
        self.mini_art.setFixedSize(20, 20)
        self.mini_art.hide() 
        
        self.top_title = QLabel(QTime.currentTime().toString("HH:mm"))
        self.top_title.setFont(QFont("Segoe UI Variable Display", 10, QFont.Weight.Bold))
        
        self.visualizer = MiniVisualizer()
        self.visualizer.hide()
        
        self.right_widget_label = QLabel("--°C")
        self.right_widget_label.setFont(QFont("Segoe UI Variable Display", 10, QFont.Weight.Bold))

        self.header_layout.addWidget(self.mini_art)
        self.header_layout.addWidget(self.top_title, alignment=Qt.AlignmentFlag.AlignLeft)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.visualizer, alignment=Qt.AlignmentFlag.AlignRight)
        self.header_layout.addWidget(self.right_widget_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.layout.addLayout(self.header_layout)

        self.stack = QStackedWidget()
        self.stack.hide()

        self.page_player = QWidget()
        l_player = QVBoxLayout(self.page_player)
        l_player.setContentsMargins(10, 15, 10, 4)
        
        self.big_art = QLabel()
        self.big_art.setFixedSize(70, 70)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.media_title = QLabel("Not Playing")
        self.media_title.setFont(QFont("Segoe UI Variable Display", 13, QFont.Weight.Bold))
        self.media_artist = QLabel("---")
        info_layout.addWidget(self.media_title)
        info_layout.addWidget(self.media_artist)
        info_layout.addStretch()
        
        top_player = QHBoxLayout()
        top_player.addWidget(self.big_art)
        top_player.addSpacing(14)
        top_player.addLayout(info_layout)
        top_player.addStretch()
        
        timeline_layout = QHBoxLayout()
        self.time_current = QLabel("0:00")
        self.time_current.setFixedWidth(35)
        self.progress = QProgressBar()
        self.progress.setFixedHeight(5)
        self.progress.setTextVisible(False)
        self.time_total = QLabel("0:00")
        self.time_total.setFixedWidth(35)
        self.time_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        timeline_layout.addWidget(self.time_current)
        timeline_layout.addWidget(self.progress)
        timeline_layout.addWidget(self.time_total)

        controls_layout = QHBoxLayout()
        self.btn_prev = QPushButton("\uE892")
        self.btn_play = QPushButton("\uE768")
        self.btn_next = QPushButton("\uE893")
        
        for btn in (self.btn_prev, self.btn_play, self.btn_next):
            btn.setFont(QFont("Segoe Fluent Icons", 22))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            controls_layout.addWidget(btn)
            
        self.btn_prev.clicked.connect(lambda: media_control("prev"))
        self.btn_play.clicked.connect(lambda: media_control("play_pause"))
        self.btn_next.clicked.connect(lambda: media_control("next"))

        l_player.addLayout(top_player)
        l_player.addSpacing(10)
        l_player.addLayout(timeline_layout)
        l_player.addSpacing(4)
        l_player.addLayout(controls_layout)
        l_player.addStretch()

        self.page_notif = QWidget()
        l_notif = QVBoxLayout(self.page_notif)
        l_notif.setContentsMargins(10, 15, 10, 4)
        l_notif.setSpacing(6)
        
        self.lbl_notif_header = QLabel("Notifications Center")
        self.lbl_notif_header.setFont(QFont("Segoe UI Variable Display", 12, QFont.Weight.Bold))
        self.lbl_notif_title = QLabel("No new notifications")
        self.lbl_notif_title.setFont(QFont("Segoe UI Variable Display", 11, QFont.Weight.Bold))
        self.lbl_notif_title.setStyleSheet("color: #0a84ff;")
        self.lbl_notif_body = QLabel("Your recent Windows notifications will appear right here.")
        self.lbl_notif_body.setWordWrap(True)
        self.lbl_notif_body.setStyleSheet("color: #a0a0a0; font-size: 11px;")
        
        l_notif.addWidget(self.lbl_notif_header)
        l_notif.addWidget(self.lbl_notif_title)
        l_notif.addWidget(self.lbl_notif_body)
        l_notif.addStretch()

        self.page_set = QWidget()
        l_set = QVBoxLayout(self.page_set)
        l_set.setContentsMargins(10, 12, 10, 4)
        l_set.setSpacing(8)

        toggles_lay = QHBoxLayout()
        self.btn_wifi = QPushButton("\uE701  Wi-Fi")
        self.btn_bt = QPushButton("\uE702  Bluetooth")
        for b in (self.btn_wifi, self.btn_bt):
            b.setFont(QFont("Segoe Fluent Icons", 11))
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            toggles_lay.addWidget(b)
        
        self.btn_wifi.clicked.connect(lambda: os.startfile("ms-settings:network-wifi"))
        self.btn_bt.clicked.connect(lambda: os.startfile("ms-settings:bluetooth"))

        bri_lay = QHBoxLayout()
        bri_ico = QLabel("\uE706")
        bri_ico.setFont(QFont("Segoe Fluent Icons", 15))
        self.bri_slider = QSlider(Qt.Orientation.Horizontal)
        self.bri_slider.setRange(0, 100)
        self.bri_slider.setValue(get_system_brightness())
        self.bri_slider.valueChanged.connect(set_system_brightness)
        bri_lay.addWidget(bri_ico)
        bri_lay.addSpacing(10)
        bri_lay.addWidget(self.bri_slider)
        
        self.btn_mode = QPushButton("Mode: Always Idle")
        self.btn_mode.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_mode.clicked.connect(self.toggle_mode)

        self.btn_control_panel = QPushButton("Open Control Panel")
        self.btn_control_panel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_control_panel.clicked.connect(self.open_control_panel)

        self.btn_quit_app = QPushButton("Quit Dynamic Island")
        self.btn_quit_app.setStyleSheet("background-color: #ff3b30; color: white; font-weight: bold; border: none; border-radius: 10px; padding: 8px;")
        self.btn_quit_app.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_quit_app.clicked.connect(QApplication.instance().quit)

        l_set.addLayout(toggles_lay)
        l_set.addLayout(bri_lay)
        l_set.addWidget(self.btn_mode)
        l_set.addWidget(self.btn_control_panel)
        l_set.addWidget(self.btn_quit_app)
        l_set.addStretch()

        self.stack.addWidget(self.page_player)
        self.stack.addWidget(self.page_notif)
        self.stack.addWidget(self.page_set)
        self.layout.addWidget(self.stack)

        self.page_indicator = QLabel("•   ◦   ◦")
        self.page_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_indicator.hide()
        self.layout.addWidget(self.page_indicator)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_ui)
        self.timer.start(1000)

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(350)
        self.anim.setEasingCurve(QEasingCurve.Type.OutExpo)

    def apply_theme(self):
        r, g, b, _ = self.bg_color.getRgb()
        bg_str = f"rgba({r}, {g}, {b}, {self.bg_alpha / 255.0:.2f})"

        c = {"fg": "#ffffff", "sub": "#a0a0a0", "btn": "rgba(255, 255, 255, 0.1)" if self.glass_theme else "#1c1c1c", "btn_h": "rgba(255, 255, 255, 0.2)", "acc": "#ffffff"}

        self.container.setStyleSheet(f"QWidget#MainContainer {{ background-color: {bg_str}; border: none; border-bottom-left-radius: 18px; border-bottom-right-radius: 18px; }} QLabel {{ background: transparent; color: {c['fg']}; font-family: 'Segoe UI Variable Display'; }}")
        
        self.media_artist.setStyleSheet(f"color: {c['sub']}; font-size: 13px;")
        self.time_current.setStyleSheet(f"color: {c['sub']}; font-size: 11px;")
        self.time_total.setStyleSheet(f"color: {c['sub']}; font-size: 11px;")
        self.page_indicator.setStyleSheet(f"color: {c['sub']}; font-size: 15px;")
        
        self.progress.setStyleSheet(f"QProgressBar {{ background: {c['btn']}; border-radius: 2px; border: none; }} QProgressBar::chunk {{ background: {c['acc']}; border-radius: 2px; }}")
        self.bri_slider.setStyleSheet(f"QSlider::groove:horizontal {{ background: {c['btn']}; height: 6px; border-radius: 3px; }} QSlider::sub-page:horizontal {{ background: {c['acc']}; height: 6px; border-radius: 3px; }} QSlider::handle:horizontal {{ background: {c['acc']}; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }}")
        
        btn_css = f"QPushButton {{ background: {c['btn']}; border-radius: 10px; padding: 8px; color: {c['fg']}; font-family: 'Segoe UI Variable Display'; font-size: 12px; font-weight: 600; border: none; }} QPushButton:hover {{ background: {c['btn_h']}; }}"
        for b in (self.btn_wifi, self.btn_bt, self.btn_control_panel):
            b.setStyleSheet(btn_css)
            
        for b in (self.btn_prev, self.btn_play, self.btn_next):
            b.setStyleSheet(f"QPushButton {{ background: transparent; color: {c['fg']}; border: none; padding: 6px; }} QPushButton:hover {{ color: {c['acc']}; }}")

        self.visualizer.set_color(c['fg'])
        self.btn_mode.setStyleSheet(f"background: {c['btn']}; border-radius: 10px; padding: 8px; color: {c['fg']}; font-weight: bold; font-size: 12px; border: none;")

    def refresh_mini_widget(self):
        sel = self.mini_widget_selection
        if sel == "Weather":
            self.right_widget_label.setText(self.current_temp)
            self.right_widget_label.setStyleSheet("font-family: 'Segoe UI Variable Display';")
        elif sel == "CPU Usage":
            self.right_widget_label.setText(f"CPU {self.current_cpu}%")
            self.right_widget_label.setStyleSheet("font-family: 'Segoe UI Variable Display';")
        elif sel == "RAM Usage":
            self.right_widget_label.setText(f"RAM {self.current_ram}%")
            self.right_widget_label.setStyleSheet("font-family: 'Segoe UI Variable Display';")
        elif sel == "Battery":
            self.right_widget_label.setText(f"\uE83F {self.current_batt}%")
            self.right_widget_label.setStyleSheet("font-family: 'Segoe Fluent Icons';")

    def toggle_mode(self):
        self.mode_state = (self.mode_state + 1) % 3
        
        if self.mode_state == 0:
            self.auto_hide_enabled = False
            self.force_fullscreen = False
            self.btn_mode.setText("Mode: Always Idle")
            self.inactivity_timer.stop()
            if self.geometry() == self.hidden_rect: self.wake_up()
            
        elif self.mode_state == 1:
            self.auto_hide_enabled = True
            self.force_fullscreen = False
            self.btn_mode.setText("Mode: Auto-Hide (15s)")
            self.inactivity_timer.start(15000)
            
        elif self.mode_state == 2:
            self.auto_hide_enabled = False
            self.force_fullscreen = True
            self.btn_mode.setText("Mode: Fixed (Fullscreen)")
            self.inactivity_timer.stop()
            if self.geometry() == self.hidden_rect: self.wake_up()

    def open_control_panel(self):
        dlg = ControlPanelDialog(self)
        dlg.exec()

    def hide_island_completely(self):
        if self.geometry() == self.small_rect:
            self.anim.stop()
            self.anim.setStartValue(self.geometry())
            self.anim.setEndValue(self.hidden_rect)
            self.anim.start()

    def wake_up(self):
        self.inactivity_timer.stop()
        self.anim.stop()
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(self.small_rect)
        self.anim.start()
        if self.auto_hide_enabled:
            self.inactivity_timer.start(15000)

    def start_worker(self):
        self.worker = DataWorker()
        self.worker.media_updated.connect(self.update_media_ui)
        self.worker.weather_updated.connect(self.update_weather_ui)
        self.worker.sys_stats_updated.connect(self.update_sys_stats_ui)
        self.worker.start()

        self.notif_worker = NotificationWorker()
        self.notif_worker.notification_received.connect(self.show_notification)
        self.notif_worker.start()

    def show_notification(self, title, body):
        self.lbl_notif_title.setText(title)
        self.lbl_notif_body.setText(body)
        self.top_title.setText("New Message")
        self.wake_up()
        self.expand_island()
        self.stack.setCurrentIndex(1)
        self.update_dots(1)
        self.notif_timer.start(6000)

    def clear_notification(self):
        if not self.underMouse():
            self.shrink_island()

    def update_time_ui(self):
        if not self.visualizer.is_playing and self.media_title.text() == "Not Playing" and not self.notif_timer.isActive():
            self.top_title.setText(QTime.currentTime().toString("HH:mm"))
            
        fs_active = is_fullscreen()
        
        if self.force_fullscreen:
            if self.is_hidden_by_fs:
                self.show()
                self.is_hidden_by_fs = False
        else:
            if fs_active and not self.is_hidden_by_fs:
                self.hide()
                self.is_hidden_by_fs = True
            elif not fs_active and self.is_hidden_by_fs:
                self.show()
                self.is_hidden_by_fs = False

    def get_rounded_pixmap(self, img_bytes, size, radius, is_circle=False):
        pixmap = QPixmap()
        if img_bytes: pixmap.loadFromData(img_bytes)
        if pixmap.isNull():
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor("#222"))
        else:
            pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        
        target = QPixmap(size, size)
        target.fill(Qt.GlobalColor.transparent)
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        if is_circle: path.addEllipse(0, 0, size, size)
        else: path.addRoundedRect(0, 0, size, size, radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return target

    def format_time(self, seconds):
        m, s = divmod(seconds, 60)
        return f"{m}:{s:02d}"

    def update_media_ui(self, title, artist, thumb_bytes, is_playing, pos, tot):
        if not title:
            self.mini_art.hide()
            self.visualizer.hide()
            self.visualizer.is_playing = False
            self.right_widget_label.show()
            if not self.notif_timer.isActive():
                self.top_title.setText(QTime.currentTime().toString("HH:mm"))
            self.media_title.setText("Not Playing")
            self.media_artist.setText("---")
            self.progress.setValue(0)
            self.time_current.setText("0:00")
            self.time_total.setText("0:00")
            self.btn_play.setText("\uE768")
            self.big_art.setPixmap(self.get_rounded_pixmap(b"", 70, 10, False))
            return

        self.mini_art.show()
        self.media_title.setText(title)
        self.media_artist.setText(artist)
        self.btn_play.setText("\uE769" if is_playing else "\uE768") 
        
        self.visualizer.is_playing = is_playing
        if is_playing:
            self.visualizer.show()
            self.right_widget_label.hide()
            if not self.notif_timer.isActive():
                self.top_title.setText(title if len(title) < 18 else title[:15] + "...")
            if self.geometry() == self.hidden_rect: self.wake_up()
        else:
            self.visualizer.hide()
            self.right_widget_label.show()
            if not self.notif_timer.isActive():
                self.top_title.setText(QTime.currentTime().toString("HH:mm"))

        self.progress.setMaximum(tot if tot > 0 else 1)
        self.progress.setValue(pos)
        self.time_current.setText(self.format_time(pos))
        self.time_total.setText(self.format_time(tot))
        self.mini_art.setPixmap(self.get_rounded_pixmap(thumb_bytes, 20, 10, True))
        self.big_art.setPixmap(self.get_rounded_pixmap(thumb_bytes, 70, 10, False))
        
    def update_weather_ui(self, temp_str, temp_val):
        self.current_temp = temp_str
        self.refresh_mini_widget()

    def update_sys_stats_ui(self, cpu, ram, batt):
        self.current_cpu = cpu
        self.current_ram = ram
        self.current_batt = batt
        self.refresh_mini_widget()
        
    def keyPressEvent(self, event):
        if self.stack.isVisible():
            if event.key() == Qt.Key.Key_Right: self.next_page()
            elif event.key() == Qt.Key.Key_Left: self.prev_page()
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        if self.stack.isVisible():
            delta = event.angleDelta().y()
            if delta == 0: delta = event.angleDelta().x()
            if delta < 0: self.next_page()
            elif delta > 0: self.prev_page()
        super().wheelEvent(event)

    def next_page(self):
        idx = (self.stack.currentIndex() + 1) % self.stack.count()
        self.stack.setCurrentIndex(idx)
        self.update_dots(idx)
        if idx == 2:
            self.bri_slider.blockSignals(True)
            self.bri_slider.setValue(get_system_brightness())
            self.bri_slider.blockSignals(False)

    def prev_page(self):
        idx = (self.stack.currentIndex() - 1) % self.stack.count()
        self.stack.setCurrentIndex(idx)
        self.update_dots(idx)
        if idx == 2:
            self.bri_slider.blockSignals(True)
            self.bri_slider.setValue(get_system_brightness())
            self.bri_slider.blockSignals(False)

    def update_dots(self, idx):
        dots = ["◦", "◦", "◦"]
        dots[idx] = "•"
        self.page_indicator.setText("   ".join(dots))

    def resizeEvent(self, event):
        self.container.resize(self.width(), self.height())
        super().resizeEvent(event)

    def expand_island(self):
        self.anim.stop()
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(self.large_rect)
        self.anim.start()
        
        self.layout.setContentsMargins(16, 6, 16, 10)
        self.stack.show()
        self.page_indicator.show()
        self.update_dots(self.stack.currentIndex())

    def shrink_island(self):
        self.anim.stop()
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(self.small_rect)
        self.anim.start()
        
        self.layout.setContentsMargins(14, 4, 14, 4)
        self.stack.hide()
        self.page_indicator.hide()

    def enterEvent(self, event):
        self.setFocus()
        self.activateWindow()
        self.inactivity_timer.stop() 
        self.expand_island()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shrink_island()
        self.clearFocus()
        if self.auto_hide_enabled:
            self.inactivity_timer.start(15000)
        super().leaveEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    island = DynamicIsland()
    island.show()
    sys.exit(app.exec())
