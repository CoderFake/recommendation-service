# Hướng dẫn cấu hình môi trường

Hệ thống hỗ trợ ba môi trường: Development (dev), Staging (stg), và Production (prod). Mỗi môi trường có các cấu hình riêng phù hợp với mục đích sử dụng.

## Tính năng theo môi trường

| Tính năng | Development       | Staging | Production |
|-----------|-------------------|---------|------------|
| API Documentation | ✅ Enabled         | ❌ Disabled | ❌ Disabled |
| Debug logs | ✅ Chi tiết        | ⚠️ Giới hạn | ❌ Tối thiểu |
| Hot reload | ✅ Enabled         | ❌ Disabled | ❌ Disabled |
| Workers | 1      (--reload) | 2 | 4+ |
| Database | music_service_dev | music_service_stg | music_service_prod |

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

Các tính năng chính của môi trường dev:
- Hot reload được bật (thay đổi code được áp dụng tự động)
- Tài liệu API có sẵn tại `/api/v1/docs`
- Đơn luồng worker cho đơn giản trong quá trình phát triển
- Logging cấp độ debug

### Staging

```bash
# Khởi động với cấu hình staging
docker compose -f docker-compose.yml -f stg.yml up -d
```

Các tính năng chính của môi trường staging:
- Cấu hình nhiều worker (2 workers)
- Không có hot reload (hiệu suất tốt hơn)
- Tài liệu API bị vô hiệu hóa
- Cơ sở dữ liệu tách biệt với môi trường phát triển

### Production

```bash
# Khởi động với cấu hình production
docker compose -f docker-compose.yml -f prod.yml up -d
```

Các tính năng chính của môi trường production:
- Tối ưu hóa hiệu suất với 4+ workers
- Logging tối thiểu (chỉ các sự kiện quan trọng)
- Tài liệu API bị vô hiệu hóa
- Cơ sở dữ liệu riêng cho production

## Cài đặt lần đầu

Khi cài đặt hệ thống lần đầu, hãy tạo các file môi trường từ mẫu:

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

## Cấu hình tài liệu API

- Trong môi trường **development**: Tài liệu API được kích hoạt tự động vì `ENVIRONMENT=dev`
- Trong môi trường **staging** và **production**: Tài liệu API bị vô hiệu hóa tự động

## Cấu hình Worker theo môi trường

Mỗi file Docker Compose cho môi trường chỉ định cấu hình worker khác nhau:

- **dev.yml**: Sử dụng cờ `--reload` (1 worker với hot reload)
- **stg.yml**: Sử dụng `--workers 2` (2 workers)
- **prod.yml**: Sử dụng `--workers 4` (4 workers)

## Cấu hình Database

Mỗi môi trường sử dụng cơ sở dữ liệu riêng biệt để tránh xung đột:

- Development: `music_service_dev`
- Staging: `music_service_stg`
- Production: `music_service_prod`

## Đề xuất bảo mật

- Không commit các file `.env`, `.env.dev`, hoặc `.env.stg` lên Git repositories
- Chỉ commit file `.env.example` làm mẫu
- Sử dụng secret key và mật khẩu khác nhau cho mỗi môi trường
- Trong môi trường production, sử dụng các phương pháp an toàn để quản lý thông tin nhạy cảm (ví dụ: sử dụng docker secrets, vault, etc.)