FROM python:3.10-slim

# 시스템 패키지 설치 (이미지 디코딩용, torch native 연산용, git)
RUN apt-get update && \
    apt-get install -y git libgl1 libglib2.0-0 libstdc++6 && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# Celery 워커 실행
CMD ["celery", "-A", "worker", "worker", "--loglevel=info"]
