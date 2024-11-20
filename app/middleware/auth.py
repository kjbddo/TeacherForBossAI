from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        logger.info(f"Authorization 헤더: {auth_header}")
        
        if not auth_header:
            return jsonify({"error": "Authorization 헤더가 필요합니다."}), 401
        
        # 토큰을 데코레이터된 함수에 전달
        kwargs['token'] = auth_header
        return f(*args, **kwargs)
    return decorated