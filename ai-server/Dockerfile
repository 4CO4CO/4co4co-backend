# 기본 이미지 설정
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

# 빌드 인자와 환경 변수 설정
ARG USE_GPU=false
ENV USE_GPU=${USE_GPU}

# 시스템 패키지 설치 및 git 설치 (git dependency 있는 경우)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libgl1 libglib2.0-0 git \
    gcc g++ build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/*

# pip timeout 설정 추가 (timeout 문제 방지)
RUN mkdir -p /etc/pip && echo "[global]\ntimeout = 1200" > /etc/pip/pip.conf

# requirements 파일 복사
COPY requirements-cpu.txt ./requirements-cpu.txt
COPY requirements-gpu.txt ./requirements-gpu.txt

# 조건 분기 설치 (GPU 사용 여부에 따라)
RUN if [ "$USE_GPU" = "true" ]; then \
    pip install --no-cache-dir \
      --extra-index-url https://download.pytorch.org/whl/cu118 \
      -r requirements-gpu.txt ; \
  else \
    pip install --no-cache-dir -r requirements-cpu.txt ; \
  fi

# 앱 복사 및 작업 디렉토리 설정
COPY . /app
WORKDIR /app

# 실행 커맨드
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
