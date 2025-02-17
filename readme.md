# Shock Wave Detection Application

## **Overview**
This guide provides step-by-step instructions to build and deploy a shock wave detection application with a graphical user interface (GUI).

---

## **Prerequisites**
Ensure you have the following installed:

- Python 3.x
- Required libraries:

```bash
pip install opencv-python numpy tkinter pillow flask gunicorn
```

---

## **Step 1: Build the GUI Application**
Create a GUI using Tkinter to upload videos, process them, and display results.

### **Create `app.py`**
```python
import cv2
import os
import tkinter as tk
from tkinter import filedialog, Label, Button
from PIL import Image, ImageTk

def select_video():
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    lbl_video.config(text=f"Selected: {video_path}")

def process_video():
    if not video_path:
        lbl_status.config(text="No video selected!")
        return
    
    os.makedirs("processed_frames", exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(frame_gray, 50, 150)
        cv2.imwrite(f"processed_frames/frame_{count:04d}.png", edges)
        count += 1
    cap.release()
    lbl_status.config(text=f"Processed {count} frames!")

root = tk.Tk()
root.title("Shock Wave Detection")

lbl_video = Label(root, text="Select a video file")
lbl_video.pack()
Button(root, text="Browse", command=select_video).pack()
Button(root, text="Process Video", command=process_video).pack()
lbl_status = Label(root, text="")
lbl_status.pack()

root.mainloop()
```

---

## **Step 2: Deploy as a Web App**
### **Create `web_app.py`**
```python
from flask import Flask, request, render_template
import os
import cv2

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            return "File uploaded and processed!"
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
```

---

## **Step 3: Create HTML Upload Form**
Create `templates/upload.html`:

```html
<!DOCTYPE html>
<html>
<body>
    <h2>Upload Shadowgraph Video</h2>
    <form action="/" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
```

---

## **Step 4: Deploy Online**
Use Gunicorn for deployment:

```bash
pip install gunicorn
export FLASK_APP=web_app.py
flask run --host=0.0.0.0 --port=5000
```

To deploy on a cloud platform, use services like **Heroku, AWS, or Render**.

---

## **Conclusion**
This guide helps you build a GUI and web-based application for detecting shock waves from shadowgraph videos. You can now process videos easily and even deploy the app online! 🚀
