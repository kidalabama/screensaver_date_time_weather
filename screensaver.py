import sys
import os
import datetime
import json
import traceback
from urllib.request import urlopen

# Python 3.9+ ile gelen standart zaman dilimi kütüphanesi (Tüm dünyayı destekler)
try:
    import zoneinfo
    TIMEZONES = sorted(list(zoneinfo.available_timezones()))
except ImportError:
    TIMEZONES = ["Europe/Istanbul", "UTC", "America/New_York", "Europe/London", "Europe/Paris", "Europe/Berlin", "Asia/Tokyo"]

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QDialog, QComboBox, QLineEdit, QFormLayout, 
    QDialogButtonBox, QMessageBox, QPushButton, QFileDialog, QTextEdit
)
from PyQt6.QtCore import QTimer, Qt, QSettings
from PyQt6.QtGui import QFont, QPixmap

# --- GLOBAL HATA YAKALAYICI ---
def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    try:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
    except Exception:
        pass

    try:
        app = QApplication.instance()
        if app is not None:
            dlg = QDialog()
            dlg.setWindowTitle("Kritik Hata (Crash)")
            dlg.setMinimumSize(600, 400)
            
            layout = QVBoxLayout()
            lbl = QLabel("Program beklenmeyen bir hata nedeniyle kapandı!\nHata detayları aşağıdadır ve 'error_log.txt' dosyasına kaydedildi:")
            
            txt_edit = QTextEdit()
            txt_edit.setPlainText(error_msg)
            txt_edit.setReadOnly(True)
            
            btn_close = QPushButton("Kapat")
            btn_close.clicked.connect(dlg.accept)
            
            layout.addWidget(lbl)
            layout.addWidget(txt_edit)
            layout.addWidget(btn_close)
            dlg.setLayout(layout)
            dlg.exec()
    except Exception:
        print(error_msg)

sys.excepthook = global_exception_handler
# ------------------------------------

CONFIG_APP_NAME = "MinimalScreensaver"
CONFIG_ORG_NAME = "CustomScreensaver"

DEFAULT_LAT = 41.0082
DEFAULT_LON = 28.9784
DEFAULT_TZ = "Europe/Istanbul"

