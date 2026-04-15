# Chatbot Hỗ trợ Học viên ĐHCS

Chatbot web hỗ trợ học viên Trường Đại học Cảnh sát nhân dân.

Ứng dụng dùng:
- Flask cho backend
- HTML/CSS/JavaScript cho giao diện
- dữ liệu JSON nội bộ cho phần lớn câu trả lời
- Ollama để hỗ trợ fallback khi không có dữ liệu structured phù hợp

Tài liệu chi tiết cho dev xem tại:
- [README.dev.md](./README.dev.md)

## Chatbot trả lời được gì

Hiện hệ thống hỗ trợ các nhóm chính:
- lịch học, lịch thi
- thư viện
- công văn, thông tư, nghị định, biểu mẫu
- hỗ trợ học tập
- tuyển sinh

## Cách chạy nhanh

### 1. Cài Python packages

```bash
pip install flask requests
```

### 2. Cài và chạy Ollama

Tải tại:

```text
https://ollama.com/download
```

Kéo model:

```bash
ollama pull qwen2:1.5b
```

Khởi động Ollama:

```bash
ollama serve
```

### 3. Chạy chatbot

Trong thư mục project:

```bash
python app.py
```

Mở trình duyệt:

```text
http://localhost:5000
```

## Cập nhật dữ liệu

Nếu chỉ muốn cập nhật nội dung trả lời, chỉnh các file trong thư mục `data/`:
- `data/lich_hoc.json`
- `data/ho_so.json`
- `data/tai_lieu.json`
- `data/thu_vien.json`
- `data/tuyen_sinh.json`

Thông thường không cần sửa code nếu chỉ thay đổi nội dung và vẫn giữ đúng cấu trúc dữ liệu.

## Chạy test

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Khi nào cần xem tài liệu dev

Xem [README.dev.md](./README.dev.md) nếu bạn cần:
- hiểu cấu trúc thư mục và vai trò từng file
- biết luồng hoạt động backend/frontend
- thêm intent mới cho chatbot
- sửa service theo từng domain
- chạy kiểm tra kỹ thuật hoặc refactor code
