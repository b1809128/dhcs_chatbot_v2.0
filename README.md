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
- công văn, thông tư, nghị định, luật, biểu mẫu
- hỗ trợ học tập
- tuyển sinh

Ngoài câu trả lời dạng bảng, hệ thống hiện hỗ trợ tài liệu PDF pháp lý:
- khi hỏi đúng văn bản như `thông tư 62_2023` hoặc `luật an ninh mạng`
- chatbot có thể trả về thẻ tài liệu với:
  - tên văn bản
  - số hiệu
  - ngày hiệu lực
  - tóm tắt nội dung
- bấm `Xem tóm tắt` để mở sidebar
- bấm `Xem file PDF` để mở modal xem trực tiếp file PDF trong giao diện

Luồng hiện tại của chatbot:
1. frontend gửi câu hỏi đến `POST /chat`
2. backend ưu tiên tìm `structured response` theo từng domain
3. nếu match được `table`, `list` hoặc `pdf_document` thì trả thẳng cho giao diện
4. nếu không match trực tiếp, hệ thống dựng context từ RAG + dữ liệu nội bộ rồi mới gọi Ollama
5. frontend hiển thị trạng thái `Đang tìm kiếm`, sau đó render câu trả lời và cuộn mượt đến phần nội dung mới

Một số cập nhật UI gần đây:
- bảng `THÔNG TƯ` có nút `Xem tóm tắt` và `Mở PDF` ngay trên từng dòng
- mục `Bài thi VB2CA` hiển thị 4 đề CA1-CA4, cho phép xem nhanh PDF và tải file
- mục `Đơn xin nghỉ phép` hiển thị file Word, có xem nhanh nội dung mẫu và nút tải về
- câu hỏi chung về `luật` hiện ưu tiên trả đúng tài liệu pháp lý thay vì rơi sang dữ liệu thư viện
- khi phản hồi quá nhanh, giao diện vẫn giữ loading tối thiểu để tránh nháy
- câu trả lời mới được cuộn mượt tới đầu nội dung bot vừa render, không nhảy xuống cuối message dài

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

Nếu chỉ muốn cập nhật nội dung trả lời, chỉnh các file trong thư mục `data/json/`:
- `data/json/lich_hoc.json`
- `data/json/ho_so.json`
- `data/json/tai_lieu.json`
- `data/json/thu_vien.json`
- `data/json/tuyen_sinh.json`

Riêng phần tuyển sinh 2026 hiện được xây dựng theo file:

```text
data/pdf/thong_tu/tuyen_sinh_2026.pdf
```

Nội dung tuyển sinh nằm chủ yếu trong `data/json/tuyen_sinh.json`, còn thông tin liên hệ vẫn dùng của Trường Đại học Cảnh sát nhân dân. Các câu hỏi tuyển sinh thực tế như `văn bằng hai`, `chiều cao`, `BMI`, `thị lực`, `lệ phí sơ tuyển`, `hạn đăng ký`, `ngày thi 20/09/2026`, `ngành được phép đăng ký`, `chỉ tiêu CSS`, `kiểm tra sơ bộ điều kiện`, `timeline tuyển sinh`, `checklist hồ sơ sơ tuyển`, `so sánh phương thức tuyển sinh` được xử lý ở:

```text
services/chatbot/admission_context.py
services/chatbot/admission_helpers.py
services/chatbot/admission_precheck.py
services/chatbot/admission_views.py
services/chatbot/keywords.py
services/chatbot/admission_suggestions.py
```

Trong đó:
- `admission_context.py`: router intent tuyển sinh
- `admission_helpers.py`: chuẩn hóa câu hỏi, alias, mã trường, nguồn trích dẫn
- `admission_precheck.py`: kiểm tra sơ bộ điều kiện cá nhân hóa
- `admission_views.py`: dựng các bảng/view tuyển sinh
- `admission_suggestions.py`: gợi ý câu hỏi liên quan riêng cho tuyển sinh

Nếu muốn thêm tài liệu PDF pháp lý:
- đặt file vào `data/pdf/...`
- khai báo metadata tương ứng trong `data/json/ho_so.json`
  - ví dụ: `file_pdf`, `so_hieu`, `ngay_hieu_luc`, `tom_tat`, `tu_khoa`

Sau khi sửa dữ liệu có liên quan đến RAG, build lại index:

```bash
python3 scripts/build_rag_index.py
```

RAG hiện được tách thành:
- `services/chatbot/rag_documents.py`: build/chunk documents từ JSON/PDF/Word metadata
- `services/chatbot/rag_index.py`: build/load/write TF-IDF index
- `services/chatbot/rag_retrieval.py`: score và retrieve documents
- `services/chatbot/rag_service.py`: API public `build_rag_context()`

Thông thường không cần sửa code nếu chỉ thay đổi nội dung và vẫn giữ đúng cấu trúc dữ liệu. Nếu thêm kiểu câu hỏi mới hoặc muốn chatbot bắt keyword mới, hãy cập nhật thêm `keywords.py`, context builder tương ứng và service gợi ý phù hợp.

## Chạy test

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Kiểm tra cú pháp nhanh:

```bash
python3 -m py_compile app.py services/chatbot/*.py tests/*.py
node --check static/js/script.js
```

## Khi nào cần xem tài liệu dev

Xem [README.dev.md](./README.dev.md) nếu bạn cần:
- hiểu cấu trúc thư mục và vai trò từng file
- biết luồng hoạt động backend/frontend sau các cập nhật mới
- thêm intent mới cho chatbot
- sửa service theo từng domain
- chạy kiểm tra kỹ thuật hoặc refactor code