# 12 Global Dil Desteği
LANG_DATA = {
    "TR": {
        "tz_label": "BÖLGE", "weather_err": "HAVA DURUMU ALINAMADI",
        "days": ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"],
        "months": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
        "settings_title": "Ekran Koruyucu Ayarları", "lat_label": "Enlem (Latitude):", "lon_label": "Boylam (Longitude):",
        "tz_label_cfg": "Zaman Dilimi (Bölge):", "lang_label": "Dil:", "logo_label": "Logo Resmi:", "logo_btn": "Seç..."
    },
    "EN": {
        "tz_label": "ZONE", "weather_err": "WEATHER UNAVAILABLE",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "months": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        "settings_title": "Screensaver Settings", "lat_label": "Latitude:", "lon_label": "Longitude:",
        "tz_label_cfg": "Timezone:", "lang_label": "Language:", "logo_label": "Logo Image:", "logo_btn": "Browse..."
    },
    "ES": {
        "tz_label": "ZONA", "weather_err": "CLIMA NO DISPONIBLE",
        "days": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        "months": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
        "settings_title": "Configuración del Savapantallas", "lat_label": "Latitud:", "lon_label": "Longitud:",
        "tz_label_cfg": "Zona Horaria:", "lang_label": "Idioma:", "logo_label": "Imagen del Logo:", "logo_btn": "Buscar..."
    },
    "DE": {
        "tz_label": "ZONE", "weather_err": "WETTER NICHT VERFÜGBAR",
        "days": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
        "months": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
        "settings_title": "Bildschirmschoner-Einstellungen", "lat_label": "Breitengrad:", "lon_label": "Längengrad:",
        "tz_label_cfg": "Zeitzone:", "lang_label": "Sprache:", "logo_label": "Logo-Bild:", "logo_btn": "Durchsuchen..."
    },
    "FR": {
        "tz_label": "FUSEAU", "weather_err": "MÉTÉO INDISPONIBLE",
        "days": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
        "months": ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
        "settings_title": "Paramètres de l'Écran de Veille", "lat_label": "Latitude:", "lon_label": "Longitude:",
        "tz_label_cfg": "Fuseau Horaire:", "lang_label": "Langue:", "logo_label": "Image du Logo:", "logo_btn": "Parcourir..."
    },
    "IT": {
        "tz_label": "FUSO", "weather_err": "METEO NON DISPONIBILE",
        "days": ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
        "months": ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
        "settings_title": "Impostazioni Salvaschermo", "lat_label": "Latitudine:", "lon_label": "Longitudine:",
        "tz_label_cfg": "Fuso Orario:", "lang_label": "Lingua:", "logo_label": "Immagine Logo:", "logo_btn": "Sfoglia..."
    },
    "PT": {
        "tz_label": "FUSO", "weather_err": "CLIMA INDISPONÍVEL",
        "days": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"],
        "months": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
        "settings_title": "Configurações do Protetor de Tela", "lat_label": "Latitude:", "lon_label": "Longitude:",
        "tz_label_cfg": "Fuso Horário:", "lang_label": "Idioma:", "logo_label": "Imagem do Logo:", "logo_btn": "Procurar..."
    },
    "RU": {
        "tz_label": "ЗОНА", "weather_err": "ПОГОДА НЕДОСТУПНА",
        "days": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
        "months": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
        "settings_title": "Настройки заставки", "lat_label": "Широта:", "lon_label": "Долгота:",
        "tz_label_cfg": "Часовой пояс:", "lang_label": "Язык:", "logo_label": "Логотип:", "logo_btn": "Обзор..."
    },
    "NL": {
        "tz_label": "ZONE", "weather_err": "WEER NIET BESCHIKBAAR",
        "days": ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"],
        "months": ["Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"],
        "settings_title": "Schermbeveiliging Instellingen", "lat_label": "Breedtegraad:", "lon_label": "Lengtegraad:",
        "tz_label_cfg": "Tijdzone:", "lang_label": "Taal:", "logo_label": "Logo Afbeelding:", "logo_btn": "Bladeren..."
    },
    "JA": {
        "tz_label": "ゾーン", "weather_err": "天気情報取得失敗",
        "days": ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"],
        "months": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
        "settings_title": "スクリーンセーバー設定", "lat_label": "緯度:", "lon_label": "経度:",
        "tz_label_cfg": "タイムゾーン:", "lang_label": "言語:", "logo_label": "ロゴ画像:", "logo_btn": "参照..."
    },
    "ZH": {
        "tz_label": "时区", "weather_err": "天气不可用",
        "days": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
        "months": ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
        "settings_title": "屏幕保护程序设置", "lat_label": "纬度:", "lon_label": "经度:",
        "tz_label_cfg": "时区:", "lang_label": "语言:", "logo_label": "标志图片:", "logo_btn": "浏览..."
    },
    "AR": {
        "tz_label": "المنطقة", "weather_err": "الطقس غير متوفر",
        "days": ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"],
        "months": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
        "settings_title": "إعدادات شاشة التوقف", "lat_label": "خط العرض:", "lon_label": "خط الطول:",
        "tz_label_cfg": "المنطقة الزمنية:", "lang_label": "اللغة:", "logo_label": "صورة الشعار:", "logo_btn": "تصفح..."
    }
}

LANGUAGES = list(LANG_DATA.keys())

