from flask import Flask, request, render_template, send_from_directory
import os
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def detect_shockwaves(image_path, contrast=1.0, sharpness=0.0):
    # Read and validate image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Failed to read image file")

    # Convert to grayscale and adjust contrast
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=contrast, beta=0)

    # Apply Gaussian blur for noise reduction
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply sharpness using unsharp mask
    if sharpness > 0:
        blurred_sharp = cv2.GaussianBlur(gray, (0, 0), 3.0)
        gray = cv2.addWeighted(gray, 1.0 + sharpness, blurred_sharp, -sharpness, 0)

    # Apply CLAHE for contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)

    # Apply Laplacian filter to detect edges
    laplacian = cv2.Laplacian(clahe_img, cv2.CV_64F)
    laplacian_abs = cv2.convertScaleAbs(laplacian)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(laplacian_abs, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Morphological operations: Dilation to enhance shockwaves
    kernel = np.ones((3,3),np.uint8)
    dilated_edges = cv2.dilate(thresh, kernel, iterations = 1)

    # Find contours to identify shock wave boundaries
    contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw detected contours on a copy of the original image
    result = img.copy()
    cv2.drawContours(result, contours, -1, (0, 255, 0), 2)

    # Convert to monochromatic image for visualization
    mono = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    mono = cv2.equalizeHist(mono) #equalize histogram for better visualization
    return mono

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
            
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
            
        if file:
            # Save original
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + file.filename
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(original_path)
            
            # Process image
            contrast = float(request.form.get('contrast', 1.0))
            sharpness = float(request.form.get('sharpness', 0.0))
            processed_img = detect_shockwaves(original_path, contrast, sharpness)
            
            # Save processed
            processed_filename = "processed_" + filename
            processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
            cv2.imwrite(processed_path, processed_img)
            
            return render_template('upload.html', 
                                   original=filename,
                                   processed=processed_filename)
    
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def send_original(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def send_processed(filename):
    contrast_value = float(request.args.get('contrast', 1.0))
    sharpness_value = float(request.args.get('sharpness', 0.0))
    
    original_filename = filename.replace('processed_', '')
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
    
    processed_img = detect_shockwaves(original_path, contrast_value, sharpness_value)
    processed_filename = "temp_processed_" + filename
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
    cv2.imwrite(processed_path, processed_img)
    return send_from_directory(app.config['PROCESSED_FOLDER'], processed_filename)

if __name__ == '__main__':
    app.run(debug=True) 