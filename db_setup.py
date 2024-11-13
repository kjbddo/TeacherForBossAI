# db_setup.py

import glob
import logging
import os

import fitz  # PyMuPDF
from langchain.schema import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFConverter:
    """PDF 파일을 텍스트 파일로 변환하는 클래스."""

    @staticmethod
    def convert_pdf_to_text(pdf_dir, txt_dir):
        pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
        os.makedirs(txt_dir, exist_ok=True)

        for pdf_path in pdf_files:
            txt_path = os.path.join(txt_dir, os.path.basename(pdf_path).replace('.pdf', '.txt'))
            if os.path.exists(txt_path):
                logger.info(f"이미 변환된 파일이 존재합니다: {txt_path}")
                continue

            try:
                text = PDFConverter.extract_text_from_pdf(pdf_path)
                PDFConverter.save_text_to_file(text, txt_path)
                logger.info(f"PDF 파일이 성공적으로 변환되었습니다: {txt_path}")
            except Exception as e:
                logger.error(f"오류 발생: {pdf_path}, 오류 내용: {e}")

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        return ' '.join(text.split())

    @staticmethod
    def save_text_to_file(text, txt_path):
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            logger.error(f"텍스트 파일 저장 중 오류: {txt_path}, 오류 내용: {e}")

class VectorDBSetup:
    """벡터 데이터베이스 생성과 관리 클래스."""

    def __init__(self, embedding, chunk_size=1000, chunk_overlap=200):
        self.embedding = embedding
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def setup_vector_db(self, txt_directory: str, db_directory: str):
        os.makedirs(db_directory, exist_ok=True)
        documents = self.load_documents(txt_directory)

        texts = [Document(page_content=doc.page_content.strip()) for doc in self.split_text(documents)]
        vectordb = Chroma.from_documents(
            documents=texts,
            embedding=self.embedding,
            persist_directory=db_directory
        )
        vectordb.persist()

        logger.info("벡터 DB 생성 완료")
        return {"success": True}

    def load_documents(self, txt_directory: str):
        loader = DirectoryLoader(txt_directory, glob="*.txt", loader_cls=TextLoader)
        return loader.load()

    def split_text(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        return text_splitter.split_documents(documents)
