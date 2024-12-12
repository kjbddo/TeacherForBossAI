'''
from flask import Blueprint, jsonify
from langchain_openai import OpenAIEmbeddings
from app.services.db_service import PDFConverter, VectorDBSetup
from config.config import Config

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/setup_aidb', methods=['POST'])
def setup_db():
    PDFConverter.convert_pdf_to_text(
        pdf_dir=Config.PDF_DIR_PATH, 
        txt_dir=Config.TXT_DIR_PATH
    )
    vector_db_setup = VectorDBSetup(embedding=OpenAIEmbeddings())
    response = vector_db_setup.setup_vector_db(
        txt_directory=Config.TXT_DIR_PATH, 
        db_directory=Config.VECTOR_DB_PATH
    )
    return jsonify(response)
'''