# app.py

from langchain_openai import OpenAIEmbeddings
from flask import Flask, request, jsonify
from db_setup import PDFConverter, VectorDBSetup
from qa_service import QAService
import os

app = Flask(__name__)
vector_db_path = 'data/vector_db'
txt_dir_path = 'data/txt'
pdf_dir_path = 'data/pdf'

# OpenAI API 키 설정
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    os.environ['OPENAI_API_KEY'] = openai_api_key
else:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

# PDF 변환 및 벡터 DB 설정 엔드포인트
@app.route('/setup_db', methods=['POST'])
def setup_db():
    PDFConverter.convert_pdf_to_text(pdf_dir=pdf_dir_path, txt_dir=txt_dir_path)
    vector_db_setup = VectorDBSetup(embedding=OpenAIEmbeddings())
    response = vector_db_setup.setup_vector_db(txt_directory=txt_dir_path, db_directory=vector_db_path)
    return jsonify(response)

# 질의응답 엔드포인트
@app.route('/ask', methods=['POST'])
def ask():
    query = request.json.get('query')
    qa_service = QAService(db_directory=vector_db_path)
    response = qa_service.qacall(query)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
