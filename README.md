# Hệ thống Gợi ý Bài Hát

Hệ thống API cung cấp khả năng gợi ý bài hát dựa trên nhiều thuật toán khác nhau, kết hợp dữ liệu người dùng, thông tin bài hát, và ngữ cảnh thời gian thực để đưa ra gợi ý chính xác và phù hợp.

## Tính năng

- **Gợi ý cá nhân hóa**: Dựa trên lịch sử nghe và sở thích cá nhân
- **Gợi ý dựa trên nội dung**: Phân tích đặc điểm âm nhạc và metadata bài hát
- **Gợi ý theo xu hướng**: Dựa trên dữ liệu xu hướng nghe hiện tại
- **Gợi ý theo ngữ cảnh**: Thay đổi theo thời gian, địa điểm và hoạt động

## Cài đặt và Chạy

### Yêu cầu hệ thống
- Python 3.9+
- PostgreSQL
- Docker và Docker Compose (tùy chọn)

### Cài đặt

1. **Clone repository**
   ```
   git clone https://github.com/coderfake/recommendation-service.git
   cd recommendation-service
   ```

2. **Cài đặt môi trường**

   **Sử dụng Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Hoặc sử dụng Docker:**
   ```bash
   docker-compose build
   ```

3. **Cấu hình môi trường**
   - Tạo file `.env` từ file mẫu `.env.example`
   ```bash
   cp .env.example .env
   ```
   - Chỉnh sửa các tham số trong file `.env` theo cấu hình của bạn

4. **Khởi tạo database**
   ```bash
   alembic upgrade head
   ```

### Chạy ứng dụng

**Chạy trực tiếp:**
```bash
uvicorn app.main:app --reload
```

**Hoặc chạy với Docker:**
```bash
docker-compose up
```

Sau khi khởi động, API sẽ khả dụng tại: `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs`

## Cấu trúc dự án

```
recommendation-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Điểm vào ứng dụng FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Cấu hình ứng dụng, load biến môi trường
│   │   ├── auth.py             # Xác thực OTP và hàm bảo mật
│   │   └── logging.py          # Cấu hình logging
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── recommendations.py  # Các route API gợi ý
│   │   │   └── health.py           # Route kiểm tra health
│   │   ├── dependencies.py     # Các phụ thuộc chung
│   │   └── models.py           # Pydantic models cho API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recommendation_service.py # Logic gợi ý bài hát
│   │   ├── user_interaction_service.py # Xử lý tương tác người dùng
│   │   └── data_sync_service.py       # Đồng bộ dữ liệu từ DB chính
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py          # Quản lý phiên DB
│   │   ├── models.py           # ORM Models
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── song_repository.py  # Thao tác với bảng bài hát
│   │       ├── user_repository.py  # Thao tác với bảng người dùng
│   │       └── interaction_repository.py # Thao tác với bảng tương tác
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── collaborative_filtering.py # Lọc cộng tác
│   │   ├── content_based.py          # Gợi ý theo nội dung
│   │   ├── hybrid.py                 # Kết hợp các phương pháp
│   │   └── realtime_processor.py     # Xử lý dữ liệu realtime
├── tests/                      # Unit tests
├── alembic/                    # Migration DB
├── .env                        # Biến môi trường (không đưa vào git)
├── .env.example                # Mẫu biến môi trường
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker build file
└── docker-compose.yml          # Compose cho dev environment
```

## API Endpoints

### Gợi ý bài hát

```
POST /api/recommendations
```

**Request body:**
```json
{
  "song_id": "song_12345",
  "user_id": "user_67890",
  "limit": 10,
  "context": {
    "time_of_day": "evening",
    "device": "mobile",
    "previous_songs": ["song_11111", "song_22222"],
    "location": "home",
    "mood": "relaxed"
  }
}
```

**Response:**
```json
{
  "recommended_songs": ["song_33333", "song_44444", "song_55555"],
  "detailed_recommendations": [
    {
      "song_id": "song_33333",
      "score": 0.95,
      "reason": "Người dùng thường nghe bài này sau bài gốc",
      "recommendation_type": "user_preference"
    }
  ],
  "based_on_song_id": "song_12345",
  "recommendation_reason": "Dựa trên mẫu nghe và sự tương đồng giữa các bài hát"
}
```

### Kiểm tra sức khỏe hệ thống

```
GET /api/health
```

### Lấy token truy cập

```
POST /api/token
```

**Request body:**
```json
{
  "user_id": "user_67890"
}
```

## Các Thuật Toán Gợi Ý

Hệ thống sử dụng kết hợp các thuật toán gợi ý sau:

1. **Lọc cộng tác (Collaborative Filtering)**: Dựa trên hành vi của những người dùng có sở thích tương tự.
2. **Gợi ý dựa trên nội dung (Content-Based)**: Phân tích đặc điểm của bài hát để tìm bài hát tương tự.
3. **Gợi ý dựa trên ngữ cảnh (Context-Aware)**: Thay đổi gợi ý dựa trên thời gian trong ngày, thiết bị, địa điểm.
4. **Hybrid Recommendation**: Kết hợp nhiều phương pháp để tối ưu kết quả.

## Xử lý dữ liệu thời gian thực

Hệ thống sử dụng các yếu tố thời gian thực để điều chỉnh kết quả gợi ý:

- Khung giờ trong ngày (sáng, chiều, tối, đêm)
- Thiết bị nghe nhạc (điện thoại, máy tính, loa)
- Xu hướng hiện tại
- Hoạt động người dùng (tập thể dục, học tập, thư giãn)

## License

Dự án này được cấp phép theo giấy phép MIT - xem file [LICENSE.md](LICENSE.md) để biết thêm chi tiết.
