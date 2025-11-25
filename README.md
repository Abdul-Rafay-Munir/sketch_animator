## 📸 Image to Sketch Animator

A Python desktop application that converts an image into a **live sketch animation** using OpenCV and Tkinter.
It detects contours in the image and draws them gradually to create a smooth animation effect.

---

## 🚀 Features

* Load any JPG/PNG/BMP image
* Auto-resizes for performance
* Extracts sketch using OpenCV edge detection
* Animates the drawing line-by-line
* Adjustable animation speed
* Start / Stop / Reset controls
* Clean modern Tkinter UI
* Thread-safe animation (no GUI freezing)

---

## Installation

### **1. Clone the repository**

```sh
git clone https://github.com/Abdul-Rafay-Munir/sketch_animator.git
cd YOUR_REPOSITORY
```

### **2. Create a virtual environment**

Windows:

```sh
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:

```sh
python3 -m venv venv
source venv/bin/activate
```

### **3. Install dependencies**

```sh
pip install -r requirements.txt
```

---

## Run the App

```sh
python app.py
```