from flask import Blueprint, jsonify
from app.utils.database import get_db_connection

histories_bp = Blueprint('histories', __name__)

@histories_bp.route('/histories/<int:user_id>', methods=['GET'])
def get_histories(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT food_name, prediction_date 
        FROM predict_history 
        WHERE user_id = %s 
        ORDER BY prediction_date DESC
    """
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    return jsonify(rows), 200
