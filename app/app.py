from flask import Flask, request, render_template
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size = 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from predictor import predict_validity as predictHTML

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        url = request.form.get('url')

        # Get prediction
        category = predictHTML(url)
        return render_template('index.html', category=category if category != None else "Sorry, no results")
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
