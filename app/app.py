from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size = 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from predictor import predict_validity

@app.route('/')
def upload_form():
    return render_template('index.html')

# Handle file upload and prediction
@app.route('/predict', methods=['POST'])
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
        category = predict_validity(filepath)
        return render_template('result.html', category=category)

if __name__ == "__main__":
    app.run(debug=True)
