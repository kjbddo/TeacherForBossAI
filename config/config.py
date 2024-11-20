from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    VECTOR_DB_PATH = 'data/vector_db'
    TXT_DIR_PATH = 'data/txt'
    PDF_DIR_PATH = 'data/pdf'
    BASE_TARGET_URL = os.getenv('TARGET_SERVER_URL', 'https://dev.teacherforboss.store/board/teacher/questions')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    DEBUG_MODE = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    @staticmethod
    def init_app(app):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
        os.environ['OPENAI_API_KEY'] = Config.OPENAI_API_KEY