from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size = 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from predictorPixels import predict_validity as predictPixels
from predictorHTML import predict_validity as predictHTML

@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/pixels')
def pixels():
    return render_template('pixels.html')

@app.route('/html')
def html():
    return render_template('html.html')

# Handle file upload and prediction
@app.route('/predict-pixels', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get prediction
        category = predictPixels(filepath)
        return render_template('result.html', category=category)
    
@app.route('/predict-html', methods=['POST'])
def upload_url():
    if request.method == "POST":
        url = request.form.get('url')

        # Get prediction
        category = predictHTML(url)
        return render_template('result.html', category=category)

if __name__ == "__main__":
    app.run(debug=True)
