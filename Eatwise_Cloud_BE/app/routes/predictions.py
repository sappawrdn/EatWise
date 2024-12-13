from flask import Blueprint, request, jsonify
from app.model.predict import preprocess_image, get_prediction_with_threshold, get_nutrition, model, class_names
predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image file uploaded."}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image file selected."}), 400

    try:
        preprocessed_image = preprocess_image(file)
        
        predictions = model.predict(preprocessed_image)[0]
        
        result = get_prediction_with_threshold(predictions, class_names)

        response = {"image_label": result["label"], "confidence": result["confidence"]}

        if result["label"] != "Unknown":
            nutrition = get_nutrition(result["label"])
            response["nutrition_info"] = nutrition or "Nutrition information not found."

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
