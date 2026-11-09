# CDM - کلون Internet Download Manager  |  pip install PyQt6 requests  |  python cdm.py
import sys, os, re, csv, json, time, math, platform, collections, shutil, secrets, threading, http.server, subprocess, requests
from datetime import datetime
try:
    import urllib3; urllib3.disable_warnings()
except Exception: pass
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote, urljoin
from PyQt6.QtCore import Qt, QTimer, QSize, QTime, QDate, QEvent, QRectF, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPainter, QColor, QFont, QDesktopServices, QPalette, QPixmap, QLinearGradient, QActionGroup, QPen, QFontDatabase
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import *

HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))  # داخل exe: منابع از خود فایل خوانده می‌شوند
HOME = os.path.join(os.path.expanduser("~"), "Downloads")
DB = os.path.join(os.path.expanduser("~"), ".cdm_items.json")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CDM/1.0"}
SET = os.path.join(os.path.expanduser("~"), ".cdm_settings.json")
def newq(name, par=1):
    return dict(name=name, mode="daily", date="", days=list(range(7)), start_on=False, start_time="04:00", stop_on=False,
                stop_time="07:00", retry_on=False, retry=10, open_on=False, open_path="", exit_on=False, shut_on=False,
                shut_mode="Shut down", force=False, with_start=False, parallel=par)
UPDATE_URL = ""  # ← آدرس صفحه‌ی GitHub برای دکمه‌ی «بروزرسانی» را اینجا بگذارید
S = {"theme": "ocean", "fsize": 10, "token": "", "start_min": False, "row_h": 0, "show_hero": True, "prog_top": False, "pulse": True, "date_fmt": "idm", "size_unit": "auto", "speed_unit": "bytes", "clear_days": 0, "verify_ssl": True, "use_cookies": True, "cap_min": 0, "cap_excl": "", "name_clean": True, "after": "none", "dbl_action": "open", "queue_new": False, "night_on": False, "night_from": 0, "night_to": 7, "night_kb": 200, "check_space": True, "buf_kb": 64, "fa_digits": False, "log_on": True, "log_file": False, "lk_dest": "queue", "lk_queue": "", "lk_start": True, "lk_skip": True, "img_btn": False, "img_min": 1, "vid_btn": True, "vid_min": 1, "speed": 0, "ask_ext": True, "auto_prog": True, "close_prog": True, "notify": True, "sound": False,
     "retries": 5, "timeout": 20, "ua": "", "proxy": "", "subdirs": True, "del_mode": "ask", "autostart": False, "close_tray": False,
     "confirm_exit": True, "watch_clip": False, "qpar": 1, "exists": "rename", "prealloc": False, "minseg": 512, "conn": 8, "dir": HOME, "queues": [newq("صف اصلی دانلود"), newq("صف دانلودهای همزمان", 3)]}
try: S.update(json.load(open(SET, encoding="utf-8")))
except Exception: pass
def save_s():
    x = {**S, "queues": [{k: v for k, v in q.items() if k not in ("active", "last", "last_stop")} for q in S["queues"]]}
    json.dump(x, open(SET, "w", encoding="utf-8"), ensure_ascii=False)
GR = {  # گروه: (پوشه, پسوندها)
    "فایلهای فشرده": ("Compressed", "zip rar 7z gz tar iso bz2 xz part1 part2".split()),
    "اسناد": ("Documents", "pdf doc docx xls xlsx ppt pptx txt epub".split()),
    "موسیقی": ("Music", "mp3 wav flac aac ogg m4a".split()),
    "برنامه ها": ("Programs", "exe msi apk dmg deb".split()),
    "تصویری": ("Video", "mp4 mkv avi ts mov webm flv".split()),
    "تصاویر": ("Images", "jpg jpeg png gif webp bmp avif svg tif tiff".split()),
    "عمومی": ("General", [])}

def grp_of(name):
    e = name.rsplit(".", 1)[-1].lower()
    return next((g for g, (_, x) in GR.items() if e in x), "عمومی")

def fs(n):
    if n < 0: return ""
    if S.get("size_unit") == "MB": return f"{n / 1048576:.2f} MB"
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB": return f"{n:.2f} {u}" if u != "B" else f"{n} B"
        n /= 1024

def ft(t):
    t = int(t); h, m, s = t // 3600, t % 3600 // 60, t % 60
    return " و ".join(x for x in (f"{h}ساعت" if h else "", f"{m}دقیقه" if m else "", f"{s} ثانیه" if s or not (h or m) else "") if x)


# ───────────────────────── تم‌ها ─────────────────────────
QSS = """
QMainWindow,QDialog{background:qlineargradient(x1:0,y1:0,x2:0.7,y2:1,stop:0 @G1,stop:0.5 @G2,stop:1 @G3);}
QWidget{color:@FG;}
QLabel,QCheckBox,QRadioButton{background:transparent;}
QMenuBar{background:transparent;}
QMenuBar::item{padding:5px 11px;background:transparent;border-radius:@RP;}
QMenuBar::item:selected{background:@HI;}
QMenu{background:@MENU;border:@BW solid @BD;padding:5px;border-radius:@RP;}
QMenu::item{padding:6px 28px;border-radius:5px;}
QMenu::item:selected{background:@HI;}
QMenu::separator{height:1px;background:@BD;margin:5px 8px;}
QToolBar{background:transparent;border:none;spacing:4px;padding:4px;}
QToolBar::separator:horizontal{background:@BD;width:1px;margin:8px 5px;}
QToolBar::separator:vertical{background:@BD;height:1px;margin:5px 8px;}
QToolButton{background:transparent;border:@BW solid transparent;border-radius:@RB;padding:5px 7px;}
QToolButton:hover{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @B1,stop:1 @B2);border:@BW solid @BD;}
QToolButton:pressed{background:@HI;}
QPushButton{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @B1,stop:1 @B2);border:@BW solid @BD;border-radius:@RB;padding:6px 16px;min-width:64px;}
QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @B1,stop:1 @B1);}
QPushButton:pressed{background:@HI;}
QPushButton:disabled{color:@DIS;border:@BW solid @B2;}
QPushButton#primary{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @A1,stop:1 @A2);color:@PT;font-weight:bold;}
QLineEdit,QComboBox{background:@PANEL;border:@BW solid @BD;border-radius:@RP;padding:5px 8px;selection-background-color:@HI;}
QSpinBox,QTimeEdit,QDateEdit{background:@PANEL;padding:3px 6px;}
QComboBox QAbstractItemView,QCalendarWidget QWidget{background:@MENU;color:@FG;selection-background-color:@HI;}
QTableWidget,QTreeWidget,QListWidget{background:@PANEL;border:@BW solid @BD;border-radius:@RP;gridline-color:transparent;outline:0;}
QTableWidget::item:selected,QTreeWidget::item:selected,QListWidget::item:selected{background:@HI;color:@FG;}
QHeaderView::section{background:@HEAD;color:@FG;border:none;border-left:@BW solid @BD;padding:6px;}
QTableCornerButton::section{background:@HEAD;border:none;}
QTabWidget::pane{border:@BW solid @BD;border-radius:@RP;}
QTabBar::tab{background:@B2;border:@BW solid @BD;padding:6px 14px;border-top-left-radius:@RP;border-top-right-radius:@RP;margin:0 2px;}
QTabBar::tab:selected{background:@HI;}
QProgressBar{border:@BW solid @BD;border-radius:@RP;background:@PANEL;text-align:center;min-height:18px;}
QProgressBar::chunk{border-radius:@RP;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 @A1,stop:1 @A2);}
QDockWidget::title{background:@HEAD;padding:6px;}
QCheckBox::indicator,QRadioButton::indicator{width:15px;height:15px;border:@BW solid @BD;background:@PANEL;border-radius:4px;}
QRadioButton::indicator{border-radius:8px;}
QCheckBox::indicator:checked,QRadioButton::indicator:checked{background:@A1;}
QScrollBar:vertical{background:transparent;width:11px;margin:0;}
QScrollBar::handle:vertical{background:@SB;border-radius:5px;min-height:28px;}
QScrollBar:horizontal{background:transparent;height:11px;margin:0;}
QScrollBar::handle:horizontal{background:@SB;border-radius:5px;min-width:28px;}
QScrollBar::add-line,QScrollBar::sub-line{height:0;width:0;}
QToolTip{background:@MENU;color:@FG;border:@BW solid @BD;padding:4px;}
"""
THEMES = {
 "ocean": dict(name="۱) اقیانوسی", sw=("#031c4d", "#0a56a6", "#10809a"), hdrbg="rgba(255,255,255,40)", badge="rgba(255,255,255,55)",
   pal=("#0a56a6", "#ffffff", "#0b4a93", "#2a7bc8", "#4a9be8", "#ffffff"),
   q=dict(G1="#031c4d", G2="#0a56a6", G3="#10809a", FG="#ffffff", PANEL="rgba(255,255,255,34)", HEAD="rgba(0,20,70,120)", MENU="#07356e",
          HI="rgba(255,255,255,85)", B1="rgba(255,255,255,120)", B2="rgba(255,255,255,40)", BD="rgba(255,255,255,140)",
          A1="#7fe9ff", A2="#2f8bff", PT="#03204f", DIS="rgba(255,255,255,120)")),
 "desert": dict(name="۲) صحرایی", sw=("#3b2c1b", "#69502f", "#92754a"), hdrbg="rgba(25,12,0,90)", badge="rgba(255,255,255,50)",
   pal=("#69502f", "#fff6e3", "#4d3a22", "#8a6d45", "#b08d57", "#ffffff"),
   q=dict(G1="#3b2c1b", G2="#69502f", G3="#92754a", FG="#fff6e3", PANEL="rgba(25,12,0,80)", HEAD="rgba(25,12,0,120)", MENU="#4a3822",
          HI="rgba(255,255,255,75)", B1="rgba(255,255,255,115)", B2="rgba(255,255,255,38)", BD="rgba(255,246,227,130)",
          A1="#ffe0a0", A2="#e3a33c", PT="#3b2200", DIS="rgba(255,246,227,120)")),
 "sunset": dict(name="۳) غروب", sw=("#ff8a1f", "#ffad3b", "#ffd36e"), hdrbg="rgba(255,255,255,120)", badge="rgba(255,255,255,150)",
   pal=("#ffad3b", "#2e1500", "#ffe2a8", "#ffc468", "#ff8a1f", "#2e1500"),
   q=dict(G1="#ff8a1f", G2="#ffad3b", G3="#ffd36e", FG="#2e1500", PANEL="rgba(255,255,255,140)", HEAD="rgba(255,255,255,120)", MENU="#fff1d6",
          HI="rgba(255,120,0,120)", B1="rgba(255,255,255,215)", B2="rgba(255,255,255,95)", BD="rgba(255,255,255,230)",
          A1="#ff9a2e", A2="#e8590c", PT="#ffffff", DIS="rgba(46,21,0,110)")),
 "light": dict(name="۴) روز", sw=("#f9fbff", "#dfe8f8"), hdrbg="#e1eafb", badge="#ffffff", bar="#c3d0ea",
   pal=("#f4f7fc", "#1b2433", "#ffffff", "#eaf0fb", "#cfe0ff", "#10203a"),
   q=dict(G1="#f9fbff", G2="#eff3fb", G3="#e5ecf8", FG="#1b2433", PANEL="#ffffff", HEAD="#e3eaf7", MENU="#ffffff", HI="rgba(47,111,224,50)",
          B1="#ffffff", B2="#e6edf9", BD="#c5d1e8", A1="#6aa8ff", A2="#2f6fe0", PT="#ffffff", DIS="#9aa7bd")),
 "dark": dict(name="۵) شب", sw=("#2a3145", "#0e1118"), hdrbg="#232a3a", badge="#2d364b", bar="#47516b",
   pal=("#141821", "#e8ecf5", "#1c212d", "#2a3144", "#4b3fb0", "#ffffff"),
   q=dict(G1="#0e1118", G2="#141821", G3="#1b2130", FG="#e8ecf5", PANEL="#1d2230", HEAD="#262d3e", MENU="#1d2230", HI="rgba(139,108,255,95)",
          B1="#323a52", B2="#252c3e", BD="#3a4360", A1="#a58bff", A2="#6a4cf0", PT="#ffffff", DIS="#6d7691")),
}

THEMES.update({
 "neon": dict(name="۶) نئون", sw=("#07040f", "#7a2bff", "#00e5ff"), hdrbg="#1a0f3a", badge="#2a1660", bar="#7a2bff",
   pal=("#0d0820", "#e9f7ff", "#140a30", "#1b0f3d", "#00a9c0", "#000000"), tb="icon", tbsize=34, tbpos="top", hero=True, rowh=40, dock="right",
   q=dict(G1="#07040f", G2="#0d0820", G3="#150a33", FG="#e9f7ff", PANEL="rgba(30,16,70,190)", HEAD="rgba(60,20,120,210)", MENU="#12082a",
          HI="rgba(0,229,255,70)", B1="#1b0f3d", B2="#120a2b", BD="#00e5ff", A1="#ff2bd6", A2="#7a2bff", PT="#ffffff", DIS="#6a5f8f", RB="4px", RP="4px"),
   x="QPushButton:hover,QToolButton:hover{border:1px solid #ff2bd6;color:#ff7be8;}QTabBar::tab:selected{border:1px solid #ff2bd6;}QProgressBar{border:1px solid #ff2bd6;}"),
 "forest": dict(name="۷) جنگل", sw=("#0f3d2e", "#1f6b4a", "#7ac07a"), hdrbg="rgba(0,40,20,110)", badge="rgba(255,255,255,70)",
   pal=("#1f6b4a", "#f3fff6", "#17513a", "#2f8a5e", "#7ac07a", "#0b2d1c"), tb="beside", tbsize=30, tbpos="top", hero=True, rowh=44, dock="left",
   q=dict(G1="#0f3d2e", G2="#1f6b4a", G3="#4c9a62", FG="#f3fff6", PANEL="rgba(255,255,255,40)", HEAD="rgba(0,40,20,120)", MENU="#154a37",
          HI="rgba(190,255,200,80)", B1="rgba(255,255,255,120)", B2="rgba(255,255,255,50)", BD="rgba(255,255,255,150)", A1="#d9f99d", A2="#65a30d",
          PT="#173d12", DIS="rgba(243,255,246,120)", RB="20px", RP="14px"), x="QPushButton{padding:7px 22px;}"),
 "paper": dict(name="۸) کاغذی", sw=("#fbfaf6", "#e9e5d9"), hdrbg="#f1eee6", badge="#ffffff", bar="#cfc9b8",
   pal=("#fbfaf6", "#262626", "#ffffff", "#f1eee6", "#e4dfd0", "#111111"), tb="text", tbsize=20, tbpos="bottom", hero=False, rowh=32, dock="left",
   q=dict(G1="#fbfaf6", G2="#fbfaf6", G3="#fbfaf6", FG="#262626", PANEL="#ffffff", HEAD="#f1eee6", MENU="#fffefb", HI="rgba(0,0,0,18)",
          B1="#ffffff", B2="#ffffff", BD="#d9d4c7", A1="#222222", A2="#222222", PT="#ffffff", DIS="#b5b0a3", RB="0px", RP="0px"),
   x="QTabBar::tab{background:transparent;border:none;border-bottom:2px solid transparent;}QTabBar::tab:selected{border-bottom:2px solid #222222;background:transparent;}QToolBar{border-top:1px solid #d9d4c7;}"),
 "retro": dict(name="۹) رترو ۹۵", sw=("#c0c0c0", "#000080"), hdrbg="#b4b4b4", badge="#dcdcdc", bar="#808080",
   pal=("#c0c0c0", "#000000", "#ffffff", "#c0c0c0", "#000080", "#ffffff"), tb="under", tbsize=26, tbpos="top", hero=False, rowh=24, dock="left",
   q=dict(G1="#c0c0c0", G2="#c0c0c0", G3="#c0c0c0", FG="#000000", PANEL="#ffffff", HEAD="#c0c0c0", MENU="#c0c0c0", HI="#000080",
          B1="#c0c0c0", B2="#c0c0c0", BD="#808080", A1="#000080", A2="#000080", PT="#ffffff", DIS="#808080", RB="0px", RP="0px"),
   x="QPushButton,QToolButton{border:2px solid #808080;border-top-color:#ffffff;border-left-color:#ffffff;border-bottom-color:#404040;border-right-color:#404040;border-radius:0;background:#c0c0c0;padding:4px 12px;}"
     "QPushButton:pressed,QToolButton:pressed{border-top-color:#404040;border-left-color:#404040;border-bottom-color:#ffffff;border-right-color:#ffffff;}QPushButton:hover,QToolButton:hover{background:#d4d0c8;}"
     "QLineEdit,QComboBox,QTableWidget,QTreeWidget,QListWidget{border:2px solid #808080;border-top-color:#404040;border-left-color:#404040;border-bottom-color:#ffffff;border-right-color:#ffffff;border-radius:0;}"
     "QTableWidget::item:selected,QTreeWidget::item:selected,QListWidget::item:selected,QMenu::item:selected{background:#000080;color:#ffffff;}"
     "QHeaderView::section{background:#c0c0c0;border:2px solid #808080;border-top-color:#ffffff;border-left-color:#ffffff;border-bottom-color:#404040;border-right-color:#404040;}QProgressBar::chunk{background:#000080;border-radius:0;}"),
 "terminal": dict(name="۱۰) ترمینال", sw=("#020402", "#0a1a0d", "#14a83a"), hdrbg="#0a1a0d", badge="#0f2a14", bar="#1f8f3a",
   pal=("#020402", "#35ff6b", "#050b06", "#07120a", "#14a83a", "#001a06"), tb="text", tbsize=18, tbpos="left", hero=False, rowh=26, dock="right",
   q=dict(G1="#020402", G2="#020402", G3="#020402", FG="#35ff6b", PANEL="#050b06", HEAD="#0a1a0d", MENU="#050b06", HI="rgba(53,255,107,60)",
          B1="#07120a", B2="#07120a", BD="#1f8f3a", A1="#35ff6b", A2="#14a83a", PT="#001a06", DIS="#1d6b30", RB="0px", RP="0px"),
   x='QWidget{font-family:Consolas,"Irancell Medium";}QPushButton:hover,QToolButton:hover{background:#0c2412;border:1px solid #35ff6b;}QTableWidget::item:selected{color:#001a06;background:#35ff6b;}'),
})

def _fix(k, **kw): THEMES[k]["q"].update(kw)
_fix("ocean", HI="rgba(0,12,48,120)", B1="rgba(255,255,255,44)", B2="rgba(255,255,255,26)", SB="rgba(255,255,255,170)")
_fix("desert", SB="rgba(255,246,227,170)", HI="rgba(20,8,0,115)", B1="rgba(255,255,255,38)", B2="rgba(255,255,255,24)")
_fix("sunset", PT="#2e1500", SB="rgba(46,21,0,120)")
_fix("light", A1="#4688ee", SB="#aebddb")
_fix("dark", A1="#8566f5", SB="#56628a")
_fix("neon", SB="#7a2bff")
_fix("forest", HI="rgba(4,36,20,125)", B1="rgba(255,255,255,34)", B2="rgba(255,255,255,22)", PANEL="rgba(0,30,15,70)", SB="rgba(255,255,255,150)")
_fix("paper", SB="#bfb8a4")
_fix("retro", SB="#808080")
_fix("terminal", SB="#1f8f3a")
THEMES["terminal"]["font"] = "Consolas"
THEMES["terminal"]["x"] = THEMES["terminal"]["x"].replace('QWidget{font-family:Consolas,"Irancell Medium";}', "")

