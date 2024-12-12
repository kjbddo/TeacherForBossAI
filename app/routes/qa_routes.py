from flask import Blueprint, request, jsonify
from app.middleware.auth import token_required
from app.services.qa_service import QAService
from config.config import Config
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)
qa_bp = Blueprint('qa', __name__)

# QA 서비스 인스턴스 생성
#qa_service = QAService(db_directory=Config.VECTOR_DB_PATH)
qa_service = QAService()

@qa_bp.route('/<int:questionId>/answers', methods=['POST'])
@token_required
def ask(questionId, token):
    logger.info(f"질문 ID {questionId}에 대한 답변 요청 시작")
    
    # 요청 본문 데이터 가져오기
    data = request.json
    if not data:
        return jsonify({"error": "유효한 요청 본문이 필요합니다."}), 400

    # 요청 데이터 파싱
    query_id = data.get("id")
    query_content = data.get("content")
    query_category = data.get("category")
    query_extra_data = data.get("extraData")

    # QA 서비스 호출
    response_body = qa_service.qacall(query_category, query_content, query_extra_data)

    # 결과 데이터를 questionId 포함한 target_server_url로 전송
    target_server_url = f"{Config.BASE_TARGET_URL}/{query_id}/answers"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {
        "answer": response_body
    }

    logger.info(f"외부 서버 URL: {target_server_url}")
    logger.info(f"외부 서버 헤더: {headers}")
    logger.info(f"외부 서버 페이로드: {payload}")

    # 재시도 설정
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        external_response = session.post(
            target_server_url, 
            headers=headers, 
            json=payload,
            timeout=30
        )
        external_response.raise_for_status()
        return jsonify(external_response.json()), external_response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"외부 서버 요청 실패: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"외부 서버 요청 실패: {str(e)}"
        }), 500