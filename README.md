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
- **Keyevent Management**: Execute input events on multiple devices simultaneously with 3 execution strategies
- **Cross-Platform Support**: Works on Windows, Linux, and macOS
- **Comprehensive UI Help System**: Tooltips, contextual help, and status messages for all UI elements

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
- 🎨 **Dark Theme**: Modern dark UI with professional styling and gradient elements
- 🔄 **Multi-threading**: Background workers for non-blocking operations
- ⌨️ **Keyevent Execution**: Execute input events on multiple devices with 3 strategies:
  - **Dedicated Thread Per Worker**: Maximum parallelism (separate thread per device)
  - **Sequential Worker Queue**: Single thread with chained workers (resource efficient)
  - **Thread Pool**: Optimal balance using QThreadPool for many devices
- 🎯 **UI Help System**: Comprehensive tooltips, contextual help (F1), and status bar messages for all components
- 🌐 **Multi-Platform Support**: Full Windows/Linux/macOS compatibility with platform-specific optimizations

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
- **Keyevent Method Selection**: Choose between 3 execution strategies for keyevents
- Settings are saved persistently across sessions

### Keyevent Tab
- **Search**: Filter keyevents by name or description
- **Device Selection**: Check/uncheck devices to execute keyevents on
- **Execution Methods**: Choose from 3 different strategies:
  - **Dedicated Thread Per Worker**: One thread per device (maximum parallelism)
  - **Sequential Queue**: Single thread executing one device at a time (minimum resources)
  - **Thread Pool**: Balanced approach using QThreadPool (optimal for many devices)
- **Execution Logs**: Real-time feedback on keyevent execution status
- **Device Filtering**: Only enabled devices are selectable

### Terminal Tab
- **Professional ADB Terminal**: Full-featured terminal environment
- **Command Execution**: Execute any ADB or shell command
- **Smart Autocomplete**: Tab key for command suggestions
- **Command History**: Up/Down arrow keys to navigate previous commands
- **ADB Auto-Detection**: Automatically injects ADB into terminal session
- **Output Management**: Clear command history and manage transcript
- **Status Feedback**: Real-time command status and working directory display

## 🏗️ Project Structure

```
ADBez/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── core/                   # Core business logic
│   ├── __init__.py         # Package initialization
│   ├── dataTypes.py        # Data models, ConnectedDevice, CheckData with signals
│   ├── dataManager.py      # Data persistence and management
│   ├── requests.py         # Data manager request/response system
│   ├── workers.py          # ADB/Nmap background worker threads (cross-platform)
│   ├── keyevent.py         # Keyevent execution workers (3 strategies)
│   ├── terminalWorker.py   # Professional terminal worker with ADB integration
│   └── scrcpy.py           # Scrcpy integration utilities
├── tabs/                   # UI Tab Components
│   ├── __init__.py         # Package initialization
│   ├── connect.py          # Connection management tab (TCP/IP connections)
│   ├── find.py             # Network discovery tab (Nmap integration)
│   ├── settings.py         # Settings configuration tab (ADB path, execution methods)
│   ├── keyevents.py        # Keyevent execution tab with 3 strategies
│   └── terminal.py         # Professional terminal tab with autocomplete
├── ui/                     # Custom UI Components
│   ├── keyeventItem.py     # Keyevent list item widget
│   └── terminalInput.py    # Terminal input field with history and autocomplete
├── styles/                 # UI Styling (Dark Theme)
│   ├── main.qss            # Main Qt stylesheet (dark theme with gradients)
│   └── main.css            # Alternative CSS styles
├── data/                   # Application Data
│   └── settings.json       # User settings and preferences (persisted)
└── adb/                    # ADB Tools Directory
    ├── adb.exe             # Android Debug Bridge executable (Windows)
    ├── adb                 # Android Debug Bridge executable (Unix-like)
    └── ...                 # Other ADB-related files
```


### - Professional Terminal & Architecture Improvements

**✨ New Features:**
- 💻 **Professional Terminal Tab**: Built-in ADB terminal with autocomplete and history
- 🔄 **Command History**: Navigate previous commands with arrow keys
- 🎯 **Smart Autocomplete**: Tab completion for ADB commands
- ⌨️ **Keyevent Tab**: Execute input events on multiple devices with 3 execution strategies
- 🎨 **Comprehensive UI Help System**: Tooltips, WhatsThis dialogs, and status messages for all UI elements
- 🌐 **Enhanced Cross-Platform Support**: Platform-specific optimizations for Windows/Linux/macOS

