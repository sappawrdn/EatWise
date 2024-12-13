from flask import Flask
from flask_cors import CORS  
from app.routes.articles import articles_bp
from app.routes.predictions import predictions_bp
from app.routes.users import users_bp

def create_app():
    app = Flask(__name__)
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    app.register_blueprint(articles_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(users_bp)
    
    app.config.from_object('app.utils.config.Config')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)