THEMES.update({
 "facebook": dict(name="۱۱) فیسبوک", sw=("#1565d8", "#f0f2f5"), hdrbg="#ffffff", badge="#e7f3ff", bar="#bcc0c4", tbbg="#1565d8", tbfg="#ffffff",
   pal=("#f0f2f5", "#1c1e21", "#ffffff", "#e4e6eb", "#cfe3ff", "#1c1e21"), tb="beside", tbsize=22, tbpos="top", hero=True, rowh=46, dock="left",
   q=dict(G1="#f0f2f5", G2="#f0f2f5", G3="#f0f2f5", FG="#1c1e21", PANEL="#ffffff", HEAD="#e4e6eb", MENU="#ffffff", HI="rgba(24,119,242,40)", B1="#e4e6eb", B2="#e4e6eb",
          BD="#ced0d4", A1="#2d88ff", A2="#1877f2", PT="#ffffff", DIS="#a8abb2", RB="8px", RP="8px", SB="#9da1a6"),
   x="QToolBar{background:#1565d8;border:none;padding:4px 10px;}QToolBar QToolButton{color:#ffffff;border-radius:18px;padding:5px 12px;}QToolBar QToolButton:hover{background:rgba(255,255,255,45);border:1px solid transparent;}"
     "QToolBar::separator:horizontal{background:rgba(255,255,255,70);}QMenuBar{background:#ffffff;border-bottom:1px solid #ced0d4;}QPushButton:hover{background:#d8dadf;}"),
 "pinterest": dict(name="۱۲) پینترست", sw=("#ffffff", "#e60023"), hdrbg="#f7f7f7", badge="#efefef", bar="#c4c4c4",
   pal=("#ffffff", "#111111", "#f7f7f7", "#efefef", "#ffd9de", "#111111"), tb="icon", tbsize=34, tbpos="top", hero=True, rowh=54, dock="left",
   q=dict(G1="#ffffff", G2="#ffffff", G3="#ffffff", FG="#111111", PANEL="#f7f7f7", HEAD="#efefef", MENU="#ffffff", HI="rgba(230,0,35,30)", B1="#efefef", B2="#e2e2e2",
          BD="#d6d6d6", A1="#ee1d3b", A2="#cc001f", PT="#ffffff", DIS="#9a9a9a", RB="24px", RP="16px", SB="#a8a8a8"),
   x="QToolBar QToolButton{border-radius:22px;padding:8px;}QToolBar QToolButton:hover{background:#efefef;border:1px solid transparent;}QLineEdit{border-radius:22px;padding:8px 16px;background:#efefef;border:2px solid transparent;}"
     "QLineEdit:focus{border:2px solid #e60023;background:#ffffff;}QTabBar::tab{border-radius:18px;margin:2px 4px;}QTabBar::tab:selected{background:#111111;color:#ffffff;}"),
 "instagram": dict(name="۱۳) اینستاگرام", sw=("#feda75", "#d62976", "#4f5bd5"), hdrbg="#ffffff", badge="#efefef", bar="#d62976",
   pal=("#fafafa", "#262626", "#ffffff", "#efefef", "#f3d6e8", "#262626"), tb="icon", tbsize=30, tbpos="bottom", hero=True, rowh=48, dock="left",
   q=dict(G1="#fafafa", G2="#fafafa", G3="#fafafa", FG="#262626", PANEL="#ffffff", HEAD="#f2f2f2", MENU="#ffffff", HI="rgba(193,53,132,32)", B1="#ffffff", B2="#f5f5f5",
          BD="#dbdbdb", A1="#e1306c", A2="#833ab4", PT="#ffffff", DIS="#a8a8a8", RB="8px", RP="8px", SB="#a9a9a9"),
   x="QToolBar{background:#ffffff;border-top:1px solid #dbdbdb;}QToolButton:hover{background:#f2f2f2;border:1px solid transparent;}QLineEdit{background:#efefef;border:1px solid #dbdbdb;}"
     "QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #feda75,stop:0.3 #fa7e1e,stop:0.55 #d62976,stop:0.8 #962fbf,stop:1 #4f5bd5);}"
     "QPushButton#primary{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #e1306c,stop:1 #833ab4);}"),
 "whatsapp": dict(name="۱۴) واتس‌اپ", sw=("#008069", "#efeae2"), hdrbg="#ffffff", badge="#d9fdd3", bar="#b6bec3", tbbg="#008069", tbfg="#ffffff",
   pal=("#efeae2", "#111b21", "#ffffff", "#f0f2f5", "#c8f2e6", "#111b21"), tb="beside", tbsize=24, tbpos="top", hero=True, rowh=58, dock="left",
   q=dict(G1="#efeae2", G2="#efeae2", G3="#efeae2", FG="#111b21", PANEL="#ffffff", HEAD="#f0f2f5", MENU="#ffffff", HI="rgba(0,168,132,40)", B1="#f0f2f5", B2="#e9edef",
          BD="#d1d7db", A1="#00a884", A2="#008069", PT="#ffffff", DIS="#8696a0", RB="20px", RP="10px", SB="#9aa6ad"),
   x="QToolBar{background:#008069;border:none;padding:4px 10px;}QToolBar QToolButton{color:#ffffff;border-radius:18px;padding:5px 12px;}QToolBar QToolButton:hover{background:rgba(255,255,255,45);border:1px solid transparent;}"
     "QToolBar::separator:horizontal{background:rgba(255,255,255,70);}QLineEdit{border-radius:18px;background:#f0f2f5;border:1px solid transparent;}"),
 "arabic": dict(name="۱۵) عربی", sw=("#062a28", "#0f5a52", "#d4af37"), hdrbg="rgba(2,30,27,170)", badge="rgba(212,175,55,70)", bar="#d4af37",
   pal=("#0b3d3a", "#fdf6e3", "#06302d", "#14594f", "#b8932a", "#1a1405"), tb="beside", tbsize=28, tbpos="top", hero=True, rowh=44, dock="right",
   q=dict(G1="#062a28", G2="#0b3d3a", G3="#0f5a52", FG="#fdf6e3", PANEL="rgba(2,30,27,150)", HEAD="rgba(2,30,27,210)", MENU="#0a322f", HI="rgba(212,175,55,75)", B1="#14594f", B2="#0d4640",
          BD="#d4af37", A1="#e6c35c", A2="#b8932a", PT="#1a1405", DIS="#86a39a", RB="6px", RP="6px", SB="#d4af37"),
   x="QPushButton{border:3px double #d4af37;}QToolButton:hover{border:3px double #d4af37;}QTableWidget,QTreeWidget,QListWidget,QTabWidget::pane{border:3px double #d4af37;}"
     "QTabBar::tab:selected{background:#b8932a;color:#1a1405;}QMenu{border:2px solid #d4af37;}"),
 "iranian": dict(name="۱۶) ایرانی", sw=("#fbf5e6", "#19a3a0", "#1e3a8a"), hdrbg="#efe0b9", badge="#cfe9e6", bar="#c9a24a", tbbg="#22409a", tbfg="#fff8e1",
   pal=("#f6ecd2", "#1b2a4e", "#fffaf0", "#5ed2cd", "#9fe0dc", "#1b2a4e"), tb="under", tbsize=36, tbpos="top", hero=True, rowh=42, dock="right",
   q=dict(G1="#fbf5e6", G2="#f6ecd2", G3="#efe0b9", FG="#1b2a4e", PANEL="#fffaf0", HEAD="#e6d6a8", MENU="#fffaf0", HI="rgba(25,163,160,70)", B1="#7adcd7", B2="#4cc4bf",
          BD="#1e3a8a", A1="#2e5bd8", A2="#1e3a8a", PT="#fff8e1", DIS="#8b8f9f", RB="14px", RP="10px", SB="#b8903a"),
   x="QToolBar{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #274aa8,stop:1 #1b3380);border-bottom:3px solid #e8b100;padding:4px 10px;}QToolBar QToolButton{color:#fff8e1;}"
     "QToolBar QToolButton:hover{background:rgba(255,255,255,40);border:1px solid #e8b100;}QToolBar::separator:horizontal{background:#e8b100;}"
     "QTabBar::tab:selected{border-bottom:3px solid #e8b100;}QTableWidget,QTreeWidget,QListWidget{border:2px solid #1e3a8a;}"),
 "roman": dict(name="۱۷) رومی", sw=("#f4f0e8", "#7a1313", "#c9a227"), hdrbg="#d9cfbb", badge="#efe6d2", bar="#c9a227", tbbg="#7a1313", tbfg="#fff3d6", font="Georgia",
   pal=("#ece6da", "#2b2118", "#fbf8f2", "#efe6d2", "#e3c9c3", "#2b2118"), tb="under", tbsize=30, tbpos="left", hero=True, rowh=40, dock="right",
   q=dict(G1="#f4f0e8", G2="#ece6da", G3="#e2dacb", FG="#2b2118", PANEL="#fbf8f2", HEAD="#d9cfbb", MENU="#fbf8f2", HI="rgba(139,26,26,45)", B1="#efe6d2", B2="#dccfae",
          BD="#8a6d1a", A1="#a52a2a", A2="#7a1313", PT="#fff3d6", DIS="#9b9181", RB="0px", RP="0px", BW="2px", SB="#a08a4a"),
   x="QToolBar{background:#7a1313;border:2px solid #c9a227;padding:4px;}QToolBar QToolButton{color:#fff3d6;border-radius:0;}QToolBar QToolButton:hover{background:rgba(201,162,39,75);border:1px solid #c9a227;}"
     "QToolBar::separator:horizontal{background:#c9a227;}QToolBar::separator:vertical{background:#c9a227;}QTabBar::tab{border:2px solid #8a6d1a;border-bottom:none;}"
     "QTabBar::tab:selected{background:#7a1313;color:#fff3d6;}"),
})
def TH(): return THEMES.get(S.get("theme"), THEMES["ocean"])
def build_qss(T):
    q = QSS; d = {"RB": "10px", "RP": "9px", "BW": "1px", **T.get("q", {})}; d.setdefault("SB", d.get("B1", "#888888"))
    for k, v in d.items(): q = q.replace("@" + k, v)
    return q + T.get("x", "") if T.get("q") else ""
def apply_theme(key):
    app = QApplication.instance(); key = key if key in THEMES else "ocean"; T = THEMES[key]; S["theme"] = key
    app.setStyleSheet(""); app.setStyle("Fusion")
    R_ = QPalette.ColorRole; pl = QPalette(); w, tx, base, btn, hl, ht = T["pal"]
    for r, c in ((R_.Window, w), (R_.WindowText, tx), (R_.Base, base), (R_.AlternateBase, base), (R_.Text, tx), (R_.Button, btn),
                 (R_.ButtonText, tx), (R_.Highlight, hl), (R_.HighlightedText, ht), (R_.ToolTipBase, btn), (R_.ToolTipText, tx),
                 (R_.PlaceholderText, tx), (R_.BrightText, "#ffffff")): pl.setColor(r, QColor(c))
    for r in (R_.Text, R_.ButtonText, R_.WindowText): pl.setColor(QPalette.ColorGroup.Disabled, r, QColor("#888888"))
    app.setPalette(pl); app.setStyleSheet(build_qss(T)); apply_font(); log(f"تم برنامه: {T['name']}")
    for w_ in app.allWidgets(): w_.update()
def swatch(T):
    pm = QPixmap(18, 18); pm.fill(Qt.GlobalColor.transparent); p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    g = QLinearGradient(0, 0, 18, 18); n = len(T["sw"])
    for i, c in enumerate(T["sw"]): g.setColorAt(i / (n - 1), QColor(c))
    p.setBrush(g); p.setPen(QColor("#888")); p.drawRoundedRect(1, 1, 16, 16, 4, 4); p.end(); return QIcon(pm)
BADGE = {"فایلهای فشرده": "📦", "اسناد": "📄", "موسیقی": "🎵", "برنامه ها": "💿", "تصویری": "🎬", "عمومی": "📁"}
def logo_pm(n):
    pm = QPixmap(os.path.join(HERE, "cdmlogo.png"))
    return pm if pm.isNull() else pm.scaled(n, n, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
def urls_in(txt):
    out = []
    for u in re.findall(r"(?:https?|ftp)://[^\s<>\"']+", txt or ""):
        u = u.rstrip(".,;:!?")
        if u not in out: out.append(u)
    return out
def sniff(url):  # بررسی لینک: حجم، نوع، نام
    try:
        r = rhead(url, headers=ua(), timeout=10, allow_redirects=True)
        if r.status_code >= 400 or "content-length" not in r.headers:
            r = rget(url, headers=ua(), timeout=10, stream=True); r.close()
        h = r.headers; m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', h.get("content-disposition", ""))
        nm = unquote(m.group(1)) if m else unquote(os.path.basename(urlparse(r.url).path))
        return dict(ok=r.status_code < 400, size=int(h.get("content-length", -1)), type=h.get("content-type", "").split(";")[0],
                    rng=h.get("accept-ranges", "").lower() == "bytes", name=nm)
    except Exception: return dict(ok=False, size=-1, type="", rng=False, name="")


# ───────────────────────── آیکون‌های شیشه‌ای و طراحی ─────────────────────────
_IC = {}
def gpix(g, c1="#6aa9ff", c2="#2f6fe0", n=48):  # فقط ایموجی، بدون پس‌زمینه
    pm = QPixmap(n, n); pm.fill(Qt.GlobalColor.transparent); p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing); p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    f = QFont("Segoe UI Emoji"); f.setPixelSize(int(n * .78)); p.setFont(f); p.setPen(QColor(c2))
    p.drawText(QRectF(0, 0, n, n), Qt.AlignmentFlag.AlignCenter, g); p.end(); return pm
def gicon(g, c1="#6aa9ff", c2="#2f6fe0", n=48):
    k = (g, c1, c2, n)
    if k not in _IC: _IC[k] = QIcon(gpix(g, c1, c2, n))
    return _IC[k]
FMAP = [("📦", "#ffb347", "#e8590c", "zip rar 7z gz tar bz2 xz".split()), ("💿", "#9fb3c8", "#4a6075", ["iso", "img"]),
        ("🎬", "#b388ff", "#6a3fd1", "mp4 mkv avi ts mov webm flv wmv".split()), ("🎵", "#f48fb1", "#c2185b", "mp3 wav flac aac ogg m4a".split()),
        ("🖥", "#5eb0ff", "#1a62d6", "exe msi apk dmg deb".split()), ("📕", "#ff8a80", "#d32f2f", ["pdf"]), ("📘", "#64b5f6", "#1565c0", ["doc", "docx"]),
        ("📗", "#81c784", "#2e7d32", ["xls", "xlsx", "csv"]), ("📙", "#ffb74d", "#e65100", ["ppt", "pptx"]), ("📝", "#fff176", "#f9a825", ["txt", "epub"]),
        ("🖼", "#4dd0e1", "#00838f", "jpg jpeg png gif webp bmp".split())]
def fileicon(name):
    e = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    for g, c1, c2, ex in FMAP:
        if e in ex: return gicon(g, c1, c2, 40)
    return gicon("📄", "#b0bec5", "#546e7a", 40)
TREEI = {"همه دانلودها": ("📥", "#5eb0ff", "#1a62d6"), "فایلهای فشرده": ("📦", "#ffb347", "#e8590c"), "اسناد": ("📄", "#64b5f6", "#1565c0"),
         "موسیقی": ("🎵", "#f48fb1", "#c2185b"), "برنامه ها": ("🖥", "#5eb0ff", "#1a62d6"), "تصویری": ("🎬", "#b388ff", "#6a3fd1"),
         "ناتمام": ("⏳", "#ffd54f", "#f9a825"), "تکمیل شده": ("✅", "#69f0ae", "#00a152"), "پروژه های گربر": ("🕷", "#a1887f", "#5d4037"),
         "تصاویر": ("🖼", "#4dd0e1", "#00838f"), "صفها": ("🗓", "#4dd0e1", "#00838f")}
EXI = {"json": ("🧾", "#4dd0e1", "#00838f"), "csv": ("📊", "#81c784", "#2e7d32"), "txt": ("🔗", "#90a4ae", "#455a64")}
DECO = [("انصراف", "✖"), ("تأیید", "✔"), ("بستن", "✖"), ("پنهان کردن", "🔼"), ("نمایش جزئیات", "🔽"), ("ایست", "⏸"), ("ادامه", "▶"),
        ("شروع", "▶"), ("توقف", "⏹"), ("راهنما", "❓"), ("اجرا", "⚡"), ("صف جدید", "➕"), ("حذف", "🗑"), ("علامت گذاری همه", "☑"),
        ("برداشتن علامت همه", "⬜"), ("جستجو", "📂")]
TABS = {"وضعیت دانلود": "📊", "محدود کننده سرعت": "🚦", "گزینه هاي اتمام دانلود": "🏁", "زمان بندی": "⏰", "فایلهای موجود در صف": "📋"}
class GDialog(QDialog):  # پایه دیالوگ‌ها: ایموجی به‌صورت پیشوند متن دکمه‌ها و تب‌ها (بدون همپوشانی)
    def showEvent(s, e):
        if not getattr(s, "_deco", False):
            s._deco = True
            for b in s.findChildren(QPushButton):
                tx = b.text().strip()
                if not tx: continue
                if tx == "...": b.setText("📂"); continue
                for k, g in DECO:
                    if tx == k or (len(k) > 3 and tx.startswith(k)): b.setText(f"{g}  {tx}"); break
            for tw in s.findChildren(QTabWidget):
                for i in range(tw.count()):
                    if tw.tabText(i) in TABS: tw.setTabText(i, f"{TABS[tw.tabText(i)]}  {tw.tabText(i)}")
        super().showEvent(e)
class StatDelegate(QStyledItemDelegate):  # نوار پیشرفت داخل سلول وضعیت (نرم و زنده)
    def __init__(s, parent, look=None): super().__init__(parent); s.look = look
    def paint(s, p, opt, idx):
        pc = idx.data(Qt.ItemDataRole.UserRole)
        if pc is None: return super().paint(p, opt, idx)
        kind = idx.data(Qt.ItemDataRole.UserRole + 1); tx = idx.data(Qt.ItemDataRole.DisplayRole)
        if kind == "run" and s.look:
            jb = s.look(idx.row())
            if jb is not None and jb.size > 0: pc = jb.smooth() / jb.size * 100; tx = fd(f"⬇  {pc:.1f}%")
        o = QStyleOptionViewItem(opt); s.initStyleOption(o, idx); o.text = ""
        (o.widget.style() if o.widget else QApplication.style()).drawControl(QStyle.ControlElement.CE_ItemViewItem, o, p, o.widget)
        cols = {"ok": ("#3ecf7f", "#1f8f4e"), "run": ("#58a6f5", "#1f62c9"), "pause": ("#f5be55", "#c98a14"), "err": ("#f2776d", "#b3261e")}[kind]
        m = max(3, int(opt.rect.height() * .22)); r = QRectF(opt.rect).adjusted(6, m, -6, -m); w = r.width() * min(pc, 100) / 100
        p.save(); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(128, 128, 128, 60)); p.drawRoundedRect(r, 7, 7)
        f = p.font(); f.setBold(True); p.setFont(f); p.setPen(opt.palette.color(QPalette.ColorRole.Text)); p.drawText(r, Qt.AlignmentFlag.AlignCenter, tx)
        if w > 2:
            g = QLinearGradient(r.topLeft(), r.bottomLeft()); g.setColorAt(0, QColor(cols[0])); g.setColorAt(1, QColor(cols[1]))
            fr = QRectF(r.x(), r.y(), max(w, 10), r.height()); p.setPen(Qt.PenStyle.NoPen); p.setBrush(g); p.drawRoundedRect(fr, 7, 7)
            p.setClipRect(fr); p.setPen(QColor("white")); p.drawText(r, Qt.AlignmentFlag.AlignCenter, tx)
        p.restore()
def theme_pm(T):
    pm = QPixmap(132, 84); pm.fill(Qt.GlobalColor.transparent); p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    g = QLinearGradient(0, 0, 132, 84); n = len(T["sw"])
    for i, c in enumerate(T["sw"]): g.setColorAt(i / (n - 1), QColor(c))
    p.setPen(QPen(QColor(255, 255, 255, 140), 1.5)); p.setBrush(g); p.drawRoundedRect(QRectF(2, 2, 128, 80), 12, 12); p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(T["bar"]) if "bar" in T else QColor(255, 255, 255, 105))
    for i in range(3): p.drawRoundedRect(QRectF(12 + i * 38, 56, 32, 16), 7, 7)
    p.drawRoundedRect(QRectF(12, 14, 64, 8), 4, 4); p.drawRoundedRect(QRectF(12, 29, 104, 14), 6, 6); p.end(); return pm


