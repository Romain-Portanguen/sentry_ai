import mediapipe as mp
import cv2
import numpy as np
from app.utils.config import Config

class FaceDetector:
    def __init__(self, config: Config):
        self.config = config
        self.detector = mp.solutions.face_detection.FaceDetection(
            min_detection_confidence=config.FACE_CONFIDENCE,
            model_selection=config.MODEL_SELECTION
        )

    def detect(self, frame: np.ndarray) -> bool:
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb_frame)
        return results.detections is not None and len(results.detections) > 0
