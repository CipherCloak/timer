#!/bin/python3

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSpinBox, QLineEdit
)

from PySide6.QtCore import Qt, QTimer, QPoint, Signal, QSettings
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtGui import QIcon

# =============================================================================
# 1. THEME MANAGER
# Centralizes colors for light and dark themes.
# This makes it easy to change the appearance of the entire application.
# =============================================================================
class ThemeManager:
    """Gestiona los colores para diferentes temas."""
    THEMES = {
        "light": {
            "window_bg": QColor("#FFFFFF"),
            "text_primary": QColor("#000000"),
            "text_secondary": QColor("#555555"),
            "border": QColor("#CCCCCC"),
            "button_primary_bg": QColor("#4CAF50"),
            "button_primary_text": QColor("#FFFFFF"),
            "button_danger_bg": QColor("#D9534F"),
            "button_danger_text": QColor("#FFFFFF"),
            "button_secondary_bg": QColor("#F0F0F0"),
            "button_secondary_text": QColor("#000000"),
            "input_bg": QColor("#FFFFFF"),
            "input_border": QColor("#AAAAAA"),
        },
        "dark": {
            "window_bg": QColor("#2D2D2D"),
            "text_primary": QColor("#EAEAEA"),
            "text_secondary": QColor("#AAAAAA"),
            "border": QColor("#555555"),
            "button_primary_bg": QColor("#5DBB63"),
            "button_primary_text": QColor("#000000"),
            "button_danger_bg": QColor("#E57373"),
            "button_danger_text": QColor("#000000"),
            "button_secondary_bg": QColor("#4A4A4A"),
            "button_secondary_text": QColor("#EAEAEA"),
            "input_bg": QColor("#3A3A3A"),
            "input_border": QColor("#666666"),
        }
    }
    
    def __init__(self, theme="light"):
        self.current_theme = theme

    def get_color(self, color_name):
        """Get a color from the current theme."""
        return self.THEMES[self.current_theme].get(color_name, QColor("black"))

    def set_theme(self, theme_name):
        """Change the current theme."""
        if theme_name in self.THEMES:
            self.current_theme = theme_name

# =============================================================================
# 2. BASE WINDOW
#    Improved base class for all windows. It is now theme-aware,
#    has the border you requested, and handles dragging.
# =============================================================================
class BaseWindow(QWidget):
    """Rounded base window, draggable, and with theme support."""
    theme_changed = Signal()

    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self._drag_pos = None
        
        # Initial window configuration
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(320, 440) # Tamaño más compacto

        # Connect the theme change signal to the UI update
        self.theme_changed.connect(self.update_styles)
        self.theme_changed.connect(self.update) # Repintar la ventana

    def paintEvent(self, event):
        """Draw the window with rounded corners and a 1px border.."""
        radius = 20
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background color
        painter.setBrush(self.theme_manager.get_color("window_bg"))
        
        # Gray border
        pen = QPen(self.theme_manager.get_color("border"), 8)
        painter.setPen(pen)
        
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), radius, radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def update_styles(self):
        pass

