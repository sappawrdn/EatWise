from flask import Blueprint, request, jsonify, make_response
from app.utils.database import get_db_connection, execute_query

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['POST'])
def add_user():
    data = request.json
    conn = get_db_connection()
    query = """
        INSERT INTO users (id, name, age, gender, height, weight, eat_goal)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    execute_query(conn, query, (
        data['id'],
        data['name'], data['age'], data['gender'], 
        data['height'], data['weight'], data['eat_goal']
    ))
    return jsonify({"message": "User added successfully"}), 201

@users_bp.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    
    if user:
        columns = [desc[0] for desc in cursor.description]  
        user_dict = dict(zip(columns, user))  
        
        response = make_response(jsonify(user_dict), 200)
        response.headers['X-Data-Name'] = 'User Data'
        response.headers['X-User-Id'] = user_id
        response.headers['Content-Type'] = 'application/json'
        
        for column, value in user_dict.items():
            response.headers[f'X-User-{column}'] = str(value)  
        
        return response
    
    response = jsonify({"error": "User not found"})
    response.headers['X-Error'] = 'User Not Found'
    response.headers['Content-Type'] = 'application/json'
    return response, 404

@users_bp.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM users"
    cursor.execute(query)
    users = cursor.fetchall()  
    if users:
        columns = [desc[0] for desc in cursor.description]
        
        users_list = [dict(zip(columns, user)) for user in users]
        
        response = make_response(jsonify(users_list), 200)
        response.headers['X-Data-Name'] = 'Users Data'
        response.headers['Content-Type'] = 'application/json'
        
        response.headers['X-Total-Users'] = str(len(users_list)) 
        
        return response
    
    response = jsonify({"error": "Users not found"})
    response.headers['X-Error'] = 'Users Not Found'
    response.headers['Content-Type'] = 'application/json'
    return response, 404

@users_bp.route('/users/<string:user_id>', methods=['PATCH'])
def update_user(user_id):
    update_data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    current_user = cursor.fetchone()
    
    if not current_user:
        return jsonify({"error": "User not found"}), 404
    
    update_fields = []
    update_values = []
    
    allowed_fields = ['name', 'age', 'gender', 'height', 'weight', 'eat_goal']
    
    for field in allowed_fields:
        if field in update_data and update_data[field] is not None:
            update_fields.append(f"{field} = %s")
            update_values.append(update_data[field])
    
    if not update_fields:
        return jsonify({"message": "No updates provided"}), 200
    
    update_values.append(user_id)
    
    update_query = f"""
        UPDATE users 
        SET {', '.join(update_fields)}
        WHERE id = %s
    """
    
    try:
        execute_query(conn, update_query, tuple(update_values))
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to update user", "details": str(e)}), 500