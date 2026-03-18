FROM python:3.11-slim

# 파이썬 출력 버퍼링 비활성화
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 작업 디렉토리
WORKDIR /app

# 시스템 의존성 설치 (필요한 경우에만 주석 해제)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl gcc libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install --no-cache-dir poetry==1.8.3

# pyproject.toml, poetry.lock 복사
COPY pyproject.toml poetry.lock* ./

# 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev

# 앱 코드 복사
COPY . .

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]