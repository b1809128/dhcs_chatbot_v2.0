# Chatbot Hỗ trợ Sinh viên ĐHCS
Chạy hoàn toàn offline – không cần internet sau khi cài đặt.

---

## Cấu trúc thư mục

```
dhcs_chatbot/
├── app.py                  ← Server Flask chính
├── app_mysql.py            ← Biến thể dùng MySQL
├── db/
│   ├── __init__.py
│   └── mysql.py            ← Kết nối MySQL dùng lại cho service
├── sandbox/
│   ├── __init__.py
│   ├── README.md
│   ├── test.py             ← File backend thử nghiệm / nháp
│   └── test.js             ← File frontend thử nghiệm / nháp
├── services/
│   └── lich_hoc_service.py
├── templates/
│   └── index.html          ← Giao diện web
├── static/
│   ├── css/
│   │   └── style.css
│   ├── image/
│   └── js/
│       └── script.js       ← Frontend chính
└── data/
    ├── lich_hoc.json       ← Lịch học, lịch thi
    ├── ho_so.json          ← Công văn, thông tư, biểu mẫu
    ├── tai_lieu.json       ← Tài liệu nghiệp vụ
    ├── thu_vien.json       ← Dữ liệu thư viện
    └── tuyen_sinh.json     ← Thông tin tuyển sinh CAND
```

---

## Bước 1 – Cài Ollama

Tải tại: https://ollama.com/download

Sau khi cài, mở terminal và kéo model (chỉ cần làm 1 lần):
```bash
ollama pull llama3
```
> Hoặc dùng model nhỏ hơn nếu máy yếu:
> `ollama pull qwen2:1.5b`
> (nhớ đổi MODEL_NAME trong app.py thành "qwen2:1.5b")

Khởi động Ollama (luôn phải chạy trước khi dùng chatbot):
```bash
ollama serve
```

---

## Bước 2 – Cài Python packages

```bash
cd dhcs_chatbot
pip install -r requirements.txt
```

---

## Bước 3 – Chạy chatbot

```bash
python app.py
```

Mở trình duyệt: http://localhost:5000

---

## Cập nhật dữ liệu

Chỉnh sửa các file JSON trong thư mục `data/` để cập nhật:
- Lịch học mới → `data/lich_hoc.json`
- Công văn mới → `data/cong_van.json`
- Thêm xe → `data/the_xe.json`
- Cập nhật tuyển sinh → `data/tuyen_sinh.json`

Không cần restart server, dữ liệu được đọc mỗi lần có câu hỏi.

---

## Mô hình được khuyến nghị

| Máy tính          | Model gợi ý           | RAM cần  |
|-------------------|-----------------------|----------|
| Mạnh (≥16GB RAM)  | llama3                | ~8GB     |
| Trung bình (8GB)  | qwen2:7b              | ~5GB     |
| Yếu (4GB)         | qwen2:1.5b hoặc phi3  | ~2GB     |
