from flask import Flask, request, render_template
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size = 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from predictor import predict_validity as predictHTML

@app.route('/')
def landing():
    return render_template('index.html')
    
@app.route('/predict-html', methods=['POST'])
def upload_url():
    if request.method == "POST":
        url = request.form.get('url')

        # Get prediction
        category = predictHTML(url)
        return render_template('result.html', category=category)

if __name__ == "__main__":
    app.run(debug=True)