def ua(): return {"User-Agent": S.get("ua") or UA["User-Agent"]}
def _kw(k):
    k.setdefault("verify", bool(S.get("verify_ssl", True)))
    pr = (S.get("proxy") or "").strip()
    if pr: k.setdefault("proxies", {"http": pr, "https": pr})
    return k
def rget(url, **k): return requests.get(url, **_kw(k))
def rhead(url, **k): return requests.head(url, **_kw(k))
def gdir(g): return S.get("gdirs", {}).get(g) or (os.path.join(S["dir"], GR[g][0]) if S.get("subdirs", True) else S["dir"])
KNOWN = {e for _, x in GR.values() for e in x} | {"jpg", "png"}
FONT = "Tahoma"
def load_font():
    fn = os.path.join(HERE, "Irancell_Duran-Medium.ttf")
    if os.path.exists(fn):
        i = QFontDatabase.addApplicationFont(fn)
        fam = QFontDatabase.applicationFontFamilies(i) if i >= 0 else []
        if fam: return fam[0]
    return "Tahoma"
def apply_font():
    f = QFont(FONT, int(S.get("fsize", 10))); fam = THEMES.get(S.get("theme"), {}).get("font")
    if fam: f.setFamilies([fam, FONT])
    QApplication.instance().setFont(f)
def set_autostart(on):
    if os.name != "nt": return
    import winreg
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    try:
        if on:
            cmd = f'"{sys.executable}"' if getattr(sys, "frozen", False) else f'"{sys.executable.replace("python.exe", "pythonw.exe")}" "{os.path.join(HERE, "cdm.py")}"'
            winreg.SetValueEx(k, "CDM", 0, winreg.REG_SZ, cmd)
        else:
            try: winreg.DeleteValue(k, "CDM")
            except OSError: pass
    finally: winreg.CloseKey(k)

FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
def fd(x): return x.translate(FA) if S.get("fa_digits") else x
def fspd(v): return f"{v * 8 / 1e6:.2f} Mbps" if S.get("speed_unit") == "mbit" else f"{fs(v)}/s"
DFMT = {"idm": "%b %d %H:%M:%S %Y", "iso": "%Y-%m-%d %H:%M", "dmy": "%d/%m/%Y %H:%M", "time": "%H:%M:%S"}
def fdate(j): return time.strftime(DFMT.get(S.get("date_fmt"), DFMT["idm"]), time.localtime(j.ts))
def pts(d):
    try: return time.mktime(time.strptime(d, DFMT["idm"]))
    except Exception: return time.time()
def is_hls(u): return urlparse(u).path.lower().endswith(".m3u8")
def clean(n): return (re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", n).strip(" .") or "download") if S.get("name_clean", True) else n
def cpath(p): d, n = os.path.split(p); return os.path.join(d, clean(n))
def glim():
    if S.get("night_on"):
        h = datetime.now().hour; a, b = S["night_from"], S["night_to"]
        if (a <= h < b) if a < b else (h >= a or h < b): return S["night_kb"]
    return S["speed"]
LOGQ = collections.deque(maxlen=5000); LOGN = [0]; _LL = threading.Lock()
def log(msg, lv="INFO"):  # ثبت گزارش برنامه (قابل مشاهده و ذخیره در بخش «گزارش‌ها»)
    if not S.get("log_on", True): return
    with _LL:
        LOGN[0] += 1; e = (LOGN[0], time.strftime("%Y-%m-%d %H:%M:%S"), lv, str(msg)); LOGQ.append(e)
    if S.get("log_file"):
        try:
            fn = os.path.join(os.path.expanduser("~"), ".cdm_log.txt")
            if os.path.exists(fn) and os.path.getsize(fn) > 2000000: os.replace(fn, fn + ".old")
            with open(fn, "a", encoding="utf-8") as f: f.write(f"[{e[1]}] {lv:<5} {e[3]}\n")
        except OSError: pass
def reveal(path):  # باز کردن پوشه و انتخاب خود فایل
    path = os.path.normpath(path)
    tgt = path if os.path.exists(path) else (path + ".part" if os.path.exists(path + ".part") else None)
    try:
        if os.name == "nt" and tgt: subprocess.Popen(f'explorer /select,"{tgt}"'); return
        if sys.platform == "darwin" and tgt: subprocess.Popen(["open", "-R", tgt]); return
    except Exception: pass
    QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))
class Job:
    def __init__(s, url, path, group, n=8):
        s.url, s.path, s.group, s.n = url, path, group, n
        s.size, s.segs, s.status, s.speed = -1, [], "توقف", 0
        s.date = time.strftime("%b %d %H:%M:%S %Y"); s.ts = time.time(); s.msg = ""; s.hls = is_hls(url); s.vdone = 0.0; s.vt = time.time(); s.th = None
        s.stop = s.err = s.eof = False; s.limit = 0; s.hdr = {}; s.notified = True; s.dlg = None; s.hidewin = False; s.queue = ""; s.paused = False; s.qtries = 0
    done = property(lambda s: sum(x[2] for x in s.segs))
    name = property(lambda s: os.path.basename(s.path))
    running = property(lambda s: s.th is not None and s.th.is_alive())
    finished = property(lambda s: s.status == "تکمیل شد.")
    def fin(s, g): return (g[1] >= 0 and g[2] >= g[1] - g[0] + 1) or (g[1] < 0 and s.eof)
    def smooth(s, tau=.14):  # مقدار نمایشی نرم (بدون پرش پله‌ای)؛ چند بار فراخوانی در یک لحظه بی‌اثر است
        now = time.time(); d = s.done
        if not s.running or s.finished or d < s.vdone: s.vdone = float(d)
        else: s.vdone += (d - s.vdone) * (1 - math.exp(-max(now - s.vt, 0) / tau))
        s.vt = now; return s.vdone
    def halt(s):
        if s.running: log(f"توقف دانلود: {s.name}")
        s.stop = s.paused = True
    def start(s):
        if s.running or s.finished: return
        s.stop = s.err = s.eof = s.paused = False; s.notified = False; s.hidewin = False; s.msg = ""; s.speed = 0; s.status = "در حال دریافت..."; log(f"شروع/ادامه دانلود: {s.name}")
        s.th = threading.Thread(target=s._run, daemon=True); s.th.start()
    def _run(s):
        try:
            if s.hls: return s._hls()
            if not s.segs:
                r = rget(s.url, stream=True, headers={**ua(), **s.hdr}, timeout=S["timeout"])
                if r.status_code == 404: s.status = "یافت نشد"; return
                r.raise_for_status()
                s.size = int(r.headers.get("content-length", -1))
                rg = r.headers.get("accept-ranges", "").lower() == "bytes"; r.close()
                os.makedirs(os.path.dirname(s.path), exist_ok=True)
                if S["check_space"] and s.size > 0 and shutil.disk_usage(os.path.dirname(s.path)).free < s.size:
                    s.status = "خطا"; s.msg = "فضای دیسک کافی نیست"; return
                f0 = open(s.path + ".part", "wb"); f0.truncate(s.size) if S["prealloc"] and s.size > 0 else None; f0.close()
                if s.size > 0 and rg:
                    n = max(1, min(s.n, s.size // (max(1, S["minseg"]) * 1024))); c = s.size // n
                    s.segs = [[i * c, s.size - 1 if i == n - 1 else (i + 1) * c - 1, 0] for i in range(n)]
                else: s.segs = [[0, s.size - 1, 0]]
            ths = [threading.Thread(target=s._seg, args=(g,), daemon=True) for g in s.segs if not s.fin(g)]
            [t.start() for t in ths]
            last, lt = s.done, time.time()
            while any(t.is_alive() for t in ths):
                time.sleep(.1); d, now = s.done, time.time(); inst = (d - last) / max(now - lt, .01)
                s.speed = inst if s.speed <= 0 else s.speed * .85 + inst * .15; last, lt = d, now
            s.speed = 0
            if all(s.fin(g) for g in s.segs):
                os.replace(s.path + ".part", s.path); s.status = "تکمیل شد."
            else: s.status = "توقف" if s.stop else "خطا"
        except Exception as e: s.status = "خطا"; s.msg = s.msg or str(e)[:80]; s.speed = 0
    def _hls(s):  # دانلود پخش زنده/استریم HLS (m3u8): دریافت تکه‌ها به‌صورت موازی و اتصال به یک فایل
        try:
            hd = {**ua(), **s.hdr}; ref = s.hdr.get("Referer")
            if ref: pr = urlparse(ref); hd.setdefault("Origin", f"{pr.scheme}://{pr.netloc}")
            def get(u): r = rget(u, headers=hd, timeout=S["timeout"]); r.raise_for_status(); return r
            u = s.url; txt = get(u).text
            if "#EXT-X-STREAM-INF" in txt:  # پلی‌لیست اصلی → بهترین کیفیت
                L = txt.splitlines(); best, bw = None, -1
                for i, l in enumerate(L):
                    if l.startswith("#EXT-X-STREAM-INF"):
                        m = re.search(r"BANDWIDTH=(\d+)", l); b = int(m.group(1)) if m else 0
                        nx = next((x.strip() for x in L[i + 1:] if x.strip() and not x.startswith("#")), None)
                        if nx and b > bw: best, bw = nx, b
                if best: u = urljoin(u, best); txt = get(u).text
            items, key, seq, init = [], None, 0, None
            for l in (x.strip() for x in txt.splitlines()):
                if l.startswith("#EXT-X-MEDIA-SEQUENCE:"): seq = int(l.split(":")[1])
                elif l.startswith("#EXT-X-KEY:"):
                    if "METHOD=NONE" in l: key = None
                    elif "AES-128" in l:
                        m = re.search(r'URI="([^"]+)"', l); iv = re.search(r"IV=0[xX]([0-9A-Fa-f]+)", l)
                        key = (urljoin(u, m.group(1)), bytes.fromhex(iv.group(1).zfill(32)) if iv else None)
                    else: s.status = "خطا"; s.msg = "این نوع رمزگذاری پشتیبانی نمی‌شود"; return
                elif l.startswith("#EXT-X-MAP:"):
                    m = re.search(r'URI="([^"]+)"', l); init = urljoin(u, m.group(1)) if m else None
                elif l and not l.startswith("#"): items.append((urljoin(u, l), key, seq + len(items)))
            if not items: s.status = "خطا"; s.msg = "پلی‌لیست خالی است"; return
            if init: items.insert(0, (init, None, -1))
            keys = {}
            for _, k, _ in items:
                if k and k[0] not in keys: keys[k[0]] = get(k[0]).content
            wd = s.path + ".hls"; os.makedirs(wd, exist_ok=True); st = {"b": 0, "n": 0, "live": 0}; lock = threading.Lock(); it = iter(range(len(items)))
            def fp(i): return os.path.join(wd, f"{i:06d}.seg")
            def fetch_seg(u2):
                r = rget(u2, headers=hd, timeout=S["timeout"], stream=True); r.raise_for_status(); buf = bytearray()
                try:
                    for ch in r.iter_content(65536):
                        if s.stop: raise InterruptedError
                        buf += ch
                        with lock: st["live"] += len(ch)
                except BaseException:
                    with lock: st["live"] -= len(buf)
                    raise
                return bytes(buf)
            def dec(data, k, sq):
                from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                dc = Cipher(algorithms.AES(keys[k[0]]), modes.CBC(k[1] or sq.to_bytes(16, "big"))).decryptor(); o = dc.update(data) + dc.finalize()
                return o[:-o[-1]] if o and 1 <= o[-1] <= 16 else o
            def worker():
                while not s.stop and not s.err:
                    with lock: i = next(it, None)
                    if i is None: return
                    if os.path.exists(fp(i)):
                        with lock: st["b"] += os.path.getsize(fp(i)); st["n"] += 1
                        continue
                    u2, k, sq = items[i]
                    for _ in range(S["retries"] + 1):
                        if s.stop: return
                        got = 0
                        try:
                            data = fetch_seg(u2); got = len(data)
                            if k: data = dec(data, k, sq)
                            with open(fp(i) + ".t", "wb") as f: f.write(data)
                            os.replace(fp(i) + ".t", fp(i))
                            with lock: st["b"] += len(data); st["n"] += 1; st["live"] -= got
                            break
                        except Exception:
                            if got:
                                with lock: st["live"] -= got
                            time.sleep(1)
                    else: s.err = True; return
            ths = [threading.Thread(target=worker, daemon=True) for _ in range(max(1, min(S["conn"], 16)))]
            [x.start() for x in ths]; last, lt = 0, time.time()
            while any(x.is_alive() for x in ths):
                time.sleep(.1); b, n = st["b"] + st["live"], st["n"]; now = time.time(); inst = (b - last) / max(now - lt, .01); s.speed = inst if s.speed <= 0 else s.speed * .85 + inst * .15; last, lt = b, now
                if n: est = max(b + 1, int(b / n * len(items))); s.size = est; s.segs = [[0, est - 1, b]]
            s.speed = 0
            if st["n"] >= len(items) and not s.err:
                with open(s.path + ".part", "wb") as out:
                    for i in range(len(items)):
                        with open(fp(i), "rb") as f: shutil.copyfileobj(f, out)
                tot = os.path.getsize(s.path + ".part"); os.replace(s.path + ".part", s.path); s.size = tot; s.segs = [[0, tot - 1, tot]]
                shutil.rmtree(wd, ignore_errors=True); s.status = "تکمیل شد."
            else: s.status = "توقف" if s.stop else "خطا"; s.msg = "" if s.stop else "دریافت یکی از تکه‌ها ناموفق بود"
        except Exception as e: s.status = "خطا"; s.msg = str(e)[:70]; s.speed = 0
    def _seg(s, g):
        tries = 0
        while not s.stop and not s.fin(g) and tries < S["retries"]:
            try:
                pos, h = g[0] + g[2], {**ua(), **s.hdr}
                if g[1] >= 0: h["Range"] = f"bytes={pos}-{g[1]}"
                else: g[2] = 0
                with rget(s.url, headers=h, stream=True, timeout=S["timeout"]) as r:
                    r.raise_for_status()
                    if r.status_code != 206 and pos > g[0] + 0 and g[1] >= 0:
                        if len(s.segs) > 1: raise IOError
                        g[2] = 0; pos = g[0]
                    with open(s.path + ".part", "r+b") as f:
                        f.seek(pos)
                        for ch in r.iter_content(max(4, S["buf_kb"]) * 1024):
                            if s.stop: return
                            f.write(ch); g[2] += len(ch)
                            lim = s.limit or glim(); time.sleep(len(ch) / (lim * 1024 / max(1, len(s.segs)))) if lim else None
                    if g[1] < 0: s.eof = True
            except Exception as e: tries += 1; log(f"تلاش مجدد {tries}/{S['retries']} برای «{s.name}»: {str(e)[:90]}", "WARN"); time.sleep(1)

class AddDialog(GDialog):  # Download File Info
    got = pyqtSignal(int, object)
    def __init__(s, p, url=""):
        super().__init__(p); s.setWindowTitle("افزودن دانلود جدید"); s.setMinimumWidth(640); s.rid = 0; s.edited = False
        T = TH(); s.setWindowIcon(QIcon(logo_pm(32)))
        s.url = QLineEdit(url if url.startswith("http") else ""); s.url.setPlaceholderText("https://example.com/file.zip"); s.url.setClearButtonEnabled(True)
        s.grp = QComboBox(); s.grp.addItems(GR); s.pth = QComboBox(); s.pth.setEditable(True); s.note = QLineEdit()
        s.note.setPlaceholderText("اختیاری")
        b = QPushButton("📂"); b.setFixedWidth(38); b.setToolTip("انتخاب مسیر"); b.clicked.connect(s.browse)
        s.rem = QCheckBox("به‌خاطر سپردن این پوشه برای گروه انتخاب‌شده")
        hdr = QFrame(); hdr.setObjectName("hdr"); hdr.setStyleSheet(f"QFrame#hdr{{background:{T['hdrbg']};border-radius:12px}}")
        lg = QLabel(); lg.setPixmap(logo_pm(48)); tt = QLabel("افزودن دانلود جدید"); tt.setStyleSheet("font-size:15pt;font-weight:bold")
        sb = QLabel("آدرس فایل را وارد کنید؛ گروه و مسیر ذخیره خودکار تنظیم می‌شوند."); vt = QVBoxLayout(); vt.addWidget(tt); vt.addWidget(sb)
        hl = QHBoxLayout(hdr); hl.addWidget(lg); hl.addLayout(vt, 1)
        card = QFrame(); card.setObjectName("card"); card.setStyleSheet(f"QFrame#card{{background:{T['hdrbg']};border-radius:12px}}")
        s.bd = QLabel(BADGE["عمومی"]); s.bd.setFixedSize(70, 70); s.bd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.bd.setStyleSheet("background:transparent")
        s.stat = QLabel("🔗 آدرس را وارد کنید"); s.stat.setStyleSheet("font-weight:bold")
        s.iv = {k: QLabel("—") for k in ("نام فایل", "حجم", "نوع", "قابلیت ادامه دانلود")}
        cg = QGridLayout(card); cg.addWidget(s.bd, 0, 0, 5, 1); cg.addWidget(s.stat, 0, 1, 1, 2)
        for i, (k, v) in enumerate(s.iv.items()): cg.addWidget(QLabel(k + " :"), i + 1, 1); cg.addWidget(v, i + 1, 2); v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cg.setColumnStretch(2, 1)
        g = QGridLayout(); g.setVerticalSpacing(9)
        for i, (ic, tx) in enumerate((("🔗", "آدرس (URL)"), ("🗂", "گروه"), ("💾", "ذخیره با عنوان"), ("📝", "توضیحات"))):
            g.addWidget(QLabel(f"{ic}  {tx}"), i + (1 if i > 2 else 0), 0)
        g.addWidget(s.url, 0, 1, 1, 2); g.addWidget(s.grp, 1, 1, 1, 2); g.addWidget(s.pth, 2, 1); g.addWidget(b, 2, 2)
        g.addWidget(s.rem, 3, 1, 1, 2); g.addWidget(s.note, 4, 1, 1, 2)
        s.go = QPushButton("▶  شروع دانلود"); s.go.setObjectName("primary"); s.go.setDefault(True)
        lat = QPushButton("🕒  بعداً دانلود شود"); can = QPushButton("✖  انصراف")
        s.go.clicked.connect(lambda: s.done(1)); lat.clicked.connect(lambda: s.done(2)); can.clicked.connect(lambda: s.done(0))
        h = QHBoxLayout(); [h.addWidget(x) for x in (can, s.go, lat)]; h.addStretch()
        v = QVBoxLayout(s); v.setSpacing(12); v.addWidget(hdr); v.addLayout(g); v.addWidget(card); v.addLayout(h)
        s.tmr = QTimer(s); s.tmr.setSingleShot(True); s.tmr.timeout.connect(s.check); s.got.connect(s.on_info)
        s.pth.lineEdit().textEdited.connect(lambda _: setattr(s, "edited", True))
        s.url.textChanged.connect(s.upd); s.grp.activated.connect(lambda: s.upd(keepgrp=True)); s.upd()
        if s.url.text(): QTimer.singleShot(300, s.check)
    def setpath(s, n):
        g = s.grp.currentText(); d = gdir(g)
        s.pth.setCurrentText(os.path.join(d, n))
    def upd(s, *_, keepgrp=False):
        n = re.sub(r"\.m3u8$", ".ts", unquote(os.path.basename(urlparse(s.url.text()).path)), flags=re.I) or "download"
        if not keepgrp: s.grp.setCurrentText(grp_of(n))
        if not s.edited or keepgrp: s.setpath(os.path.basename(s.pth.currentText()) if keepgrp and s.edited else n)
        s.badge(); s.tmr.start(700)
    def badge(s): s.bd.setPixmap(fileicon(os.path.basename(s.pth.currentText()) or "x").pixmap(64, 64))
    def check(s):
        u = s.url.text().strip()
        if not u.startswith("http"): return
        s.rid += 1; r = s.rid; s.stat.setText("⏳ در حال بررسی لینک ...")
        threading.Thread(target=lambda: s.got.emit(r, sniff(u)), daemon=True).start()
    def on_info(s, rid, d):
        if rid != s.rid: return
        s.stat.setText("✔ لینک معتبر است" if d["ok"] else "⚠ لینک پاسخ نمی‌دهد یا معتبر نیست")
        s.iv["نام فایل"].setText(d["name"] or "—"); s.iv["حجم"].setText(fs(d["size"]) or "نامشخص")
        s.iv["نوع"].setText(d["type"] or "—"); s.iv["قابلیت ادامه دانلود"].setText("✔ دارد" if d["rng"] else "✖ ندارد")
        if d["ok"] and d["name"] and not s.edited:
            s.grp.setCurrentText(grp_of(d["name"])); s.setpath(d["name"]); s.badge()
    def browse(s):
        f, _ = QFileDialog.getSaveFileName(s, "ذخیره", s.pth.currentText())
        if f: s.pth.setCurrentText(os.path.normpath(f)); s.edited = True
    def done(s, c):
        if c and s.rem.isChecked(): S.setdefault("gdirs", {})[s.grp.currentText()] = os.path.dirname(s.pth.currentText()); save_s()
        super().done(c)

class LinksDialog(GDialog):  # دانلود همه لینکها
    info = pyqtSignal(int, object)
    def __init__(s, p, urls):
        super().__init__(p); s.setWindowTitle("دانلود همه لینکها توسط CDM"); s.resize(1040, 780); s.urls = urls; s.sz = {}
        s.setWindowIcon(QIcon(logo_pm(32)))
        s.exts = [os.path.splitext(urlparse(u).path)[1].lstrip(".").lower() for u in urls]
        s.t = QTableWidget(len(urls), 4); s.t.setIconSize(QSize(22, 22)); s.t.setHorizontalHeaderLabels(["نام فایل", "نوع فایل", "سایز", "دانلود از"]); s.t.verticalHeader().hide()
        s.t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); s.t.horizontalHeader().setStretchLastSection(True)
        for c, w in enumerate((330, 110, 90)): s.t.setColumnWidth(c, w)
        for i, u in enumerate(urls):
            n = re.sub(r"\.m3u8$", ".ts", unquote(os.path.basename(urlparse(u).path)), flags=re.I) or "download"; it = QTableWidgetItem(n)
            it.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable); it.setCheckState(Qt.CheckState.Checked); it.setIcon(fileicon(n))
            s.t.setItem(i, 0, it); s.t.setItem(i, 1, QTableWidgetItem(grp_of(n))); s.t.setItem(i, 2, QTableWidgetItem("...")); s.t.setItem(i, 3, QTableWidgetItem(u))
        fl = [e in KNOWN for e in s.exts]
        if any(fl) and not all(fl):   # فقط لینک‌های فایل از پیش علامت می‌خورند؛ صفحه‌های وب بدون علامت
            for i, f_ in enumerate(fl):
                if not f_: s.t.item(i, 0).setCheckState(Qt.CheckState.Unchecked)
        # ── فیلتر و انتخاب
        s.flt = QLineEdit(); s.flt.setPlaceholderText("🔍  فیلتر بر اساس نام یا آدرس ..."); s.flt.setClearButtonEnabled(True)
        s.ext = QComboBox(); s.ext.addItem(f"همه‌ی پسوندها ({len(urls)})", "")
        for e_, c_ in collections.Counter(s.exts).most_common(): s.ext.addItem(f".{e_}   ({c_})" if e_ else f"بدون پسوند   ({c_})", e_ or "-")
        ma, mu, mi = QPushButton("علامت گذاری همه"), QPushButton("برداشتن علامت همه"), QPushButton("🔁  معکوس کردن انتخاب")
        ma.clicked.connect(lambda: s.mark(1)); mu.clicked.connect(lambda: s.mark(0)); mi.clicked.connect(lambda: s.mark(2))
        s.cnt = QLabel(); s.cnt.setStyleSheet("font-weight:bold")
        s.flt.textChanged.connect(s.apply_filter); s.ext.currentIndexChanged.connect(s.apply_filter); s.t.itemChanged.connect(s.upd_cnt)
        fr = QHBoxLayout(); fr.addWidget(s.flt, 1); fr.addWidget(s.ext)
        # ── مقصد دانلود
        s.d_now = QRadioButton("▶  شروع فوری همه (همزمان)"); s.d_q = QRadioButton("🕒  افزودن به صف:"); s.d_list = QRadioButton("📋  فقط افزودن به لیست (بدون شروع؛ بعداً دانلود شود)")
        s.dg = QButtonGroup(s); [s.dg.addButton(x) for x in (s.d_now, s.d_q, s.d_list)]
        {"now": s.d_now, "list": s.d_list}.get(S["lk_dest"], s.d_q).setChecked(True)
        s.qc = QComboBox(); s.qc.addItems([q["name"] for q in S["queues"]]); s.qc.setCurrentIndex(max(0, s.qc.findText(S["lk_queue"])))
        s.qs = QCheckBox("شروع صف بلافاصله بعد از افزودن"); s.qs.setChecked(bool(S["lk_start"]))
        s.qp = QSpinBox(); s.qp.setRange(1, 16); s.qpl = QLabel("تعداد دانلود همزمان این صف:")
        s.qc.currentIndexChanged.connect(s.qchg); s.dg.buttonClicked.connect(s.dchg); s.qchg(); s.dchg()
        gq = QGroupBox("مقصد دانلود"); ql = QGridLayout(gq); ql.addWidget(s.d_now, 0, 0, 1, 3); ql.addWidget(s.d_q, 1, 0); ql.addWidget(s.qc, 1, 1, 1, 2)
        ql.addWidget(s.qpl, 2, 0); ql.addWidget(s.qp, 2, 1); ql.addWidget(s.qs, 3, 0, 1, 3); ql.addWidget(s.d_list, 4, 0, 1, 3)
        # ── نام‌گذاری و گزینه‌ها
        s.pre = QLineEdit(); s.pre.setPlaceholderText("پیشوند نام فایل (اختیاری)"); s.num = QCheckBox("شماره‌گذاری ترتیبی  (001_ ، 002_ ...)")
        s.sub = QLineEdit(); s.sub.setPlaceholderText("نام پوشه‌ی جدید برای این دسته (اختیاری)")
        s.skip = QCheckBox("نادیده گرفتن لینک‌هایی که قبلاً در لیست هستند"); s.skip.setChecked(bool(S["lk_skip"]))
        gn = QGroupBox("نام‌گذاری و گزینه‌ها"); nl = QVBoxLayout(gn); [nl.addWidget(x) for x in (s.pre, s.num, s.sub, s.skip)]
        # ── مسیر ذخیره
        s.r1 = QRadioButton("هر فایل در گروه مربوط به خود"); s.r1.setChecked(True)
        s.r2 = QRadioButton("همه فایلها در یک گروه"); s.gc = QComboBox(); s.gc.addItems(GR)
        s.r3 = QRadioButton("همه فایلها در یک مسیر"); s.dp = QLineEdit(S["dir"]); bb = QPushButton("جستجو...")
        bb.clicked.connect(lambda: s.dp.setText(QFileDialog.getExistingDirectory(s, "پوشه", s.dp.text()) or s.dp.text()))
        s.bg = QButtonGroup(s); [s.bg.addButton(x) for x in (s.r1, s.r2, s.r3)]
        gb = QGroupBox("ذخیره در"); gl = QGridLayout(gb); gl.addWidget(s.r1, 0, 0, 1, 3); gl.addWidget(s.r2, 1, 0); gl.addWidget(s.gc, 1, 1, 1, 2)
        gl.addWidget(s.r3, 2, 0); gl.addWidget(s.dp, 2, 1); gl.addWidget(bb, 2, 2)
        ok, no = QPushButton("تأیید"), QPushButton("انصراف"); ok.setObjectName("primary"); ok.clicked.connect(s.accept); no.clicked.connect(s.reject)
        bt = QHBoxLayout(); [bt.addWidget(x) for x in (no, ok)]; bt.addStretch(); bt.addWidget(s.cnt)
        bar = QHBoxLayout(); [bar.addWidget(x) for x in (ma, mu, mi)]; bar.addStretch()
        v = QVBoxLayout(s); v.addWidget(QLabel(f"{len(urls)} لینک پیدا شد. فایل‌های دلخواه را علامت بزنید، مقصد را انتخاب کنید و تأیید کنید.")); v.addLayout(fr); v.addLayout(bar); v.addWidget(s.t, 1)
        mid = QHBoxLayout(); mid.addWidget(gq, 1); mid.addWidget(gn, 1); v.addLayout(mid); v.addWidget(gb); v.addLayout(bt)
        s.upd_cnt(); s.info.connect(s.on_info); threading.Thread(target=s.work, daemon=True).start()
    def qchg(s):
        q = next((q for q in S["queues"] if q["name"] == s.qc.currentText()), None); s.qp.setValue(q["parallel"] if q else 1)
    def dchg(s, *_):
        on = s.d_q.isChecked(); [w.setEnabled(on) for w in (s.qc, s.qp, s.qpl, s.qs)]
    def work(s):
        for i, u in enumerate(s.urls[:300]):
            try: s.info.emit(i, sniff(u))
            except RuntimeError: return
    def on_info(s, i, d):
        if i < s.t.rowCount(): s.sz[i] = d["size"]; s.t.item(i, 2).setText(fs(d["size"]) or ("خطا" if not d["ok"] else "؟"))
    def vis(s): return [i for i in range(s.t.rowCount()) if not s.t.isRowHidden(i)]
    def apply_filter(s):
        q = s.flt.text().strip().lower(); e_ = s.ext.currentData()
        for i in range(s.t.rowCount()):
            ok = (not q or q in s.t.item(i, 0).text().lower() or q in s.urls[i].lower()) and (not e_ or (s.exts[i] or "-") == e_)
            s.t.setRowHidden(i, not ok)
        s.upd_cnt()
    def mark(s, mode):  # فقط روی ردیف‌های نمایان‌شده اثر می‌گذارد
        s.t.blockSignals(True)
        for i in s.vis():
            it = s.t.item(i, 0); c = it.checkState() == Qt.CheckState.Checked
            it.setCheckState(Qt.CheckState.Checked if (mode == 1 or (mode == 2 and not c)) else Qt.CheckState.Unchecked)
        s.t.blockSignals(False); s.upd_cnt()
    def upd_cnt(s, *_):
        v = s.vis(); sel = [i for i in v if s.t.item(i, 0).checkState() == Qt.CheckState.Checked]
        known = [s.sz[i] for i in sel if s.sz.get(i, -1) > 0]; unk = len(sel) - len(known)
        s.cnt.setText(fd(f"✔ {len(sel)} از {len(v)} فایل انتخاب شده   •   حجم کل ≈ {fs(sum(known)) or '0 B'}" + (f"  (+ {unk} نامشخص)" if unk else "")))
    def chosen(s):
        out = []; k = 0; pre = s.pre.text().strip(); sub = clean(s.sub.text().strip()) if s.sub.text().strip() else ""
        for i, u in enumerate(s.urls):
            it = s.t.item(i, 0)
            if s.t.isRowHidden(i) or it.checkState() != Qt.CheckState.Checked: continue
            k += 1; n = (f"{k:03d}_" if s.num.isChecked() else "") + pre + it.text()
            if s.r3.isChecked(): g = grp_of(n); d = s.dp.text()
            else: g = s.gc.currentText() if s.r2.isChecked() else grp_of(n); d = gdir(g)
            if sub: d = os.path.join(d, sub)
            out.append((u, os.path.normpath(os.path.join(d, n)), g))
        return out
    def opts(s):
        dest = "queue" if s.d_q.isChecked() else "now" if s.d_now.isChecked() else "list"
        o = dict(dest=dest, queue=s.qc.currentText(), start=s.qs.isChecked(), par=s.qp.value(), skip=s.skip.isChecked())
        S.update(lk_dest=dest, lk_queue=o["queue"], lk_start=o["start"], lk_skip=o["skip"]); save_s(); return o

