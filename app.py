from langchain_openai import OpenAIEmbeddings
from flask import Flask, request, jsonify, make_response
from db_setup import PDFConverter, VectorDBSetup
from qa_service import QAService
import os
import requests
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)

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
    # Authorization 헤더 확인
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Authorization 헤더가 필요합니다."}), 401
    token = auth_header.split(" ")[1]

    # 요청 본문 데이터 가져오기
    data = request.json
    if not data:
        return jsonify({"error": "유효한 요청 본문이 필요합니다."}), 400

    # 요청 데이터 파싱
    query_content = data.get("content")
    query_category = data.get("category")
    query_extra_data = data.get("extraData")

    # QA 서비스 호출
    qa_service = QAService(db_directory=vector_db_path)
    response_body = qa_service.qacall(query_category, query_content, query_extra_data)

    # 결과 데이터를 questionId 포함한 target_server_url로 전송
    target_server_url = f"{base_target_url}/{questionId}/answers"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "questionId": questionId,
        "response": response_body
    }

    try:
        external_response = requests.post(target_server_url, headers=headers, json=payload)
        external_response.raise_for_status()  # 오류가 발생하면 예외를 일으킴

        return jsonify({
            "status": "success",
            "forwarded_response": external_response.json()
        }), external_response.status_code
    except requests.exceptions.RequestException as e:
        # 외부 서버 요청 오류 처리
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=debug_mode)
