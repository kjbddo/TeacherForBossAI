'''
from flask import Blueprint, jsonify
from app.services.qa_service import QAService
from config.config import Config
import os
import psutil
import datetime

health_bp = Blueprint('health', __name__)


def check_vector_db():
    """벡터 DB 상태 확인"""
    try:
        # 벡터 DB 디렉토리 존재 여부 확인
        if not os.path.exists(Config.VECTOR_DB_PATH):
            return False, "벡터 DB 디렉토리가 존재하지 않습니다."
        
        # 벡터 DB 연결 테스트
        qa_service = QAService(Config.VECTOR_DB_PATH)
        qa_service.retrieve_relevant_text("test", num_results=1)
        return True, "정상"
    except Exception as e:
        return False, str(e)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """시스템 상태 체크 엔드포인트"""
    
    # 시스템 리소스 상태 확인
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    
    # 벡터 DB 상태 확인
    vector_db_status, vector_db_message = check_vector_db()
    
    health_status = {
        "status": "healthy" if vector_db_status else "unhealthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "services": {
            "vector_db": {
                "status": "healthy" if vector_db_status else "unhealthy",
                "message": vector_db_message
            }
        },
        "system": {
            "cpu_usage": f"{cpu_usage}%",
            "memory": {
                "total": f"{memory.total / (1024 * 1024 * 1024):.2f}GB",
                "used": f"{memory.used / (1024 * 1024 * 1024):.2f}GB",
                "free": f"{memory.free / (1024 * 1024 * 1024):.2f}GB",
                "percent": f"{memory.percent}%"
            },
            "disk": {
                "total": f"{disk.total / (1024 * 1024 * 1024):.2f}GB",
                "used": f"{disk.used / (1024 * 1024 * 1024):.2f}GB",
                "free": f"{disk.free / (1024 * 1024 * 1024):.2f}GB",
                "percent": f"{disk.percent}%"
            }
        }
    }
    
    status_code = 200 if vector_db_status else 503
    return jsonify(health_status), status_code 
'''