class LogDialog(GDialog):  # گزارش‌ها (لاگ)
    LV = {"INFO": "ℹ", "WARN": "⚠", "ERROR": "❌"}; RANK = {"INFO": 0, "WARN": 1, "ERROR": 2}
    def __init__(s, p):
        super().__init__(p); s.setWindowTitle("گزارش‌ها (لاگ)"); s.resize(960, 600); s.setWindowIcon(QIcon(logo_pm(32))); s.last = 0
        s.view = QPlainTextEdit(); s.view.setReadOnly(True); s.view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        s.view.setLayoutDirection(Qt.LayoutDirection.LeftToRight); s.view.setFont(QFont("Consolas", 9))
        s.lv = QComboBox(); [s.lv.addItem(a_, b_) for a_, b_ in (("همه‌ی گزارش‌ها", 0), ("هشدارها و خطاها", 1), ("فقط خطاها", 2))]
        s.q = QLineEdit(); s.q.setPlaceholderText("🔍  جستجو در گزارش‌ها ..."); s.q.setClearButtonEnabled(True)
        s.auto = QCheckBox("اسکرول خودکار"); s.auto.setChecked(True); s.cnt = QLabel()
        sv = QPushButton("💾  ذخیره به‌صورت txt"); sv.setObjectName("primary"); cp = QPushButton("📋  کپی همه"); cl = QPushButton("🧹  پاک کردن"); cs = QPushButton("بستن")
        sv.clicked.connect(s.save); cp.clicked.connect(lambda: QApplication.clipboard().setText(s.view.toPlainText())); cl.clicked.connect(s.clear); cs.clicked.connect(s.close)
        top = QHBoxLayout(); top.addWidget(s.lv); top.addWidget(s.q, 1); top.addWidget(s.auto)
        bot = QHBoxLayout(); [bot.addWidget(x) for x in (cs, cl, cp, sv)]; bot.addStretch(); bot.addWidget(s.cnt)
        v = QVBoxLayout(s); v.addLayout(top); v.addWidget(s.view, 1); v.addLayout(bot)
        s.lv.currentIndexChanged.connect(s.rebuild); s.q.textChanged.connect(s.rebuild)
        s.tm = QTimer(s); s.tm.timeout.connect(s.pull); s.tm.start(700); s.rebuild()
    def entries(s):
        with _LL: return list(LOGQ)
    def ok(s, e): return s.RANK[e[2]] >= s.lv.currentData() and (not s.q.text() or s.q.text().lower() in e[3].lower())
    def fmt(s, e): return f"[{e[1]}] {s.LV[e[2]]} {e[2]:<5} {e[3]}"
    def count(s): s.cnt.setText(fd(f"{s.view.blockCount() if s.view.toPlainText() else 0} خط  •  کل: {len(LOGQ)}"))
    def scroll(s):
        if s.auto.isChecked(): sb = s.view.verticalScrollBar(); sb.setValue(sb.maximum())
    def rebuild(s):
        es = s.entries(); s.last = es[-1][0] if es else 0
        s.view.setPlainText("\n".join(s.fmt(e) for e in es if s.ok(e))); s.count(); s.scroll()
    def pull(s):
        new = [e for e in s.entries() if e[0] > s.last]
        if not new: return
        s.last = new[-1][0]
        for e in new:
            if s.ok(e): s.view.appendPlainText(s.fmt(e))
        s.count(); s.scroll()
    def clear(s):
        with _LL: LOGQ.clear()
        log("گزارش‌ها پاک شد"); s.rebuild()
    def save(s):
        fn, _ = QFileDialog.getSaveFileName(s, "ذخیره‌ی گزارش", os.path.join(os.path.expanduser("~"), f"cdm_log_{time.strftime('%Y%m%d_%H%M%S')}.txt"), "Text (*.txt)")
        if not fn: return
        es = s.entries()
        head = [f"CDM log - {time.strftime('%Y-%m-%d %H:%M:%S')}", f"Python {sys.version.split()[0]} | {platform.platform()}",
                f"Theme: {S.get('theme')} | Connections: {S['conn']} | Entries: {len(es)}", "-" * 64]
        try:
            with open(fn, "w", encoding="utf-8-sig") as f: f.write("\n".join(head + [f"[{e[1]}] {e[2]:<5} {e[3]}" for e in es]) + "\n")
            log(f"گزارش در فایل ذخیره شد: {fn}"); QMessageBox.information(s, "ذخیره‌ی گزارش", f"{len(es)} خط در فایل ذخیره شد:\n{fn}")
        except OSError as e: QMessageBox.warning(s, "خطا", str(e))

class BatchDialog(GDialog):  # دانلود گروهی
    def __init__(s, p):
        super().__init__(p); s.setWindowTitle("اضافه نمودن دانلود گروهی"); s.setMinimumWidth(600); s.setWindowIcon(QIcon(logo_pm(32)))
        T = TH(); hdr = QFrame(); hdr.setObjectName("hdr"); hdr.setStyleSheet(f"QFrame#hdr{{background:{T['hdrbg']};border-radius:12px}}")
        hl = QHBoxLayout(hdr); ic = QLabel("🗂"); ic.setStyleSheet("font-size:26pt"); hl.addWidget(ic)
        tx = QLabel("برای ساخت لینک‌های شماره‌دار، به‌جای بخش متغیر آدرس از ستاره (*) استفاده کنید.\nمثال:  https://site.com/files/photo(*).jpg"); tx.setWordWrap(True); hl.addWidget(tx, 1)
        s.tpl = QLineEdit(); s.tpl.setPlaceholderText("https://example.com/files/photo(*).jpg")
        mk = lambda v: (lambda x: (x.setRange(0, 99999), x.setValue(v), x)[2])(QSpinBox())
        s.a, s.b, s.st = mk(1), mk(10), mk(1); s.st.setMinimum(1); s.pad = QSpinBox(); s.pad.setRange(0, 6)
        s.pv = QLabel(); s.pv.setWordWrap(True)
        g = QGridLayout(); g.addWidget(QLabel("🔗  آدرس همراه با *"), 0, 0); g.addWidget(s.tpl, 0, 1, 1, 5)
        g.addWidget(QLabel("از"), 1, 0); g.addWidget(s.a, 1, 1); g.addWidget(QLabel("تا"), 1, 2); g.addWidget(s.b, 1, 3)
        g.addWidget(QLabel("گام"), 1, 4); g.addWidget(s.st, 1, 5); g.addWidget(QLabel("تعداد ارقام (با صفر پر شود)"), 2, 0, 1, 1); g.addWidget(s.pad, 2, 1)
        ok, no = QPushButton("ادامه ▶"), QPushButton("انصراف"); ok.setObjectName("primary"); ok.clicked.connect(s.go); no.clicked.connect(s.reject)
        h = QHBoxLayout(); h.addWidget(no); h.addWidget(ok); h.addStretch()
        v = QVBoxLayout(s); v.addWidget(hdr); v.addLayout(g); v.addWidget(QLabel("پیش‌نمایش:")); v.addWidget(s.pv); v.addLayout(h)
        s.tpl.textChanged.connect(s.pre); [x.valueChanged.connect(s.pre) for x in (s.a, s.b, s.st, s.pad)]; s.pre()
    def urls(s):
        t = s.tpl.text().strip()
        if "*" not in t: return []
        return [t.replace("*", str(i).zfill(s.pad.value())) for i in range(s.a.value(), s.b.value() + 1, s.st.value())][:1000]
    def pre(s):
        u = s.urls(); s.pv.setText("آدرس باید شامل * باشد." if not u else "\n".join(u[:3]) + (f"\n... ({len(u)} لینک)" if len(u) > 3 else ""))
    def go(s):
        if s.urls(): s.accept()

class LinkParser(HTMLParser):
    def __init__(s): super().__init__(); s.l = []
    def handle_starttag(s, tag, a):
        for k, v in a:
            if k in ("href", "src", "data-src") and v: s.l.append(v)

