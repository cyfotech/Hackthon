# webapp/ml_model/predict.py
import os
from functools import lru_cache

# Use tf.keras so it matches your installed TensorFlow/Keras
from tensorflow import keras

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "report_model.h5")

@lru_cache(maxsize=1)
def get_model():
    """
    Load the model once, on first use (not at import time).
    Raises a clear error if the file is missing.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"ML model file missing at: {MODEL_PATH}\n"
            f"Place 'report_model.h5' in this folder."
        )
    return keras.models.load_model(MODEL_PATH)

def predict_report(input_data):
    """
    Your actual prediction function.
    Update pre/post-processing as per your model.
    """
    model = get_model()
    # Example: adapt this for your real input/output
    import numpy as np
    x = np.array(input_data, dtype="float32")
    preds = model.predict(x)
    return preds
