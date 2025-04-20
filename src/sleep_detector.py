import cv2
import mediapipe as mp
import time
import pyttsx3
import tkinter as tk
from threading import Thread

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Load face and eye detection
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)
mp_draw = mp.solutions.drawing_utils

# EAR threshold
EYE_AR_THRESHOLD = 0.3
CLOSED_SECONDS_TRIGGER = 5
BREAK_INTERVAL = 1 * 60  # 30 minutes
start_closed = None
last_break_time = time.time()

# Eye landmark indices for MediaPipe
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

# Function to calculate Eye Aspect Ratio
def eye_aspect_ratio(landmarks, left_ids, right_ids):
    def distance(p1, p2):
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5

    left = [landmarks[i] for i in left_ids]
    right = [landmarks[i] for i in right_ids]
    left_ear = (distance(left[1], left[5]) + distance(left[2], left[4])) / (2.0 * distance(left[0], left[3]))
    right_ear = (distance(right[1], right[5]) + distance(right[2], right[4])) / (2.0 * distance(right[0], right[3]))
    return (left_ear + right_ear) / 2.0

# Show break reminder popup + speak message
def show_break_popup():
    def popup():
        root = tk.Tk()
        root.title("Relax Reminder")
        root.geometry("400x200")
        root.configure(bg="lightyellow")

        label = tk.Label(root, text="⏳ Take a 1-minute break!\nClose your eyes & breathe deeply 😌",
                         font=("Helvetica", 14), bg="lightyellow")
        label.pack(pady=40)

        # Speak the reminder
        engine.say("Please close your eyes and take a deep breath for one minute.")
        engine.runAndWait()

        # Auto close after 1 minute
        def close_after_minute():
            time.sleep(60)
            root.destroy()

        Thread(target=close_after_minute, daemon=True).start()
        root.mainloop()

    Thread(target=popup, daemon=True).start()

# Start webcam
cap = cv2.VideoCapture(0)
print("Monitoring started. Press ESC to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            ratio = eye_aspect_ratio(face_landmarks.landmark, LEFT_EYE, RIGHT_EYE)
            cv2.putText(frame, f"EAR: {ratio:.2f}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            if ratio < EYE_AR_THRESHOLD:
                if start_closed is None:
                    start_closed = time.time()
                elif time.time() - start_closed > CLOSED_SECONDS_TRIGGER:
                    print("Sleeping detected! Triggering alarm.")
                    engine.say("Wake up! Stay focused.")
                    engine.runAndWait()
                    start_closed = None
            else:
                start_closed = None

    # Suggest break every 30 min
    if time.time() - last_break_time > BREAK_INTERVAL:
        show_break_popup()
        last_break_time = time.time()

    cv2.imshow("Eye Monitor", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
