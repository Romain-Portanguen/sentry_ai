from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Camera settings
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480
    CAMERA_FPS: int = 30
    FRAME_SKIP: int = 3

    # Detection settings
    FACE_CONFIDENCE: float = 0.5
    MODEL_SELECTION: int = 1
    ABSENCE_THRESHOLD: int = 5
    CHECK_INTERVAL: float = 0.1

    # System settings
    INACTIVITY_THRESHOLD: int = 30_000_000_000  # 30 seconds