class GrabberDialog(GDialog):  # گربر
    prog = pyqtSignal(str); fin = pyqtSignal(list)
    def __init__(s, p):
        super().__init__(p); s.setWindowTitle("اجرای گربر (Grabber)"); s.setMinimumWidth(620); s.found = []; s.stopf = False
        s.setWindowIcon(QIcon(logo_pm(32))); T = TH()
        hdr = QFrame(); hdr.setObjectName("hdr"); hdr.setStyleSheet(f"QFrame#hdr{{background:{T['hdrbg']};border-radius:12px}}")
        hl = QHBoxLayout(hdr); ic = QLabel("🕷"); ic.setStyleSheet("font-size:26pt"); hl.addWidget(ic)
        tx = QLabel("گربر صفحه یا سایت را می‌گردد و همه فایل‌های قابل دانلود را برای شما پیدا می‌کند."); tx.setWordWrap(True); hl.addWidget(tx, 1)
        s.url = QLineEdit(); s.url.setPlaceholderText("https://example.com/downloads/")
        s.dep = QSpinBox(); s.dep.setRange(1, 3); s.same = QCheckBox("فقط همین دامنه"); s.same.setChecked(True)
        s.ext = QLineEdit("zip rar 7z iso exe msi mp4 mkv avi mp3 flac pdf jpg png gif"); s.allf = QCheckBox("همه فایل‌ها (هر چیزی که صفحه وب نیست)")
        s.st = QLabel(""); s.pb = QProgressBar(); s.pb.setRange(0, 0); s.pb.hide()
        g = QGridLayout(); g.addWidget(QLabel("🌐  آدرس شروع"), 0, 0); g.addWidget(s.url, 0, 1, 1, 3)
        g.addWidget(QLabel("🔎  عمق جستجو"), 1, 0); g.addWidget(s.dep, 1, 1); g.addWidget(s.same, 1, 2)
        g.addWidget(QLabel("📦  پسوندها"), 2, 0); g.addWidget(s.ext, 2, 1, 1, 3); g.addWidget(s.allf, 3, 1, 1, 3)
        s.go = QPushButton("🔎  شروع جستجو"); s.go.setObjectName("primary"); s.stp = QPushButton("ایست"); no = QPushButton("انصراف")
        s.go.clicked.connect(s.start); s.stp.clicked.connect(lambda: setattr(s, "stopf", True)); no.clicked.connect(s.reject); s.stp.setEnabled(False)
        h = QHBoxLayout(); [h.addWidget(x) for x in (no, s.stp, s.go)]; h.addStretch()
        v = QVBoxLayout(s); v.addWidget(hdr); v.addLayout(g); v.addWidget(s.st); v.addWidget(s.pb); v.addLayout(h)
        s.prog.connect(s.st.setText); s.fin.connect(s.finish)
    def start(s):
        u = s.url.text().strip()
        if not u.startswith("http"): s.st.setText("⚠ آدرس معتبر وارد کنید."); return
        ex = {x for x in re.split(r"[\s,;]+", s.ext.text().lower()) if x}; s.stopf = False
        s.go.setEnabled(False); s.stp.setEnabled(True); s.pb.show()
        threading.Thread(target=s.crawl, args=(u, s.dep.value(), s.same.isChecked(), ex, s.allf.isChecked()), daemon=True).start()
    def crawl(s, start, depth, same, exts, allf):
        host = urlparse(start).netloc; seen = {start}; q = [(start, 0)]; found = []; n = 0; he = {"", "html", "htm", "php", "asp", "aspx", "jsp"}
        while q and not s.stopf and n < 40:
            u, d = q.pop(0); n += 1; s.prog.emit(f"⏳ صفحه {n}: {u[:70]}   |   فایل‌های یافت‌شده: {len(found)}")
            try:
                r = rget(u, headers=ua(), timeout=10)
                if "html" not in r.headers.get("content-type", ""): continue
                ps = LinkParser(); ps.feed(r.text)
            except Exception: continue
            for l in ps.l:
                l = urljoin(u, l.split("#")[0])
                if not l.startswith("http") or l in seen: continue
                seen.add(l); e = os.path.splitext(urlparse(l).path)[1].lstrip(".").lower()
                if e in exts or (allf and e not in he): found.append(l)
                elif e in he and d + 1 < depth and (not same or urlparse(l).netloc == host): q.append((l, d + 1))
        s.fin.emit(found)
    def finish(s, f):
        s.pb.hide(); s.go.setEnabled(True); s.stp.setEnabled(False)
        if f: s.found = f; s.accept()
        else: s.st.setText("هیچ فایلی پیدا نشد. پسوندها یا عمق جستجو را تغییر دهید.")
    def done(s, c): s.stopf = True; super().done(c)

class DropBox(QWidget):  # سبد پرتاب
    def __init__(s, m):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        s.m, s.hov, s.off, s.pm = m, False, None, logo_pm(52)
        s.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); s.setAcceptDrops(True); s.setFixedSize(84, 84)
        s.setToolTip("سبد پرتاب CDM\nلینک را اینجا رها کنید\nدابل‌کلیک: نمایش پنجره اصلی")
    def paintEvent(s, e):
        p = QPainter(s); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(0, 102, 255, 80 if s.hov else 40)); p.setPen(QColor(0, 102, 255, 220 if s.hov else 130))
        p.drawEllipse(3, 3, 78, 78); p.drawPixmap(16, 16, s.pm)
    def dragEnterEvent(s, e):
        if e.mimeData().hasText() or e.mimeData().hasUrls(): s.hov = True; s.update(); e.acceptProposedAction()
    def dragLeaveEvent(s, e): s.hov = False; s.update()
    def dropEvent(s, e):
        s.hov = False; s.update(); md = e.mimeData()
        u = urls_in(md.text()) or [x.toString() for x in md.urls() if x.scheme().startswith("http")]
        if len(u) == 1: QTimer.singleShot(0, lambda: s.m.add({"url": u[0]}))
        elif u: QTimer.singleShot(0, lambda: s.m.add_links(u))
    def mousePressEvent(s, e): s.off = e.position().toPoint()
    def mouseMoveEvent(s, e):
        if s.off is not None and e.buttons() & Qt.MouseButton.LeftButton: s.move(e.globalPosition().toPoint() - s.off)
    def mouseDoubleClickEvent(s, e): s.m.showNormal(); s.m.raise_(); s.m.activateWindow()

GREEN = "cdmlogo_1.png" if os.path.exists(os.path.join(HERE, "cdmlogo_1.png")) else "cdmlogo.png"
STAT = {"light": "#0a3ccc", "dark": "#6aa9ff", "ocean": "#bfeaff", "desert": "#ffe0a0", "sunset": "#0a3ccc", "neon": "#00e5ff", "forest": "#d9f99d", "paper": "#0a3ccc", "retro": "#000080", "terminal": "#35ff6b", "facebook": "#1877f2", "pinterest": "#e60023", "instagram": "#c13584", "whatsapp": "#008069", "arabic": "#e6c35c", "iranian": "#1e3a8a", "roman": "#7a1313"}
def icon_of(fn): return QIcon(os.path.join(HERE, fn))
def dim_icon(fn):
    pm = QPixmap(os.path.join(HERE, fn))
    if pm.isNull(): return QIcon()
    o = QPixmap(pm.size()); o.fill(Qt.GlobalColor.transparent); p = QPainter(o); p.setOpacity(.5); p.drawPixmap(0, 0, pm); p.end(); return QIcon(o)
def fs3(n):
    if n < 0: return ""
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB": return f"{n:.3f} {u}" if u != "B" else f"{int(n)} B"
        n /= 1024

class ElideLabel(QLabel):
    def __init__(s, t=""):
        super().__init__(); s.full = t; s.setMinimumWidth(10); s.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred); s.setToolTip(t); s.upd()
    def resizeEvent(s, e): s.upd(); super().resizeEvent(e)
    def upd(s): s.setText(s.fontMetrics().elidedText(s.full, Qt.TextElideMode.ElideRight, max(s.width() - 4, 10)))

class SegBar(QWidget):  # نوار نقاط شروع و دانلود به ترتیب اتصال
    def __init__(s, j): super().__init__(); s.j = j; s.setFixedHeight(16)
    def paintEvent(s, e):
        p = QPainter(s); h = s.height(); W = s.width() - 2; p.fillRect(s.rect(), QColor("#e4e4f4")); sz = s.j.size
        if sz > 0:
            for g in list(s.j.segs):
                x = 1 + int(g[0] / sz * W); w = int(g[2] / sz * W)
                p.fillRect(x, 0, 1, h, QColor("#202020"))
                if w > 0:
                    gr = QLinearGradient(0, 0, 0, h); gr.setColorAt(0, QColor("#8fa8f7")); gr.setColorAt(.5, QColor("#1f3fbf")); gr.setColorAt(1, QColor("#8fa8f7"))
                    p.fillRect(x, 1, w, h - 2, gr)
                if not s.j.fin(g): p.fillRect(x + w, 0, 2, h, QColor("#e01010"))
        p.setPen(QColor("#7a7a7a")); p.drawRect(s.rect().adjusted(0, 0, -1, -1))

class ProgDialog(GDialog):  # پنجره وضعیت دانلود (مثل IDM)
    def __init__(s, p, j):
        super().__init__(p); s.j = j; s.fired = False; s.pulse = False; j.dlg = s
        s.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        fl = (Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint |
                         Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        if S["prog_top"]: fl |= Qt.WindowType.WindowStaysOnTopHint
        s.setWindowFlags(fl)
        s.setWindowIcon(icon_of(GREEN)); s.setMinimumWidth(1104); sc = STAT.get(S.get("theme"), "#0a3ccc")
        tabs = QTabWidget(); tabs.setMinimumWidth(1080); t1 = QWidget(); v1 = QVBoxLayout(t1); s.u = ElideLabel(j.url); v1.addWidget(s.u)
        s.L = {k: QLabel() for k in ("وضعیت", "حجم فایل", "حجم دانلود شده", "سرعت دانلود", "زمان باقیمانده", "قابلیت ایست")}
        s.L["وضعیت"].setStyleSheet(f"color:{sc}")
        h0 = QHBoxLayout(); h0.addWidget(QLabel("وضعیت:")); h0.addSpacing(22); h0.addWidget(s.L["وضعیت"]); h0.addStretch(); v1.addLayout(h0)
        g = QGridLayout(); g.setColumnMinimumWidth(0, 108); g.setHorizontalSpacing(4); g.setVerticalSpacing(4)
        for i, k in enumerate(list(s.L)[1:]): g.addWidget(QLabel(k), i, 0); g.addWidget(s.L[k], i, 1)
        g.setColumnStretch(2, 1); v1.addLayout(g); tabs.addTab(t1, "وضعیت دانلود")
        t2 = QWidget(); l2 = QVBoxLayout(t2); s.lim = QCheckBox("محدود کردن سرعت (KB/s)"); s.sp = QSpinBox()
        s.sp.setRange(1, 1000000); s.sp.setValue(500); l2.addWidget(s.lim); l2.addWidget(s.sp); l2.addStretch(); tabs.addTab(t2, "محدود کننده سرعت")
        t3 = QWidget(); l3 = QVBoxLayout(t3); s.cl = QCheckBox("بستن این پنجره پس از اتمام دانلود"); s.cl.setChecked(bool(S["close_prog"]))
        s.of = QCheckBox("باز کردن فایل پس از اتمام دانلود"); s.od = QCheckBox("باز کردن پوشه فایل پس از اتمام دانلود")
        [l3.addWidget(x) for x in (s.cl, s.of, s.od)]; l3.addStretch(); tabs.addTab(t3, "گزینه هاي اتمام دانلود")
        s.bar = QProgressBar(); s.bar.setRange(0, 10000); s.bar.setTextVisible(False); s.bar.setFixedHeight(16)
        s.bar.setStyleSheet("QProgressBar{border:1px solid #8a8a8a;background:#e9e9e9;border-radius:0}"
                            "QProgressBar::chunk{border-radius:0;background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #35b44f,stop:1 #0f7a24)}")
        s.hb = QPushButton("پنهان کردن جزئیات <<"); s.st = QPushButton("ایست"); ca = QPushButton("انصراف")
        s.hb.setMinimumWidth(135); [x.setMinimumWidth(82) for x in (s.st, ca)]
        hr = QHBoxLayout(); hr.addWidget(s.hb); hr.addStretch(); hr.addWidget(s.st); hr.addSpacing(14); hr.addWidget(ca)
        s.cap = QLabel("نقاط شروع و دانلود به ترتیب اتصال"); s.cap.setAlignment(Qt.AlignmentFlag.AlignCenter); s.seg = SegBar(j)
        s.tb = QTableWidget(0, 3); s.tb.setHorizontalHeaderLabels(["ش.", "دانلود شده", "اطلاعات"]); s.tb.verticalHeader().hide()
        s.tb.verticalHeader().setDefaultSectionSize(19); s.tb.setShowGrid(False); s.tb.setFixedHeight(144); s.tb.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        s.tb.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection); s.tb.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        s.tb.horizontalHeader().setStretchLastSection(True); s.tb.setColumnWidth(0, 40); s.tb.setColumnWidth(1, 110)
        s.tb.setStyleSheet("QTableWidget{background:#ffffff;color:#000;border:1px solid #8a8a8a;border-radius:0}"
                           "QHeaderView::section{background:#f6f6f6;color:#000;border:none;border-right:1px solid #d4d4d4;border-bottom:1px solid #d4d4d4;padding:2px 5px}")
        v = QVBoxLayout(s); v.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize); v.setSpacing(8)
        for w in (tabs, s.bar): v.addWidget(w)
        v.addLayout(hr); v.addWidget(s.cap); v.addWidget(s.seg); v.addWidget(s.tb)
        s.hb.clicked.connect(s.tog); s.st.clicked.connect(s.toggle_run); ca.clicked.connect(lambda: (j.halt(), s.close()))
        s.gi, s.di = icon_of(GREEN), dim_icon(GREEN)  # آیکون جداگانه در ناحیه اعلان (کنار آیکون اصلی)
        s.tray = QSystemTrayIcon(s.gi, s); mn = QMenu(s)
        mn.addAction("نمایش پنجره", s.from_tray); mn.addAction("ایست / ادامه", s.toggle_run); mn.addAction("انصراف", lambda: (j.halt(), s.close()))
        s.tray.setContextMenu(mn); s.tray.activated.connect(lambda r: s.from_tray() if r in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick) else None)
        s.k = 0; s.tm = QTimer(s); s.tm.timeout.connect(s.step); s.tm.start(40); s.tick(); s.fast()
    def step(s):
        s.fast(); s.k += 1
        if s.k % 12 == 0: s.tick()
    def fast(s):  # ~۲۵ بار در ثانیه: نوار، حجم دانلودشده، درصد و سرعت به‌صورت نرم
        j = s.j; vd = j.smooth(); pc = vd / j.size * 100 if j.size > 0 else 0
        s.bar.setValue(int(pc * 100)); s.L["حجم دانلود شده"].setText(f"{fs3(vd)} ( {pc:.2f} % )")
        s.L["سرعت دانلود"].setText(f"{fs3(j.speed)}/sec" if j.running else ""); s.seg.update()
    def toggle_run(s):
        if s.j.running: s.j.halt()
        elif not s.j.finished: s.j.start()
    def tog(s):
        v = not s.tb.isVisible(); [w.setVisible(v) for w in (s.tb, s.seg, s.cap)]
        s.hb.setText("🔼  پنهان کردن جزئیات <<" if v else "🔽  نمایش جزئیات >>")
    def changeEvent(s, e):
        if e.type() == QEvent.Type.WindowStateChange and QSystemTrayIcon.isSystemTrayAvailable():
            s.tray.show() if s.isMinimized() else s.tray.hide()  # پنجره در تسک‌بار می‌ماند + آیکون سبز کنار آیکون اصلی
        super().changeEvent(e)
    def from_tray(s): s.tray.hide(); s.showNormal(); s.raise_(); s.activateWindow()
    def done(s, r):
        if s.j.running and not s.j.finished: s.j.hidewin = True
        s.tm.stop(); s.tray.hide(); s.j.dlg = None; super().done(r)
    def tick(s):
        j = s.j; j.limit = s.sp.value() if s.lim.isChecked() else 0; pc = j.done / j.size * 100 if j.size > 0 else 0
        s.setWindowTitle(f"{int(pc)}% {j.name}" if j.size > 0 else j.name); s.L["وضعیت"].setText(j.status + (f" ({j.msg})" if j.msg else ""))
        s.L["حجم فایل"].setText(fs3(j.size) or "نامشخص")
        s.L["زمان باقیمانده"].setText(ft((j.size - j.done) / j.speed) if j.running and j.speed > 0 and j.size > 0 else "")
        s.L["قابلیت ایست"].setText("دارد" if len(j.segs) > 1 or j.hls else "ندارد")
        s.st.setText("⏸  ایست" if j.running or j.finished else "▶  ادامه"); s.st.setEnabled(not j.finished)
        s.tb.setRowCount(len(j.segs))
        for i, g in enumerate(j.segs):
            fin = j.fin(g)
            for c, tx in enumerate((str(i + 1), fs3(g[2]), "تکمیل شد" if fin else ("در حال دریافت..." if j.running else "متوقف"))):
                it = QTableWidgetItem(tx); it.setBackground(QColor("#dcdcdc" if fin else "#bfb0bf")); it.setForeground(QColor("#000000")); s.tb.setItem(i, c, it)
        if s.tray.isVisible():
            s.tray.setToolTip(f"{int(pc)}% {j.name}\n{fs3(j.speed)}/sec" if j.running else f"{int(pc)}% {j.name}")
            s.pulse = not s.pulse; s.tray.setIcon(s.di if (s.pulse and j.running and S["pulse"]) else s.gi)
        if j.finished and not s.fired:
            s.fired = True
            if s.of.isChecked(): QDesktopServices.openUrl(QUrl.fromLocalFile(j.path))
            if s.od.isChecked(): reveal(j.path)
            if s.cl.isChecked(): s.close()

