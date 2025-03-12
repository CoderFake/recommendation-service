# Music Recommendation API

API gợi ý nhạc thông minh sử dụng FastAPI, Neural Collaborative Filtering và Content-based Filtering với khả năng học tăng cường (Incremental Learning) để đưa ra các gợi ý cá nhân hóa dựa trên tương tác người dùng.

## Tính năng chính

- **Backend**: FastAPI, SQLAlchemy, AsyncPG, Pydantic
- **Xác thực**: Firebase Authentication
- **API nhạc**: SoundCloud API
- **Recommender system**: 
  - Neural Collaborative Filtering (NCF)
  - Content-based Filtering
  - Hybrid Recommender
  - Incremental Learning (cập nhật mô hình real-time)
- **Cơ sở dữ liệu**: PostgreSQL
- **Docker**: Docker Compose cho dễ dàng triển khai
- **Môi trường**: Hỗ trợ Dev, Staging và Production

## Cài đặt

### Yêu cầu

- Docker và Docker Compose
- Firebase project (để xác thực)
- SoundCloud API client ID

### Cài đặt lần đầu

1. Clone repository:
```bash
git clone https://github.com/your-username/music-recommendation-api.git
cd music-recommendation-api
```

2. Chạy script setup để tạo file môi trường:
```bash
chmod +x setup.sh
./setup.sh
```

3. Chỉnh sửa các file cấu hình:
```bash
# Chỉnh sửa file cấu hình cho development
nano .env.dev

# Chỉnh sửa file cấu hình cho staging
nano .env.stg

# Chỉnh sửa file cấu hình cho production
nano .env
```

### Chạy ứng dụng

```bash
# Môi trường development (với hot reload và API docs)
./run-dev.sh

# Môi trường staging
./run-stg.sh

# Môi trường production
./run-prod.sh
```

Hoặc bạn có thể chạy trực tiếp bằng Docker Compose:

```bash
# Development
docker compose -f docker-compose.yml -f dev.yml up -d

# Staging
docker compose -f docker-compose.yml -f stg.yml up -d

# Production
docker compose -f docker-compose.yml -f prod.yml up -d
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register`: Đăng ký người dùng mới
- `GET /api/v1/auth/me`: Lấy thông tin người dùng hiện tại
- `PUT /api/v1/auth/me`: Cập nhật thông tin người dùng

### Songs

- `GET /api/v1/songs`: Tìm kiếm bài hát
- `GET /api/v1/songs/{song_id}`: Lấy thông tin bài hát
- `POST /api/v1/songs/soundcloud/search`: Tìm kiếm bài hát trên SoundCloud
- `POST /api/v1/songs/soundcloud/import`: Import bài hát từ SoundCloud

### User Interactions

- `GET /api/v1/interactions`: Lấy danh sách tương tác của người dùng
- `POST /api/v1/interactions`: Tạo/cập nhật tương tác với bài hát
- `PUT /api/v1/interactions/{song_id}`: Cập nhật tương tác hiện có
- `DELETE /api/v1/interactions/{song_id}`: Xóa tương tác 
- `POST /api/v1/interactions/events`: Gửi sự kiện tương tác (play, like, skip, etc.)

### Recommendations

- `GET /api/v1/recommendations`: Lấy danh sách gợi ý cá nhân hóa
- `GET /api/v1/recommendations/similar/{song_id}`: Tìm bài hát tương tự
- `GET /api/v1/recommendations/taste-profile`: Xem hồ sơ sở thích âm nhạc của người dùng
- `POST /api/v1/recommendations/refresh-model`: Làm mới mô hình gợi ý (admin)

## Hệ thống Recommendation

### Neural Collaborative Filtering (NCF)

NCF kết hợp:
- Embedding vectors cho người dùng và bài hát
- Generalized Matrix Factorization (GMF)
- Multi-Layer Perceptron (MLP)
- Optimized cho việc học tăng cường

### Content-based Filtering

Sử dụng đặc trưng âm nhạc:
- Thể loại, nghệ sĩ, và metadata từ SoundCloud
- Vector features từ audio signals
- Tương tự dựa trên cosine similarity

### Hybrid Recommender

Kết hợp cả hai phương pháp:
- Cân bằng giữa collaborative và content-based filtering
- Điều chỉnh trọng số dựa trên số lượng dữ liệu và context
- Thúc đẩy khám phá và cá nhân hóa

### Incremental Learning

- Cập nhật mô hình real-time dựa trên tương tác người dùng
- Xử lý các sự kiện: play, like, skip, save
- Retraining định kỳ cho mô hình đầy đủ

## Cấu trúc dự án

```
music-recommendation-api/
├── alembic/                     # Database migrations
├── app/
│   ├── api/                     # API endpoints
│   ├── core/                    # Core functionality
│   ├── db/                      # Database
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   │   ├── recommender/         # Recommendation engine
│   │   │   ├── models.py        # ML models
│   │   │   ├── data.py          # Data management
│   │   │   ├── trainer.py       # Model training
│   │   │   └── metrics.py       # Evaluation metrics
│   │   ├── auth.py              # Auth service
│   │   └── soundcloud.py        # SoundCloud API
│   └── main.py                  # App entry point
├── docker/                      # Docker configurations
├── models/                      # Trained ML models
├── dev.yml                      # Dev environment config
├── stg.yml                      # Staging environment config
├── prod.yml                     # Production environment config
├── setup.sh                     # Setup script
├── run-dev.sh                   # Script to run dev env
├── run-stg.sh                   # Script to run staging env
├── run-prod.sh                  # Script to run production env
└── docker-compose.yml           # Docker compose configuration
```

## Môi trường

Hệ thống hỗ trợ 3 môi trường với các cấu hình riêng:

| Tính năng | Development | Staging | Production |
|-----------|-------------|---------|------------|
| API Docs | ✅ | ❌ | ❌ |
| Hot Reload | ✅ | ❌ | ❌ |
| Workers | 1 | 2 | 4+ |
| DB | music_service_dev | music_service_stg | music_service_prod |

## Metrics và Evaluation

Hệ thống sử dụng các metrics sau để đánh giá chất lượng gợi ý:
- Precision@k
- Recall@k
- NDCG@k
- Diversity
- Novelty
- Coverage
- Serendipity

## Bảo mật

- Xác thực qua Firebase Auth với JWT
- Rate limiting tránh tấn công DDoS
- CORS cấu hình đúng theo môi trường
- API docs chỉ có trong môi trường dev

## License

MIT