from PIL import Image
import numpy as np
import tensorflow as tf

from model import Model  
  
model = tf.saved_model.load("../notebooks/HTMLConvolutional")
infer = model.signatures["serving_default"]

def predict_validity(url):
    custom_model = Model()  
    elements = custom_model.scrape_site(url)
        
    if elements is None or (hasattr(elements, '__len__') and len(elements) == 0):
        return None
    
    # Stack all the images into a batch
    batch_elements = tf.stack(elements)
    batch_elements = tf.cast(batch_elements, tf.float32)

    # Perform inference
    predictions = infer(batch_elements)
    predicted_classes = np.argmax(predictions['output_0'], axis=1)
    predictions = custom_model.custom_infer(predictions, predicted_classes)
        
    custom_model.close_driver()
    custom_model.cleanup()

    return predictions
