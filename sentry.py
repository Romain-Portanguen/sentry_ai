import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import time
import cv2
import mediapipe as mp
import Quartz
from threading import Timer

print("Initializing Face Detection... 🚀")
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    min_detection_confidence=0.5, model_selection=1  # 0=court range, 1=long range
)


def lock_screen():
    """Lock the user session by simulating Control + Command + Q."""
    print("Sentry protects your privacy. Session lock... 🔒")
    applescript = """
    tell application "System Events" to keystroke "q" using {control down, command down}
    """
    os.system(f"osascript -e '{applescript}'")
    return True


def is_sleep_mode():
    """Check if the Mac enters sleep mode or shuts down."""
    try:
        power_status = os.popen("pmset -g ps").read()
        return 'sleep' in power_status.lower() or 'sleeping' in power_status.lower()
    except:
        return False


def wait_for_wake(cap=None):
    """Wait for the system to fully wake up."""
    print("Sentry is in standby mode. Waiting for user activity... 💤")
    
    if cap and cap.isOpened():
        cap.release()
        cv2.destroyAllWindows()
    
    while True:
        power_status = os.popen("pmset -g ps").read()
        if 'AC Power' in power_status and not is_sleep_mode():
            time.sleep(2)
            print("System is active again! Resuming surveillance... ✨")
            return True
        time.sleep(1)

def is_user_inactive():
    """Detect user inactivity via keyboard/mouse idle time."""
    idle_time = int(
        os.popen("ioreg -c IOHIDSystem | grep HIDIdleTime").read().split()[-1]
    )
    return idle_time > 30000000000  # Inactive for 30 seconds (30 * 10^9 ns)


def detect_face(frame):
    """Detect faces in a given frame."""
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb_frame)
    return results.detections is not None and len(results.detections) > 0


def start_camera():
    """Initialize the camera with optimized settings."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Sentry cannot access the camera. Please check your camera permissions.")
        exit()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    return cap


# Optimized parameters
absence_timer = 0
absence_threshold = 5  # Time before locking (in seconds)
frame_skip = 3  # Analyze 1 frame on 3
check_interval = 0.1  # Interval between checks


class ResourceManager:
    def __init__(self):
        self.inactive_timer = None
        self.camera_active = True

    def schedule_camera_shutdown(self, cap):
        """Schedule camera shutdown after inactivity."""
        if self.inactive_timer:
            self.inactive_timer.cancel()
        self.shutdown_camera(cap)
        self.camera_active = False

    def shutdown_camera(self, cap):
        """Shutdown the camera cleanly."""
        if cap and cap.isOpened():
            cap.release()
            cv2.destroyAllWindows()
            self.camera_active = False

    def restart_camera(self):
        """Restart the camera."""
        self.camera_active = True
        return start_camera()

    def cleanup(self):
        """Clean up resources."""
        if self.inactive_timer:
            self.inactive_timer.cancel()


def is_screen_locked():
    """Check if the screen is locked via Quartz."""
    current_dict = Quartz.CGSessionCopyCurrentDictionary()
    if current_dict:
        return current_dict.get("CGSSessionScreenIsLocked", False)
    return False


def wait_for_unlock(cap=None):
    """Wait for the user to unlock their session."""
    print("Session locked. Sentry is waiting for unlock... 🔓")
    time.sleep(2)

    if cap:
        cap.release()
        cv2.destroyAllWindows()

    while is_screen_locked():
        time.sleep(1)

    time.sleep(1)
    print("Session unlocked! Sentry is resuming surveillance... ✨")
    return True


def main():
    global absence_timer
    resource_manager = ResourceManager()

    try:
        while True:
            cap = start_camera()
            frame_count = 0
            absence_timer = 0
            last_check_time = time.time()

            print("Hey there, Sentry is watching you... 🔎")
            while True:
                current_time = time.time()
                if current_time - last_check_time < check_interval:
                    continue
                last_check_time = current_time

                if is_sleep_mode():
                    if wait_for_wake():
                        break
                    continue

                if is_user_inactive():
                    if resource_manager.camera_active:
                        print("User inactive. Sentry is stopping the camera... 📴")
                        resource_manager.schedule_camera_shutdown(cap)
                    time.sleep(1)
                    continue
                elif not resource_manager.camera_active:
                    print(
                        "User activity detected. Sentry is restarting the camera... 📴"
                    )
                    cap = resource_manager.restart_camera()
                    continue

                ret, frame = cap.read()
                if not ret:
                    print(
                        "Sentry cannot capture video. Please check your camera permissions."
                    )
                    break

                frame_count += 1
                if frame_count % frame_skip != 0:
                    continue

                has_face = detect_face(frame)
                if has_face:
                    absence_timer = 0
                else:
                    absence_timer += 1

                if absence_timer >= absence_threshold:
                    print("No face detected. Sentry is locking the screen... 🔒")
                    resource_manager.shutdown_camera(cap)
                    lock_screen()
                    wait_for_unlock(cap)
                    break

    except KeyboardInterrupt:
        print("\nSentry is shutting down... 🔴")
        raise
    finally:
        resource_manager.cleanup()
        if "cap" in locals() and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSentry is shutting down... 🔴")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