**🏗️ Architecture & Data Model Improvements:**
- **ConnectedDevice Data Model**: New comprehensive device tracking with:
  - Device types: USB and TCPIP connections
  - Device states: device, offline, unauthorized, recovery, sideload, bootloader
  - Device properties: serial, product, model, transport_id, icon representation
  - Hash and equality comparison methods for deduplication
- **Enhanced checkData Structure**: 
  - `founded_ips`: IPs discovered via Nmap scans
  - `connected_devices`: List of ConnectedDevice objects (improved from simple IP strings)
  - `keyeventMethod`: Selected keyevent execution strategy
  - `did_adb_work`: ADB availability status
  - Granular signals for each field: `changed_connected_devices`, `changed_founded_ips`, `changed_choosen_path_for_adb`, `changed_keyeventMethod`
- **Granular Signal System**: Individual signals for each data field change enabling:
  - Reactive UI updates without global refresh
  - Type-safe signal/slot connections
  - Per-field event handling
- **Request/Response Architecture**: New clean data manager system with:
  - Separate read/write request signals
  - Response signals for async operations
  - Type-safe data flow between UI and core
- **Terminal Worker Thread**: Dedicated `terminalWorker.py` with:
  - ADB command detection and smart prefix injection
  - Command history management
  - Autocomplete suggestions (file paths, ADB commands)
  - Output coloring (input/output/error differentiation)
  - Working directory tracking

