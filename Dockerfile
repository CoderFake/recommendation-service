FROM python:3.11-slim

WORKDIR /app

# Cài đặt các gói phụ thuộc hệ thống
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt poetry
RUN pip install --no-cache-dir poetry

# Sao chép chỉ pyproject.toml và poetry.lock (nếu có)
COPY pyproject.toml poetry.lock* ./

# Cấu hình poetry để không tạo virtualenv
RUN poetry config virtualenvs.create false

# Cài đặt dependencies
RUN poetry install --no-interaction --no-ansi --no-dev

# Sao chép toàn bộ mã nguồn
COPY . .

# Tạo thư mục logs
RUN mkdir -p logs

# Cài đặt các dependencies còn lại nếu cần
RUN pip install --no-cache-dir -r requirements.txt

# Thiết lập biến môi trường
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Khởi động ứng dụng
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]