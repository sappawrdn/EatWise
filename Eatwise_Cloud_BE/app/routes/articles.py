from flask import Blueprint, request, make_response, jsonify
from app.utils.database import get_db_connection, execute_query
from app.utils.gcloud import upload_to_bucket
from app.utils.config import Config  

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/articles', methods=['GET'])
def get_articles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles")
    rows = cursor.fetchall()
    
    articles_data = []
    
    for row in rows:
        article_id, title, description, content, image_url, timestamp = row
        
        articles_data.append({
            'id': article_id,
            'title': title,
            'description': description,
            'content': content,
            'image_url': image_url,
            'timestamp': timestamp
        })
    
    response = jsonify(articles_data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['X-Data-Name'] = 'Articles_List'
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response, 200

@articles_bp.route('/articles', methods=['POST'])
def add_article():
    data = request.form  
    file = request.files.get('image')  
    
    if not file:
        return jsonify({"error": "No image file provided"}), 400

    try:
        image_url = upload_to_bucket(Config.BUCKET_NAME, file) 
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

    conn = get_db_connection()
    query = "INSERT INTO articles (title, description, content, image_url) VALUES (%s, %s, %s, %s)"
    
    try:
        execute_query(conn, query, (
            data['title'], 
            data['description'], 
            data['content'], 
            image_url
        ))
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500

    response = jsonify({
        "message": "Article added successfully",
        "image_url": image_url
    })
    
    response.headers['X-Operation'] = 'Article_Creation'
    
    return response, 201