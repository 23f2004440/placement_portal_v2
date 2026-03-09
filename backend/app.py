from flask import Flask
from models import db
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    from utils.cache import cache
    cache.init_app(app)

    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.company_routes import company_bp
    from routes.student_routes import student_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    @app.route('/')
    def index():
        return {"status": "success", "message": "PPA API is running at /api"}, 200

    @app.route('/api/ping')
    def ping():
        return {"status": "success", "message": "PPA API is running"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
