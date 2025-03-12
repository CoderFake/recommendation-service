# Hướng dẫn cấu hình môi trường

Hệ thống hỗ trợ 3 môi trường: Development (dev), Staging (stg), và Production (prod). Mỗi môi trường có các cấu hình riêng phù hợp với mục đích sử dụng.

## Tính năng theo môi trường

| Tính năng | Development | Staging | Production |
|-----------|-------------|---------|------------|
| API Documentation | ✅ Enabled | ❌ Disabled | ❌ Disabled |
| Debug logs | ✅ Verbose | ⚠️ Limited | ❌ Minimal |
| Hot reload | ✅ Enabled | ❌ Disabled | ❌ Disabled |
| Workers | 1 (default) | 2 | 4+ |

## File cấu hình môi trường

Mỗi môi trường sử dụng các file cấu hình riêng:

- **Development**: `.env.dev`
- **Staging**: `.env.stg`
- **Production**: `.env` (file mặc định)

## Chạy ứng dụng trong các môi trường khác nhau

### Development

```bash
# Khởi động với cấu hình dev
docker compose -f docker-compose.yml -f dev.yml up -d

# Xem logs
docker compose -f docker-compose.yml -f dev.yml logs -f api
```

### Staging

```bash
# Khởi động với cấu hình staging
docker compose -f docker-compose.yml -f stg.yml up -d
```

### Production

```bash
# Khởi động với cấu hình production
docker compose -f docker-compose.yml -f prod.yml up -d
```

## Cài đặt lần đầu

Khi cài đặt hệ thống lần đầu, bạn cần tạo các file môi trường:

```bash
# Tạo các file môi trường từ file mẫu
cp .env.example .env.dev
cp .env.example .env.stg
cp .env.example .env

# Chỉnh sửa cấu hình cho từng môi trường
nano .env.dev   # Cấu hình cho development
nano .env.stg   # Cấu hình cho staging
nano .env       # Cấu hình cho production
```

## Cấu hình OpenAPI Documentation

- Trong môi trường **dev**: API documentation được kích hoạt tự động vì ENVIRONMENT=dev
- Trong môi trường **stg** và **prod**: API documentation bị vô hiệu hóa tự động vì ENVIRONMENT là stg hoặc prod

## Cấu hình Worker theo môi trường

Trong các file docker-compose cho từng môi trường, số worker được cấu hình khác nhau:

- **dev.yml**: `--reload` (1 worker với hot reload)
- **stg.yml**: `--workers 2` (2 workers)
- **prod.yml**: `--workers 4` (4 workers)

## Database

Mỗi môi trường sẽ sử dụng một database riêng để tránh xung đột:

- Development: `music_service_dev`
- Staging: `music_service_stg`
- Production: `music_service_prod`

## Một số lưu ý bảo mật

- Không commit các file `.env`, `.env.dev`, `.env.stg` lên git repository
- Chỉ commit file `.env.example` làm mẫu
- Sử dụng secret key và password khác nhau cho mỗi môi trường
- Trong môi trường production, hãy đảm bảo rằng secret keys, passwords, và thông tin nhạy cảm khác được quản lý an toàn (ví dụ: sử dụng docker secrets, vault, etc.)