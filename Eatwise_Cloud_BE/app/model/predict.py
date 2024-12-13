import numpy as np
import tensorflow as tf
import pandas as pd
import io
import logging

physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    tf.config.set_visible_devices([], 'GPU')  

model = tf.keras.models.load_model('app/model/model.h5')

df_labels = pd.read_csv('https://raw.githubusercontent.com/rivestudy/Eatwise_Cloud_BE/refs/heads/main/app/model/food_labels.csv')
df_nutrition = pd.read_csv('https://raw.githubusercontent.com/rivestudy/Eatwise_Cloud_BE/refs/heads/main/app/model/nutritiondata.csv')

index_to_label = df_labels.set_index('Index')['Label'].to_dict()

class_names = df_nutrition['food'].str.strip().str.lower().unique().tolist()

def preprocess_image(file_stream):
    """Preprocess image for prediction."""
    try:
        file_bytes = io.BytesIO(file_stream.read())
        img = tf.keras.utils.load_img(file_bytes, target_size=(224, 224))
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
        return np.expand_dims(img_array, axis=0)
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        raise ValueError("Image preprocessing failed.")

def get_prediction_with_threshold(predictions, class_names, threshold=80):
    try:
        max_confidence_idx = np.argmax(predictions)
        max_confidence_score = predictions[max_confidence_idx] * 100
        if max_confidence_score >= threshold:
            label = index_to_label.get(max_confidence_idx, "Unknown")
            return {
                "label": label.replace('_', ' ').title(),
                "confidence": max_confidence_score
            }
        return {
            "label": "Unknown",
            "confidence": 0.0
        }
    except Exception as e:
        logging.error(f"Error in prediction: {str(e)}")
        return {
            "label": "Error",
            "confidence": 0.0
        }

def get_nutrition(label):
    try:
        normalized_label = label.strip().lower()
        row = df_nutrition[df_nutrition['food'].str.strip().str.lower() == normalized_label]
        
        if not row.empty:
            nutrition_info = {
                key.lower(): int(value) if isinstance(value, (np.int64, np.float64)) and value.is_integer() else value
                for key, value in row.iloc[0].items() if key != 'food'
            }
            return nutrition_info
        return None
    except Exception as e:
        logging.error(f"Error fetching nutrition info: {str(e)}")
        return None