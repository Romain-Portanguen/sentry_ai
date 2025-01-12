from setuptools import setup, find_packages
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, 'app', 'public', 'assets')

setup(
    name="sentry-ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python-headless>=4.8.0",
        "mediapipe>=0.10.0",
        "pyobjc-framework-Quartz>=9.0",
        "rumps>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "py2app>=0.28.0",
        ]
    },
    python_requires=">=3.10",
    app=['app/main.py'],
    data_files=[
        ('app/public/assets', [
            os.path.join(ASSETS_PATH, 'MenuBarIcon.icns'),
            os.path.join(ASSETS_PATH, 'AppIcon.png')
        ])
    ],
    options={
        'py2app': {
            'argv_emulation': False,
            'packages': ['cv2', 'mediapipe', 'rumps'],
            'includes': ['numpy', 'mediapipe', 'cv2', 'rumps'],
            'excludes': [
                'sitecustomize', 
                'usercustomize', 
                'site',
                'pip', 
                'setuptools',
                'typing_extensions',
                'pkg_resources',
                '_distutils_hack'
            ],
            'resources': [
                ('app/public/assets', [
                    os.path.join(ASSETS_PATH, 'MenuBarIcon.icns'),
                    os.path.join(ASSETS_PATH, 'AppIcon.png')
                ])
            ],
            'iconfile': os.path.join(ASSETS_PATH, 'AppIcon.png'),
            'strip': False,
            'optimize': 0,
            'plist': {
                'LSUIElement': True,
                'CFBundleName': 'SentryAI',
                'CFBundleDisplayName': 'SentryAI',
                'CFBundleIdentifier': 'com.sentry.ai',
                'CFBundleVersion': '1.0.0',
                'CFBundleShortVersionString': '1.0.0',
                'LSMinimumSystemVersion': '10.13',
                'NSHighResolutionCapable': True,
                'LSMultipleInstancesProhibited': True,
                'NSAppleEventsUsageDescription': 'This app needs to control other applications.',
                'NSSystemAdministrationUsageDescription': 'This app needs to manage startup items.',
                'NSCameraUsageDescription': 'This app needs access to the camera for face detection.',
                'CFBundleDocumentTypes': [],
                'CFBundleTypeRole': 'None',
                'LSBackgroundOnly': True,
                'NSSupportsAutomaticTermination': True,
                'NSDockTilePlugIn': False,
                'com.apple.security.automation.apple-events': True,
                'com.apple.security.temporary-exception.apple-events': [
                    'com.apple.systemevents'
                ]
            }
        }
    }
)
