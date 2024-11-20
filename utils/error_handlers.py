from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "요청한 리소스를 찾을 수 없습니다."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"서버 오류 발생: {str(error)}")
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"예상치 못한 오류 발생: {str(error)}")
        return jsonify({"error": "예상치 못한 오류가 발생했습니다."}), 500