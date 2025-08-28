# Dockerfile
FROM python:3.10-slim

# 작업 디렉토리 생성
WORKDIR /app

# 종속성 복사
COPY requirements.txt .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 최적 설정 반영된 Dockerfile CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "asyncio", "--http", "h11", "--timeout-keep-alive", "30"]
