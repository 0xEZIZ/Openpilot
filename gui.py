"""
TOYOTA CAN CONTROL SYSTEM v3.0
Premium Hacker Terminal Dashboard
All CAN logic preserved - visual layer completely redesigned.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading
import time
import math
import os
import ctypes
import tkinter.font as tkfont

# Load custom Quantum font (Windows)
_QUANTUM_FONT_NAME = "Quantum"
try:
    import sys as _sys
    _base = getattr(_sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    _font_path = os.path.join(_base, "Quantum.otf")
    if os.path.exists(_font_path):
        # FR_PRIVATE = 0x10 — only this process can see the font
        ctypes.windll.gdi32.AddFontResourceExW(_font_path, 0x10, 0)
except Exception:
    pass

from config import CAN_BITRATE, DEMO_MODE
from can_interface import CANInterface
from can_parser import CANParser
from toyota_commands import ToyotaCommander
import dbc_loader

def _get_app_dir():
    """Get persistent app directory (next to EXE, or script dir in dev)"""
    import sys as _s
    if getattr(_s, 'frozen', False):
        return os.path.dirname(_s.executable)
    return os.path.dirname(os.path.abspath(__file__))

# ==========================================================
#  HACKER TERMINAL COLOR SCHEME v3
# ==========================================================
BG        = "#060910"
BG2       = "#0a0f18"
BG3       = "#111822"
BG4       = "#182030"
BORDER    = "#0f2b1f"
GREEN     = "#00ff41"
GREEN2    = "#00cc33"
GREEN3    = "#00ff6a"
GREEN_DIM = "#0a3d1a"
GREEN_GLOW= "#003311"
CYAN      = "#00e5ff"
CYAN2     = "#00b8d4"
CYAN_DIM  = "#002233"
RED       = "#ff0044"
RED2      = "#ff1a5e"
RED_DIM   = "#2a0011"
RED_GLOW  = "#1a000a"
ORANGE    = "#ff9100"
YELLOW    = "#ffea00"
YELLOW2   = "#e5c07b"
PURPLE    = "#d475ff"
MAGENTA   = "#ff00aa"
WHITE     = "#e0e6ed"
DIM       = "#1e2a38"
DIM_TEXT  = "#4a5568"
NEON_BLUE = "#0080ff"
FONT      = "Consolas"
FONT2     = "Courier New"

_BLOCK_FULL  = chr(9608)
_BLOCK_LIGHT = chr(9617)
_BLOCK_MED   = chr(9618)

# ==========================================================
#  MULTI-LANGUAGE TRANSLATIONS
# ==========================================================
LANGS = ['ENG', 'RUS', 'TKM']

TR = {
    # Header
    'offline':          {'ENG': '● OFFLINE',       'RUS': '● ОТКЛЮЧЁН',       'TKM': '● ÖÇÜK'},
    'online':           {'ENG': '● [{}] ONLINE',   'RUS': '● [{}] ПОДКЛЮЧЁН', 'TKM': '● [{}] BIRIKDI'},
    # Toolbar
    'scan':             {'ENG': '⟳ SCAN',          'RUS': '⟳ ПОИСК',          'TKM': '⟳ GÖZLE'},
    'browse':           {'ENG': '📂 BROWSE',       'RUS': '📂 ОБЗОР',         'TKM': '📂 SAÝLA'},
    'start':            {'ENG': '⚡ START',         'RUS': '⚡ СТАРТ',         'TKM': '⚡ BAŞLA'},
    'no_dbc':           {'ENG': '» no DBC loaded',  'RUS': '» DBC не загружен', 'TKM': '» DBC ýüklenmedi'},
    'connect':          {'ENG': '⏻ CONNECT',       'RUS': '⏻ ПОДКЛЮЧИТЬ',    'TKM': '⏻ BIRIK'},
    'disconnect':       {'ENG': '⏻ DISCONNECT',    'RUS': '⏻ ОТКЛЮЧИТЬ',     'TKM': '⏻ AÝYR'},
    # Sections
    'telemetry':        {'ENG': '⚡ TELEMETRY MONITORING', 'RUS': '⚡ МОНИТОРИНГ ТЕЛЕМЕТРИИ', 'TKM': '⚡ TELEMETRIÝA GÖZEGÇILIGI'},
    'safety':           {'ENG': '🛡 SAFETY',        'RUS': '🛡 БЕЗОПАСНОСТЬ',  'TKM': '🛡 HOWPSUZLYK'},
    'vehicle_ctrl':     {'ENG': '🎮 VEHICLE CONTROL', 'RUS': '🎮 УПРАВЛЕНИЕ',  'TKM': '🎮 ULAG DOLANDYRYŞY'},
    'steering':         {'ENG': '┌── STEERING ──┐', 'RUS': '┌── РУЛЬ ──┐',     'TKM': '┌── DOLANDYRYŞ ──┐'},
    'gas_lbl':          {'ENG': '┌GAS┐',           'RUS': '┌ГАЗ┐',            'TKM': '┌GAZ┐'},
    'brake_lbl':        {'ENG': '┌BRK┐',           'RUS': '┌ТРМ┐',            'TKM': '┌TRM┐'},
    'acceleration':     {'ENG': '⚡ ACCELERATION',  'RUS': '⚡ УСКОРЕНИЕ',     'TKM': '⚡ TIZLENDIRIŞ'},
    'can_monitor':      {'ENG': '📡 CAN BUS MONITOR', 'RUS': '📡 CAN МОНИТОР', 'TKM': '📡 CAN GÖZEGÇISI'},
    'terminal':         {'ENG': '⌨ TERMINAL',       'RUS': '⌨ ТЕРМИНАЛ',       'TKM': '⌨ TERMINAL'},
    # Control buttons
    'left':             {'ENG': '◄◄ LEFT',         'RUS': '◄◄ ЛЕВО',          'TKM': '◄◄ ÇEPE'},
    'center':           {'ENG': '◉ CENTER',        'RUS': '◉ ЦЕНТР',          'TKM': '◉ MERKEZ'},
    'right':            {'ENG': 'RIGHT ►►',        'RUS': 'ПРАВО ►►',         'TKM': 'SAGA ►►'},
    'accel_btn':        {'ENG': '▲ ACCEL',          'RUS': '▲ ГАЗ',            'TKM': '▲ TIZLEN'},
    'stop_btn':         {'ENG': '■ STOP',           'RUS': '■ СТОП',           'TKM': '■ DUR'},
    'brake_btn':        {'ENG': '▼ BRAKE',          'RUS': '▼ ТОРМОЗ',         'TKM': '▼ TORMOZ'},
    'emergency':        {'ENG': '⚠  E M E R G E N C Y   K I L L   S W I T C H  ⚠',
                         'RUS': '⚠  А В А Р И Й Н О Е   О Т К Л Ю Ч Е Н И Е  ⚠',
                         'TKM': '⚠  H O W P L Y   Ö Ç Ü R I Ş   D Ü W M E S I  ⚠'},
    'hints':            {'ENG': '[←→] steer  [↑↓/WS] accel  [SPACE] kill  [ESC] reset',
                         'RUS': '[←→] руль  [↑↓/WS] газ  [ПРОБЕЛ] стоп  [ESC] сброс',
                         'TKM': '[←→] rul  [↑↓/WS] tizlik  [BOŞLUK] dur  [ESC] arassala'},
    'load_dbc':         {'ENG': '» load DBC to begin', 'RUS': '» загрузите DBC', 'TKM': '» DBC ýükläň'},
    # Gauge labels
    'brake_g':          {'ENG': '◄ BRAKE',          'RUS': '◄ ТОРМОЗ',         'TKM': '◄ TORMOZ'},
    'accel_g':          {'ENG': 'ACCEL ►',          'RUS': 'ГАЗ ►',            'TKM': 'TIZLEN ►'},
    # Safety Badge terms
    'st_engaged':       {'ENG': '▓ ENGAGED ▓',      'RUS': '▓ АКТИВЕН ▓',      'TKM': '▓ IŞJEŇ ▓'},
    'st_override':      {'ENG': '⚠ OVERRIDE ⚠',     'RUS': '⚠ ПЕРЕХВАТ ⚠',     'TKM': '⚠ SÜRÜJI ELI ⚠'},
    'st_fault':         {'ENG': '✖ EPS FAULT ✖',    'RUS': '✖ ОШИБКА EPS ✖',   'TKM': '✖ EPS ÝALŇYŞLYK ✖'},
    'st_standby':       {'ENG': 'STANDBY',          'RUS': 'ОЖИДАНИЕ',         'TKM': 'GARAŞYLÝAR'},
    'st_off':           {'ENG': '[OFF]',            'RUS': '[ВЫКЛ]',           'TKM': '[ÖÇÜK]'},
    # Log messages
    'log_scan':         {'ENG': 'scan complete: {} DBC files found',
                         'RUS': 'поиск завершён: {} DBC файлов найдено',
                         'TKM': 'gözleg tamamlandy: {} DBC faýl tapyldy'},
    'log_loading':      {'ENG': 'loading: {} ...',  'RUS': 'загрузка: {} ...', 'TKM': 'ýüklenýär: {} ...'},
    'log_no_dbc':       {'ENG': 'ERROR: no DBC file selected',
                         'RUS': 'ОШИБКА: DBC файл не выбран',
                         'TKM': 'ÝALŇYŞLYK: DBC faýl saýlanmady'},
    'log_online':       {'ENG': 'Toyota control panel ONLINE (STEERING_LKA / ACC_CONTROL detected)',
                         'RUS': 'Панель управления Toyota ОНЛАЙН (STEERING_LKA / ACC_CONTROL обнаружены)',
                         'TKM': 'Toyota dolandyryş paneli ONLAÝN (STEERING_LKA / ACC_CONTROL tapyldy)'},
    'log_no_toyota':    {'ENG': 'info: this DBC has no Toyota LKA/ACC support',
                         'RUS': 'инфо: этот DBC не поддерживает Toyota LKA/ACC',
                         'TKM': 'maglumat: bu DBC-de Toyota LKA/ACC goldawy ýok'},
    'log_dbc_loaded':   {'ENG': 'DBC loaded: {} │ {} │ {} msg │ {} known signals',
                         'RUS': 'DBC загружен: {} │ {} │ {} сообщ │ {} известных сигналов',
                         'TKM': 'DBC ýüklendi: {} │ {} │ {} habar │ {} belli signallar'},
    'log_disconnected': {'ENG': 'disconnected.',    'RUS': 'отключён.',         'TKM': 'aýryldy.'},
    'log_warn_dbc':     {'ENG': 'WARNING: load DBC first for signal decoding',
                         'RUS': 'ВНИМАНИЕ: сначала загрузите DBC для декодирования',
                         'TKM': 'DUÝDURYŞ: signal dekodirlemek üçin ilki DBC ýükläň'},
    'log_connected':    {'ENG': 'connected [{}] — safety: ACTIVE',
                         'RUS': 'подключён [{}] — безопасность: АКТИВНА',
                         'TKM': 'birikdi [{}] — howpsuzlyk: IŞJEŇ'},
    'log_steer':        {'ENG': 'steer: {:+d} Nm',  'RUS': 'руль: {:+d} Нм',  'TKM': 'rul: {:+d} Nm'},
    'log_accel':        {'ENG': 'accel: {:+.1f} m/s²', 'RUS': 'ускор: {:+.1f} м/с²', 'TKM': 'tizlik: {:+.1f} m/s²'},
    'log_emergency':    {'ENG': '[!!!] EMERGENCY KILL ACTIVATED [!!!]',
                         'RUS': '[!!!] АВАРИЙНОЕ ОТКЛЮЧЕНИЕ [!!!]',
                         'TKM': '[!!!] HOWPLY ÖÇÜRIŞ IŞJEŇLEŞDI [!!!]'},
    'log_reset':        {'ENG': 'controls reset to zero',
                         'RUS': 'управление сброшено в ноль',
                         'TKM': 'dolandyryş nola gaýtaryldy'},
    'log_copy':         {'ENG': 'copied: {} -> dbc_files/', 'RUS': 'скопировано: {} -> dbc_files/', 'TKM': 'göçürildi: {} -> dbc_files/'},
    'log_copy_fail':    {'ENG': 'ERROR: copy failed: {}', 'RUS': 'ОШИБКА: копирование не удалось: {}', 'TKM': 'ÝALŇYŞLYK: göçürme başartmady: {}'},
}

def t(key, *args):
    """Get translated string for current language"""
    lang = getattr(t, '_lang', 'ENG')
    text = TR.get(key, {}).get(lang, key)
    if args:
        try:
            return text.format(*args)
        except Exception:
            return text
    return text

t._lang = 'ENG'


def _bar(value, vmin, vmax, width=12):
    if vmax <= vmin:
        return _BLOCK_LIGHT * width
    ratio = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    filled = int(ratio * width)
    return _BLOCK_FULL * filled + _BLOCK_LIGHT * (width - filled)


def _center_bar(value, vmin, vmax, width=12):
    half = width // 2
    bar = list(_BLOCK_LIGHT * width)
    if value >= 0 and vmax > 0:
        n = int(min(value / vmax, 1.0) * half)
        for i in range(half, half + n):
            if i < width:
                bar[i] = _BLOCK_FULL
    elif value < 0 and vmin < 0:
        n = int(min(abs(value) / abs(vmin), 1.0) * half)
        for i in range(half - n, half):
            if 0 <= i:
                bar[i] = _BLOCK_FULL
    return "".join(bar)


# ==========================================================
#  MAIN APPLICATION
# ==========================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("[root@ADU_openpilot] ~ ezizysmailov v3.0")
        self.configure(bg=BG)
        self.geometry("1440x920")
        self.minsize(1200, 750)

        # -- state --
        self._db        = None
        self._db_info   = None
        self._parser    = None
        self._commander = None

        self._values    = {}
        self._lock      = threading.Lock()

        self._raw_buffer = []
        self._raw_lock   = threading.Lock()

        self._can = CANInterface(on_message=self._on_can_msg)

        self._safety_alerts = []
        self._safety_lock   = threading.Lock()

        self._steer_cmd = 0
        self._pulse_phase = 0
        self._start_time = time.time()
        self._lang = 'ENG'
        t._lang = 'ENG'
        self._translatable = []  # list of (widget, tr_key, config_key) for dynamic updates

        self._build_ui()
        self._refresh_dbc_list()
        self._bind_keys()
        self._start_ui_update()

    # ==========================================================
    #  KEYBOARD SHORTCUTS
    # ==========================================================
    def _bind_keys(self):
        # Use bind_all so keys work even when a Combobox or other widget has focus.
        # Return 'break' to prevent the event from reaching Combobox dropdowns.
        self.bind_all('<Left>',    lambda e: self._key_steer(-200) or 'break')
        self.bind_all('<Right>',   lambda e: self._key_steer(+200) or 'break')
        self.bind_all('<Up>',      lambda e: self._key_accel(+0.5) or 'break')
        self.bind_all('<Down>',    lambda e: self._key_accel(-0.5) or 'break')
        self.bind_all('w',         lambda e: self._key_accel(+0.5) or 'break')
        self.bind_all('s',         lambda e: self._key_accel(-0.5) or 'break')
        self.bind_all('a',         lambda e: self._key_steer(-200) or 'break')
        self.bind_all('d',         lambda e: self._key_steer(+200) or 'break')
        self.bind_all('<space>',   lambda e: self._emergency_stop() or 'break')
        self.bind_all('<Escape>',  lambda e: self._reset_controls() or 'break')

    def _key_steer(self, delta):
        cur = self._var_steer.get()
        new = max(-1500, min(1500, cur + delta))
        self._set_steer(new)

    def _key_accel(self, delta):
        cur = self._var_accel.get()
        new = max(-3.5, min(2.0, cur + delta))
        self._set_accel(round(new, 1))

    def _reset_controls(self):
        self._set_steer(0)
        self._set_accel(0.0)
        self._log_write(t('log_reset'))

    # ==========================================================
    #  LANGUAGE SWITCHER
    # ==========================================================
    def _cycle_language(self):
        """Cycle through ENG → RUS → TKM → ENG ..."""
        idx = LANGS.index(self._lang)
        self._lang = LANGS[(idx + 1) % len(LANGS)]
        t._lang = self._lang
        self._btn_lang.config(text=f"🌐 {self._lang}")
        self._apply_translations()

    def _tr_label(self, widget, tr_key, config_key='text'):
        """Register a widget for dynamic translation"""
        self._translatable.append((widget, tr_key, config_key))

    def _apply_translations(self):
        """Update all registered translatable widgets"""
        for widget, tr_key, config_key in self._translatable:
            try:
                if config_key == 'textvariable':
                    widget.set(t(tr_key))
                else:
                    widget.config(**{config_key: t(tr_key)})
            except Exception:
                pass
        # Update status label
        if self._can.connected:
            import config as cfg
            mode = "DEMO" if cfg.DEMO_MODE else self._var_iface.get().upper()
            self._lbl_status.config(text=t('online', mode))
        else:
            self._lbl_status.config(text=t('offline'))

    # ==========================================================
    #  BUILD UI
    # ==========================================================
    def _build_ui(self):
        self._build_header()
        self._build_toolbar()

        self._main = tk.Frame(self, bg=BG)
        self._main.pack(fill='both', expand=True, padx=6, pady=2)

        self._build_telemetry(self._main)
        self._build_control_panel(self._main)
        self._build_can_monitor(self._main)

        self._build_terminal()

    # ----------------------------------------------------------
    #  HEADER
    # ----------------------------------------------------------
    def _build_header(self):
        hdr = tk.Frame(self, bg=BG, height=52)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        # left: terminal prompt
        left = tk.Frame(hdr, bg=BG)
        left.pack(side='left', padx=8, pady=4)

        tk.Label(left, text="┌─[", bg=BG, fg=DIM,
                 font=(FONT, 9)).pack(side='left')
        tk.Label(left, text="root@ADU_openpilot", bg=BG, fg=RED,
                 font=(FONT, 9, "bold")).pack(side='left')
        tk.Label(left, text="]─[", bg=BG, fg=DIM,
                 font=(FONT, 9)).pack(side='left')
        tk.Label(left, text="~/can-bus", bg=BG, fg=CYAN,
                 font=(FONT, 9, "bold")).pack(side='left')
        tk.Label(left, text="]", bg=BG, fg=DIM,
                 font=(FONT, 9)).pack(side='left')

        # center: title (absolutely centered in header)
        self._lbl_title = tk.Label(hdr, text="ADU OPEN PILOT",
                 bg=BG, fg=GREEN, font=(_QUANTUM_FONT_NAME, 20))
        self._lbl_title.place(relx=0.5, rely=0.5, anchor='center')
        # Ensure title stays centered on resize
        hdr.bind('<Configure>', lambda e: self._lbl_title.place(relx=0.5, rely=0.5, anchor='center'))

        # right: status + language
        right = tk.Frame(hdr, bg=BG)
        right.pack(side='right', padx=8, pady=4)

        # Language toggle button
        self._btn_lang = tk.Button(right, text="🌐 ENG", bg=BG3, fg=CYAN,
                                   font=(FONT, 9, "bold"), relief='flat',
                                   padx=6, bd=0, cursor="hand2",
                                   activebackground=CYAN, activeforeground=BG,
                                   command=self._cycle_language)
        self._btn_lang.pack(side='right', padx=4)
        self._btn_lang.bind('<Enter>', lambda e: self._btn_lang.config(bg=BG4))
        self._btn_lang.bind('<Leave>', lambda e: self._btn_lang.config(bg=BG3))

        self._lbl_status = tk.Label(right, text=t('offline'),
                                    bg=BG, fg=RED, font=(FONT, 11, "bold"))
        self._lbl_status.pack(side='right', padx=6)
        self._tr_label(self._lbl_status, 'offline')

        self._lbl_brand = tk.Label(right, text="", bg=BG, fg=ORANGE,
                                   font=(FONT, 10, "bold"))
        self._lbl_brand.pack(side='right', padx=4)

        self._lbl_uptime = tk.Label(right, text="00:00:00", bg=BG, fg=DIM_TEXT,
                                    font=(FONT, 9))
        self._lbl_uptime.pack(side='right', padx=8)

        self._neon_line(self, GREEN_DIM)

    # ----------------------------------------------------------
    #  TOOLBAR
    # ----------------------------------------------------------
    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG2, height=44)
        bar.pack(fill='x', padx=6, pady=(2, 1))
        bar.pack_propagate(False)

        tk.Label(bar, text="[DBC]", bg=BG2, fg=GREEN,
                 font=(FONT, 9, "bold")).pack(side='left', padx=(8, 3), pady=8)

        self._var_dbc = tk.StringVar()
        self._cb_dbc  = ttk.Combobox(bar, textvariable=self._var_dbc,
                                     width=30, state='readonly', font=(FONT, 9))
        self._cb_dbc.pack(side='left', padx=2, pady=8)

        self._btn_scan = self._hacker_btn(bar, t('scan'), self._refresh_dbc_list, GREEN)
        self._btn_scan.pack(side='left', padx=2, pady=8)
        self._tr_label(self._btn_scan, 'scan')

        self._btn_browse = self._hacker_btn(bar, t('browse'), self._browse_dbc, GREEN)
        self._btn_browse.pack(side='left', padx=2, pady=8)
        self._tr_label(self._btn_browse, 'browse')

        self._btn_start = self._hacker_btn(bar, t('start'), self._load_selected_dbc, CYAN, bold=True)
        self._btn_start.pack(side='left', padx=(4, 10), pady=8)
        self._tr_label(self._btn_start, 'start')

        self._lbl_dbc_info = tk.Label(bar, text=t('no_dbc'),
                                      bg=BG2, fg=DIM_TEXT, font=(FONT, 8))
        self._lbl_dbc_info.pack(side='left', padx=4, pady=8)
        self._tr_label(self._lbl_dbc_info, 'no_dbc')

        # separator
        tk.Frame(bar, bg=DIM, width=2).pack(side='left', fill='y', padx=10, pady=6)

        tk.Label(bar, text="[IF]", bg=BG2, fg=GREEN,
                 font=(FONT, 9, "bold")).pack(side='left', padx=3, pady=8)

        self._var_iface = tk.StringVar(value="ixxat")
        self._cb_iface = ttk.Combobox(bar, textvariable=self._var_iface, width=10,
                     values=["ixxat", "network", "demo", "socketcan", "pcan", "vector"],
                     state='readonly', font=(FONT, 9))
        self._cb_iface.pack(side='left', padx=2, pady=8)

        # Return focus to main window after Combobox selection so arrow keys
        # control gas/brake instead of cycling dropdown items.
        for cb in (self._cb_dbc, self._cb_iface):
            cb.bind('<<ComboboxSelected>>', lambda e: self.focus_set())

        self._btn_conn = tk.Button(bar, text=t('connect'), bg=GREEN_DIM, fg=GREEN,
                                   font=(FONT, 10, "bold"), relief='flat',
                                   padx=12, bd=0, cursor="hand2",
                                   activebackground=GREEN, activeforeground=BG,
                                   command=self._toggle_connect)
        self._btn_conn.pack(side='left', padx=8, pady=8)
        self._tr_label(self._btn_conn, 'connect')

        self._neon_line(self, GREEN_DIM)

    # ----------------------------------------------------------
    #  LEFT COLUMN — TELEMETRY
    # ----------------------------------------------------------
    def _build_telemetry(self, parent):
        self._telem_frm = tk.Frame(parent, bg=BG2, width=280)
        self._telem_frm.pack(side='left', fill='y', padx=(0, 3))
        self._telem_frm.pack_propagate(False)

        self._lbl_telem_hdr = self._section_hdr(self._telem_frm, t('telemetry'), CYAN)

        self._speed_canvas = tk.Canvas(self._telem_frm, width=260, height=210,
                                       bg=BG2, highlightthickness=0)
        self._speed_canvas.pack(pady=(2, 0))
        self._draw_speed_gauge(0)

        self._rpm_canvas = tk.Canvas(self._telem_frm, width=260, height=36,
                                     bg=BG2, highlightthickness=0)
        self._rpm_canvas.pack(pady=2)
        self._draw_rpm_bar(0)

        self._sig_frame = tk.Frame(self._telem_frm, bg=BG2)
        self._sig_frame.pack(fill='x', padx=6, pady=2)
        self._sig_labels = {}

        self._lbl_no_dbc = tk.Label(self._sig_frame,
                                    text=t('load_dbc'),
                                    bg=BG2, fg=DIM_TEXT, font=(FONT, 9))
        self._lbl_no_dbc.pack()
        self._tr_label(self._lbl_no_dbc, 'load_dbc')

        # safety section
        self._lbl_safety_hdr = self._section_hdr(self._telem_frm, t('safety'), RED)
        sf = tk.Frame(self._telem_frm, bg=BG2)
        sf.pack(fill='x', padx=8, pady=2)

        self._safety_canvas = tk.Canvas(sf, width=250, height=60,
                                        bg=BG2, highlightthickness=0)
        self._safety_canvas.pack(pady=2)

        self._var_safety_engaged = tk.StringVar(value="[OFF]")
        self._lbl_safety_engaged = tk.Label(sf,
                                            textvariable=self._var_safety_engaged,
                                            bg=BG2, fg=DIM_TEXT,
                                            font=(FONT, 13, "bold"))
        self._lbl_safety_engaged.pack(anchor='w')

        self._var_safety_info = tk.StringVar(value="")
        tk.Label(sf, textvariable=self._var_safety_info,
                 bg=BG2, fg=DIM_TEXT, font=(FONT, 8)).pack(anchor='w')

        self._var_rate_torque = tk.StringVar(value="torque: 0")
        tk.Label(sf, textvariable=self._var_rate_torque,
                 bg=BG2, fg=DIM_TEXT, font=(FONT, 8)).pack(anchor='w')

    # ----------------------------------------------------------
    #  CENTER COLUMN — VEHICLE CONTROL
    # ----------------------------------------------------------
    def _build_control_panel(self, parent):
        self._ctrl_frm = tk.Frame(parent, bg=BG2, width=440)
        # NOT packed by default

        self._lbl_vctrl_hdr = self._section_hdr(self._ctrl_frm, t('vehicle_ctrl'), YELLOW)

        top = tk.Frame(self._ctrl_frm, bg=BG2)
        top.pack(fill='x', padx=4, pady=2)

        # -- steering wheel --
        steer_col = tk.Frame(top, bg=BG2)
        steer_col.pack(side='left', padx=6)

        self._lbl_steer = tk.Label(steer_col, text=t('steering'), bg=BG2, fg=YELLOW,
                 font=(FONT, 9, "bold"))
        self._lbl_steer.pack()
        self._tr_label(self._lbl_steer, 'steering')

        self._steer_canvas = tk.Canvas(steer_col, width=240, height=240,
                                       bg=BG2, highlightthickness=0)
        self._steer_canvas.pack(pady=2)
        self._draw_steering_wheel(0, 0)

        sl = tk.Frame(steer_col, bg=BG2)
        sl.pack(fill='x')
        tk.Label(sl, text="-1500", bg=BG2, fg=RED,
                 font=(FONT, 7, "bold")).pack(side='left')
        self._var_steer = tk.IntVar(value=0)
        tk.Scale(sl, from_=-1500, to=1500, orient='horizontal',
                 variable=self._var_steer, bg=BG3, fg=YELLOW,
                 troughcolor=GREEN_DIM, highlightthickness=0,
                 length=180, font=(FONT, 8), showvalue=True,
                 activebackground=YELLOW,
                 command=self._on_steer_change).pack(side='left', padx=2)
        tk.Label(sl, text="+1500", bg=BG2, fg=GREEN,
                 font=(FONT, 7, "bold")).pack(side='left')

        sb = tk.Frame(steer_col, bg=BG2)
        sb.pack(pady=2)
        for tr_key, val, col in [('left', -600, YELLOW),
                                  ('center', 0, WHITE),
                                  ('right', 600, YELLOW)]:
            btn = self._hacker_btn(sb, t(tr_key), lambda v=val: self._set_steer(v), col)
            btn.pack(side='left', padx=3)
            self._tr_label(btn, tr_key)

        # -- gas / brake bars --
        bars_col = tk.Frame(top, bg=BG2)
        bars_col.pack(side='left', padx=(16, 6), anchor='n', pady=(26, 0))

        gf = tk.Frame(bars_col, bg=BG2)
        gf.pack(side='left', padx=6)
        self._lbl_gas = tk.Label(gf, text=t('gas_lbl'), bg=BG2, fg=GREEN,
                 font=(FONT, 8, "bold"))
        self._lbl_gas.pack()
        self._tr_label(self._lbl_gas, 'gas_lbl')
        self._gas_canvas = tk.Canvas(gf, width=50, height=210,
                                     bg=BG2, highlightthickness=0)
        self._gas_canvas.pack()
        self._draw_bar_gauge(self._gas_canvas, 0, 100, GREEN, 50, 210)

        bf = tk.Frame(bars_col, bg=BG2)
        bf.pack(side='left', padx=6)
        self._lbl_brk = tk.Label(bf, text=t('brake_lbl'), bg=BG2, fg=RED,
                 font=(FONT, 8, "bold"))
        self._lbl_brk.pack()
        self._tr_label(self._lbl_brk, 'brake_lbl')
        self._brake_canvas = tk.Canvas(bf, width=50, height=210,
                                       bg=BG2, highlightthickness=0)
        self._brake_canvas.pack()
        self._draw_bar_gauge(self._brake_canvas, 0, 255, RED, 50, 210)

        # -- acceleration --
        self._lbl_accel_hdr = self._section_hdr(self._ctrl_frm, t('acceleration'), GREEN)

        acc_area = tk.Frame(self._ctrl_frm, bg=BG2)
        acc_area.pack(fill='x', padx=8, pady=2)

        self._accel_canvas = tk.Canvas(acc_area, width=400, height=75,
                                       bg=BG2, highlightthickness=0)
        self._accel_canvas.pack(pady=2)
        self._draw_accel_gauge(0)

        al = tk.Frame(acc_area, bg=BG2)
        al.pack()
        tk.Label(al, text="-3.5", bg=BG2, fg=RED,
                 font=(FONT, 7, "bold")).pack(side='left')
        self._var_accel = tk.DoubleVar(value=0.0)
        tk.Scale(al, from_=-3.5, to=2.0, resolution=0.1,
                 orient='horizontal', variable=self._var_accel,
                 bg=BG3, fg=GREEN, troughcolor=GREEN_DIM,
                 highlightthickness=0, length=310, font=(FONT, 8),
                 showvalue=True, activebackground=GREEN,
                 command=self._on_accel_change).pack(side='left', padx=2)
        tk.Label(al, text="+2.0", bg=BG2, fg=GREEN,
                 font=(FONT, 7, "bold")).pack(side='left')

        ab = tk.Frame(acc_area, bg=BG2)
        ab.pack(pady=3)
        for tr_key, val, col in [('accel_btn', 1.5, GREEN),
                                  ('stop_btn',  0,   WHITE),
                                  ('brake_btn', -2.0, RED)]:
            btn = self._hacker_btn(ab, t(tr_key), lambda v=val: self._set_accel(v), col)
            btn.pack(side='left', padx=4)
            self._tr_label(btn, tr_key)

        # -- EMERGENCY KILL --
        ek = tk.Frame(self._ctrl_frm, bg=BG2)
        ek.pack(fill='x', padx=8, pady=(8, 4))
        self._btn_kill = tk.Button(ek,
                  text=t('emergency'),
                  bg="#1a0000", fg=RED,
                  font=(FONT, 13, "bold"), relief='flat',
                  padx=10, pady=10, bd=0, cursor="hand2",
                  activebackground=RED, activeforeground=WHITE,
                  command=self._emergency_stop)
        self._btn_kill.pack(fill='x')
        self._tr_label(self._btn_kill, 'emergency')

        # keyboard hints
        self._lbl_hints = tk.Label(self._ctrl_frm,
                         text=t('hints'),
                         bg=BG2, fg=DIM_TEXT, font=(FONT, 7))
        self._lbl_hints.pack(pady=(0, 4))
        self._tr_label(self._lbl_hints, 'hints')

    # ----------------------------------------------------------
    #  RIGHT COLUMN — CAN BUS MONITOR
    # ----------------------------------------------------------
    def _build_can_monitor(self, parent):
        self._monitor_frm = tk.Frame(parent, bg=BG2)
        self._monitor_frm.pack(side='left', fill='both', expand=True, padx=(3, 0))

        self._lbl_can_hdr = self._section_hdr(self._monitor_frm, t('can_monitor'), CYAN)

        cols = ('ID', 'MSG', 'SIGNAL', 'VALUE', 'UNIT')
        self._tree = ttk.Treeview(self._monitor_frm, columns=cols,
                                  show='headings', height=22)
        for c in cols:
            self._tree.heading(c, text=c)
        self._tree.column('ID',     width=65,  anchor='center')
        self._tree.column('MSG',    width=140, anchor='w')
        self._tree.column('SIGNAL', width=160, anchor='w')
        self._tree.column('VALUE',  width=90,  anchor='e')
        self._tree.column('UNIT',   width=50,  anchor='center')

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
                        background=BG3, foreground=GREEN,
                        fieldbackground=BG3, rowheight=20,
                        font=(FONT, 9))
        style.configure("Treeview.Heading",
                        background=BG2, foreground=CYAN,
                        font=(FONT, 9, "bold"))
        style.map("Treeview",
                  background=[('selected', GREEN_DIM)],
                  foreground=[('selected', GREEN)])

        sb = ttk.Scrollbar(self._monitor_frm, orient='vertical',
                           command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        self._tree_rows = {}

    # ----------------------------------------------------------
    #  BOTTOM — TERMINAL LOG
    # ----------------------------------------------------------
    def _build_terminal(self):
        self._neon_line(self, GREEN_DIM)

        frm = tk.Frame(self, bg=BG2)
        frm.pack(fill='x', padx=6, pady=(2, 4))

        self._lbl_term_hdr = self._section_hdr(frm, t('terminal'), GREEN)

        self._log = scrolledtext.ScrolledText(
            frm, height=5, bg="#030508", fg=GREEN,
            insertbackground=GREEN, font=(FONT, 9),
            state='disabled', relief='flat', bd=1,
            selectbackground=GREEN_DIM, selectforeground=GREEN)
        self._log.pack(fill='x', padx=4, pady=(0, 4))
        self._log.tag_config("warn", foreground=YELLOW)
        self._log.tag_config("error", foreground=RED)
        self._log.tag_config("info", foreground=GREEN)
        self._log.tag_config("system", foreground=CYAN)

    # ----------------------------------------------------------
    #  UI HELPERS
    # ----------------------------------------------------------
    def _section_hdr(self, parent, text, color=GREEN):
        f = tk.Frame(parent, bg=BG2)
        f.pack(fill='x', padx=6, pady=(6, 2))
        lbl = tk.Label(f, text=f"╔══ {text} ",
                 bg=BG2, fg=color, font=(FONT, 9, "bold"))
        lbl.pack(side='left')
        c = tk.Canvas(f, bg=BG2, height=1, highlightthickness=0)
        c.pack(side='left', fill='x', expand=True, pady=7)
        c.create_line(0, 0, 2000, 0, fill=color, width=1)
        return lbl

    def _neon_line(self, parent, color=GREEN_DIM):
        c = tk.Canvas(parent, bg=BG, height=2, highlightthickness=0)
        c.pack(fill='x', padx=6)
        c.create_line(0, 1, 3000, 1, fill=color, width=1)

    def _hacker_btn(self, parent, text, command, color=GREEN, bold=False):
        font_style = (FONT, 8, "bold") if bold else (FONT, 8)
        btn = tk.Button(parent, text=text, bg=BG3, fg=color,
                        font=font_style, relief='flat', padx=8, bd=0,
                        cursor="hand2",
                        activebackground=color, activeforeground=BG,
                        command=command)
        btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(bg=BG4))
        btn.bind('<Leave>', lambda e, b=btn: b.config(bg=BG3))
        return btn

    # ==========================================================
    #  CUSTOM GAUGES
    # ==========================================================

    def _draw_speed_gauge(self, speed):
        c  = self._speed_canvas
        cx, cy = 130, 105
        r  = 90
        c.delete("all")

        # scanline grid
        for i in range(0, 261, 20):
            c.create_line(i, 0, i, 210, fill="#040a08")
        for i in range(0, 211, 20):
            c.create_line(0, i, 260, i, fill="#040a08")

        # outer glow ring
        c.create_oval(cx-r-4, cy-r-4, cx+r+4, cy+r+4,
                      outline=GREEN_GLOW, width=3)
        # background arc
        c.create_arc(cx-r, cy-r, cx+r, cy+r,
                     start=225, extent=-270, style='arc',
                     outline=DIM, width=6)

        # tick marks
        for i in range(0, 201, 10):
            ang   = math.radians(225 - 270 * i / 200.0)
            major = (i % 50 == 0)
            r1 = r - (16 if major else 8)
            x1 = cx + r1 * math.cos(ang)
            y1 = cy - r1 * math.sin(ang)
            x2 = cx + (r - 1) * math.cos(ang)
            y2 = cy - (r - 1) * math.sin(ang)
            c.create_line(x1, y1, x2, y2,
                          fill=DIM_TEXT if major else "#1a2a1a",
                          width=2 if major else 1)
            if major:
                tx = cx + (r - 24) * math.cos(ang)
                ty = cy - (r - 24) * math.sin(ang)
                c.create_text(tx, ty, text=str(i),
                              fill=DIM_TEXT, font=(FONT, 7))

        # speed arc with glow
        pct = min(speed / 200.0, 1.0)
        if speed > 0.5:
            col = GREEN if speed < 80 else (YELLOW if speed < 140 else RED)
            glow = GREEN_GLOW if speed < 80 else (
                "#332200" if speed < 140 else RED_GLOW)
            c.create_arc(cx-r-2, cy-r-2, cx+r+2, cy+r+2,
                         start=225, extent=-int(270 * pct), style='arc',
                         outline=glow, width=12)
            c.create_arc(cx-r, cy-r, cx+r, cy+r,
                         start=225, extent=-int(270 * pct), style='arc',
                         outline=col, width=7)

        # needle
        ang = math.radians(225 - 270 * pct)
        c.create_line(cx, cy,
                      cx + (r - 18) * math.cos(ang),
                      cy - (r - 18) * math.sin(ang),
                      fill=CYAN, width=2)
        c.create_oval(cx-5, cy-5, cx+5, cy+5, fill=CYAN, outline=GREEN_GLOW)

        # digital readout
        c.create_text(cx, cy + 30, text=f"{speed:.0f}",
                      fill=GREEN, font=(FONT, 26, "bold"))
        c.create_text(cx, cy + 52, text="KM/H",
                      fill=DIM_TEXT, font=(FONT, 8, "bold"))

    def _draw_rpm_bar(self, rpm):
        c = self._rpm_canvas
        c.delete("all")
        w, h = 260, 36
        mx = 8
        bar_w = w - 2 * mx
        bar_y, bar_h = 16, 14

        c.create_text(mx, 4, text="RPM", fill=CYAN,
                      font=(FONT, 7, "bold"), anchor='w')
        c.create_text(w - mx, 4, text=f"{rpm:.0f}",
                      fill=CYAN, font=(FONT, 9, "bold"), anchor='e')

        # background segments
        seg = 30
        seg_w = (bar_w - seg) / seg
        for i in range(seg):
            x = mx + i * (seg_w + 1)
            c.create_rectangle(x, bar_y, x + seg_w, bar_y + bar_h,
                               fill="#081208", outline="")

        max_rpm = 7000
        pct = min(rpm / max_rpm, 1.0) if rpm > 0 else 0
        lit = int(pct * seg)
        for i in range(lit):
            x = mx + i * (seg_w + 1)
            if i < seg * 0.6:
                col = CYAN
            elif i < seg * 0.8:
                col = YELLOW
            else:
                col = RED
            c.create_rectangle(x, bar_y, x + seg_w, bar_y + bar_h,
                               fill=col, outline="")

    def _draw_steering_wheel(self, angle_deg, torque_cmd):
        c  = self._steer_canvas
        cx, cy = 120, 120
        R       = 95
        r_inner = 65
        r_hub   = 28
        c.delete("all")

        # background grid
        for i in range(0, 241, 25):
            c.create_line(i, 0, i, 240, fill="#040a06")
            c.create_line(0, i, 240, i, fill="#040a06")

        rot = math.radians(-(torque_cmd / 1500.0) * 90.0)

        # intensity color
        intensity = abs(torque_cmd) / 1500.0
        if intensity < 0.3:
            rim_color = GREEN2
            glow_color = GREEN_GLOW
        elif intensity < 0.7:
            rim_color = CYAN
            glow_color = CYAN_DIM
        else:
            rim_color = YELLOW
            glow_color = "#332200"

        # outer glow
        c.create_oval(cx-R-6, cy-R-6, cx+R+6, cy+R+6,
                      outline=glow_color, width=4)
        # outer rim
        c.create_oval(cx-R, cy-R, cx+R, cy+R,
                      outline=rim_color, width=5)
        # inner ring
        c.create_oval(cx-r_inner, cy-r_inner,
                      cx+r_inner, cy+r_inner,
                      outline=GREEN_DIM, width=1)

        # top marker
        c.create_polygon(cx-8, cy-R-8,
                         cx+8, cy-R-8,
                         cx, cy-R+5,
                         fill=YELLOW, outline=ORANGE)

        # 3 spokes with gradient
        for base_deg in [90, 210, 330]:
            a = math.radians(base_deg) + rot
            x1 = cx + r_hub * math.cos(a)
            y1 = cy - r_hub * math.sin(a)
            x2 = cx + r_inner * math.cos(a)
            y2 = cy - r_inner * math.sin(a)
            c.create_line(x1, y1, x2, y2, fill=rim_color, width=3)

        # cross-bar
        mid_r = (r_hub + r_inner) / 2
        for dr in [-8, 8]:
            a1 = math.radians(210) + rot
            a2 = math.radians(330) + rot
            rr = mid_r + dr
            x1 = cx + rr * math.cos(a1)
            y1 = cy - rr * math.sin(a1)
            x2 = cx + rr * math.cos(a2)
            y2 = cy - rr * math.sin(a2)
            c.create_line(x1, y1, x2, y2, fill=GREEN_DIM, width=1)

        # center hub
        c.create_oval(cx-r_hub, cy-r_hub, cx+r_hub, cy+r_hub,
                      outline=rim_color, fill=BG3, width=2)
        c.create_text(cx, cy-6, text=f"{torque_cmd:+d}",
                      fill=CYAN, font=(FONT, 13, "bold"))
        c.create_text(cx, cy+10, text="Nm",
                      fill=DIM_TEXT, font=(FONT, 7))

        # angle readout
        c.create_text(cx, cy+R+14,
                      text=f"ANGLE: {angle_deg:+.1f}°",
                      fill=YELLOW, font=(FONT, 9, "bold"))

        # direction arrows
        if torque_cmd < -50:
            c.create_text(12, cy, text="◄◄", fill=YELLOW,
                          font=(FONT, 16, "bold"))
        elif torque_cmd > 50:
            c.create_text(228, cy, text="►►", fill=YELLOW,
                          font=(FONT, 16, "bold"))

    def _draw_bar_gauge(self, canvas, value, max_val, color, w=50, h=210):
        canvas.delete("all")
        n     = 22
        seg_h = (h - 28) / n
        gap   = 2
        mx    = 5
        bar_w = w - 2 * mx

        ratio = min(abs(value) / max(max_val, 1), 1.0) if max_val > 0 else 0
        lit   = int(ratio * n)

        for i in range(n):
            y = h - 24 - (i + 1) * seg_h
            if i < lit:
                if i < n * 0.5:
                    sc = color
                elif i < n * 0.75:
                    sc = YELLOW
                else:
                    sc = RED
                canvas.create_rectangle(mx, y+gap, mx+bar_w, y+seg_h,
                                        fill=sc, outline="")
                # glow edge
                canvas.create_rectangle(mx-1, y+gap, mx, y+seg_h,
                                        fill=sc, outline="")
                canvas.create_rectangle(mx+bar_w, y+gap, mx+bar_w+1, y+seg_h,
                                        fill=sc, outline="")
            else:
                canvas.create_rectangle(mx, y+gap, mx+bar_w, y+seg_h,
                                        fill="#081208", outline="")

        canvas.create_text(w/2, h-8, text=f"{value:.0f}",
                           fill=color, font=(FONT, 10, "bold"))

    def _draw_accel_gauge(self, accel):
        c = self._accel_canvas
        c.delete("all")
        w, h   = 400, 75
        bar_y  = 22
        bar_h  = 26
        mx     = 15
        bar_w  = w - 2 * mx

        # background segments
        seg = 40
        seg_w = (bar_w - seg) / seg
        for i in range(seg):
            x = mx + i * (seg_w + 1)
            c.create_rectangle(x, bar_y, x+seg_w, bar_y+bar_h,
                               fill="#081208", outline="")

        # zero point
        zero_x = mx + bar_w * (3.5 / 5.5)

        # fill segments
        if accel > 0.05:
            fw = (accel / 2.0) * (bar_w * 2.0 / 5.5)
            seg_lit = int(fw / (seg_w + 1))
            zero_seg = int((zero_x - mx) / (seg_w + 1))
            for i in range(zero_seg, min(zero_seg + seg_lit + 1, seg)):
                x = mx + i * (seg_w + 1)
                c.create_rectangle(x, bar_y, x+seg_w, bar_y+bar_h,
                                   fill=GREEN, outline="")
        elif accel < -0.05:
            fw = (abs(accel) / 3.5) * (bar_w * 3.5 / 5.5)
            seg_lit = int(fw / (seg_w + 1))
            zero_seg = int((zero_x - mx) / (seg_w + 1))
            for i in range(max(zero_seg - seg_lit, 0), zero_seg):
                x = mx + i * (seg_w + 1)
                c.create_rectangle(x, bar_y, x+seg_w, bar_y+bar_h,
                                   fill=RED, outline="")

        # zero line
        c.create_line(zero_x, bar_y-4, zero_x, bar_y+bar_h+4,
                      fill=WHITE, width=2)

        # labels
        c.create_text(mx, bar_y-8, text=t('brake_g') + " -3.5",
                      fill=RED, font=(FONT, 7, "bold"), anchor='w')
        c.create_text(w-mx, bar_y-8, text="+2.0 " + t('accel_g'),
                      fill=GREEN, font=(FONT, 7, "bold"), anchor='e')
        c.create_text(zero_x, bar_y-8, text="0",
                      fill=DIM_TEXT, font=(FONT, 7))

        col = GREEN if accel >= 0 else RED
        c.create_text(w/2, bar_y+bar_h+18,
                      text=f"{accel:+.1f} m/s²",
                      fill=col, font=(FONT, 16, "bold"))

    # ==========================================================
    #  SAFETY CANVAS
    # ==========================================================
    def _draw_safety_badge(self, state, color):
        c = self._safety_canvas
        c.delete("all")
        w, h = 250, 60
        # glow border
        c.create_rectangle(2, 2, w-2, h-2, outline=color, width=2)
        c.create_rectangle(5, 5, w-5, h-5, outline=BG3, width=1)
        c.create_text(w//2, h//2, text=state,
                      fill=color, font=(FONT, 16, "bold"))

    # ==========================================================
    #  SIGNAL LABELS
    # ==========================================================
    def _rebuild_signal_labels(self):
        for w in self._sig_frame.winfo_children():
            w.destroy()
        self._sig_labels.clear()

        if not self._db_info:
            return

        known = self._db_info['known']
        display = {
            'speed':       ("SPD",   "km/h", GREEN,    0, 200),
            'steer_angle': ("STR",   "deg",  YELLOW, -45,  45),
            'gas_pct':     ("GAS",   "%",    GREEN,    0, 100),
            'brake':       ("BRK",   "",     RED,      0, 255),
            'rpm':         ("RPM",   "rpm",  CYAN,     0, 7000),
            'cruise':      ("CRZ",   "",     ORANGE,   0,   1),
            'cruise_state':("CRZ.S", "",     ORANGE,   0,   1),
            'wheel_FL':    ("W.FL",  "km/h", DIM_TEXT, 0, 200),
            'wheel_FR':    ("W.FR",  "km/h", DIM_TEXT, 0, 200),
            'wheel_RL':    ("W.RL",  "km/h", DIM_TEXT, 0, 200),
            'wheel_RR':    ("W.RR",  "km/h", DIM_TEXT, 0, 200),
            'driver_torq': ("D.TQ",  "",     PURPLE,   0, 200),
            'steer_ovrrd': ("OVRD",  "",     RED,      0,   1),
        }

        grid = tk.Frame(self._sig_frame, bg=BG2)
        grid.pack(fill='x')

        row = 0
        for internal, (disp, unit, color, vmin, vmax) in display.items():
            if internal not in known:
                continue

            tk.Label(grid, text=disp, bg=BG2, fg=DIM_TEXT,
                     font=(FONT, 9), anchor='w', width=5).grid(
                row=row, column=0, sticky='w', pady=1)

            bar_var = tk.StringVar(value=_BLOCK_LIGHT * 12)
            tk.Label(grid, textvariable=bar_var, bg=BG2, fg=color,
                     font=(FONT, 8), anchor='w').grid(
                row=row, column=1, sticky='w', padx=2)

            val_var = tk.StringVar(value="---")
            tk.Label(grid, textvariable=val_var, bg=BG2, fg=color,
                     font=(FONT, 10, "bold"), anchor='e', width=7).grid(
                row=row, column=2, sticky='e')

            if unit:
                tk.Label(grid, text=unit, bg=BG2, fg=DIM_TEXT,
                         font=(FONT, 7), anchor='w').grid(
                    row=row, column=3, sticky='w', padx=(2, 0))

            self._sig_labels[internal] = (val_var, bar_var, vmin, vmax, color)
            row += 1

        if not self._sig_labels:
            tk.Label(grid, text="no known signals",
                     bg=BG2, fg=DIM_TEXT, font=(FONT, 9)).grid(
                row=0, column=0, columnspan=4)

    # ==========================================================
    #  DBC OPERATIONS
    # ==========================================================
    def _refresh_dbc_list(self):
        files = dbc_loader.find_dbc_files()
        self._cb_dbc['values'] = files
        if files and not self._var_dbc.get():
            self._var_dbc.set(files[0])
        self._log_write(t('log_scan', len(files)))

    def _browse_dbc(self):
        app_dir = _get_app_dir()
        path = filedialog.askopenfilename(
            title=t('browse'),
            filetypes=[("DBC files", "*.dbc"), ("All files", "*.*")],
            initialdir=app_dir
        )
        if path:
            fname = os.path.basename(path)
            dbc_dir = os.path.join(app_dir, 'dbc_files')
            os.makedirs(dbc_dir, exist_ok=True)
            dest = os.path.join(dbc_dir, fname)
            if os.path.abspath(path) != os.path.abspath(dest):
                import shutil
                try:
                    shutil.copy2(path, dest)
                    self._log_write(t('log_copy', fname))
                except Exception as e:
                    self._log_write(t('log_copy_fail', e), "error")
                    return
            self._refresh_dbc_list()
            self._var_dbc.set(fname)

    def _load_selected_dbc(self):
        fname = self._var_dbc.get()
        if not fname:
            self._log_write(t('log_no_dbc'), "error")
            return

        self._log_write(t('log_loading', fname), "system")
        db, info = dbc_loader.load_dbc(fname)

        if db is None:
            self._log_write(f"ERROR: {info}", "error")
            return

        self._db      = db
        self._db_info = info
        self._parser  = CANParser(db, info['known'])

        cap   = info['capabilities']
        brand = info['brand']
        self._lbl_brand.config(text=f"[{brand}]")
        self._lbl_dbc_info.config(
            fg=GREEN,
            text=(f"{fname} │ {brand} │ "
                  f"{info['msg_count']} msg │ {info['sig_count']} sig │ "
                  f"STEER:{'✓' if cap['steering'] else '✗'} "
                  f"ACCEL:{'✓' if cap['accel'] else '✗'}")
        )

        self._rebuild_signal_labels()
        self._values.clear()

        if cap['toyota_lka'] or cap['toyota_acc']:
            self._ctrl_frm.pack(side='left', fill='y', padx=3,
                                before=self._monitor_frm)
            self._log_write(t('log_online'), "system")
        else:
            self._ctrl_frm.pack_forget()
            self._log_write(t('log_no_toyota'))

        for item in self._tree.get_children():
            self._tree.delete(item)
        self._tree_rows.clear()

        self._log_write(
            t('log_dbc_loaded', fname, brand, info['msg_count'], len(info['known'])),
            "system")

    # ==========================================================
    #  CAN MESSAGE HANDLING (PRESERVED)
    # ==========================================================
    def _on_can_msg(self, msg):
        if not self._parser:
            return
        if self._commander:
            self._commander.feed_can_msg(msg)
        result = self._parser.parse(msg)
        if result:
            with self._lock:
                self._values.update(result['values'])
        raw = self._parser.parse_all(msg)
        if raw:
            with self._raw_lock:
                self._raw_buffer.append(raw)

    def _update_tree(self, raw):
        mid      = raw['msg_id']
        msg_name = raw['msg_name']
        for sig_name, val in raw['signals'].items():
            key = (mid, sig_name)
            try:
                msg_def = self._db.get_message_by_frame_id(mid)
                sig_def = next(
                    (s for s in msg_def.signals if s.name == sig_name), None)
                unit = sig_def.unit if sig_def else ''
            except Exception:
                unit = ''
            row_data = (hex(mid), msg_name, sig_name, str(val), unit)
            if key in self._tree_rows:
                try:
                    self._tree.item(self._tree_rows[key], values=row_data)
                except Exception:
                    pass
            else:
                iid = self._tree.insert('', 'end', values=row_data)
                self._tree_rows[key] = iid

    # ==========================================================
    #  UI UPDATE LOOP (50ms)
    # ==========================================================
    def _start_ui_update(self):
        self._update_ui()

    def _update_ui(self):
        with self._lock:
            vals = dict(self._values)

        speed = vals.get('speed', 0)
        self._draw_speed_gauge(speed)

        rpm = vals.get('rpm', 0)
        self._draw_rpm_bar(rpm)

        # signal labels
        for internal, (val_var, bar_var, vmin, vmax, _) in self._sig_labels.items():
            if internal in vals:
                v = vals[internal]
                if isinstance(v, float):
                    val_var.set(f"{v:+.1f}" if internal == 'steer_angle'
                                else f"{v:.1f}")
                else:
                    val_var.set(str(v))
                if isinstance(v, (int, float)):
                    fv = float(v)
                    bar_var.set(
                        _center_bar(fv, vmin, vmax, 12) if vmin < 0
                        else _bar(fv, vmin, vmax, 12))
            else:
                val_var.set("---")
                bar_var.set(_BLOCK_LIGHT * 12)

        # control panel gauges
        if self._ctrl_frm.winfo_ismapped():
            angle = vals.get('steer_angle', 0)
            self._draw_steering_wheel(angle, self._steer_cmd)
            gas   = vals.get('gas_pct', 0)
            self._draw_bar_gauge(self._gas_canvas, gas, 100, GREEN, 50, 210)
            brake = vals.get('brake', 0)
            self._draw_bar_gauge(self._brake_canvas, brake, 255, RED, 50, 210)

        # raw CAN -> treeview
        with self._raw_lock:
            buffered = self._raw_buffer
            self._raw_buffer = []
        for raw in buffered:
            self._update_tree(raw)

        self._update_safety_ui()

        # safety alerts
        with self._safety_lock:
            alerts = list(self._safety_alerts)
            self._safety_alerts.clear()
        for reason in alerts:
            self._log_write(f"[!] DISENGAGE: {reason}", "error")

        # uptime
        elapsed = int(time.time() - self._start_time)
        h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
        self._lbl_uptime.config(text=f"{h:02d}:{m:02d}:{s:02d}")

        # pulse phase for animations
        self._pulse_phase = (self._pulse_phase + 1) % 20

        # emergency button pulse
        if self._pulse_phase < 10:
            self._btn_kill.config(bg="#1a0000")
        else:
            self._btn_kill.config(bg="#2a0008")

        self.after(50, self._update_ui)

    def _update_safety_ui(self):
        if not self._commander:
            self._var_safety_engaged.set("[OFF]")
            self._lbl_safety_engaged.config(fg=DIM_TEXT)
            self._var_safety_info.set("")
            self._var_rate_torque.set("torque: 0")
            self._draw_safety_badge("STANDBY", DIM_TEXT)
            return

        st = self._commander.get_safety_status()

        if st['engaged']:
            self._var_safety_engaged.set(t('st_engaged'))
            self._lbl_safety_engaged.config(fg=GREEN)
            self._draw_safety_badge(t('st_engaged'), GREEN)
        elif st['driver_override']:
            self._var_safety_engaged.set(t('st_override'))
            self._lbl_safety_engaged.config(fg=YELLOW)
            self._draw_safety_badge(t('st_override'), YELLOW)
        elif st['eps_fault']:
            self._var_safety_engaged.set(t('st_fault'))
            self._lbl_safety_engaged.config(fg=RED)
            self._draw_safety_badge(t('st_fault'), RED)
        else:
            self._var_safety_engaged.set(t('st_standby'))
            self._lbl_safety_engaged.config(fg=DIM_TEXT)
            self._draw_safety_badge(t('st_standby'), DIM_TEXT)

        parts = []
        if st['driver_override']:
            parts.append(f"driver:{st['driver_torque']}Nm")
        parts.append(f"LKA:{st['lka_state']}")
        if st['fault_count'] > 0:
            parts.append(f"flt:{st['fault_count']}")
        self._var_safety_info.set(" │ ".join(parts))
        self._var_rate_torque.set(f"torque: {st['rate_limited_torque']}")

    # ==========================================================
    #  CONNECTION (PRESERVED)
    # ==========================================================
    def _toggle_connect(self):
        if self._can.connected:
            if self._commander:
                self._commander.stop()
                self._commander = None
            self._can.disconnect()
            self._btn_conn.config(text=t('connect'), bg=GREEN_DIM, fg=GREEN)
            self._lbl_status.config(text=t('offline'), fg=RED)
            self._log_write(t('log_disconnected'), "warn")
        else:
            if not self._parser:
                self._log_write(t('log_warn_dbc'), "warn")

            iface = self._var_iface.get()
            import config as cfg
            cfg.DEMO_MODE     = (iface == 'demo')
            cfg.CAN_INTERFACE = iface if iface != 'demo' else 'ixxat'

            try:
                self._can.connect()
                if self._db_info and (
                        self._db_info['capabilities']['toyota_lka'] or
                        self._db_info['capabilities']['toyota_acc']):
                    c_ids = self._db_info.get('control_ids', {})
                    self._commander = ToyotaCommander(
                        self._can,
                        steer_id=c_ids.get('STEERING_LKA'),
                        accel_id=c_ids.get('ACC_CONTROL'))
                    self._commander.safety.on_disengage = \
                        self._on_safety_disengage
                    self._commander.start()

                mode = "DEMO" if cfg.DEMO_MODE else iface.upper()
                self._btn_conn.config(text=t('disconnect'),
                                      bg=RED_DIM, fg=RED)
                self._lbl_status.config(text=t('online', mode), fg=GREEN)
                self._log_write(t('log_connected', mode), "system")
            except Exception as e:
                self._log_write(f"ERROR: {e}", "error")

    # ==========================================================
    #  STEERING + ACCELERATION (PRESERVED)
    # ==========================================================
    def _on_steer_change(self, val):
        t = int(float(val))
        self._steer_cmd = t
        if self._commander and abs(t) > 50:
            self._commander.set_steer(t)
        elif self._commander:
            self._commander.stop_steer()

    def _set_steer(self, torque):
        self._var_steer.set(torque)
        self._steer_cmd = torque
        if self._commander:
            if abs(torque) > 0:
                self._commander.set_steer(torque)
            else:
                self._commander.stop_steer()
        self._log_write(t('log_steer', torque))

    def _on_accel_change(self, val):
        a = float(val)
        if self._commander and abs(a) > 0.05:
            self._commander.set_accel(a)
        elif self._commander:
            self._commander.stop_accel()

    def _set_accel(self, val):
        self._var_accel.set(val)
        if self._commander:
            if abs(val) > 0.05:
                self._commander.set_accel(val)
            else:
                self._commander.stop_accel()
        self._log_write(t('log_accel', val))
        self._draw_accel_gauge(val)

    def _emergency_stop(self):
        if self._commander:
            self._commander.stop()
            # Restart commander so controls remain usable after emergency stop
            self._commander.start()
        self._var_steer.set(0)
        self._var_accel.set(0)
        self._steer_cmd = 0
        self._draw_accel_gauge(0)
        self._log_write(t('log_emergency'), "error")

    # ==========================================================
    #  SAFETY CALLBACK (PRESERVED)
    # ==========================================================
    def _on_safety_disengage(self, reason: str):
        with self._safety_lock:
            self._safety_alerts.append(reason)

    # ==========================================================
    #  LOG
    # ==========================================================
    def _log_write(self, text, level="info"):
        ts = time.strftime("%H:%M:%S")
        tag = level if level in ("warn", "error", "system") else "info"
        self._log.config(state='normal')
        self._log.insert('end', f"  [{ts}] {text}\n", tag)
        line_count = int(self._log.index('end-1c').split('.')[0])
        if line_count > 500:
            self._log.delete('1.0', f"{line_count - 500}.0")
        self._log.see('end')
        self._log.config(state='disabled')

    # ==========================================================
    #  CLOSE
    # ==========================================================
    def on_close(self):
        if self._commander:
            self._commander.stop()
        self._can.disconnect()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
