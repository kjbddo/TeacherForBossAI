FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 데이터 디렉토리 생성
RUN mkdir -p data/vector_db

# 환경 변수 설정
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV VECTOR_DB_PATH=/mnt/efs/vector_db

EXPOSE 5000

# Gunicorn으로 서버 실행
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "main:create_app()"] 