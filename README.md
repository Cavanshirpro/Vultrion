# Vultrion - ADB Manager (ADBez V1)

**Simplify your ADB workflow:** *A Python GUI for Android device management and Nmap integration.*

[![PySide6](https://img.shields.io/badge/PySide6-6.11.0-blue.svg)](https://pypi.org/project/PySide6/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)

## 🎯 Why Vultrion?

**New to using ADB?**
**Do you want to use ADB in an easier way?**
**Do you want to manage everything easily with a simple interface?**

> **Then this repo is just for you.**

This is the PySide6 version of the Adbez project - a modern, user-friendly Android Debug Bridge (ADB) management application with an intuitive graphical interface.

## ✨ Key Features

- **Easy Interface with PySide6**: Modern, clean GUI built with Qt6
- **Network Discovery**: Scan local networks using Nmap to find Android devices
- **ADB Management**: Connect/disconnect to Android devices via ADB
- **Smart IP Management**: Automatically populate found IPs for easy connection
- **Real-time Logging**: Monitor connection status and operations
- **Auto ADB Detection**: Automatically find and configure ADB installation path
- **Persistent Settings**: Save your ADB path and preferences
- **Professional Terminal**: Built-in ADB terminal with autocomplete and history
- **Cross-Platform Support**: Works on Windows, Linux, and macOS

## 🚀 Current Features

- 🔍 **Network Scanning**: Search for devices with Nmap integration
- 🔗 **ADB Connection**: Connect to IP addresses with ADB
- 📋 **Auto IP Population**: Found IPs from Nmap scans are automatically added to the connection dropdown
- 💻 **Professional Terminal**: Built-in ADB terminal with:
  - Command autocomplete (Tab key)
  - Command history (↑/↓ arrow keys)
  - Automatic ADB prefix detection
  - Colored output (input/output/error)
  - Real-time execution
- ⚙️ **Settings Management**: Configure ADB path and application preferences with auto-detection
- 📊 **Progress Tracking**: Real-time progress bars for long-running operations
- 🛡️ **Input Validation**: Comprehensive IP address and port validation
- 🎨 **Dark Theme**: Modern dark UI with custom styling
- 🔄 **Multi-threading**: Background workers for non-blocking operations

## 📋 Requirements

- Python 3.8+
- PySide6
- YoungLion library
- ADB tools
- Nmap (for network scanning)

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Cavanshirpro/Vultrion.git
cd Vultrion
```

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

3. **Set up ADB tools:**
   - Download ADB tools and place them in the `adb` folder, OR
   - Use the Settings tab to specify your ADB path
   - The application will try to detect ADB automatically

4. **Run the application:**
```bash
python main.py
```

## 📖 Usage

### Connect Tab
- Enter IP address and port (default port: 5555)
- Click "Connect" button to establish ADB connection
- Click "Disconnect" button to disconnect
- View real-time logs in the text area

### Find Tab
- Enter network CIDR notation (e.g.: 192.168.1.0/24)
- Click "Connect" button to start network scan
- Found IPs are automatically added to the Connect tab's dropdown

### Settings Tab
- **Auto Find**: Automatically detect ADB installation path
- **Manual Selection**: Browse and select ADB folder manually
- **Path Display**: Shows current ADB path
- Settings are saved persistently across sessions

## 🏗️ Project Structure

```
ADBez/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── core/                   # Core business logic
│   ├── dataTypes.py        # Data models and types
│   ├── dataManager.py      # Data persistence and management
│   ├── requests.py         # Data manager request/response system
│   ├── terminalWorker.py   # Professional terminal worker
│   └── workers.py          # Background worker threads
├── tabs/                   # UI components
│   ├── __init__.py         # Package initialization
│   ├── connect.py          # Connection management tab
│   ├── find.py             # Network discovery tab
│   ├── settings.py         # Settings configuration tab
│   └── terminal.py         # Professional terminal tab
├── ui/                     # Custom UI components
│   └── terminal.py         # Terminal UI components
├── styles/                 # UI styling
│   ├── main.qss            # Qt stylesheet
│   └── TerminalTab.qss     # Terminal stylesheet
├── data/                   # Application data
│   └── settings.json       # User settings and preferences
└── adb/                    # ADB tools and utilities
    ├── adb.exe             # Android Debug Bridge executable
    ├── MyNotes.txt         # Usage notes and tips
    └── ...                 # Other ADB-related files
```


### - Professional Terminal & Architecture Improvements

**✨ New Features:**
- 💻 **Professional Terminal Tab**: Built-in ADB terminal with autocomplete and history
- 🔄 **Command History**: Navigate previous commands with arrow keys
- 🎯 **Smart Autocomplete**: Tab completion for ADB commands

**🏗️ Architecture & Data Model Improvements:**
- **ConnectedDevice Data Model**: New comprehensive device tracking with:
  - Device types: USB and TCPIP
  - Device states: device, offline, unauthorized, recovery, sideload, bootloader
  - Device properties: serial, product, model, transport_id
  - Hash and equality comparison methods
- **Enhanced checkData Structure**: 
  - `founded_ips`: IPs discovered via Nmap scans
  - `connected_devices`: List of ConnectedDevice objects (previously simple IP strings)
- **Granular Signal System**: Individual signals for each data field change for better event handling
- **Request/Response Architecture**: New data manager system for cleaner request/response patterns
- **Terminal Worker Thread**: Dedicated `terminalWorker.py` with ADB command detection and smart autocomplete
- **Professional Terminal UI**: Enhanced terminal components with colored output (input/output/error)

**🐛 Bug Fixes & Improvements:**
- Fixed Signal type definitions for better type safety
- UTF-8 encoding improvements
- Enhanced error handling in worker threads
- Cross-platform path handling (Windows/Linux/macOS)

**📂 New & Modified Files:**
- `core/requests.py` - Data manager request/response system
- `core/terminalWorker.py` - Professional terminal worker with ADB command detection
- `tabs/terminal.py` - Professional terminal tab with worker thread integration
- `ui/terminal.py` - Terminal UI components with colored output
- `core/dataTypes.py` - Updated with ConnectedDevice model and new data fields
- `main.py` - Updated with terminal tab integration

## 🛠️ Development

This application uses the following technologies:

- **PySide6**: Python binding for Qt6 - provides the modern GUI framework
- **YoungLion**: Custom utility library for data management
- **QThread**: Multi-threading support for background operations
- **subprocess**: System command execution for ADB and Nmap
- **ipaddress**: Network address validation and manipulation

### Building from Source

```bash
# Install development dependencies
pip install -r requirements.txt

# Build executable (optional)
pyinstaller --onefile --windowed main.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Android Debug Bridge (ADB) team
- Nmap project
- PySide6/Qt6 community
- All contributors and users

---

**Made with ❤️ for Android developers and enthusiasts**
