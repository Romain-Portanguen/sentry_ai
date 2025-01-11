<div align="center">
  <h1>🛡️ Sentry AI</h1>
  <p><em>Your Intelligent Privacy Guardian for macOS</em></p>
  
  <img src="app/public/assets/AppIcon.png" alt="Sentry AI Logo" width="500"/>
  
  <p>
    <img src="https://img.shields.io/badge/Platform-macOS%2010.13+-brightgreen.svg" alt="Platform macOS" />
    <img src="https://img.shields.io/badge/Python-3.10-blue.svg" alt="Python 3.10" />
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License MIT" />
  </p>
</div>

## 🎯 Overview

Sentry AI is your intelligent workstation guardian that automatically protects your privacy by locking your Mac when you step away. Using state-of-the-art face detection AI, it provides seamless and efficient surveillance while respecting your privacy.

## ✨ Key Features

### 🤖 AI-Powered Detection

- Real-time face detection using MediaPipe
- Intelligent frame analysis optimization
- Resource-efficient processing

### 🔐 Smart Security

- Instant lock when you step away (5-second threshold)
- Seamless macOS lock integration
- Automatic monitoring resume

### 🍎 Native macOS Experience

- Elegant menu bar integration
- Dock presence for easy access
- Global keyboard shortcuts
- Launch at login support

### ⚡️ Performance Optimized

- Smart sleep mode during inactivity
- Optimized camera resolution (640x480)
- Efficient frame analysis (1:3 ratio)
- Automatic resource management

### 🎛️ System Integration

- Deep macOS integration
- Sleep mode awareness
- Intelligent interruption handling

## ⌨️ Controls & Shortcuts

| Shortcut | Action            | Description               |
|----------|-------------------|---------------------------|
| ⌘M       | Toggle Monitoring | Start/Stop face detection |
| ⌘L       | Launch at Login   | Enable/Disable auto-start |
| ⌘,       | About             | Show app information      |
| ⌘Q       | Quit              | Exit application          |

## 🚀 Getting Started

### 📋 Prerequisites

- macOS 10.13 or later
- Python 3.10
- Camera access permissions

### ⚡️ Quick Install

```bash
# Get the code
git clone https://github.com/Romain-Portanguen/sentry_ai.git
cd sentry_ai

# Install & Run
make install && source .venv/bin/activate && make run
```

### 📦 Build Native App

```bash
# Create standalone app
make build-mac-release

# Find in dist/Sentry AI.app
```

### 🛠️ Development Commands

```bash
make clean          # 🧹 Clean installation
make install        # 📥 Basic install
make install-dev    # 🔧 Dev environment
make run           # ▶️  Run from terminal
make build-mac     # 🔨 Dev build
make build-mac-release  # 📦 Production build
```

### 📦 Build & Distribution

```bash
# Create standalone app
make build-mac-release

# Create DMG for distribution
make create-dmg

# Find in:
# - App: dist/Sentry AI.app
# - DMG: dist/Sentry AI.dmg
```

## 🔧 Setup Guide

### 📸 Camera Access

1. Open System Settings
2. Navigate to Privacy & Security > Camera
3. Enable access for Sentry AI

### 🚀 Auto-Start (Optional)

- Use ⌘L or menu option to enable
- Starts minimized in menu bar

## 🛟 Troubleshooting

### 🔄 Installation Reset

```bash
make clean-all
make install-dev
```

### 🔍 Common Issues

- ✓ Verify camera permissions
- ✓ Check for camera conflicts
- ✓ Confirm system requirements

## 🔒 Privacy First

- 💻 **Local Processing**: All computations stay on your Mac
- 🚫 **Zero Storage**: No image data saved
- 🎯 **Smart Resource Use**:
  - Camera active only when needed
  - Efficient memory management
  - Automatic cleanup

## 📚 Dependencies

- 📸 **OpenCV** (`opencv-python-headless>=4.8.0`)
- 🤖 **MediaPipe** (`mediapipe>=0.10.0`)
- 🍎 **PyObjC-Quartz** (`pyobjc-framework-Quartz>=9.0`)
- 🔝 **Rumps** (`rumps>=0.4.0`)

## 📄 License

This project is protected under the MIT License. See [`LICENSE`](LICENSE) for details.

## 🤝 Contributing

Your contributions make Sentry AI better! Check our [contribution guidelines](CONTRIBUTING.md) to get started.
