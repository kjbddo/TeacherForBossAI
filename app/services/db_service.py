# db_setup.py
'''
import glob
import logging
import os

import fitz  # PyMuPDF
from langchain.schema import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

#this modules need for OCR(not installed in venv)
# import cv2
# import easyocr
# import numpy as np
# from typing import List,Optional

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

if __name__ == "__main__":
    pdf_converter = PDFConverter()
    pdf_converter.convert_pdf_to_text("data/pdf", "data/txt")
    db_service = VectorDBSetup(embedding=OpenAIEmbeddings())
    db_service.setup_vector_db("data/txt", "data/vector_db")
'''

# class PDFConverterOCR:
#     """PDF 파일을 텍스트 파일로 변환하는 클래스."""
#
#     def __init__(self, languages: Optional[List[str]] = None, use_gpu: bool = False):
#         """
#         초기화 메서드로 OCR을 위한 EasyOCR Reader 인스턴스를 생성합니다.
#
#         매개변수:
#         - languages: EasyOCR에 사용할 언어 목록 (예: ['en', 'ko'])
#         - use_gpu: GPU 사용 여부
#         """
#         self.reader = easyocr.Reader(languages or ['en'], gpu=use_gpu)
#
#     def convert_pdf_to_text(self, pdf_dir: str, txt_dir: str):
#         """PDF 디렉토리를 텍스트 파일로 변환하여 지정된 디렉토리에 저장"""
#         pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
#         os.makedirs(txt_dir, exist_ok=True)
#
#         for pdf_path in pdf_files:
#             txt_path = os.path.join(txt_dir, os.path.basename(pdf_path).replace('.pdf', '.txt'))
#             if os.path.exists(txt_path):
#                 logger.info(f"이미 변환된 파일이 존재합니다: {txt_path}")
#                 continue
#
#             try:
#                 text = self.extract_text_from_pdf(pdf_path)
#                 if not text.strip():  # 빈 텍스트 체크
#                     logger.warning(f"OCR 결과가 비어 있습니다: {pdf_path}")
#                     continue
#                 self.save_text_to_file(text, txt_path)
#                 logger.info(f"PDF 파일이 성공적으로 변환되었습니다: {txt_path}")
#             except Exception as e:
#                 logger.error(f"오류가 발생했습니다: {pdf_path}, 오류 내용: {e}")
#
#     def extract_text_from_pdf(self, pdf_path: str) -> str:
#         """PDF 파일에서 각 페이지를 이미지로 변환 후 OCR 텍스트 추출"""
#         text = ""
#         with fitz.open(pdf_path) as doc:
#             for page_num in range(doc.page_count):
#                 page = doc[page_num]
#
#                 # 해상도 조정 (200 DPI 이상 권장)
#                 zoom = 2.0  # 2배 확대
#                 mat = fitz.Matrix(zoom, zoom)
#                 pixmap = page.get_pixmap(matrix=mat)
#
#                 # OpenCV와 호환되는 이미지로 변환
#                 image_np = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape((pixmap.height, pixmap.width, pixmap.n))
#                 if pixmap.n == 4:  # RGBA 형식이면 RGB로 변환
#                     image_np = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)
#
#                 # 전처리 적용
#                 preprocessed_image = self.preprocess_image(image_np)
#
#                 # OCR을 통해 텍스트 추출
#                 ocr_text = self.perform_ocr(preprocessed_image)
#                 text += ocr_text + "\n\n"
#
#         return text
#
#     def preprocess_image(self, image: np.ndarray) -> np.ndarray:
#         """이미지 전처리를 수행하여 OCR 성능 향상"""
#         # 그레이스케일로 변환
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#         # 노이즈 제거 (GaussianBlur)
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#
#         # 대비 조정
#         _, binary_image = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#
#         # 이미지 확대
#         enlarged_image = cv2.resize(binary_image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
#
#         return enlarged_image
#
#     def perform_ocr(self, image_np) -> str:
#         """이미지에서 OCR로 텍스트를 추출"""
#         try:
#             results = self.reader.readtext(image_np, detail=0)
#             return " ".join(results)
#         except Exception as e:
#             logger.error(f"OCR 처리 중 오류 발생: {e}")
#             return ""
#
#     @staticmethod
#     def save_text_to_file(text: str, txt_path: str):
#         """텍스트 파일로 저장"""
#         with open(txt_path, 'w', encoding='utf-8') as f:
#             f.write(text)
