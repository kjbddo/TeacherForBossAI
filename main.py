from flask import Flask
from flask_cors import CORS
from config.config import Config
from app.routes.qa_routes import qa_bp
from app.routes.setup_routes import setup_bp
from utils.error_handlers import register_error_handlers
import logging

def create_app():
    app = Flask(__name__)
    
    # CORS 설정
    CORS(app)
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 설정 초기화
    Config.init_app(app)
    
    # 블루프린트 등록
    app.register_blueprint(qa_bp)
    app.register_blueprint(setup_bp)
    
    # 에러 핸들러 등록
    register_error_handlers(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG_MODE, port=5000)