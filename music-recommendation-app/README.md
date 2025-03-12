# Ứng dụng Web Đề xuất Âm nhạc

Ứng dụng web hiện đại sử dụng Next.js, React và hệ thống đề xuất âm nhạc AI để cung cấp trải nghiệm nghe nhạc cá nhân hóa. Ứng dụng kết nối với API Recommendation Engine để phân tích thói quen nghe nhạc và đề xuất các bài hát phù hợp với sở thích của người dùng.

## Tính năng chính

- **Giao diện hiện đại**: UI/UX tinh tế, responsive trên mọi thiết bị
- **Đề xuất cá nhân hóa**: Đề xuất dựa trên thói quen nghe và bài hát đã thích
- **Tích hợp Spotify**: Tìm kiếm và nhập bài hát từ thư viện Spotify
- **Quản lý playlist**: Tạo, chỉnh sửa và chia sẻ playlist
- **Phát nhạc**: Trình phát nhạc tích hợp với các điều khiển cơ bản
- **Hồ sơ người dùng**: Quản lý tài khoản và xem thống kê nghe nhạc
- **Chế độ tối/sáng**: Chuyển đổi giao diện phù hợp với môi trường

## Công nghệ

- **Frontend**: Next.js 14, React 18, TypeScript
- **State Management**: React Context API, SWR cho fetching data
- **Styling**: Tailwind CSS, shadcn/ui components
- **Authentication**: Firebase Authentication
- **Charts**: Recharts cho visualization

## Cài đặt và Chạy

### Yêu cầu

- Node.js 18.x trở lên
- NPM hoặc Yarn
- Backend API đã được chạy và cấu hình (xem [API README](../music-recommendation-api/README.md))

### Cài đặt

1. Clone repository:

```bash
git clone https://github.com/CoderFake/song-recommendation.git
cd music-recommendation-app
```

2. Cài đặt dependencies:

```bash
npm install
# hoặc
yarn install
```

3. Tạo file môi trường:

```bash
cp .env.example .env.local
```

4. Cấu hình các biến môi trường trong `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:22222
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_firebase_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_firebase_app_id
```

### Chạy ứng dụng

```bash
npm run dev
# hoặc
yarn dev
```

Ứng dụng sẽ chạy ở địa chỉ `http://localhost:3000`

### Build cho môi trường production

```bash
npm run build
npm run start
# hoặc
yarn build
yarn start
```

## Cấu trúc dự án

```
music-recommendation-app/
├── public/                     # Static files (images, icons)
├── src/
│   ├── app/                    # App router pages
│   │   ├── (auth)/             # Auth pages (login, register)
│   │   ├── (main)/             # Main app pages (protected)
│   │   ├── admin/              # Admin pages (protected)
│   │   ├── api/                # API routes
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   ├── components/             # UI components
│   │   ├── layout/             # Layout components (header, sidebar)
│   │   ├── music/              # Music-related components
│   │   ├── recommendations/    # Recommendation components
│   │   ├── search/             # Search components
│   │   └── ui/                 # Basic UI components
│   ├── contexts/               # React contexts
│   ├── hooks/                  # Custom hooks
│   ├── lib/                    # Utilities and libraries
│   │   ├── api/                # API client functions
│   │   ├── firebase.ts         # Firebase config
│   │   ├── types.ts            # TypeScript types
│   │   └── utils.ts            # Utility functions
│   ├── providers/              # Context providers
│   └── styles/                 # Global styles
└── public/                     # Static assets
    └── images/                 # Images and icons
```

## Tương tác với API

Ứng dụng sử dụng custom API client trong `src/lib/api/client.ts` để tương tác với backend API. Tất cả các chức năng API được phân loại trong thư mục `src/lib/api/` theo chức năng:

- `auth.ts`: Xác thực và quản lý người dùng
- `songs.ts`: Tìm kiếm và quản lý bài hát
- `interactions.ts`: Tương tác với bài hát (play, like, etc.)
- `recommendations.ts`: Lấy đề xuất cá nhân hóa
- `playlists.ts`: Quản lý playlist
- `admin.ts`: Chức năng quản trị

## Hướng dẫn sử dụng

### Đăng ký và đăng nhập

- Truy cập `/register` để tạo tài khoản mới
- Truy cập `/login` để đăng nhập với tài khoản hiện có

### Tìm kiếm và nghe nhạc

- Sử dụng thanh tìm kiếm để tìm bài hát
- Nhấn vào biểu tượng phát để nghe bài hát
- Nhấn vào biểu tượng tim để thích bài hát

### Quản lý playlist

- Tạo playlist mới từ trang Library
- Thêm bài hát vào playlist bằng cách nhấn vào biểu tượng "..."
- Sắp xếp lại bài hát trong playlist bằng kéo và thả

### Khám phá âm nhạc

- Xem đề xuất cá nhân hóa ở trang Recommendations
- Khám phá bài hát tương tự tại trang chi tiết bài hát
- Xem hồ sơ sở thích âm nhạc tại trang Taste Profile

## Authentication & Authorization

Ứng dụng sử dụng Firebase Authentication cho xác thực người dùng. Token JWT được lưu trong cookie và được sử dụng cho các request API. Middleware Next.js đảm bảo rằng người dùng đã đăng nhập mới có thể truy cập các trang được bảo vệ.

## Themes và Styling

Ứng dụng sử dụng Tailwind CSS với shadcn/ui components. Chế độ tối/sáng được quản lý bởi next-themes và được lưu trong localStorage.

## Error Handling

Ứng dụng sử dụng ErrorBoundary của Next.js để bắt và xử lý lỗi. API errors được xử lý bởi custom APIError class.

## Đóng góp

Vui lòng đọc [CONTRIBUTING.md](./CONTRIBUTING.md) để biết chi tiết về quy trình đóng góp.

## Phát triển và mở rộng

### Thêm components mới

1. Tạo component trong thư mục `src/components/`
2. Import và sử dụng trong pages hoặc components khác

### Thêm trang mới

1. Tạo file mới trong thư mục `src/app/`
2. Implement page component
3. Cập nhật navigation nếu cần

### Thêm API endpoints mới

1. Thêm hàm mới trong thư mục `src/lib/api/`
2. Import và sử dụng trong hooks hoặc components

## Performance Optimization

- Sử dụng Next.js Image component cho tối ưu hóa hình ảnh
- Sử dụng React.memo để tránh render không cần thiết
- Sử dụng SWR cho caching và revalidation
- Sử dụng Next.js Suspense cho loading states

## License

[MIT](LICENSE)