# =============================================================================
# 3. CONFIGURATION SCREEN (Config Screen)
#    Inherits from BaseWindow and handles timer configuration.
# =============================================================================
class ConfigScreen(BaseWindow):
    # Señal que emite los datos del temporizador cuando se presiona "Start"
    start_timer_signal = Signal(int, str)

    def __init__(self, theme_manager):
        super().__init__(theme_manager)
        self.setWindowTitle("Timer")
        self._init_ui()
        self.update_styles()

    def _init_ui(self):
        """Initialize the user interface."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 15, 25, 25)

        # --- Layout of the close button and theme change ---
        top_bar_layout = QHBoxLayout()
        self.theme_toggle_btn = QPushButton("🌙") # Botón para cambiar de tema
        self.theme_toggle_btn.setFixedSize(25, 25)
        self.theme_toggle_btn.clicked.connect(self._toggle_theme)

        minimize_btn = QPushButton("—") # Character to minimize
        minimize_btn.setFixedSize(25, 25)
        minimize_btn.setObjectName("minimize_button")
        minimize_btn.clicked.connect(self.showMinimized)

        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(25, 25)
        close_btn.setObjectName("close_button")
        close_btn.clicked.connect(QApplication.instance().quit)
        
        top_bar_layout.addWidget(self.theme_toggle_btn)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(minimize_btn)
        top_bar_layout.addWidget(close_btn)
        
        self.main_layout.addLayout(top_bar_layout)
        self.main_layout.addStretch(1)

        # --- Time controls (Hours, Minutes, Seconds) ---
        time_layout = QHBoxLayout()
        self.hours_spin = self._create_spinbox()
        self.minutes_spin = self._create_spinbox()
        self.seconds_spin = self._create_spinbox()
        
        self.colon1 = QLabel(":")
        self.colon2 = QLabel(":")
        
        time_layout.addWidget(self.hours_spin)
        time_layout.addWidget(self.colon1)
        time_layout.addWidget(self.minutes_spin)
        time_layout.addWidget(self.colon2)
        time_layout.addWidget(self.seconds_spin)
        
        self.main_layout.addLayout(time_layout)
        self.main_layout.addSpacing(15)

        # --- Message field (optional) ---
        self.msg_label = QLabel("Menssage (optional):")
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("")
        
        self.main_layout.addWidget(self.msg_label)
        self.main_layout.addWidget(self.msg_input)
        self.main_layout.addSpacing(20)

        # --- Start button ---
        self.start_btn = QPushButton("Start Timer")
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self._on_start)
        
        self.main_layout.addWidget(self.start_btn)
        self.main_layout.addStretch(1)
        
    def _create_spinbox(self):
        spin = QSpinBox()
        spin.setRange(0, 60)
        spin.setAlignment(Qt.AlignCenter)
        spin.setButtonSymbols(QSpinBox.NoButtons) # We hide the default buttons
        return spin
        
    def _on_start(self):
        """Send the signal to start the timer.."""
        total_seconds = (self.hours_spin.value() * 3600 +
                         self.minutes_spin.value() * 60 +
                         self.seconds_spin.value())
        message = self.msg_input.text() or self.msg_input.placeholderText()
        
        if total_seconds > 0:
            self.start_timer_signal.emit(total_seconds, message)

    def _toggle_theme(self):
        """Switch between light and dark themes."""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == "light" else "light"
        self.theme_manager.set_theme(new_theme)
        # Emitir la señal para que todas las ventanas se actualicen
        app_controller.broadcast_theme_change()

    def update_styles(self):
        """Apply the colors of the current theme to the widgets."""
        tm = self.theme_manager
        
        # Top bar buttons
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {tm.get_color('text_secondary').name()};
                border: none;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {tm.get_color('text_primary').name()};
            }}
        """
        self.theme_toggle_btn.setText("☀️" if tm.current_theme == "dark" else "🌙")
        self.theme_toggle_btn.setStyleSheet(btn_style)
        self.findChild(QPushButton, "minimize_button").setStyleSheet(btn_style)
        self.findChild(QPushButton, "close_button").setStyleSheet(btn_style)

        # SpinBoxes and separators
        spin_style = f"""
            QSpinBox {{
                background-color: {tm.get_color('input_bg').name()};
                color: {tm.get_color('text_primary').name()};
                border: 1px solid {tm.get_color('input_border').name()};
                border-radius: 5px;
                padding: 5px;
                font-size: 40px;
                font-weight: bold;
            }}
        """
        colon_style = f"color: {tm.get_color('text_primary').name()}; font-size: 20px; font-weight: bold;"
        
        self.hours_spin.setStyleSheet(spin_style)
        self.minutes_spin.setStyleSheet(spin_style)
        self.seconds_spin.setStyleSheet(spin_style)
        self.colon1.setStyleSheet(colon_style)
        self.colon2.setStyleSheet(colon_style)
        
        # Labels and text fields
        label_style = f"color: {tm.get_color('text_secondary').name()}; font-size: 12px;"
        self.msg_label.setStyleSheet(label_style)
        
        input_style = f"""
            QLineEdit {{
                background-color: {tm.get_color('input_bg').name()};
                color: {tm.get_color('text_primary').name()};
                border: 1px solid {tm.get_color('input_border').name()};
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
        """
        self.msg_input.setStyleSheet(input_style)
        
        # Start button
        start_btn_style = f"""
            QPushButton {{
                background-color: {tm.get_color('button_primary_bg').name()};
                color: {tm.get_color('button_primary_text').name()};
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {tm.get_color('button_primary_bg').lighter(110).name()};
            }}
        """
        self.start_btn.setStyleSheet(start_btn_style)

