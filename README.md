# 🛡️ Sentry AI - Privacy Guardian

Sentry AI is an intelligent security application that automatically protects your privacy by locking your Mac when you step away from your workstation. Using artificial intelligence-based face detection, Sentry ensures discreet and efficient surveillance.

## 🌟 Features

- **AI Face Detection**:
  - MediaPipe implementation for accurate detection
  - Performance optimization with intelligent resizing
  - Selective frame analysis to save resources

- **Smart Locking**:
  - Automatic locking after 5 seconds without face detection
  - Control + Command + Q key combination simulation
  - Automatic resume after unlock

- **Advanced Resource Management**:
  - Automatic sleep mode during inactivity
  - Resolution optimization (640x480)
  - 1-in-3 frame analysis to reduce CPU load
  - Camera deactivation during inactive periods

- **System Monitoring**:
  - macOS sleep mode detection
  - User activity monitoring
  - System interruption handling

## 🛠 Installation Guide

### Prerequisites

1. **System Requirements**
   - macOS 10.15 or later
   - Python 3.10 (required for MediaPipe compatibility)
   - pip (Python package installer)
   - Camera permissions

2. **Python Installation**

   ```bash
   # Install Python 3.10 using Homebrew
   brew install python@3.10

   # Verify installation
   python3.10 --version
   ```

### Quick Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/your-username/sentry.git
cd sentry

# Install and run in one command
make install && source .venv/bin/activate && make run
```

### Alternative Installation Methods

1. **Manual Installation**

   ```bash
   # Create virtual environment
   python3.10 -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Development Installation**

   ```bash
   # Install with development tools
   make install-dev && source .venv/bin/activate
   ```

### Useful Make Commands

```bash
make clean          # Clean previous installation
make install        # Fresh installation
make install-dev    # Install with development tools
make run           # Run the application
make format        # Format code with black
make lint          # Check code with flake8
make test          # Run tests
```

### Post-Installation Setup

1. **Camera Permissions**
   - Open System Preferences > Security & Privacy > Camera
   - Enable camera access for Terminal/IDE

2. **First Run**

   ```bash
   # After installation, simply run:
   make run
   ```

### Troubleshooting

1. **Installation Issues**

   ```bash
   # Complete reinstallation
   make clean
   make install && source .venv/bin/activate && make run
   ```

2. **Dependencies Issues**

   ```bash
   # From activated environment
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. **Launch**

   ```bash
   python3 sentry.py
   ```

2. **Application States**
   - 🟢 **Active Mode**: Face detection running
   - 🟡 **Sleep Mode**: Camera disabled, minimal monitoring
   - 🔴 **Locked Mode**: Waiting for unlock

3. **Commands**
   - `Ctrl + C`: Clean application shutdown

## ⚙️ Technical Configuration

### Main Parameters

```python
absence_threshold = 5    # Time before locking (seconds)
frame_skip = 3          # Analyze 1 frame out of 3
check_interval = 0.1    # Check interval (seconds)
```

### Camera Parameters

```python
CAP_PROP_FRAME_WIDTH = 640   # Capture width
CAP_PROP_FRAME_HEIGHT = 480  # Capture height
CAP_PROP_FPS = 30           # Frames per second
```

## 🔒 Security and Privacy

- **Local Processing**: No data sent over the Cloud ☁️
- **No Storage**: Real-time image processing
- **Intelligent Management**:
  - Camera deactivation during inactivity
  - System resource release
  - Automatic memory cleanup

## 📋 Dependencies

- **OpenCV** (`opencv-python-headless>=4.8.0`)
  - Optimized video capture and processing
  - Headless version for reduced memory footprint

- **MediaPipe** (`mediapipe>=0.10.0`)
  - AI-powered face detection
  - Performance-optimized model

- **PyObjC-Quartz** (`pyobjc-framework-Quartz>=9.0`)
  - macOS interaction
  - Screen lock management

## 🔗 Useful Links

- **MediaPipe Documentation**
  - [MediaPipe Face Detection](https://developers.google.com/mediapipe/solutions/vision/face_detector)

- **OpenCV Resources**
  - [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
  - [Camera Capture Guide](https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html)

- **macOS Development**
  - [PyObjC Documentation](https://pyobjc.readthedocs.io/en/latest/)
  - [Apple Developer Documentation](https://developer.apple.com/documentation/)

## 🐛 Troubleshooting

1. **Camera Issues**
   - Check system permissions
   - Ensure no other application is using the camera
   - Verify `Info.plist` file presence

2. **Performance**
   - Increase `frame_skip` to reduce CPU load
   - Check system activity with Activity Monitor
   - Ensure no heavy processes are running

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 👥 Contributing

Contributions are welcome! Please check our contribution guidelines for more information.
