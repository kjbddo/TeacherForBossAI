from langchain_openai import OpenAIEmbeddings
from flask import Flask, request, jsonify, make_response
from db_setup import PDFConverter, VectorDBSetup
from qa_service import QAService
import os
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException, Timeout
import logging
from flask_cors import CORS


# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

# 환경 변수 설정
vector_db_path = 'data/vector_db'
txt_dir_path = 'data/txt'
pdf_dir_path = 'data/pdf'  # 이곳에 DB에 저장하고 싶은 문서 넣기
base_target_url = os.getenv('TARGET_SERVER_URL', 'https://dev.teacherforboss.store/board/teacher/questions')  # 기본 URL 설정
openai_api_key = os.getenv('OPENAI_API_KEY')
debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

# OpenAI API 키 설정 확인
if not openai_api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
os.environ['OPENAI_API_KEY'] = openai_api_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PDF 변환 및 벡터 DB 설정 엔드포인트
@app.route(f'/setup_aidb', methods=['POST'])
def setup_db():
    PDFConverter.convert_pdf_to_text(pdf_dir=pdf_dir_path, txt_dir=txt_dir_path)
    vector_db_setup = VectorDBSetup(embedding=OpenAIEmbeddings())
    response = vector_db_setup.setup_vector_db(txt_directory=txt_dir_path, db_directory=vector_db_path)
    return jsonify(response)

# 질의응답 엔드포인트
@app.route(f"/<int:questionId>/answers", methods=['POST'])
def ask(questionId):
    logger.info(f"질문 ID {questionId}에 대한 답변 요청 시작")
    logger.info(f"수신된 헤더: {request.headers}")
    
    # Authorization 헤더 확인
    auth_header = request.headers.get("Authorization")
    logger.info(f"Authorization 헤더: {auth_header}")
    
    if not auth_header:
        return jsonify({"error": "Authorization 헤더가 필요합니다."}), 401
    token = auth_header  # 전체 헤더를 그대로 사용

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
    qa_service = QAService(db_directory=vector_db_path)
    response_body = qa_service.qacall(query_category, query_content, query_extra_data)

    # 결과 데이터를 questionId 포함한 target_server_url로 전송
    target_server_url = f"{base_target_url}/{query_id}/answers"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {
        "answer": response_body
    }

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
        logger.info(f"외부 서버로 답변 전송 시도: {target_server_url}")
        external_response = session.post(
            target_server_url, 
            headers=headers, 
            json=payload,
            timeout=30
        )
        logger.info(f"외부 서버 응답 수신: {external_response.status_code}")
        external_response.raise_for_status()
        
        response_data = external_response.json()
        # 응답 형식 검증
        if not all(key in response_data for key in ['isSuccess', 'code', 'message', 'result']):
            return jsonify({
                "status": "error",
                "message": "서버 응답 형식이 올바르지 않습니다."
            }), 500
        
        return jsonify(response_data), external_response.status_code
    except Timeout:
        return jsonify({
            "status": "error",
            "message": "요청 시간이 초과되었습니다."
        }), 504
    except RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"외부 서버 요청 실패: {str(e)}"
        }), 500
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    app.run(debug=debug_mode, port=5000)