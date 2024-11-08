from PIL import Image
import numpy as np
from keras import models
import tensorflow as tf

model = tf.saved_model.load("../notebooks/pixelsConvolutional")
infer = model.signatures["serving_default"]

def predict_validity(image_path):
    img = Image.open(image_path)

    # Resize the image to 48x48 (size expected by the model)
    img = img.resize((48, 48))

    # Convert to grayscale (L mode)
    img = img.convert('L')

    # Convert the image to a numpy array
    img_array = np.array(img)

    # Add an extra dimension for the channel (i.e., (1, 48, 48, 1))
    img_array = np.expand_dims(img_array, axis=-1)  # Shape becomes (48, 48, 1)

    # Add batch dimension (i.e., (1, 48, 48, 1))
    img_array = np.expand_dims(img_array, axis=0)  # Shape becomes (1, 48, 48, 1)

    # Normalize to range [0, 1] and convert to float32
    # img_array = img_array.astype('float32') / 255.0  # Normalize

    # Convert to tensor
    input_tensor = tf.convert_to_tensor(img_array.astype('float32'), dtype=tf.float32)
    
    # Make prediction
    predictions = infer(input_tensor)

    predicted_class = np.argmax(predictions['output_0'])

    return predicted_class