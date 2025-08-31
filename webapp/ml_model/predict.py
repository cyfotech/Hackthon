from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# Load model
model_path = os.path.join(os.path.dirname(__file__), 'report_model.h5')
model = load_model(model_path)

# Class mapping
class_labels = ['cutting','dumping','reclamation','damage','restoration']

def predict_report(img_path):
    img = image.load_img(img_path, target_size=(224,224))
    img_array = image.img_to_array(img)/255.0
    img_array = np.expand_dims(img_array, axis=0)
    pred = model.predict(img_array)
    pred_class = np.argmax(pred, axis=1)[0]
    return class_labels[pred_class]
