from setuptools import setup, find_packages

setup(
    name="sentry-ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python-headless>=4.8.0",
        "mediapipe>=0.10.0",
        "pyobjc-framework-Quartz>=9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
        ]
    },
    python_requires=">=3.10",
)