class SchedDialog(GDialog):  # زمان بند
    DAYS = [("شنبه", 5), ("یکشنبه", 6), ("دوشنبه", 0), ("سه شنبه", 1), ("چهارشنبه", 2), ("پنج شنبه", 3), ("جمعه", 4)]
    def __init__(s, m):
        super().__init__(m); s.m, s.cur, s.q = m, None, []; s.setWindowTitle("زمان بند"); s.resize(700, 580)
        P = QStyle.StandardPixmap; st = s.style()
        def H(*ws):
            h = QHBoxLayout()
            for w in ws: h.addStretch() if w is None else h.addWidget(w)
            return h
        def tm(): x = QTimeEdit(); x.setDisplayFormat("h:mm:ss AP"); x.setMinimumWidth(110); return x
        s.lst = QListWidget(); s.lst.setFixedWidth(190); nb, db = QPushButton("صف جدید"), QPushButton("حذف")
        s.ttl = QLabel(); s.ttl.setAlignment(Qt.AlignmentFlag.AlignCenter); s.ttl.setStyleSheet("font-weight:bold")
        tabs = QTabWidget(); t1 = QWidget(); v = QVBoxLayout(t1)
        s.once = QRadioButton("دانلود یکباره"); s.once.setChecked(True); sy = QRadioButton("سینک کردن متناوب"); sy.setEnabled(False)
        s.g1 = QButtonGroup(s); s.g1.addButton(s.once); s.g1.addButton(sy)
        s.wst = QCheckBox("دانلودها همراه با شروع اجرای CDM آغاز شوند")
        s.son = QCheckBox("زمان شروع دانلود:"); s.stm = tm()
        s.rdt = QRadioButton("یکبار در تاریخ:"); s.dt = QDateEdit(QDate.currentDate()); s.dt.setCalendarPopup(True)
        s.dt.setDisplayFormat("dddd , MMMM d, yyyy"); s.rdy = QRadioButton("روزانه")
        s.g2 = QButtonGroup(s); s.g2.addButton(s.rdt); s.g2.addButton(s.rdy)
        gd = QGridLayout(); s.dc = {}
        for i, (n, w) in enumerate(s.DAYS): c = QCheckBox(n); s.dc[w] = c; gd.addWidget(c, i // 3, i % 3)
        s.pon = QCheckBox("قطع دانلود در زمان:"); s.ptm = tm()
        s.ron = QCheckBox("تعداد دفعات سعی مجدد برای فایلهایی که با خطا مواجه میشوند:"); s.rsp = QSpinBox(); s.rsp.setRange(1, 99)
        s.oon = QCheckBox("فایل زیر بعد از اتمام دانلود باز شود:"); s.ope = QLineEdit(); ob = QPushButton("...")
        ob.setFixedWidth(30); ob.clicked.connect(lambda: s.ope.setText(QFileDialog.getOpenFileName(s)[0] or s.ope.text()))
        s.eon = QCheckBox("بعد از اتمام دانلودها، CDM را ببند")
        s.hon = QCheckBox("بعد از اتمام دانلودها، کامپیوتر را خاموش کن"); s.hm = QComboBox(); s.hm.addItems(["Shut down", "Sleep", "Hibernate", "Restart"])
        s.fon = QCheckBox("برنامه های در حال اجرا را « مجبور » به بستن کن")
        for w in (H(s.once, sy), H(s.wst)): v.addLayout(w)
        v.addLayout(H(s.son, s.stm, None)); v.addLayout(H(s.rdt, s.dt, None)); v.addLayout(H(s.rdy)); v.addLayout(gd)
        v.addLayout(H(s.pon, s.ptm, None)); v.addLayout(H(s.ron, s.rsp, None)); v.addLayout(H(s.oon, s.ope, ob))
        v.addWidget(s.eon); v.addLayout(H(s.hon, s.hm, None)); v.addWidget(s.fon); v.addStretch(); tabs.addTab(t1, "زمان بندی")
        t2 = QWidget(); v2 = QVBoxLayout(t2); s.par = QSpinBox(); s.par.setRange(1, 16)
        v2.addLayout(H(QLabel("دانلود همزمان"), s.par, QLabel("فایل"), None))
        s.tb = QTableWidget(0, 4); s.tb.setHorizontalHeaderLabels(["نام فایل", "سایز", "وضعیت", "زمان باقیمانده"]); s.tb.verticalHeader().hide()
        s.tb.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); s.tb.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        s.tb.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); s.tb.horizontalHeader().setStretchLastSection(True); s.tb.setColumnWidth(0, 260)
        v2.addWidget(s.tb); bs = []
        for ic, f in ((("⬇", "#5eb0ff", "#1a62d6"), lambda: s.move(1)), (("⬆", "#69f0ae", "#00a152"), lambda: s.move(-1)), (("✖", "#ff8a80", "#d32f2f"), s.rem)):
            b = QPushButton(); b.setIcon(gicon(*ic, 36)); b.clicked.connect(f); bs.append(b)
        v2.addLayout(H(*bs, None)); tabs.addTab(t2, "فایلهای موجود در صف")
        right = QVBoxLayout(); right.addWidget(s.ttl); right.addWidget(tabs)
        left = QVBoxLayout(); left.addWidget(QLabel("صفها")); left.addWidget(s.lst); left.addLayout(H(nb, db))
        top = QHBoxLayout(); top.addLayout(right, 1); top.addLayout(left)
        bt = {k: QPushButton(k) for k in ("بستن", "راهنما", "اجرا", "شروع", "توقف")}; bt["اجرا"].setEnabled(False)
        bt["بستن"].clicked.connect(s.accept); bt["شروع"].clicked.connect(lambda: s.run(True)); bt["توقف"].clicked.connect(lambda: s.run(False))
        bt["راهنما"].clicked.connect(lambda: QMessageBox.information(s, "راهنما", "برای افزودن فایل به صف، روی فایل راست‌کلیک کنید و «افزودن به صف» را بزنید، یا در پنجره افزودن «بعداً دانلود شود» را انتخاب کنید."))
        bot = QHBoxLayout()
        for k in ("بستن", "راهنما", "اجرا"): bot.addWidget(bt[k])
        bot.addStretch(); bot.addWidget(bt["توقف"]); bot.addWidget(bt["شروع"])
        l = QVBoxLayout(s); l.addLayout(top); l.addLayout(bot)
        for q in S["queues"]: s.lst.addItem(QListWidgetItem(gicon("🗓", "#ffd54f", "#f9a825", 32), q["name"]))
        s.lst.currentRowChanged.connect(s.pick); nb.clicked.connect(s.new); db.clicked.connect(s.delq); s.lst.setCurrentRow(0)
        s.tm = QTimer(s); s.tm.timeout.connect(s.fill); s.tm.start(1000)
    def pick(s, i):
        s.apply()
        if i >= 0: s.load(S["queues"][i])
    def load(s, q):
        s.cur = q; s.ttl.setText(q["name"]); s.wst.setChecked(q["with_start"]); s.son.setChecked(q["start_on"])
        s.stm.setTime(QTime.fromString(q["start_time"], "HH:mm")); (s.rdt if q["mode"] == "date" else s.rdy).setChecked(True)
        s.dt.setDate(QDate.fromString(q["date"], "yyyy-MM-dd") if q["date"] else QDate.currentDate())
        for w, c in s.dc.items(): c.setChecked(w in q["days"])
        s.pon.setChecked(q["stop_on"]); s.ptm.setTime(QTime.fromString(q["stop_time"], "HH:mm")); s.ron.setChecked(q["retry_on"])
        s.rsp.setValue(q["retry"]); s.oon.setChecked(q["open_on"]); s.ope.setText(q["open_path"]); s.eon.setChecked(q["exit_on"])
        s.hon.setChecked(q["shut_on"]); s.hm.setCurrentText(q["shut_mode"]); s.fon.setChecked(q["force"]); s.par.setValue(q["parallel"]); s.fill()
    def apply(s):
        if not s.cur: return
        s.cur.update(with_start=s.wst.isChecked(), start_on=s.son.isChecked(), start_time=s.stm.time().toString("HH:mm"),
            mode="date" if s.rdt.isChecked() else "daily", date=s.dt.date().toString("yyyy-MM-dd"),
            days=[w for w, c in s.dc.items() if c.isChecked()], stop_on=s.pon.isChecked(), stop_time=s.ptm.time().toString("HH:mm"),
            retry_on=s.ron.isChecked(), retry=s.rsp.value(), open_on=s.oon.isChecked(), open_path=s.ope.text(), exit_on=s.eon.isChecked(),
            shut_on=s.hon.isChecked(), shut_mode=s.hm.currentText(), force=s.fon.isChecked(), parallel=s.par.value())
    def fill(s):
        q = s.cur
        if not q: return
        s.q = [j for j in s.m.jobs if j.queue == q["name"]]; s.tb.setRowCount(len(s.q))
        for r, j in enumerate(s.q):
            pc = j.done / j.size * 100 if j.size > 0 else 0
            rem = ft((j.size - j.done) / j.speed) if j.running and j.speed > 0 and j.size > 0 else ""
            for c, x in enumerate((j.name, fs(j.size), f"{pc:.2f}%" if j.running else j.status, rem)): s.tb.setItem(r, c, QTableWidgetItem(x))
    def move(s, d):
        r = s.tb.currentRow(); k = r + d
        if r < 0 or not 0 <= k < len(s.q): return
        J = s.m.jobs; a, b = J.index(s.q[r]), J.index(s.q[k]); J[a], J[b] = J[b], J[a]; s.fill(); s.tb.selectRow(k)
    def rem(s):
        r = s.tb.currentRow()
        if 0 <= r < len(s.q): s.q[r].queue = ""; s.fill()
    def new(s):
        n, ok = QInputDialog.getText(s, "صف جدید", "نام صف:")
        if ok and n.strip():
            S["queues"].append(newq(n.strip())); s.lst.addItem(QListWidgetItem(gicon("🗓", "#ffd54f", "#f9a825", 32), n.strip()))
            s.lst.setCurrentRow(len(S["queues"]) - 1)
    def delq(s):
        i = s.lst.currentRow()
        if i <= 0: return
        for j in s.m.jobs:
            if j.queue == S["queues"][i]["name"]: j.queue = ""
        s.cur = None; S["queues"].pop(i); s.lst.takeItem(i); s.lst.setCurrentRow(0)
    def run(s, go):
        s.apply(); (s.m.qstart if go else s.m.qstop)(s.cur["name"])
    def done(s, r): s.apply(); save_s(); s.m.save(); super().done(r)