**🎨 Professional UI & Styling System:**
- **Dark Theme Implementation**: 
  - Modern dark backgrounds (#1a1a1a, #252525)
  - Professional cyan/turquoise accents (#4fc3f7, #00d4ff)
  - Gradient elements for interactive feedback
  - Consistent styling across all 100+ UI widgets
  - Custom QSS stylesheet with 200+ style rules
- **Comprehensive UI Help System**:
  - **Tooltips (ToolTip)**: 50+ contextual hover hints for quick reference
  - **WhatsThis (WhatsThis)**: 50+ detailed help dialogs accessible via F1 or Help button
  - **Status Tips (StatusTip)**: Status bar help messages for 30+ major UI elements
  - Implemented on: buttons, inputs, dropdowns, lists, tabs, group boxes, and dialogs
  - Example: Hovering over "Connect" button shows "Establish TCP/IP connection to device"
  - Example: Pressing F1 on Terminal tab shows detailed keyboard shortcuts and commands
- **Enhanced Professional Terminal UI**: 
  - Monospace font display (Consolas 11pt)
  - Colored output streams (input/output/error)
  - Scrollable history with 5000 line buffer
  - Real-time command prompt display with working directory

**🔧 Keyevent Execution System:**
- **3 Execution Strategies** with selectable modes:
  1. **KeyeventQObjectWorker (Dedicated Threads)**: 
     - One QThread + QObject worker per device
     - Maximum parallelism, higher resource usage
     - Best for small number of devices (1-5 devices)
  2. **Sequential Worker Queue**:
     - Single QThread with chained workers
     - Minimum resource usage
     - Devices executed one after another
     - Best for resource-constrained systems
  3. **QThreadPool with Runnable Workers**:
     - Optimal resource management
     - Ideal for many devices (5+ devices)
     - Thread count managed by system (default: CPU count)
- **Timeout Handling**: 5-second timeout per device with graceful error handling
- **Real-time Status**: Individual success/failure feedback per device with visual indicators
- **Execution Logs**: Detailed per-device execution logs for debugging

**🐛 Bug Fixes & Improvements:**
- Fixed Signal type definitions using lowercase `list` type hints for Python 3.9+ compatibility
- UTF-8 BOM encoding handled correctly in README and configuration files
- QSS syntax corrections (qradial → qradialgradient with proper parameters)
- ListView checkbox rendering with custom styling and proper state management
- RadioButton signal integration with proper callback handlers
- **AutoFind Path Validation**:
  - Proper file existence checking with `os.path.isfile()`
  - Executable permission verification with `os.access()`
  - Return only valid found paths or None for error handling
  - Common ADB paths database for all platforms
  - System PATH search using `shutil.which()`
- **Cross-platform Path Handling**:
  - Platform-specific ADB executable detection (adb.exe on Windows, adb on Unix)
  - Proper path normalization using `os.path.normpath()`
  - Directory separator handling for Windows/Linux/macOS
  - Platform detection using `platform.system()`
- **Cross-platform Subprocess Management**:
  - STARTUPINFO for console hiding on Windows
  - Proper signal handling for process termination
  - Exception handling for missing executables
  - Timeout handling with graceful cleanup

**📂 New & Modified Core Files (24 files updated):**
- `core/requests.py` - New: Data manager request/response system
- `core/keyevent.py` - New: Keyevent workers with 3 execution strategies (KeyeventQObjectWorker, KeyeventQRunnableWorker)
- `core/terminalWorker.py` - New: Professional terminal worker with ADB integration
- `core/workers.py` - Enhanced: Cross-platform support (Windows/Linux/macOS), helper functions
- `core/dataTypes.py` - Enhanced: ConnectedDevice model, granular signals, CheckData fields
- `tabs/terminal.py` - New: Professional terminal tab with worker integration
- `tabs/keyevents.py` - New: Keyevent execution tab with 3 strategy selection
- `tabs/settings.py` - Enhanced: Auto-detection, method selection, UI help system
- `tabs/connect.py` - Enhanced: UI help system (tooltips, whatsThis, statusTip)
- `tabs/find.py` - Enhanced: UI help system, improved network scanning feedback
- `ui/keyeventItem.py` - New: Keyevent item widget with execution button
- `ui/terminalInput.py` - New: Terminal input with history and autocomplete
- `main.py` - Enhanced: Tab integration, UI help support, QWhatsThis mode
- `styles/main.qss` - Enhanced: Dark theme with 200+ style rules, gradients, animations
- Additional README improvements and documentation

## 🛠️ Development

This application uses the following technologies:

- **PySide6 (6.11.0+)**: Python binding for Qt6 - provides the modern GUI framework with signals/slots
- **YoungLion Library**: Custom DDM (Data Data Manager) for data type inheritance and persistence
- **QThread**: Multi-threading support with worker patterns (QObject and QRunnable)
- **QThreadPool**: Thread pool management for optimal resource usage
- **subprocess**: System command execution for ADB and Nmap with cross-platform support
- **ipaddress**: Network address validation and CIDR notation parsing
- **platform**: OS detection for cross-platform code paths
- **shutil**: Utility functions including PATH search with `which()`

### Architecture Overview

**Threading Model:**
- Main GUI Thread: Handles all UI operations and user interactions
- Per-Device Thread: Dedicated QThread for each connected device (Keyevent mode 1)
- Sequential Thread: Single background thread for sequential operations (Keyevent mode 2)
- Thread Pool: System-managed thread pool for optimal concurrency (Keyevent mode 3)
- Terminal Worker Thread: Separate thread for ADB terminal operations

**Data Flow:**
1. User input in UI → Signal emitted
2. Signal caught by tab/widget → Process data
3. Data manager requested → Request signal emitted
4. Core thread retrieves data → Response signal emitted
5. Tab receives data → Update UI and emit change signal
6. Other tabs listen for change signal → Update dependent UI elements

**Event Handling:**
- Signals/Slots: Qt's native event system for thread-safe communication
- Worker Signals: Progress, finished, line, error signals for feedback
- Data Signals: Granular change signals for reactive UI updates

### Building from Source

```bash
# Install development dependencies
pip install -r requirements.txt

# Run directly
python main.py

# Build executable (optional - requires PyInstaller)
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 7+, Ubuntu 16.04+, macOS 10.12+
- **Python**: 3.8 or higher
- **RAM**: 512 MB
- **Disk Space**: 200 MB (including ADB tools)
- **Display**: 1024x768 minimum resolution

### Recommended Requirements
- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.14+
- **Python**: 3.9 or higher
- **RAM**: 2 GB or more
- **Disk Space**: 500 MB (with Android emulator support)
- **Display**: 1920x1080 or higher
- **Network**: Gigabit Ethernet for optimal scanning performance

### Platform-Specific Notes

**Windows:**
- ADB can be placed in `C:/Android/platform-tools/` or any location
- Auto-detection searches: `%USERPROFILE%/AppData/Local/Android/Sdk/platform-tools/`
- Requires Python to be added to PATH for command line usage
- Console is hidden by default (STARTUPINFO flags)

**Linux:**
- Install ADB: `sudo apt-get install android-tools-adb`
- Common paths: `/usr/bin/adb`, `/usr/local/bin/adb`, `/snap/bin/adb`
- Requires `libc6` and other dependencies (usually pre-installed)
- Works with WSL (Windows Subsystem for Linux)

**macOS:**
- Install via Homebrew: `brew install android-platform-tools`
- Common paths: `/usr/local/bin/adb`, `~/Library/Android/sdk/platform-tools/`
- Requires Xcode Command Line Tools
- May need to allow in System Preferences > Security & Privacy

## 🚀 Advanced Usage

### Using Keyboard Shortcuts

**Terminal Tab:**
- `↑/↓ Arrow Keys`: Navigate command history
- `Tab`: Command autocomplete
- `Ctrl+L`: Clear screen (terminal)
- `Enter`: Execute command

**General UI:**
- `F1`: Show help (WhatsThis) for focused widget
- `Shift+F1`: Enable WhatsThis mode for pointer selection
- `Alt+Tab`: Switch between tabs
- `Tab`: Navigate between UI elements

### Network Scanning with Different Ranges

```
192.168.1.0/24    - Scans 192.168.1.1 to 192.168.1.254
10.0.0.0/8        - Scans entire private network (10.0.0.0 to 10.255.255.255)
172.16.0.0/12     - Scans 172.16.0.0 to 172.31.255.255
127.0.0.0/24      - Scans localhost range (testing)
```

### Selecting Appropriate Keyevent Strategy

1. **Small Network (1-3 devices)**:
   - Use: Dedicated Thread Per Worker
   - Reason: Maximum parallelism, lowest latency
   - Execution time: ~2 seconds (all parallel)

2. **Medium Network (4-10 devices)**:
   - Use: Thread Pool (recommended)
   - Reason: Balanced resources, optimal performance
   - Execution time: ~4-6 seconds (system manages threads)

3. **Large Network (10+ devices) or Low Resources**:
   - Use: Sequential Worker Queue
   - Reason: Minimum memory usage, predictable behavior
   - Execution time: ~10+ seconds (one per second per device)

## 🔒 Security Considerations

- **ADB Connections**: Ensure devices are connected to trusted networks
- **Port 5555**: Keep ADB port closed to external networks
- **File Permissions**: ADB executable should have proper permissions (755 on Unix)
- **Settings Storage**: Passwords are NOT stored; only paths are saved
- **Command Injection**: Terminal has basic protection against command injection
- **SSL/TLS**: Currently no encryption for network transfers; use on trusted networks only

## ⚙️ Performance Optimization

### Tips for Faster Operations

1. **Network Scanning**:
   - Use specific network ranges instead of large subnets
   - Example: Use `192.168.1.0/24` instead of `192.168.0.0/16`
   - Scanning large ranges (8+) can take 5-10 minutes

2. **Keyevent Execution**:
   - Use Thread Pool mode for best overall performance
   - Timeout is 5 seconds per device; slow devices may timeout
   - Pre-connect devices via USB if possible (faster than network)

3. **Terminal Operations**:
   - Use autocomplete to avoid typos and re-execution
   - Command history is stored per session

### Resource Usage

- **Idle State**: ~50 MB RAM
- **One Connection**: ~60-80 MB RAM
- **With Terminal**: ~80-100 MB RAM
- **During Keyevent Execution**:
  - Mode 1 (Threads): +10 MB per device
  - Mode 2 (Sequential): +5 MB
  - Mode 3 (Pool): +8 MB

## 🆘 Troubleshooting

### Common Issues and Solutions

#### 1. ADB Path Not Found
**Problem**: "ADB Not Found" message in Settings tab
**Solutions**:
- Click "Auto Find" button (will search common paths)
- Manually select ADB location using "Change" button
- Ensure ADB tools are installed (download from Android SDK)
- Check Windows PATH environment variable includes ADB folder

#### 2. Network Scan Takes Too Long
**Problem**: Nmap scan appears to be stuck or is very slow
**Solutions**:
- Scan smaller network ranges (e.g., /24 instead of /16)
- Check network connectivity: `ping` a device in the range
- Ensure Nmap is installed: `nmap --version`
- Try scanning known working devices first with `/32` range

#### 3. Cannot Connect to Device
**Problem**: Connection fails with "Connection refused" error
**Solutions**:
- Verify device IP: Run `adb shell ifconfig` on the device
- Check port: Default ADB port is 5555 (configurable)
- Firewall: Disable or allow port 5555 on both device and computer
- Device-side: Enable "ADB over Network" in developer settings
- USB Connection: First connect device via USB, then enable network

#### 4. Command History Not Working in Terminal
**Problem**: Up/Down arrows don't navigate history
**Solutions**:
- Ensure cursor is in terminal input field
- Click in the input box first to focus
- Clear any text before using arrow keys
- Recent commands are shown with history feature

#### 5. Keyevent Execution Timeout
**Problem**: "Timeout" error when executing keyevents
**Solutions**:
- Check device connectivity: `adb connect device.ip.address`
- Reduce number of parallel devices (use Sequential Queue mode)
- Ensure device is responsive: `adb shell echo "test"`
- Some devices are slower; increase timeout in code if needed (core/keyevent.py)

#### 6. Dark Theme Not Applied
**Problem**: UI shows default colors instead of dark theme
**Solutions**:
- Restart application
- Check `styles/main.qss` file exists and is readable
- Try moving application to different location (might be permission issue)
- On Linux/Mac: Ensure ~/.config/Vultrion has write permissions

#### 7. Application Crashes on Startup
**Problem**: Application exits immediately with traceback
**Solutions**:
- Check Python version: `python --version` (must be 3.8+)
- Verify all dependencies: `pip install -r requirements.txt`
- Check for file encoding issues in settings.json
- Try deleting `data/settings.json` and restart (resets to defaults)
- Check terminal for error messages

### Getting More Help

**Check Logs:**
- Terminal output shows detailed error messages
- For network scanning: Check Nmap output in Find tab logs
- For connections: Check Connect tab logs for ADB output

**Enable Debug Mode (for developers):**
```python
# In main.py, add before MainWindow creation:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Changelog

### Version 1.1.0 (Current Release)
- ✨ Professional Terminal Tab with autocomplete and history
- ✨ Keyevent Tab with 3 execution strategies
- ✨ Comprehensive UI Help System (tooltips, WhatsThis, status messages)
- 🎨 Dark Theme with professional gradient elements
- 🌐 Full cross-platform support (Windows, Linux, macOS)
- 🏗️ Enhanced data model with ConnectedDevice and granular signals
- 🔧 Improved ADB auto-detection with better path validation
- 📚 Enhanced documentation and README
- 🐛 Multiple bug fixes and performance improvements
- Files Modified: 24+ core and UI files

### Version 1.0.0 (Previous Release)
- Initial PySide6 release
- Basic ADB connection functionality
- Network scanning with Nmap
- Settings management
- Professional UI with dark theme

## 📱 Platform Support & Testing

**Tested On:**
- ✅ Windows 10, 11 (x86_64)
- ✅ Ubuntu 18.04, 20.04, 22.04 (x86_64)
- ✅ macOS 10.14, 11, 12 (Intel and Apple Silicon)
- ✅ WSL (Windows Subsystem for Linux) 2

**Browser/Device Compatibility:**
- ✅ Android 5.0+ devices
- ✅ Android emulators (tested with Android Studio emulator)
- ✅ Connected via USB
- ✅ Connected via TCP/IP network

## 🔗 Related Projects & Dependencies

- [Android Debug Bridge (ADB)](https://developer.android.com/studio/command-line/adb)
- [Nmap](https://nmap.org/) - Network discovery tool
- [PySide6](https://wiki.qt.io/PySide6) - Python Qt6 binding
- [YoungLion Library](https://github.com/Cavanshirpro/YoungLion) - Custom data management library

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute

1. **Report Issues**: Found a bug? Create an issue with detailed information
2. **Feature Requests**: Have an idea? Open a discussion or issue
3. **Code Contributions**: Fork → Create feature branch → Submit PR
4. **Documentation**: Improve README, add examples, fix typos
5. **Testing**: Test on different platforms and devices

### Development Workflow

```bash
# 1. Fork and clone the repository
git clone https://github.com/Cavanshirpro/Vultrion.git
cd Vultrion

# 2. Create feature branch
git checkout -b feature/YourFeature

# 3. Install dependencies
pip install -r requirements.txt

# 4. Make your changes
# Edit files, add features, fix bugs

# 5. Test thoroughly
python main.py

# 6. Commit and push
git add .
git commit -m "Add: Description of your changes"
git push origin feature/YourFeature

# 7. Submit Pull Request on GitHub
```

### Code Style Guidelines
- Use meaningful variable names
- Add docstrings to functions
- Follow PEP 8 style guide
- Test on multiple platforms if possible
- Update README if adding features

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

**Key Points:**
- You are free to use, modify, and distribute this software
- If you distribute modified versions, you must include the source code
- No warranty is provided; use at your own risk
- Derivative works must be under GPLv3 as well

## 🙏 Acknowledgments

- **Android Debug Bridge (ADB)** team - Essential tool for Android development
- **Nmap project** - Powerful network scanning capabilities
- **PySide6/Qt6 community** - Excellent framework for cross-platform GUI development
- **All contributors** - Code, bug reports, feature suggestions, and testing
- **Users** - Feedback and support

## 📧 Support & Contact

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Pull Requests**: Welcome for all improvements

---

**Made with ❤️ for Android developers and enthusiasts**

*Last Updated: April 2026*
*Version: 1.1.0*
