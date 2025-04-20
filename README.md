# EyeCare 👁️💤

A real-time Eye Care Detection system using **Streamlit** and **MediaPipe**.  
It helps detect signs of eye fatigue, drowsiness, and reminds you to take breaks — perfect for students, developers, and anyone spending long hours on screens!

## 🚀 Features
- **Real-time eye monitoring** using your webcam.
- **Sleep detection** using Eye Aspect Ratio (EAR).
- **Break reminders** after continuous activity.
- **Inspirational quotes** when sleep or fatigue is detected.

## 🛠️ Tech Stack
- Python 🐍
- Streamlit 🎈
- MediaPipe 🖐️
- OpenCV 📸

## 📷 How It Works
- The webcam captures live video frames.
- Eye landmarks are detected using MediaPipe.
- Eye Aspect Ratio (EAR) is calculated.
- If EAR drops below a threshold → Sleep detected!
- A buzzer alarm + motivational quote is displayed.

## 🏁 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Devil9816/EyeCare.git
cd EyeCare

