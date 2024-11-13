from langchain_openai import OpenAIEmbeddings
from flask import Flask, request, jsonify, make_response
from db_setup import PDFConverter, VectorDBSetup
from qa_service import QAService
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# 환경 변수 설정
vector_db_path = 'data/vector_db'
txt_dir_path = 'data/txt'
pdf_dir_path = 'data/pdf' #이곳에 DB에 저장하고 싶은 문서 넣기
base_url = os.getenv('BASE_URL', '/board/teacher/questions')  # BASE_URL 기본값 설정
openai_api_key = os.getenv('OPENAI_API_KEY')
debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

# OpenAI API 키 설정 확인
if not openai_api_key:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
os.environ['OPENAI_API_KEY'] = openai_api_key

# PDF 변환 및 벡터 DB 설정 엔드포인트
@app.route(f'{base_url}/setup_aidb', methods=['POST'])
def setup_db():
    PDFConverter.convert_pdf_to_text(pdf_dir=pdf_dir_path, txt_dir=txt_dir_path)
    vector_db_setup = VectorDBSetup(embedding=OpenAIEmbeddings())
    response = vector_db_setup.setup_vector_db(txt_directory=txt_dir_path, db_directory=vector_db_path)
    return jsonify(response)

# 질의응답 엔드포인트 (BASE_URL 사용)
@app.route(f"{base_url}/<int:questionId>/answers", methods=['POST'])
def ask(questionId):
    # Authorization 헤더 확인
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]

    # 요청 본문 데이터 가져오기
    data = request.json
    if not data:
        return jsonify({"error": "유효한 요청 본문이 필요합니다."}), 400

    # 요청 데이터 파싱
    query_content = data.get("content")
    query_category = data.get("category")
    query_extra_data = data.get("extraData")
    #query_hashtag = data.get("hashtagList")

    # QA 서비스 호출
    qa_service = QAService(db_directory=vector_db_path)
    response_body = qa_service.qacall(query_category, query_content, query_extra_data)

    response = make_response(jsonify({
        "questionId": questionId,
        "response": response_body
    }))
    response.headers['Authorization'] = f"Bearer {token}"

    return response

if __name__ == "__main__":
    app.run(debug=debug_mode)
