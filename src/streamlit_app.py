import streamlit as st
import cv2
import mediapipe as mp
import time
import numpy as np

#pip install streamlit opencv-python mediapipe pyttsx3 FuzzyTM numpy==1.23.5 scipy==1.10.1
# Streamlit run EyeCare\src\streamlit_app.py --server.port 8502


# Load face and eye detection
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)
mp_draw = mp.solutions.drawing_utils

# EAR threshold
EYE_AR_THRESHOLD = 0.3
CLOSED_SECONDS_TRIGGER = 5
BREAK_INTERVAL = 30 * 60  # 30 minutes
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

# Title
st.title("👁️ Real-Time Eye Blink & Relaxation Monitor")
st.markdown("Stay focused and take breaks to relax your eyes! 🚀")

# Start camera
run = st.checkbox('Start Monitoring')

frame_placeholder = st.empty()
status_placeholder = st.empty()

if run:
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to access camera!")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:
            for face_landmarks in result.multi_face_landmarks:
                ratio = eye_aspect_ratio(face_landmarks.landmark, LEFT_EYE, RIGHT_EYE)
                cv2.putText(frame, f"EAR: {ratio:.2f}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                # Check if eyes are closed for too long
                if ratio < EYE_AR_THRESHOLD:
                    if start_closed is None:
                        start_closed = time.time()
                    elif time.time() - start_closed > CLOSED_SECONDS_TRIGGER:
                        status_placeholder.error("😴 Sleeping detected! Please wake up!")
                        start_closed = None
                else:
                    start_closed = None

        # Suggest break every 30 minutes
        if time.time() - last_break_time > BREAK_INTERVAL:
            st.warning("🧘 Time to take a deep breath and close your eyes for 1 minute!")
            last_break_time = time.time()

        # Display Frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame, channels="RGB")

        # Allow stopping
        if not run:
            break

    cap.release()
