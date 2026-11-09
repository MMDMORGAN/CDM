# CDM — Carbon Download Manager

**A powerful, feature-rich download manager inspired by Internet Download Manager (IDM).**

CDM is a modern desktop download manager built with Python and PyQt6. It is designed to make downloading files easier, faster, and more organized through multi-connection downloads, intelligent queues, scheduling, browser integration, and a highly customizable interface.

With support for segmented downloading, pause and resume, automatic file organization, HLS streams, and an advanced download Grabber, CDM brings essential download management tools together in one application.

---

## ✨ Features

### ⚡ Advanced Download Engine
- Multi-connection and segmented downloads.
- Up to 32 simultaneous connections per download.
- Pause and resume supported downloads.
- Real-time download speed monitoring.
- Live progress bars and estimated remaining time.
- Automatic retry on download failures.
- HTTP Range support detection.
- Automatic file size and download information detection.
- Configurable connection and buffer settings.

### 🌐 Browser Integration
- Companion browser extension integration.
- Capture download links directly from your browser.
- Receive multiple selected links from the browser.
- Support for browser cookies and Referer headers.
- Optional automatic download interception.
- Floating download basket.

### 🕷 Advanced Grabber
- Scan web pages for downloadable files.
- Extract multiple download links from a webpage.
- Filter files by extension.
- Configure scanning depth.
- Restrict scanning to the same domain.
- Select discovered files for batch downloading.

### 📋 Download Management
- Multiple download queues.
- Independent queue configurations.
- Simultaneous queue execution.
- Batch download support.
- Generate download links from URL patterns.
- Import and export download lists.
- JSON, CSV, and TXT support.
- Automatic file categorization.
- Separate folders for different file types.
- Search and filter downloads.
- Persistent download history.

### 🗓 Smart Scheduling
- Schedule downloads by date and time.
- Configure daily and weekly schedules.
- Set automatic queue start and stop times.
- Configure download retries.
- Automatically open files after completion.
- Automatically shut down the computer after downloads.
- Run selected queues automatically.

### 🎬 HLS Download Support
- Download HLS streams using `.m3u8` playlists.
- Automatic selection of the highest-bandwidth playlist variant.
- Parallel segment downloading.
- Support for AES-128 encrypted HLS streams.
- Combine downloaded segments into a single output file.

### 🎨 Customization
- 17 built-in interface themes.
- Light and dark appearance options.
- Custom font size.
- Adjustable interface layout.
- Custom download directories.
- Persian and English-friendly interface elements.
- Optional Persian numerals.
- Configurable file size and speed units.

### ⚙️ Advanced Settings
- Configurable download speed limits.
- Scheduled bandwidth limitations.
- HTTP proxy support.
- SSL verification settings.
- Custom User-Agent.
- Configurable connection timeout.
- Automatic retry configuration.
- Disk space checking.
- Download logging.
- System tray integration.
- Windows startup integration.
- Clipboard URL monitoring.
- Custom file naming and duplicate handling.

---

## 🖥 Technology Stack

CDM is built using:

- **Python** — Core application logic.
- **PyQt6** — Desktop graphical user interface.
- **Requests** — HTTP communication and file downloading.
- **Threading** — Parallel download operations.
- **JSON** — Application settings and download persistence.

---

## 🚀 Installation

### Requirements

- Python 3.10 or newer recommended.
- pip package manager.

### Install dependencies

```bash
pip install PyQt6 requests
```

For AES-128 encrypted HLS support:

```bash
pip install cryptography
```

### Run CDM

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/CDM.git
```

Navigate to the project directory:

```bash
cd CDM
```

Run the application:

```bash
python cdm.py
```

---

## 📁 Project Structure

```text
CDM/
│
├── cdm.py
├── cdmlogo.png
├── Irancell_Duran-Medium.ttf
├── README.md
└── requirements.txt
```

---

## 💾 Data & Configuration

CDM stores its settings and download information locally on your computer.

- Download history: `~/.cdm_items.json`
- Application settings: `~/.cdm_settings.json`
- Download logs: `~/.cdm_log.txt` (when enabled)

Your download configuration and preferences remain available between application sessions.

---

## 🔒 Privacy

CDM is designed as a local desktop application. Download management, application settings, and history are handled locally.

Downloads may communicate with the servers hosting the requested files. Browser integration can also use cookies and Referer information when enabled.

---

## ⚠️ Disclaimer

CDM is an independent download manager inspired by the functionality of Internet Download Manager (IDM).

It is not affiliated with, endorsed by, or associated with Internet Download Manager or its developers.

Users are responsible for ensuring that their downloads comply with applicable laws and the terms of the websites they access.

---

## 📌 Project Status

CDM is under active development.

Features, performance, compatibility, and the user interface may change between releases.

**CDM — Download Smarter. Download Faster.**
