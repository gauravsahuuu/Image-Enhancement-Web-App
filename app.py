from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_upload_folder():
    """Clear the uploads folder before saving new files."""
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

@app.route('/')
def index():
    # Clear the uploads folder when the site is accessed
    clear_upload_folder()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Enhance the image quality
        enhanced_image_path = enhance_image(filepath)

        return jsonify({
            'original_url': filepath,
            'enhanced_url': enhanced_image_path
        })

    return jsonify({'error': 'File type not allowed'})

def enhance_image(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Slightly adjust brightness and contrast
    contrast = 1.1  # Slight increase in contrast
    brightness = 10  # Slight increase in brightness
    enhanced_image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

    # Improve pixel quality by reducing noise using a slight bilateral filter
    enhanced_image = cv2.bilateralFilter(enhanced_image, d=9, sigmaColor=75, sigmaSpace=75)

    # Convert to HSV to adjust saturation
    hsv_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2HSV)
    hsv_image[:, :, 1] = cv2.add(hsv_image[:, :, 1], 10)  # Slightly increase saturation

    # Convert back to BGR color space
    enhanced_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    # Save the enhanced image
    enhanced_image_path = image_path.replace('.', '_enhanced.')
    cv2.imwrite(enhanced_image_path, enhanced_image)

    return enhanced_image_path

@app.route('/static/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