def get_localized_time(tz_string):
    try:
        if 'zoneinfo' in sys.modules:
            tz = zoneinfo.ZoneInfo(tz_string)
            return datetime.datetime.now(tz)
    except Exception:
        pass
    return datetime.datetime.now(datetime.timezone.utc)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings(CONFIG_ORG_NAME, CONFIG_APP_NAME)
        self.init_ui()

    def init_ui(self):
        curr_lang = self.settings.value("language", "TR")
        self.lang_dict = LANG_DATA.get(curr_lang, LANG_DATA["TR"])

        self.setWindowTitle(self.lang_dict["settings_title"])
        self.setMinimumWidth(450)

        layout = QFormLayout()

        self.txt_lat = QLineEdit(str(self.settings.value("lat", DEFAULT_LAT)))
        self.txt_lon = QLineEdit(str(self.settings.value("lon", DEFAULT_LON)))
        
        self.cmb_tz = QComboBox()
        self.cmb_tz.addItems(TIMEZONES)
        curr_tz = self.settings.value("timezone", DEFAULT_TZ)
        if curr_tz in TIMEZONES:
            self.cmb_tz.setCurrentText(curr_tz)

        self.cmb_lang = QComboBox()
        self.cmb_lang.addItems(LANGUAGES)
        self.cmb_lang.setCurrentText(curr_lang)

        self.txt_logo = QLineEdit(self.settings.value("logo_path", ""))
        self.btn_logo = QPushButton(self.lang_dict["logo_btn"])
        self.btn_logo.clicked.connect(self.browse_logo)
        
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.txt_logo)
        logo_layout.addWidget(self.btn_logo)

        layout.addRow(self.lang_dict["lat_label"], self.txt_lat)
        layout.addRow(self.lang_dict["lon_label"], self.txt_lon)
        layout.addRow(self.lang_dict["tz_label_cfg"], self.cmb_tz)
        layout.addRow(self.lang_dict["lang_label"], self.cmb_lang)
        layout.addRow(self.lang_dict["logo_label"], logo_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

    def browse_logo(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            self.lang_dict["logo_label"], 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.txt_logo.setText(file_name)

    def save_settings(self):
        try:
            lat = float(self.txt_lat.text().replace(',', '.'))
            lon = float(self.txt_lon.text().replace(',', '.'))
        except ValueError:
            QMessageBox.critical(self, "Hata", "Enlem ve Boylam sayısal olmalıdır!")
            return

        self.settings.setValue("lat", lat)
        self.settings.setValue("lon", lon)
        self.settings.setValue("timezone", self.cmb_tz.currentText())
        self.settings.setValue("language", self.cmb_lang.currentText())
        self.settings.setValue("logo_path", self.txt_logo.text().strip())

        self.accept()

class ScreenSaver(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(CONFIG_ORG_NAME, CONFIG_APP_NAME)
        self.load_settings()

        self.last_mouse_pos = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #0b0b0b;")
        self.setCursor(Qt.CursorShape.BlankCursor)

        self.init_ui()
        self.init_timers()

    def load_settings(self):
        self.lat = float(self.settings.value("lat", DEFAULT_LAT))
        self.lon = float(self.settings.value("lon", DEFAULT_LON))
        self.timezone_str = self.settings.value("timezone", DEFAULT_TZ)
        self.lang_code = self.settings.value("language", "TR")
        self.logo_path = self.settings.value("logo_path", "")

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 50, 60, 60)

        top_layout = QHBoxLayout()
        top_layout.addStretch()

        self.lbl_lang_display = QLabel(f"[ LANG: {self.lang_code} ]")
        self.lbl_lang_display.setStyleSheet("color: #555555; font-family: 'Segoe UI'; font-size: 16px; font-weight: bold;")
        top_layout.addWidget(self.lbl_lang_display)

        main_layout.addLayout(top_layout)

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        screen_height = QApplication.primaryScreen().geometry().height()

        self.lbl_logo = QLabel()
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        has_logo = False
        if self.logo_path and os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            if not pixmap.isNull():
                logo_height = int(screen_height * 0.12)
                pixmap = pixmap.scaledToHeight(logo_height, Qt.TransformationMode.SmoothTransformation)
                self.lbl_logo.setPixmap(pixmap)
                has_logo = True

        self.lbl_tz = QLabel()
        self.lbl_tz.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tz.setFont(QFont("Segoe UI", int(screen_height * 0.038), QFont.Weight.Bold))
        self.lbl_tz.setStyleSheet("color: #777777;")

        clock_layout = QHBoxLayout()
        clock_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clock_layout.setSpacing(20)

        text_style = "color: #F0F0F0; background: transparent;"
        
        card_font = QFont("Segoe UI", int(screen_height * 0.18), QFont.Weight.Bold)
        card_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

        self.lbl_hour = QLabel("00")
        self.lbl_hour.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hour.setFont(card_font)
        self.lbl_hour.setStyleSheet(text_style)

        self.lbl_min = QLabel("00")
        self.lbl_min.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_min.setFont(card_font)
        self.lbl_min.setStyleSheet(text_style)

        self.lbl_sec = QLabel("00")
        self.lbl_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sec.setFont(card_font)
        self.lbl_sec.setStyleSheet(text_style)

        sep1 = QLabel(":")
        sep1.setFont(card_font)
        sep1.setStyleSheet(text_style)
        sep1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep2 = QLabel(":")
        sep2.setFont(card_font)
        sep2.setStyleSheet(text_style)
        sep2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        clock_layout.addWidget(self.lbl_hour)
        clock_layout.addWidget(sep1)
        clock_layout.addWidget(self.lbl_min)
        clock_layout.addWidget(sep2)
        clock_layout.addWidget(self.lbl_sec)

        self.lbl_date = QLabel()
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_date.setFont(QFont("Segoe UI", int(screen_height * 0.050), QFont.Weight.Bold))
        self.lbl_date.setStyleSheet("color: #AAAAAA;")

        self.lbl_weather = QLabel("...")
        self.lbl_weather.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_weather.setFont(QFont("Segoe UI", int(screen_height * 0.045), QFont.Weight.Bold))
        self.lbl_weather.setStyleSheet("color: #DDDDDD;")

        center_layout.addStretch()
        
        if has_logo:
            center_layout.addWidget(self.lbl_logo)
            center_layout.addSpacing(25)
            
        center_layout.addWidget(self.lbl_tz)
        center_layout.addSpacing(15)
        center_layout.addLayout(clock_layout)
        center_layout.addSpacing(25)
        center_layout.addWidget(self.lbl_date)
        center_layout.addSpacing(20)
        center_layout.addWidget(self.lbl_weather)
        center_layout.addStretch()

        main_layout.addLayout(center_layout)
        self.setLayout(main_layout)

    def init_timers(self):
        self.timer_clock = QTimer(self)
        self.timer_clock.timeout.connect(self.update_clock)
        self.timer_clock.start(1000)
        self.update_clock()

        self.timer_weather = QTimer(self)
        self.timer_weather.timeout.connect(self.fetch_weather)
        self.timer_weather.start(900000)
        self.fetch_weather()

    def update_clock(self):
        lang_dict = LANG_DATA.get(self.lang_code, LANG_DATA["TR"])
        tz_now = get_localized_time(self.timezone_str)

        self.lbl_hour.setText(tz_now.strftime("%H"))
        self.lbl_min.setText(tz_now.strftime("%M"))
        self.lbl_sec.setText(tz_now.strftime("%S"))

        weekday_idx = tz_now.weekday()
        month_idx = tz_now.month - 1
        
        day_name = lang_dict["days"][weekday_idx]
        month_name = lang_dict["months"][month_idx]

        date_str = f"{tz_now.day} {month_name} {tz_now.year} - {day_name}".upper()
        tz_title = f"{lang_dict['tz_label']}: {self.timezone_str}"

        self.lbl_tz.setText(tz_title)
        self.lbl_date.setText(date_str)

    def fetch_weather(self):
        lang_dict = LANG_DATA.get(self.lang_code, LANG_DATA["TR"])

        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current=temperature_2m,precipitation,wind_speed_10m"
            response = urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            
            current = data.get("current", {})
            temp = round(current.get("temperature_2m", 0))
            rain = current.get("precipitation", 0.0)
            wind = round(current.get("wind_speed_10m", 0))
            
            weather_text = f"{temp}°C   •   💧 {rain} mm   •   💨 {wind} km/h"
            self.lbl_weather.setText(weather_text)
            
        except Exception:
            self.lbl_weather.setText(lang_dict["weather_err"])

    def keyPressEvent(self, event):
        QApplication.quit()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return
        
        delta = event.pos() - self.last_mouse_pos
        if abs(delta.x()) > 10 or abs(delta.y()) > 10:
            QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    args = [arg.lower() for arg in sys.argv[1:]]
    
    is_config = False
    is_preview = False

    if len(args) == 0:
        is_config = True
    else:
        for arg in args:
            if arg.startswith("/c") or arg.startswith("-c"):
                is_config = True
                break
            elif arg.startswith("/p") or arg.startswith("-p"):
                is_preview = True
                break

    if is_config:
        dlg = SettingsDialog()
        dlg.exec()
        sys.exit(0)

    if is_preview:
        sys.exit(0)

    # --- TÜM MONİTÖRLERDE EKRAN KORUYUCUYU BAŞLAT ---
    screensaver_windows = []
    for screen in QApplication.screens():
        ex = ScreenSaver()
        ex.setGeometry(screen.geometry())
        ex.showFullScreen()
        screensaver_windows.append(ex)

    sys.exit(app.exec())