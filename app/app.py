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
        prediction = predictHTML(url)
                
        if prediction is None or len(prediction) <= 0:
            text = "Sorry, no results"
        else:
            predictions = list(map(lambda item: item['prediction'], prediction))
            text = 'Yes!' if all(predictions) == 1 else 'No, here are the problem areas:'
    
        return render_template('index.html', text=text)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
