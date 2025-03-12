# Hướng dẫn triển khai ứng dụng Music Recommendation App

## 1. Chuẩn bị môi trường

### Yêu cầu hệ thống
- Node.js phiên bản 18 trở lên
- NPM hoặc Yarn
- Tài khoản Firebase (cho Authentication)
- API Backend đã được triển khai

### Cài đặt biến môi trường
Sao chép file `.env.local.example` thành `.env.local` và cấu hình các biến môi trường phù hợp:

```bash
cp .env.local.example .env.local
```

Chỉnh sửa file `.env.local` với thông tin cấu hình Firebase và URL API của bạn.

## 2. Cài đặt ứng dụng

Cài đặt các dependencies:

```bash
npm install
# hoặc
yarn install
```

## 3. Chạy ứng dụng trong môi trường phát triển

```bash
npm run dev
# hoặc
yarn dev
```

Ứng dụng sẽ chạy ở `http://localhost:3000`

## 4. Xây dựng ứng dụng cho môi trường sản xuất

```bash
npm run build
# hoặc
yarn build
```

Kiểm tra bản build:

```bash
npm run start
# hoặc
yarn start
```

## 5. Triển khai

### Triển khai lên Vercel (Khuyến nghị)

Cách đơn giản nhất là triển khai lên Vercel:

1. Đẩy code lên GitHub, GitLab hoặc Bitbucket
2. Truy cập [vercel.com](https://vercel.com) và đăng nhập
3. Nhấp vào "New Project" và chọn repository của bạn
4. Cấu hình các biến môi trường cần thiết
5. Nhấp vào "Deploy"

### Triển khai lên các nền tảng khác

#### AWS Amplify

1. Đăng nhập vào AWS Management Console
2. Truy cập dịch vụ AWS Amplify
3. Chọn "New app" > "Host web app"
4. Kết nối với repository của bạn
5. Cấu hình biến môi trường và triển khai

#### Netlify

1. Đăng nhập vào Netlify
2. Nhấp vào "New site from Git"
3. Chọn repository của bạn
4. Cấu hình build command: `npm run build`
5. Cấu hình publish directory: `.next`
6. Thêm biến môi trường và triển khai

#### Docker

Bạn cũng có thể chạy ứng dụng trong Docker container:

```bash
# Xây dựng Docker image
docker build -t music-recommendation-app .

# Chạy container
docker run -p 3000:3000 music-recommendation-app
```

## 6. Hướng dẫn cấu hình Firebase

### Tạo Project Firebase

1. Truy cập [Firebase Console](https://console.firebase.google.com/)
2. Nhấp vào "Add project" và làm theo hướng dẫn
3. Bật tính năng Authentication
4. Bật các phương thức đăng nhập (ít nhất là Email/Password)

### Lấy thông tin cấu hình Firebase

1. Trong Firebase Console, chọn project của bạn
2. Nhấp vào biểu tượng bánh răng và chọn "Project settings"
3. Cuộn xuống mục "Your apps" và nhấp vào "</>" để thêm ứng dụng web
4. Đặt tên cho ứng dụng và nhấp "Register app"
5. Sao chép thông tin cấu hình vào file `.env.local`

## 7. Hướng dẫn kết nối API Backend

Đảm bảo rằng API Backend Music Recommendation đã được triển khai và đang chạy. Cập nhật biến môi trường `NEXT_PUBLIC_API_URL` trong file `.env.local` để trỏ đến URL của API.

## 8. Khắc phục sự cố

### Vấn đề xác thực Firebase

Nếu gặp vấn đề về xác thực Firebase, hãy kiểm tra:
- Đã cấu hình đúng thông tin Firebase trong `.env.local`
- Phương thức đăng nhập đã được bật trong Firebase Console
- CORS đã được cấu hình đúng trên Firebase

### Vấn đề kết nối API

Nếu không thể kết nối đến API Backend:
- Kiểm tra URL API trong `.env.local`
- Đảm bảo API đang chạy và có thể truy cập
- Kiểm tra cài đặt CORS trên API
- Kiểm tra các lỗi trong Console của trình duyệt