# =============================================================================
#4. Timer Screen
#    Displays the countdown and controls.
# =============================================================================
class TimerScreen(BaseWindow):
    # Signal to return to the configuration screen
    back_to_config_signal = Signal()

    def __init__(self, theme_manager):
        super().__init__(theme_manager)
        self.setWindowTitle("Timer")
        self.initial_duration = 0
        self.remaining_time = 0
        self.is_paused = True
        
        self._init_ui()
        self.update_styles()
        
        # Main timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)

    def _init_ui(self):
        """Initialize the user interface."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 15, 25, 25)

        # --- Top bar ---
        top_bar_layout = QHBoxLayout()
        self.settings_btn = QPushButton("⚙️") # Button to go to settings
        self.settings_btn.setFixedSize(25, 25)
        self.settings_btn.clicked.connect(self.back_to_config_signal.emit)

        minimize_btn = QPushButton("—")
        minimize_btn.setFixedSize(25, 25)
        minimize_btn.setObjectName("minimize_button")
        minimize_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(25, 25)
        close_btn.setObjectName("close_button")
        close_btn.clicked.connect(QApplication.instance().quit)
        
        top_bar_layout.addWidget(self.settings_btn)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(minimize_btn)
        top_bar_layout.addWidget(close_btn)
        
        self.main_layout.addLayout(top_bar_layout)
        self.main_layout.addStretch(1)
        
        # --- Time stamp ---
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.time_label)
        
        # --- Message label ---
        self.message_label = QLabel("Countdown")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.message_label)
        
        self.main_layout.addStretch(1)
        
        # --- Control buttons (Pause/Play, Reset) ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.pause_play_btn = QPushButton("▶")
        self.pause_play_btn.setFixedSize(60, 40)
        self.pause_play_btn.clicked.connect(self.toggle_pause)
        
        self.reset_btn = QPushButton("⟳") # Reset icon
        self.reset_btn.setFixedSize(60, 40)
        self.reset_btn.clicked.connect(self.reset_timer)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.pause_play_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addSpacing(10)

        # --- Button to edit the time ---
        self.edit_time_btn = QPushButton("✎")
        self.edit_time_btn.setFixedSize(60, 40)
        self.edit_time_btn.clicked.connect(self.back_to_config_signal.emit)
        self.main_layout.addWidget(self.edit_time_btn, alignment=Qt.AlignCenter)

    def start(self, duration, message):
        """Configura e inicia el temporizador con nuevos valores."""
        self.initial_duration = duration
        self.message_label.setText(message)
        self.reset_timer()
        self.toggle_pause() # Inicia automáticamente

    def reset_timer(self):
        """Reset the timer to its initial value."""
        self.timer.stop()
        self.remaining_time = self.initial_duration
        self.time_label.setText(self._format_time(self.remaining_time))
        self.is_paused = True
        self.pause_play_btn.setText("▶")
        self.update_styles() # To reset the color if it's “Time's up!”

    def toggle_pause(self):
        """Pause or resume the timer."""
        if self.remaining_time <= 0:
            return
            
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.timer.stop()
            self.pause_play_btn.setText("▶")
        else:
            self.timer.start(1000)
            self.pause_play_btn.setText("⏸")
            
    def _update_time(self):
        """Update the timestamp every second."""
        if not self.is_paused and self.remaining_time > 0:
            self.remaining_time -= 1
            self.time_label.setText(self._format_time(self.remaining_time))
            
            if self.remaining_time == 0:
                self.timer.stop()
                self.is_paused = True
                self.pause_play_btn.setText("▶")
                self.update_styles() # Update to the status “Time's up!”

    def _format_time(self, seconds):
        """Format seconds as HH:MM:SS."""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def update_styles(self):
        """Apply the colors of the current theme."""
        tm = self.theme_manager
        
        # Top bar buttons
        top_btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {tm.get_color('text_secondary').name()};
                border: none;
                font-size: 18px;
            }}
            QPushButton:hover {{
                color: {tm.get_color('text_primary').name()};
            }}
        """
        self.settings_btn.setStyleSheet(top_btn_style)
        self.findChild(QPushButton, "minimize_button").setStyleSheet(top_btn_style)
        self.findChild(QPushButton, "close_button").setStyleSheet(top_btn_style)

        # Time stamp
        time_color = tm.get_color('button_danger_bg') if self.remaining_time == 0 else tm.get_color('text_primary')
        time_label_style = f"""
            color: {time_color.name()};
            font-size: 90px;
            font-weight: bold;
        """
        self.time_label.setStyleSheet(time_label_style)
        
        # Message label
        message_label_style = f"color: {tm.get_color('text_secondary').name()}; font-size: 14px;"
        self.message_label.setStyleSheet(message_label_style)
        
        # Control buttons
        control_btn_style = f"""
            QPushButton {{
                background-color: {tm.get_color('button_secondary_bg').name()};
                color: {tm.get_color('button_secondary_text').name()};
                border: 1px solid {tm.get_color('border').name()};
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {tm.get_color('button_secondary_bg').lighter(120).name()};
            }}
        """
        self.pause_play_btn.setStyleSheet(control_btn_style)
        self.reset_btn.setStyleSheet(control_btn_style)
        self.edit_time_btn.setStyleSheet(control_btn_style)

