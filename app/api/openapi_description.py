"""
API Gợi Ý Bài Hát
---
Hệ thống API cung cấp khả năng gợi ý bài hát dựa trên nhiều thuật toán khác nhau,
kết hợp dữ liệu người dùng, thông tin bài hát, và ngữ cảnh thời gian thực
để đưa ra gợi ý chính xác và phù hợp.

## Tính năng chính

* **Gợi ý cá nhân hóa**: Dựa trên lịch sử nghe và sở thích cá nhân
* **Gợi ý dựa trên nội dung**: Phân tích đặc điểm âm nhạc và metadata bài hát
* **Gợi ý theo xu hướng**: Dựa trên dữ liệu xu hướng nghe hiện tại
* **Gợi ý theo ngữ cảnh**: Thay đổi theo thời gian, địa điểm và hoạt động

## Các loại gợi ý

* `similar_song`: Bài hát có đặc điểm âm nhạc tương tự
* `user_preference`: Dựa trên sở thích cá nhân của người dùng
* `trending`: Bài hát đang được nhiều người nghe
* `genre_based`: Cùng thể loại với bài hát gốc
* `artist_based`: Từ cùng nghệ sĩ hoặc nghệ sĩ tương tự
* `collaborative_filtering`: Dựa trên hành vi của người dùng tương tự
* `content_based`: Dựa trên phân tích nội dung và đặc điểm bài hát
* `hybrid`: Kết hợp nhiều phương pháp gợi ý khác nhau
* `real_time`: Dựa trên dữ liệu thời gian thực và ngữ cảnh hiện tại

## Xác thực và bảo mật
API sử dụng phương thức xác thực API key. API key được cung cấp trong header `X-API-Key`
của mỗi request. API key có thể được lấy thông qua endpoint `/api/token`.

## Giới hạn tốc độ
- 100 requests/phút cho endpoint gợi ý
- 10 requests/phút cho các endpoint quản lý token

## Tương tác với API
API tuân theo chuẩn RESTful và trả về dữ liệu dưới dạng JSON. Tất cả các endpoint
đều trả về mã lỗi HTTP phù hợp cùng với thông báo lỗi chi tiết trong trường hợp có vấn đề.
"""

API_DESCRIPTION = __doc__

API_TAGS_METADATA = [
    {
        "name": "recommendations",
        "description": "Các endpoint liên quan đến gợi ý bài hát.",
    },
    {
        "name": "health",
        "description": "Các endpoint kiểm tra trạng thái hoạt động của hệ thống.",
    }
]