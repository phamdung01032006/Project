# Movie Recommendation System

Hệ thống gợi ý phim sử dụng 3 phương pháp: Collaborative Filtering, Content-based Filtering và Hybrid Filtering.

## Cấu trúc Project
```
app/
├── models/         # Chứa các model gợi ý
├── views/          # Giao diện người dùng (Streamlit)
├── controllers/    # Xử lý logic
├── data/           # Dữ liệu và tiền xử lý
└── utils/          # Các tiện ích
```

## Cài đặt (Python thuần, không dùng Conda)
1. Clone repository:
   ```bash
   git clone https://github.com/phamdung01032006/Project.git
   cd Project
   ```
2. Tạo và kích hoạt môi trường ảo (`venv`):
   ```bash
   python -m venv .venv
   ```
   Windows (PowerShell):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```
3. Cài đặt thư viện:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

## Cấu hình biến môi trường
1. Tạo file `.env` trong thư mục gốc của dự án.
2. Thêm biến sau vào `.env`:
   ```env
   YOUTUBE_API_KEY=your_api_key_here
   ```
3. Thay `your_api_key_here` bằng API key từ Google Cloud và bật **YouTube Data API v3**.

## Chạy ứng dụng
Từ thư mục gốc dự án:
```bash
python -m streamlit run app/views/main.py
```

## Tính năng
- Xem trailer phim
- Đánh giá và bình luận phim
- Gợi ý phim dựa trên:
  - Collaborative Filtering
  - Content-based Filtering
  - Hybrid Filtering
