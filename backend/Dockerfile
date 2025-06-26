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

# 기본 실행 명령 (uvicorn은 docker-compose에서 지정)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