class SettingsDialog(GDialog):
    def __init__(s, p):
        super().__init__(p); s.setWindowTitle("تنظیمات"); s.setMinimumSize(940, 660); s.setWindowIcon(QIcon(logo_pm(32))); T = TH()
        s.w = {}; s.f0 = S["fsize"]; S["qpar"] = S["queues"][0]["parallel"]
        hdr = QFrame(); hdr.setObjectName("hdr"); hdr.setStyleSheet(f"QFrame#hdr{{background:{T['hdrbg']};border-radius:12px}}")
        lg = QLabel(); lg.setPixmap(gpix("⚙", "#90a4ae", "#455a64", 52)); tt = QLabel("تنظیمات"); tt.setStyleSheet("font-size:16pt;font-weight:bold")
        vt = QVBoxLayout(); vt.addWidget(tt); vt.addWidget(QLabel("ظاهر، دانلود، مرورگر، شبکه و رفتار برنامه را شخصی‌سازی کنید.")); hl = QHBoxLayout(hdr); hl.addWidget(lg); hl.addLayout(vt, 1)
        def chk(k, tx): c = QCheckBox(tx); c.setChecked(bool(S[k])); s.w[k] = c; return c
        def spn(k, lo, hi, suf=""): x = QSpinBox(); x.setRange(lo, hi); x.setValue(int(S[k])); x.setSuffix(suf); s.w[k] = x; return x
        def txt(k, ph=""): x = QLineEdit(str(S[k])); x.setPlaceholderText(ph); s.w[k] = x; return x
        def cmb(k, items):
            x = QComboBox(); [x.addItem(a_, b_) for a_, b_ in items]; x.setCurrentIndex(max(0, x.findData(S[k]))); s.w[k] = x; return x
        tabs = QTabWidget()
        def form(title):
            w_ = QWidget(); f = QFormLayout(w_); f.setVerticalSpacing(11); sa = QScrollArea(); sa.setWidgetResizable(True); sa.setFrameShape(QFrame.Shape.NoFrame)
            sa.setStyleSheet("QScrollArea{background:transparent}QScrollArea>QWidget>QWidget{background:transparent}"); sa.setWidget(w_); tabs.addTab(sa, title); return f
        f = form("🎨 ظاهر"); grid = QGridLayout()
        for i, (k, Tk) in enumerate(THEMES.items()):
            b = QToolButton(); b.setCheckable(True); b.setAutoExclusive(True); b.setChecked(S["theme"] == k); b.setIcon(QIcon(theme_pm(Tk))); b.setIconSize(QSize(132, 84))
            b.setText(Tk["name"]); b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            b.setStyleSheet("QToolButton{border:2px solid transparent;border-radius:14px;padding:6px}QToolButton:checked{border:2px solid #4da3ff;background:rgba(77,163,255,45)}")
            b.clicked.connect(lambda _=False, k=k: s.pick(k)); grid.addWidget(b, i // 5, i % 5)
        f.addRow(grid); fz = spn("fsize", 8, 20, " pt"); fz.valueChanged.connect(s.setfont); f.addRow("🔤  اندازه‌ی فونت برنامه", fz)
        rh = spn("row_h", 0, 80, " px"); rh.setSpecialValueText("خودکار (طبق تم)"); f.addRow("↕  ارتفاع ردیف‌های جدول", rh)
        f.addRow("🧭  نوار بالایی", chk("show_hero", "نمایش نوار بالایی (آمار سرعت و کادر جستجو)"))
        f.addRow("📅  قالب تاریخ", cmb("date_fmt", [("مثل IDM  (Nov 05 04:08:20 2026)", "idm"), ("2026-11-05 04:08", "iso"), ("05/11/2026 04:08", "dmy"), ("فقط ساعت", "time")]))
        f.addRow("📏  واحد حجم", cmb("size_unit", [("خودکار (KB / MB / GB)", "auto"), ("همیشه مگابایت", "MB")]))
        f.addRow("🚀  واحد سرعت", cmb("speed_unit", [("بایت بر ثانیه (MB/s)", "bytes"), ("مگابیت بر ثانیه (Mbps)", "mbit")]))
        f.addRow("🔢  ارقام", chk("fa_digits", "نمایش ارقام فارسی (۱۲۳) در جدول و نشان‌ها"))
        f.addRow("📌  پنجره‌های دانلود", chk("prog_top", "پنجره‌ی وضعیت دانلود همیشه روی بقیه‌ی پنجره‌ها باشد")); f.addRow("✨  آیکون تری", chk("pulse", "آیکون سبز ناحیه‌ی اعلان هنگام دانلود چشمک بزند"))
        f = form("⬇ دانلود")
        dr = txt("dir"); bb = QPushButton("..."); bb.setFixedWidth(44); bb.clicked.connect(lambda: dr.setText(QFileDialog.getExistingDirectory(s, "پوشه", dr.text()) or dr.text()))
        hb = QHBoxLayout(); hb.addWidget(dr, 1); hb.addWidget(bb); f.addRow("📁  پوشه‌ی پیش‌فرض دانلود", hb)
        f.addRow("⚡  تعداد اتصال همزمان برای هر فایل", spn("conn", 1, 32)); f.addRow("📥  تعداد دانلود همزمان صف اصلی", spn("qpar", 1, 16))
        f.addRow("🚦  محدودیت سرعت کل (۰ = نامحدود)", spn("speed", 0, 10000000, " KB/s")); f.addRow("🧩  حداقل حجم هر بخش", spn("minseg", 64, 65536, " KB"))
        nr = QHBoxLayout(); [nr.addWidget(x) for x in (chk("night_on", "فعال"), QLabel("از ساعت"), spn("night_from", 0, 23), QLabel("تا"), spn("night_to", 0, 23), spn("night_kb", 10, 10000000, " KB/s"))]
        f.addRow("🌙  محدودیت سرعت در ساعات مشخص", nr); f.addRow("📦  بافر خواندن داده", spn("buf_kb", 4, 4096, " KB"))
        f.addRow("♻  تعداد تلاش مجدد هنگام خطا", spn("retries", 0, 50)); f.addRow("⏱  مهلت اتصال", spn("timeout", 5, 300, " ثانیه"))
        f.addRow("📛  اگر فایل از قبل وجود داشت", cmb("exists", [("نام جدید بساز  (file (2).zip)", "rename"), ("جایگزین کن", "overwrite")]))
        f.addRow("🗂  پوشه‌ی گروه‌ها", chk("subdirs", "برای هر گروه فایل، پوشه‌ی جدا ساخته شود")); f.addRow("💾  فضای دیسک", chk("prealloc", "فضای فایل از ابتدا رزرو شود"))
        f.addRow("🛡  بررسی فضا", chk("check_space", "قبل از شروع، کافی بودن فضای دیسک بررسی شود")); f.addRow("🧼  نام فایل", chk("name_clean", "نویسه‌های غیرمجاز ویندوز از نام فایل پاک شوند"))
        f.addRow("🕒  دانلودهای جدید", chk("queue_new", "همه‌ی دانلودهای جدید وارد صف اصلی شوند (ترتیبی)"))
        f = form("🔔 اعلان‌ها و پنجره‌ها")
        for k, tx in (("auto_prog", "نمایش خودکار پنجره‌ی وضعیت با شروع هر دانلود"), ("close_prog", "بستن خودکار پنجره‌ی وضعیت پس از اتمام دانلود"),
                      ("notify", "نمایش اعلان هنگام تکمیل دانلود"), ("sound", "پخش صدا هنگام تکمیل دانلود")): f.addRow(chk(k, tx))
        f.addRow("📂  بعد از اتمام دانلود", cmb("after", [("کاری نکن", "none"), ("فایل را باز کن", "file"), ("پوشه‌ی فایل را باز کن", "folder")]))
        f.addRow("🖱  دابل‌کلیک روی فایل تکمیل‌شده", cmb("dbl_action", [("باز کردن فایل", "open"), ("باز کردن پوشه", "folder"), ("نمایش پنجره‌ی وضعیت", "info")]))
        f = form("🧩 مرورگر"); s.st_l = QLabel(); port = getattr(p, "port", None)
        s.st_l.setText(f"✔ سرور افزونه فعال است (پورت {port})" if port else "✖ سرور افزونه راه‌اندازی نشد (همه‌ی پورت‌ها اشغال هستند)"); f.addRow("🔗  وضعیت اتصال افزونه", s.st_l)
        f.addRow("📏  حداقل حجم برای دریافت از مرورگر", spn("cap_min", 0, 100000, " MB")); f.addRow("🚫  پسوندهای نادیده گرفته‌شده", txt("cap_excl", "مثلاً: pdf jpg png"))
        f.addRow(chk("vid_btn", "نمایش دکمه‌ی دانلود CDM روی ویدیوها و کلیپ‌های صفحه‌ی وب"))
        f.addRow("🎬  حداقل حجم ویدیو برای نمایش دکمه", spn("vid_min", 1, 10000, " MB"))
        f.addRow(chk("img_btn", "نمایش دکمه‌ی دانلود CDM روی تصاویر بزرگ صفحه‌ی وب"))
        f.addRow("🖼  حداقل حجم تصویر برای نمایش دکمه", spn("img_min", 1, 1000, " MB"))
        f.addRow(chk("use_cookies", "ارسال کوکی‌های مرورگر همراه دانلود (برای سایت‌های نیازمند ورود)"))
        f.addRow(chk("ask_ext", "نمایش پنجره‌ی تأیید برای دانلودهای مرورگر")); f.addRow(chk("watch_clip", "شناسایی خودکار لینک‌های کپی‌شده"))
        f = form("🌐 شبکه"); f.addRow("🕵  User-Agent (خالی = پیش‌فرض)", txt("ua", "Mozilla/5.0 ...")); f.addRow("🔌  پروکسی", txt("proxy", "http://127.0.0.1:8080"))
        f.addRow("🔒  گواهی SSL", chk("verify_ssl", "گواهی امنیتی سایت‌ها بررسی شود (توصیه می‌شود)"))
        f = form("🖥 سیستم")
        f.addRow(chk("autostart", "اجرای خودکار CDM با روشن شدن ویندوز")); f.addRow(chk("start_min", "شروع برنامه به‌صورت پنهان در ناحیه‌ی اعلان"))
        f.addRow(chk("close_tray", "با بستن پنجره، برنامه در ناحیه‌ی اعلان بماند")); f.addRow(chk("confirm_exit", "تأیید قبل از خروج هنگام وجود دانلود فعال"))
        f.addRow("📜  گزارش‌ها (لاگ)", chk("log_on", "ثبت گزارش‌های برنامه (نمایش ← گزارش‌ها)")); f.addRow(chk("log_file", "ذخیره‌ی خودکار گزارش‌ها در فایل ‎.cdm_log.txt‎ در پوشه‌ی کاربر"))
        cd = spn("clear_days", 0, 3650, " روز"); cd.setSpecialValueText("هرگز"); f.addRow("🧹  حذف خودکار تکمیل‌شده‌ها از لیست بعد از", cd)
        f.addRow("🗑  هنگام حذف از لیست", cmb("del_mode", [("هر بار بپرس", "ask"), ("فایل را هم حذف کن", "delete"), ("فایل را نگه دار", "keep")]))
        ok, no = QPushButton("تأیید"), QPushButton("انصراف"); ok.setObjectName("primary"); ok.clicked.connect(s.accept); no.clicked.connect(s.reject)
        h = QHBoxLayout(); h.addWidget(no); h.addWidget(ok); h.addStretch()
        v = QVBoxLayout(s); v.setSpacing(12); v.addWidget(hdr); v.addWidget(tabs, 1); v.addLayout(h)
    def setfont(s, v): S["fsize"] = v; apply_font()
    def pick(s, k):
        apply_theme(k); save_s(); par = s.parent()
        if hasattr(par, "restyle"): par.restyle()
    def done(s, r):
        if r:
            for k, w in s.w.items():
                S[k] = (w.isChecked() if isinstance(w, QCheckBox) else w.value() if isinstance(w, QSpinBox) else
                        w.text().strip() if isinstance(w, QLineEdit) else w.currentData())
            S["queues"][0]["parallel"] = S["qpar"]
            try: set_autostart(S["autostart"])
            except Exception: pass
        else: S["fsize"] = s.f0; apply_font()
        if r: log("تنظیمات ذخیره شد")
        save_s(); par = s.parent()
        if hasattr(par, "restyle"): par.restyle()
        super().done(r)

class AboutDialog(GDialog):
    def __init__(s, p):
        super().__init__(p); s.setWindowTitle("معرفی CDM"); s.setMinimumWidth(560); s.setWindowIcon(QIcon(logo_pm(32))); T = TH()
        hdr = QFrame(); hdr.setObjectName("hdr"); hdr.setStyleSheet(f"QFrame#hdr{{background:{T['hdrbg']};border-radius:16px}}")
        lg = QLabel(); lg.setPixmap(logo_pm(104)); tt = QLabel("CDM"); tt.setStyleSheet("font-size:28pt;font-weight:bold")
        st = QLabel("مدیر دانلود چندبخشی هوشمند"); st.setStyleSheet("font-size:12pt"); vr = QLabel("نسخه 1.0"); vt = QVBoxLayout(); [vt.addWidget(x) for x in (tt, st, vr)]
        hl = QHBoxLayout(hdr); hl.setContentsMargins(18, 14, 18, 14); hl.addWidget(lg); hl.addLayout(vt, 1)
        v = QVBoxLayout(s); v.setSpacing(10); v.addWidget(hdr)
        for g_, tx in (("⚡", "دانلود چندبخشی تا ۳۲ اتصال همزمان"), ("⏯", "توقف و ادامه‌ی دانلود بدون از دست رفتن اطلاعات"), ("🗓", "زمان‌بند، صف‌ها و خاموشی خودکار"),
                       ("🌐", "افزونه‌ی مرورگر و سبد پرتاب"), ("🕷", "گربر: پیدا کردن همه‌ی فایل‌های یک صفحه"), ("🎨", "پنج تم: اقیانوسی، صحرایی، غروب، روز و شب")):
            r = QHBoxLayout(); ic = QLabel(); ic.setPixmap(gpix(g_, "#5eb0ff", "#1a62d6", 30)); r.addWidget(ic); r.addWidget(QLabel(tx), 1); v.addLayout(r)
        ok = QPushButton("👍  عالیه!"); ok.setObjectName("primary"); ok.clicked.connect(s.accept); h = QHBoxLayout(); h.addWidget(ok); h.addStretch(); v.addLayout(h)

class Main(QMainWindow):
    got = pyqtSignal(dict)
    COLS = ["نام فایل", "ن", "سایز", "وضعیت", "زمان باقیمانده", "سرعت", "آخرین تاریخ دانلود"]
    def __init__(s):
        super().__init__(); s.setWindowTitle("CDM 1.0"); s.resize(1250, 750)
        s.jobs, s.vis, s.flt, s.dl = [], [], "all", {}
        if os.path.exists(os.path.join(HERE, "cdmlogo.png")): s.setWindowIcon(QIcon(os.path.join(HERE, "cdmlogo.png")))
        st = s.style(); P = QStyle.StandardPixmap
        A = lambda t, i, f: (lambda a: (a.triggered.connect(lambda: f()), a)[1])(QAction(gicon(*i), t, s))
        s.a = dict(add=A("آدرس", ("➕", "#3ddc84", "#0e9f4f"), s.add), res=A("ادامه", ("▶", "#5eb0ff", "#1a62d6"), s.resume),
            stp=A("توقف", ("⏹", "#ff9a76", "#e0452c"), s.stop_sel), sta=A("توقف همه", ("✋", "#ffc266", "#f57c00"), s.stop_all),
            dele=A("حذف", ("🗑", "#ff7b7b", "#c62828"), s.delete), delc=A("حذف تکمیلها", ("🧹", "#c4a1ff", "#6a3fd1"), s.del_done),
            set=A("تنظیمات", ("⚙", "#a7b8c2", "#455a64"), s.settings), sch=A("زمان بندی", ("⏰", "#ffe082", "#f9a825"), s.schedule),
            q1=A("آغاز صف", ("📥", "#5ee0ee", "#00838f"), s.start_q), q2=A("توقف صف", ("⏸", "#f8a1c4", "#c2185b"), s.stop_q),
            abt=A("معرفی", ("👍", "#ffd699", "#ef6c00"), s.about))
        tb = QToolBar(); s.tb = tb; tb.setMovable(False); tb.setIconSize(QSize(38, 38)); tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        s.addToolBar(tb)
        for grp_ in (("add",), ("res", "stp", "sta"), ("dele", "delc"), ("set", "sch", "q1", "q2"), ("abt",)):
            [tb.addAction(s.a[k]) for k in grp_]
            if grp_[0] != "abt": tb.addSeparator()
        s.mn = {}; s.drop = DropBox(s)
        m = s.menuBar().addMenu("امور"); s.mn["امور"] = m
        s.ma(m, "اضافه کردن آدرس جدید ...", s.add, "Ctrl+N", ("➕", "#3ddc84", "#0e9f4f")); s.ma(m, "اضافه نمودن دانلود گروهی", s.batch, None, ("🗂", "#5eb0ff", "#1a62d6"))
        s.ma(m, "اضافه کردن لیست لینک از حافظه ویندوز", s.clip_links, "Ctrl+Shift+V", ("📋", "#c4a1ff", "#6a3fd1")); s.ma(m, "اجرای گربر (grabber)", s.grabber, None, ("🕷", "#bfa095", "#5d4037"))
        m.addSeparator(); da = s.ma(m, "نمایش سبد پرتاب", None, None, ("🎯", "#ff9a76", "#e0452c")); da.setCheckable(True); da.toggled.connect(s.toggle_drop); m.addSeparator()
        ex = m.addMenu("استخراج"); ex.setIcon(gicon("📤", "#5ee0ee", "#00838f", 32))
        for tx, k in (("لیست دانلودها (JSON)", "json"), ("جدول دانلودها (CSV)", "csv"), ("فقط لینک‌ها (متن)", "txt")): s.ma(ex, tx, lambda k=k: s.export(k), None, EXI[k])
        im = m.addMenu("وارد کردن"); im.setIcon(gicon("📥", "#3ddc84", "#0e9f4f", 32))
        for tx, k in (("از فایل JSON", "json"), ("از فایل لینک (متن)", "txt")): s.ma(im, tx, lambda k=k: s.imp(k), None, EXI[k])
        m.addSeparator(); s.ma(m, "خروج", s.quit_app, None, ("⏻", "#ff8a80", "#d32f2f"))
        for t, ks in (("فایل", ("add", "set", "delc")), ("دانلودها", ("res", "stp", "sta", "dele", "q1", "q2")),
                      ("نمایش", ()), ("راهنما", ("abt",))):
            m = s.menuBar().addMenu(t); s.mn[t] = m; [m.addAction(s.a[k]) for k in ks]
        s.ma(s.mn["نمایش"], "📜  گزارش‌ها (لاگ)", s.show_log, "Ctrl+L", ("📜", "#90a4ae", "#455a64"))
        ua_ = QAction(gicon("🔄", "#5ee0ee", "#00838f", 32), "بروزرسانی", s); ua_.triggered.connect(lambda _=False: s.update_app()); s.menuBar().addAction(ua_)
        tm = s.mn["نمایش"].addMenu("🎨 تم برنامه"); ag = QActionGroup(s)
        for k, T in THEMES.items():
            a = QAction(swatch(T), T["name"], s); a.setCheckable(True); a.setChecked(S["theme"] == k)
            a.triggered.connect(lambda _=False, k=k: (apply_theme(k), save_s(), s.restyle())); ag.addAction(a); tm.addAction(a)
        s.tree = QTreeWidget(); s.tree.setHeaderHidden(True)
        r = QTreeWidgetItem(["همه دانلودها"]); r.setData(0, Qt.ItemDataRole.UserRole, "all"); s.tree.addTopLevelItem(r)
        for g in list(GR)[:-1]:
            c = QTreeWidgetItem([g]); c.setData(0, Qt.ItemDataRole.UserRole, g); r.addChild(c)
        for t, k in (("ناتمام", "unfin"), ("تکمیل شده", "fin"), ("پروژه های گربر", "none"), ("صفها", "all")):
            i = QTreeWidgetItem([t]); i.setData(0, Qt.ItemDataRole.UserRole, k); s.tree.addTopLevelItem(i)
        r.setExpanded(True); s.tree.setCurrentItem(r)
        s.tree.currentItemChanged.connect(lambda c, _: setattr(s, "flt", c.data(0, Qt.ItemDataRole.UserRole)))
        d = QDockWidget("گروه ها"); s.dock = d; d.setWidget(s.tree); s.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, d)
        s.t = QTableWidget(0, 7); s.t.setHorizontalHeaderLabels(s.COLS); s.t.verticalHeader().hide(); s.t.setShowGrid(False)
        s.t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows); s.t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        hh = s.t.horizontalHeader(); hh.setStretchLastSection(True); [s.t.setColumnWidth(i, w) for i, w in enumerate((380, 44, 95, 175, 130, 95, 170))]
        s.t.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu); s.t.customContextMenuRequested.connect(s.ctx)
        s.t.cellDoubleClicked.connect(s.dbl); s.load()
        s.t.verticalHeader().setDefaultSectionSize(38); s.t.setIconSize(QSize(26, 26)); s.t.setItemDelegateForColumn(3, StatDelegate(s.t, lambda r: s.vis[r] if 0 <= r < len(s.vis) else None)); s.t.setAlternatingRowColors(False)
        s.search = QLineEdit(); s.search.setPlaceholderText("🔍  جستجو در دانلودها ..."); s.search.setClearButtonEnabled(True); s.search.setFixedWidth(290)
        s.hero = QFrame(); s.hero.setObjectName("hero"); hl = QHBoxLayout(s.hero); hl.setContentsMargins(16, 9, 16, 9)
        lg = QLabel(); lg.setPixmap(logo_pm(42)); vt = QVBoxLayout(); vt.setSpacing(0); t1 = QLabel("CDM"); t1.setStyleSheet("font-size:17pt;font-weight:bold")
        vt.addWidget(t1); vt.addWidget(QLabel("مدیریت هوشمند دانلود")); s.chips = [QLabel() for _ in range(3)]
        s.brand = QWidget(); bl = QHBoxLayout(s.brand); bl.setContentsMargins(0, 0, 0, 0); bl.addWidget(lg); bl.addLayout(vt); hl.addWidget(s.brand); hl.addStretch(); [(c.setObjectName("chip"), hl.addWidget(c)) for c in s.chips]; hl.addSpacing(10); hl.addWidget(s.search)
        s.emp = QWidget(); ev = QVBoxLayout(s.emp); ev.addStretch(); e1 = QLabel(); e1.setPixmap(gpix("📥", "#5eb0ff", "#1a62d6", 96)); e1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.e2 = QLabel(); s.e2.setStyleSheet("font-size:15pt;font-weight:bold"); s.e3 = QLabel(); [x.setAlignment(Qt.AlignmentFlag.AlignCenter) for x in (s.e2, s.e3)]
        eb = QPushButton("➕  افزودن آدرس جدید"); eb.setObjectName("primary"); eb.setFixedWidth(230); eb.clicked.connect(lambda: s.add())
        for w_ in (e1, s.e2, s.e3): ev.addWidget(w_)
        ev.addSpacing(8); ev.addWidget(eb, 0, Qt.AlignmentFlag.AlignCenter); ev.addStretch()
        s.stk = QStackedWidget(); s.stk.addWidget(s.t); s.stk.addWidget(s.emp); cw = QWidget(); cl = QVBoxLayout(cw); cl.setContentsMargins(8, 2, 8, 8)
        cl.addWidget(s.hero); cl.addWidget(s.stk, 1); s.setCentralWidget(cw); s.style_tree(); s.restyle()
        s.got.connect(s.from_browser); s.serve()
        QTimer.singleShot(1500, lambda: [s.qstart(q["name"]) for q in S["queues"] if q.get("with_start")])
        s.tray = QSystemTrayIcon(icon_of("cdmlogo.png"), s); s.tray.setToolTip("CDM"); tmn = QMenu(s)
        tmn.addAction("باز کردن CDM", s.pop); tmn.addAction("توقف همه دانلودها", s.stop_all); tmn.addSeparator(); tmn.addAction("خروج", s.quit_app)
        s.tray.setContextMenu(tmn)
        s.tray.activated.connect(lambda r: s.pop() if r in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick) else None)
        s.last_clip = ""; s.clipu = None; QApplication.clipboard().dataChanged.connect(s.clip_changed); s.tray.messageClicked.connect(s.clip_clicked)
        log("برنامه شروع شد — CDM 1.0"); s.tray.show(); s.tm = QTimer(s); s.tm.timeout.connect(s.refresh); s.tm.start(500); s.refresh(); s.ft = QTimer(s); s.ft.timeout.connect(s.fast); s.ft.start(50)
    def sel(s): return [s.vis[i.row()] for i in s.t.selectionModel().selectedRows() if i.row() < len(s.vis)]
    def fast(s):  # بازنقاشی نرم نوار پیشرفت‌ها + به‌روزرسانی سریع سرعت/زمان باقیمانده
        if not s.isVisible() or s.stk.currentIndex() != 0: return
        run = [(r, j) for r, j in enumerate(s.vis) if j.running]
        if not run: return
        s._fk = (getattr(s, "_fk", 0) + 1) % 5
        if s._fk == 0:
            for r, j in run:
                rem = ft((j.size - j.done) / j.speed) if j.speed > 0 and j.size > 0 else ""
                for c, tx in ((4, fd(rem)), (5, fd(fspd(j.speed)))):
                    it = s.t.item(r, c)
                    if it is not None and it.text() != tx: it.setText(tx)
        s.t.viewport().update()
    def pop(s): s.showNormal(); s.raise_(); s.activateWindow()
    def refresh(s):
        s.sched(); s._ac = (getattr(s, "_ac", 0) + 1) % 7200
        if s._ac == 1: s.autoclear()
        for j in s.jobs:
            if j.status != getattr(j, "_ls", None):
                if getattr(j, "_ls", None) is not None: log(f"«{j.name}» ← {j.status}" + (f" ({j.msg})" if j.msg else ""), "ERROR" if j.status == "خطا" else "INFO")
                j._ls = j.status
            if j.finished and not j.notified:
                j.notified = True
                if S["notify"]: s.tray.showMessage("دانلود کامل شد", j.name, QSystemTrayIcon.MessageIcon.Information, 4000)
                if S["sound"]: QApplication.beep()
                if S["after"] == "file": QDesktopServices.openUrl(QUrl.fromLocalFile(j.path))
                elif S["after"] == "folder": reveal(j.path)
            if S["auto_prog"] and j.running and j.dlg is None and not j.hidewin: s.show_prog(j, True)
        n = sum(j.running for j in s.jobs); s.tray.setToolTip(f"CDM — {n} دانلود فعال" if n else "CDM")
        f = s.flt; qt = s.search.text().strip().lower()
        s.vis = [j for j in reversed(s.jobs) if (f == "all" or j.group == f or (f == "unfin" and not j.finished) or (f == "fin" and j.finished)) and (not qt or qt in j.name.lower())]
        s.stk.setCurrentIndex(0 if s.vis else 1)
        if not s.vis:
            s.e2.setText("هنوز دانلودی وجود ندارد" if not s.jobs else "موردی پیدا نشد")
            s.e3.setText("روی «آدرس» بزنید، Ctrl+N را فشار دهید یا لینک را روی سبد پرتاب رها کنید." if not s.jobs else "فیلتر یا عبارت جستجو را تغییر دهید.")
        sp = sum(j.speed for j in s.jobs if j.running)
        s.chips[0].setText(fd(f"⚡  {fspd(sp)}")); s.chips[1].setText(fd(f"⬇  {n} فعال")); s.chips[2].setText(fd(f"✅  {sum(j.finished for j in s.jobs)} کامل"))
        s.t.setRowCount(len(s.vis))
        for r, j in enumerate(s.vis):
            pc = j.done / j.size * 100 if j.size > 0 else 0
            if j.finished: stt, kind, pv = "✅  تکمیل شد", "ok", 100
            elif j.running: stt, kind, pv = (f"⬇  {pc:.1f}%" if j.size > 0 else "⬇  در حال دریافت..."), "run", pc
            elif j.status == "خطا": stt, kind, pv = "❌  خطا", "err", pc
            elif j.status == "یافت نشد": stt, kind, pv = "🔍  یافت نشد", "err", 0
            elif j.queue and not j.paused: stt, kind, pv = "🕒  در صف", "pause", pc
            else: stt, kind, pv = (f"⏸  متوقف  {pc:.0f}%" if pc else "⏸  متوقف"), "pause", pc
            rem = ft((j.size - j.done) / j.speed) if j.running and j.speed > 0 and j.size > 0 else ""
            for c, tx in enumerate((j.name, "", fs(j.size), stt, rem, fspd(j.speed) if j.running else "", fdate(j))):
                it = QTableWidgetItem(fd(tx))
                if c == 0: it.setIcon(fileicon(j.name))
                if c == 1 and j.queue: it.setIcon(gicon("🗓", "#ffe082", "#f9a825", 32)); it.setToolTip(j.queue)
                if c == 3: it.setData(Qt.ItemDataRole.UserRole, pv); it.setData(Qt.ItemDataRole.UserRole + 1, kind)
                s.t.setItem(r, c, it)
        s.upd_tree()
    def restyle(s):  # ظاهر + ساختار رابط بر اساس تم
        T = TH(); q = T.get("q", {}); compact = not T.get("hero", True)
        if compact:   # تم‌های فشرده: نوار بالایی ساده؛ جستجو و آمار همیشه در دسترس می‌مانند
            s.hero.setStyleSheet(f"QFrame#hero{{background:transparent;border:none;border-bottom:1px solid {q.get('BD', '#888')};border-radius:0}}"
                                 f"QLabel#chip{{background:transparent;border:1px solid {q.get('BD', '#888')};border-radius:{q.get('RP', '9px')};padding:2px 10px}}")
            s.hero.layout().setContentsMargins(6, 3, 6, 3)
        else:
            s.hero.setStyleSheet(f"QFrame#hero{{background:{T['hdrbg']};border-radius:14px}}"
                                 f"QLabel#chip{{background:{T['badge']};border-radius:13px;padding:5px 13px;font-weight:bold}}")
            s.hero.layout().setContentsMargins(16, 9, 16, 9)
        s.brand.setVisible(not compact); s.hero.setVisible(bool(S["show_hero"]))
        TB = Qt.ToolButtonStyle; st = {"under": TB.ToolButtonTextUnderIcon, "beside": TB.ToolButtonTextBesideIcon, "icon": TB.ToolButtonIconOnly, "text": TB.ToolButtonTextOnly}[T.get("tb", "under")]
        sz = T.get("tbsize", 38); s.tb.setToolButtonStyle(st); s.tb.setIconSize(QSize(sz, sz))
        TA = Qt.ToolBarArea; ar = {"top": TA.TopToolBarArea, "left": TA.LeftToolBarArea, "bottom": TA.BottomToolBarArea}[T.get("tbpos", "top")]
        if s.toolBarArea(s.tb) != ar: s.removeToolBar(s.tb); s.addToolBar(ar, s.tb); s.tb.show()
        DA = Qt.DockWidgetArea; da = {"right": DA.RightDockWidgetArea, "left": DA.LeftDockWidgetArea}[T.get("dock", "right")]
        if s.dockWidgetArea(s.dock) != da: s.removeDockWidget(s.dock); s.addDockWidget(da, s.dock); s.dock.show()
        rh = S["row_h"] or T.get("rowh", 38); s.t.verticalHeader().setDefaultSectionSize(rh); k_ = max(14, min(26, rh - 8)); s.t.setIconSize(QSize(k_, k_))
    def style_tree(s):
        its = [s.tree.topLevelItem(i) for i in range(s.tree.topLevelItemCount())]; its += [its[0].child(i) for i in range(its[0].childCount())]
        for it in its:
            b = it.text(0); it.setData(0, Qt.ItemDataRole.UserRole + 1, b); it.setSizeHint(0, QSize(0, 32))
            if b in TREEI: it.setIcon(0, gicon(*TREEI[b], 32))
        s.tree.setIconSize(QSize(22, 22)); s.tree_items = its
    def upd_tree(s):
        cn = {"همه دانلودها": len(s.jobs), "ناتمام": sum(not j.finished for j in s.jobs), "تکمیل شده": sum(j.finished for j in s.jobs)}
        for g in GR: cn[g] = sum(j.group == g for j in s.jobs)
        for it in s.tree_items:
            b = it.data(0, Qt.ItemDataRole.UserRole + 1); k = cn.get(b); it.setText(0, f"{b}  ({k})" if k else b)
    def add(s, ext=None):
        ext = ext if isinstance(ext, dict) else {}
        if ext.get("_br") and ext.get("url") and not S["ask_ext"]:
            n = ext.get("filename") or unquote(os.path.basename(urlparse(ext["url"]).path)) or "download"; g = grp_of(n)
            j = Job(ext["url"], s.uniq(os.path.join(gdir(g), n)), g, S["conn"]); log(f"افزودن دانلود (مرورگر): {ext['url']}")
            j.hls = j.hls or bool(ext.get("hls"))
            if ext.get("referer"): j.hdr["Referer"] = ext["referer"]
            if ext.get("cookie"): j.hdr["Cookie"] = ext["cookie"]
            s.jobs.append(j); s.save(); s.start_new(j); return
        if ext: s.showNormal(); s.raise_(); s.activateWindow()
        d = AddDialog(s, ext.get("url") or QApplication.clipboard().text())
        if ext.get("filename"):
            fn = ext["filename"]; d.grp.setCurrentText(grp_of(fn)); d.pth.setCurrentText(os.path.join(gdir(grp_of(fn)), fn)); d.edited = True
        c = d.exec(); u = d.url.text().strip()
        if not c or not u: return
        j = Job(u, s.uniq(d.pth.currentText()), d.grp.currentText(), S["conn"]); log(f"افزودن دانلود: {u}")
        j.hls = j.hls or bool(ext.get("hls"))
        if ext.get("referer"): j.hdr["Referer"] = ext["referer"]
        if ext.get("cookie"): j.hdr["Cookie"] = ext["cookie"]
        s.jobs.append(j); s.save()
        if c == 2: j.queue = S["queues"][0]["name"]
        if c == 1: s.start_new(j); s.show_prog(j) if S["auto_prog"] and not S["queue_new"] else None
    def ma(s, m, text, fn, key=None, ic=None):
        a = QAction(gicon(*ic, 32) if ic else QIcon(), text, s)
        if fn: a.triggered.connect(lambda _=False: fn())
        if key: a.setShortcut(key)
        m.addAction(a); return a
    def toggle_drop(s, on):
        if on: g = QApplication.primaryScreen().availableGeometry(); s.drop.move(g.right() - 110, g.bottom() - 130); s.drop.show()
        else: s.drop.hide()
    def batch(s):
        d = BatchDialog(s)
        if d.exec(): s.add_links(d.urls())
    def clip_links(s):
        u = urls_in(QApplication.clipboard().text())
        if u: s.add_links(u)
        else: QMessageBox.information(s, "حافظه ویندوز", "هیچ لینکی در حافظه (Clipboard) پیدا نشد.\nابتدا لینک‌ها را کپی کنید.")
    def grabber(s):
        d = GrabberDialog(s)
        if d.exec() and d.found: s.add_links(d.found, d.url.text().strip())
    def show_log(s):
        if getattr(s, "logwin", None) is None: s.logwin = LogDialog(s)
        s.logwin.show(); s.logwin.raise_(); s.logwin.activateWindow()
    def add_links(s, urls, referer="", cookie=""):
        if not urls: return
        d = LinksDialog(s, urls)
        if not d.exec(): return
        o = d.opts(); have = {j.url for j in s.jobs}; used = {j.path for j in s.jobs}; made = []; dup = 0
        for u, p, g in d.chosen():
            if o["skip"] and u in have: dup += 1; continue
            p = cpath(p); b, e = os.path.splitext(p); k = 2
            while p in used or (S["exists"] == "rename" and os.path.exists(p)): p = f"{b} ({k}){e}"; k += 1
            used.add(p); j = Job(u, p, g, S["conn"])
            if referer: j.hdr["Referer"] = referer
            if cookie and S["use_cookies"]: j.hdr["Cookie"] = cookie
            s.jobs.append(j); made.append(j)
        if not made:
            if dup: QMessageBox.information(s, "دانلود همه لینکها", f"همه‌ی {dup} لینک انتخاب‌شده از قبل در لیست بودند.")
            return
        qn = o["queue"]; q = s.qget(qn)
        if o["dest"] == "queue" and q:
            q["parallel"] = o["par"]
            for j in made: j.queue = qn
            if o["start"]: s.qstart(qn)
        elif o["dest"] == "now": [j.start() for j in made]
        log(f"{len(made)} لینک از «دانلود همه لینکها» افزوده شد — مقصد: " + {"queue": f"صف «{qn}»", "now": "شروع فوری", "list": "فقط لیست"}[o["dest"]] + (f" ({dup} تکراری رد شد)" if dup else ""))
        s.save(); save_s()
    def export(s, kind):
        f, _ = QFileDialog.getSaveFileName(s, "ذخیره", "cdm_export." + kind)
        if not f: return
        try:
            if kind == "json":
                json.dump([dict(url=j.url, path=j.path, group=j.group, size=j.size, status=j.status, date=j.date) for j in s.jobs],
                          open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            elif kind == "csv":
                with open(f, "w", newline="", encoding="utf-8-sig") as fh:
                    w = csv.writer(fh); w.writerow(["name", "url", "size", "status", "date"])
                    for j in s.jobs: w.writerow([j.name, j.url, j.size, j.status, j.date])
            else: open(f, "w", encoding="utf-8").write("\n".join(j.url for j in s.jobs))
            log(f"استخراج لیست ({kind}): {len(s.jobs)} مورد → {f}"); QMessageBox.information(s, "استخراج", f"{len(s.jobs)} مورد ذخیره شد.")
        except Exception as e: QMessageBox.warning(s, "خطا", str(e))
    def imp(s, kind):
        f, _ = QFileDialog.getOpenFileName(s, "انتخاب فایل", "", "JSON (*.json)" if kind == "json" else "Text (*.txt *.lst *.csv)")
        if not f: return
        try:
            if kind == "json":
                have = {j.url for j in s.jobs}; n = 0
                for d in json.load(open(f, encoding="utf-8")):
                    if d["url"] in have: continue
                    s.jobs.append(Job(d["url"], d["path"], d.get("group") or grp_of(d["path"]), S["conn"])); n += 1
                s.save(); log(f"وارد کردن از JSON: {n} مورد جدید"); QMessageBox.information(s, "وارد کردن", f"{n} مورد جدید اضافه شد.")
            else: s.add_links(urls_in(open(f, encoding="utf-8", errors="ignore").read()))
        except Exception as e: QMessageBox.warning(s, "خطا", str(e))
    def serve(s):  # سرور محلی افزونه: توکن امنیتی + چند پورت جایگزین
        m = s
        if not S.get("token"): S["token"] = secrets.token_hex(12); save_s()
        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a): pass
            def eo(self):
                o = self.headers.get("Origin", ""); return o if o.startswith(("chrome-extension://", "moz-extension://")) else ""
            def out(self, code, body=b""):
                self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body))); o = self.eo()
                if o:
                    for k, v in (("Access-Control-Allow-Origin", o), ("Vary", "Origin"), ("Access-Control-Allow-Headers", "*"),
                                 ("Access-Control-Allow-Methods", "GET,POST,OPTIONS"), ("Access-Control-Allow-Private-Network", "true")): self.send_header(k, v)
                self.end_headers(); self.wfile.write(body)
            def host_ok(self): return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")
            def do_OPTIONS(self): self.out(204)
            def do_GET(self):
                if not self.host_ok(): return self.out(403)
                cfg = dict(app="CDM", v=2, token=S["token"], cap_min=S["cap_min"], img_btn=S["img_btn"], img_min=S["img_min"], vid_btn=S["vid_btn"], vid_min=S["vid_min"], use_cookies=S["use_cookies"],
                           cap_excl=[x for x in re.split(r"[\s,;.]+", str(S["cap_excl"]).lower()) if x])
                self.out(200, json.dumps(cfg).encode())
            def do_POST(self):
                if not self.host_ok() or self.headers.get("X-CDM-Token") != S["token"]: return self.out(403, b'{"ok":false}')
                try: m.got.emit(json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)))))
                except Exception: pass
                self.out(200, b'{"ok":true}')
        s.port = None
        for pt in (18765, 18766, 18767, 28765, 28766, 38765, 38766, 8765):
            try: srv = http.server.ThreadingHTTPServer(("127.0.0.1", pt), H); s.port = pt; break
            except OSError: continue
        if s.port: threading.Thread(target=srv.serve_forever, daemon=True).start(); log(f"سرور افزونه‌ی مرورگر روی پورت {s.port} فعال شد")
        else: log("راه‌اندازی سرور افزونه ناموفق بود (همه‌ی پورت‌ها اشغال هستند)", "ERROR")
    def show_prog(s, j, auto=False):
        if j.dlg is not None:
            if not auto: j.dlg.from_tray()
            return
        d = ProgDialog(None, j); d.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if auto: d.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        d.show()
    def resume(s): [j.start() for j in s.sel()]
    def stop_sel(s): [j.halt() for j in s.sel()]
    def stop_all(s): [j.halt() for j in s.jobs]
    def start_q(s): s.qstart(S["queues"][0]["name"])
    def stop_q(s): s.qstop(S["queues"][0]["name"])
    def qget(s, n): return next((q for q in S["queues"] if q["name"] == n), None)
    def qstart(s, n):
        q = s.qget(n)
        if q:
            q["active"] = True; log(f"صف «{n}» شروع شد")
            for j in s.jobs:
                if j.queue == n: j.paused = False; j.qtries = 0
    def qstop(s, n):
        q = s.qget(n)
        if q:
            q["active"] = False; log(f"صف «{n}» متوقف شد")
            for j in s.jobs:
                if j.queue == n and j.running: j.halt()
    def sched(s):
        now = datetime.now(); key = now.strftime("%Y%m%d%H%M"); hm = now.strftime("%H:%M")
        for q in S["queues"]:
            if q["start_on"] and q.get("last") != key and hm == q["start_time"]:
                if (q["mode"] == "date" and q["date"] == now.strftime("%Y-%m-%d")) or (q["mode"] == "daily" and now.weekday() in q["days"]):
                    q["last"] = key; s.qstart(q["name"])
            if q["stop_on"] and q.get("last_stop") != key and hm == q["stop_time"]: q["last_stop"] = key; s.qstop(q["name"])
            if not q.get("active"): continue
            pend = []
            for j in s.jobs:
                if j.queue != q["name"] or j.finished or j.status == "یافت نشد": continue
                if j.status == "خطا" and not j.running and not (q["retry_on"] and j.qtries < q["retry"]): continue
                pend.append(j)
            if not pend: s.qdone(q); continue
            run = sum(j.running for j in pend)
            for j in pend:
                if run >= q["parallel"]: break
                if j.running or j.paused: continue
                if j.status == "خطا": j.qtries += 1
                j.start(); run += 1
    def qdone(s, q):
        q["active"] = False; log(f"صف «{q['name']}» به پایان رسید")
        if q["open_on"] and q["open_path"]: QDesktopServices.openUrl(QUrl.fromLocalFile(q["open_path"]))
        if q["shut_on"] and os.name == "nt":
            f = ["/f"] if q["force"] else []
            subprocess.Popen({"Shut down": ["shutdown", "/s", "/t", "30"] + f, "Restart": ["shutdown", "/r", "/t", "30"] + f,
                              "Hibernate": ["shutdown", "/h"], "Sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]}[q["shut_mode"]])
        if q["exit_on"]: QTimer.singleShot(500, s.quit_app)
    def delete(s):
        js = s.sel()
        if not js: return
        rm = S["del_mode"] == "delete"
        box = QMessageBox(s); box.setWindowTitle("حذف"); box.setIcon(QMessageBox.Icon.Question)
        box.setText(f"«{js[0].name}» حذف شود؟" if len(js) == 1 else f"{len(js)} مورد انتخاب‌شده حذف شوند؟")
        if S["del_mode"] == "ask":
            box.setInformativeText("می‌توانید فقط از لیست حذف کنید یا فایل دانلودشده را هم از دیسک پاک کنید.")
            b1 = box.addButton("🗑  حذف از لیست و دیسک", QMessageBox.ButtonRole.DestructiveRole); box.addButton("📋  فقط حذف از لیست", QMessageBox.ButtonRole.AcceptRole)
        else:
            box.setInformativeText("فایل دانلودشده هم از دیسک پاک می‌شود." if rm else "فایل دانلودشده روی دیسک می‌ماند.")
            b1 = box.addButton("✔  حذف", QMessageBox.ButtonRole.AcceptRole)
        bc = box.addButton("انصراف", QMessageBox.ButtonRole.RejectRole); box.setDefaultButton(bc); box.setEscapeButton(bc); box.exec()
        c = box.clickedButton()
        if c is None or c is bc: return          # انصراف: هیچ چیز تغییر نمی‌کند
        if S["del_mode"] == "ask": rm = c is b1
        log(f"حذف از لیست{' و دیسک' if rm else ''}: " + "، ".join(j.name for j in js))
        for j in js:                              # فقط بعد از تأیید
            j.halt()
            if j.th is not None: j.th.join(1.5)
            if j.dlg is not None: j.dlg.close()
            if j in s.jobs: s.jobs.remove(j)
            if rm:
                for pth in (j.path, j.path + ".part"):
                    try:
                        if os.path.exists(pth): os.remove(pth)
                    except OSError: pass
                shutil.rmtree(j.path + ".hls", ignore_errors=True)
        s.save()
    def want_del(s, j):
        m = S["del_mode"]
        if m == "ask": return QMessageBox.question(s, "حذف", f"فایل «{j.name}» هم از دیسک حذف شود؟") == QMessageBox.StandardButton.Yes
        return m == "delete"
    def uniq(s, p):
        p = cpath(p)
        if S["exists"] != "rename": return p
        b, e = os.path.splitext(p); k = 2; used = {j.path for j in s.jobs}
        while p in used or os.path.exists(p): p = f"{b} ({k}){e}"; k += 1
        return p
    def from_browser(s, d):
        d["_br"] = True; log("دریافت از مرورگر: " + (f"{len(d['urls'])} لینک انتخاب‌شده" if isinstance(d.get("urls"), list) else str(d.get("url", ""))))
        if not S["use_cookies"]: d.pop("cookie", None)
        if isinstance(d.get("urls"), list):   # چند لینک انتخاب‌شده در مرورگر → پنجره‌ی «دانلود همه لینکها»
            us = list(dict.fromkeys(u for u in d["urls"][:2000] if isinstance(u, str) and u.startswith(("http://", "https://"))))
            if us: s.pop(); s.add_links(us, d.get("referer", ""), d.get("cookie", ""))
            return
        s.add(d)
    def start_new(s, j):
        if S["queue_new"]: j.queue = S["queues"][0]["name"]; s.qstart(j.queue)
        else: j.start()
    def autoclear(s):
        if S["clear_days"] > 0:
            cut = time.time() - S["clear_days"] * 86400; s.jobs = [j for j in s.jobs if not (j.finished and j.ts < cut)]
    def clip_changed(s):
        if not S["watch_clip"]: return
        u = urls_in(QApplication.clipboard().text())
        if len(u) == 1 and u[0] != s.last_clip and os.path.splitext(urlparse(u[0]).path)[1].lstrip(".").lower() in KNOWN:
            s.last_clip = s.clipu = u[0]; log("لینک در حافظه شناسایی شد: " + u[0])
            s.tray.showMessage("لینک دانلود شناسایی شد", "برای افزودن به CDM اینجا کلیک کنید:\n" + (os.path.basename(urlparse(u[0]).path) or u[0]), QSystemTrayIcon.MessageIcon.Information, 7000)
    def clip_clicked(s):
        u, s.clipu = s.clipu, None
        if u: s.add({"url": u})
    def quit_app(s): s._quit = True; s.close()
    def update_app(s):
        if UPDATE_URL: QDesktopServices.openUrl(QUrl(UPDATE_URL))
        else: QMessageBox.information(s, "بروزرسانی", "آدرس صفحه‌ی بروزرسانی (GitHub) هنوز تنظیم نشده است.")
    def del_done(s): s.jobs = [j for j in s.jobs if not j.finished]; s.save()
    def dbl(s, r, c):
        j = s.vis[r]
        a_ = S["dbl_action"]
        if j.finished and a_ == "open": QDesktopServices.openUrl(QUrl.fromLocalFile(j.path))
        elif j.finished and a_ == "folder": reveal(j.path)
        else: s.show_prog(j)
    def ctx(s, pos):
        m = QMenu(s); js = s.sel()
        if not js: return
        m.addAction("ادامه", s.resume); m.addAction("توقف", s.stop_sel)
        m.addAction("📍 نمایش فایل در پوشه", lambda: reveal(js[0].path))
        m.addAction("کپی آدرس", lambda: QApplication.clipboard().setText(js[0].url)); m.addAction("حذف", s.delete)
        qm = m.addMenu("افزودن به صف")
        for q in S["queues"]: qm.addAction(q["name"], lambda _=False, q=q: [setattr(j, "queue", q["name"]) for j in js])
        m.addAction("حذف از صف", lambda: [setattr(j, "queue", "") for j in js])
        m.exec(s.t.viewport().mapToGlobal(pos))
    def settings(s): SettingsDialog(s).exec()
    def schedule(s): SchedDialog(s).exec()
    def about(s): AboutDialog(s).exec()
    def save(s):
        json.dump([dict(hls=j.hls, queue=j.queue, hdr=j.hdr, url=j.url, path=j.path, group=j.group, size=j.size, segs=j.segs, status=j.status, date=j.date, ts=j.ts) for j in s.jobs],
                  open(DB, "w", encoding="utf-8"), ensure_ascii=False)
    def load(s):
        try:
            for d in json.load(open(DB, encoding="utf-8")):
                j = Job(d["url"], d["path"], d["group"], S["conn"]); j.size, j.segs, j.date, j.hdr = d["size"], d["segs"], d["date"], d.get("hdr", {}); j.ts = d.get("ts") or pts(d["date"]); j.queue = d.get("queue", ""); j.hls = d.get("hls", j.hls)
                j.status = d["status"] if d["status"] in ("تکمیل شد.", "یافت نشد") else "توقف"; s.jobs.append(j)
        except Exception: pass
    def closeEvent(s, e):
        if not getattr(s, "_quit", False):
            if S["close_tray"]:
                e.ignore(); s.hide(); s.tray.showMessage("CDM", "برنامه در ناحیه‌ی اعلان در حال اجراست.", QSystemTrayIcon.MessageIcon.Information, 2500); return
            if S["confirm_exit"] and any(j.running for j in s.jobs):
                if QMessageBox.question(s, "خروج", "دانلودهایی در حال انجام هستند. از برنامه خارج می‌شوید؟") != QMessageBox.StandardButton.Yes: e.ignore(); return
        log("خروج از برنامه")
        for j in s.jobs:
            if j.dlg is not None: j.dlg.close()
        s.tray.hide(); s.drop.close(); s.stop_all(); time.sleep(.3); s.save(); save_s(); e.accept(); QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setLayoutDirection(Qt.LayoutDirection.RightToLeft); app.setQuitOnLastWindowClosed(False)
    def _hook(et, ev, tb):
        import traceback; log("".join(traceback.format_exception(et, ev, tb)).strip(), "ERROR")
        try: sys.__excepthook__(et, ev, tb)
        except Exception: pass
    sys.excepthook = _hook; threading.excepthook = lambda a: log(f"خطا در Thread: {a.exc_type.__name__}: {a.exc_value}", "ERROR")
    FONT = load_font(); apply_theme(S.get("theme", "ocean")); apply_font()
    w = Main()
    if not (S["start_min"] and QSystemTrayIcon.isSystemTrayAvailable()): w.show()
    sys.exit(app.exec())