# =============================================================================
#5. MAIN CONTROLLER (App Controller)
#    Orchestrates application logic, such as switching between windows.
# =============================================================================
class AppController:
    """Main controller that manages the windows and logic of the app."""
    def __init__(self, app):
        self.app = app
        self.settings = QSettings("NoNe", "TimerApp")

        self.theme_manager = ThemeManager("light") # Start with a clear topic
        
        # Create instances of windows
        self.config_screen = ConfigScreen(self.theme_manager)
        self.timer_screen = TimerScreen(self.theme_manager)
        
        # Connect signals and slots
        self.config_screen.start_timer_signal.connect(self.show_timer_screen)
        self.timer_screen.back_to_config_signal.connect(self.show_config_screen)

        # Connect the close signal to save the configuration
        self.app.aboutToQuit.connect(self.save_settings)

    def show_config_screen(self):
        """Displays the settings screen and hides the timer screen."""
        # If the timer window is visible, use its position for the new one.
        if self.timer_screen.isVisible():
            self.config_screen.setGeometry(self.timer_screen.geometry())
        else:
            # Otherwise, it is the start of the app: load the last saved position.
            geometry = self.settings.value("geometry")
            if geometry:
                self.config_screen.setGeometry(geometry)

        self.timer_screen.hide()
        self.config_screen.show()

    def show_timer_screen(self, duration, message):
        """Displays the timer screen and hides the settings screen."""
        # The new window (timer) appears in the same position as the previous one (config).
        self.timer_screen.setGeometry(self.config_screen.geometry())
        self.config_screen.hide()
        self.timer_screen.start(duration, message)
        self.timer_screen.show()

    def broadcast_theme_change(self):
        """Notify all windows that the theme has changed."""
        self.config_screen.theme_changed.emit()
        self.timer_screen.theme_changed.emit()

    def save_settings(self):
        """Saves the geometry of the visible window when closing the application."""
        if self.config_screen.isVisible():
            self.settings.setValue("geometry", self.config_screen.geometry())
        elif self.timer_screen.isVisible():
            self.settings.setValue("geometry", self.timer_screen.geometry())

# =============================================================================
#6. ENTRY POINT (Main Execution)
# =============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("/usr/share/icons/Moka/64x64/apps/gnome-break-timer.png"))
    app_controller = AppController(app)
    # Start by displaying the configuration screen
    app_controller.show_config_screen()
    sys.exit(app.exec())
