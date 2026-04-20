# Tài liệu Dev - Chatbot Hỗ trợ Học viên ĐHCS

Chatbot web hỗ trợ học viên Trường Đại học Cảnh sát nhân dân, chạy bằng Flask ở backend và giao diện HTML/CSS/JavaScript ở frontend.

Hệ thống ưu tiên trả lời trực tiếp từ dữ liệu nội bộ JSON theo từng domain như:
- lịch học, lịch thi
- thư viện
- công văn, thông tư, nghị định, luật, biểu mẫu
- tài liệu học tập
- tuyển sinh

Khi không có dữ liệu cấu trúc phù hợp, chatbot có thể fallback sang Ollama để sinh câu trả lời dựa trên context nội bộ.

## Mục tiêu kiến trúc

Code đã được tách theo hướng dễ bảo trì hơn:
- `app.py` chỉ giữ vai trò entrypoint Flask
- mỗi domain nghiệp vụ có module riêng
- logic gợi ý, gọi LLM, helper dữ liệu, keyword được tách riêng
- có test cho từng domain để refactor sau này an toàn hơn

Thiết kế này giúp dự án phù hợp hơn với làm việc nhóm, tái sử dụng code tốt hơn, và giảm rủi ro khi file logic ngày càng lớn.

## Cấu trúc thư mục

```text
dhcs_chatbot/
├── app.py
├── app_mysql.py
├── README.md
├── README.dev.md
├── data/
├── db/
├── services/
│   ├── lich_hoc_service.py
│   └── chatbot/
├── static/
│   ├── css/
│   ├── image/
│   └── js/
├── templates/
├── tests/
└── sandbox/
```

## Vai trò từng thư mục

### `data/`

Chứa dữ liệu nội bộ để chatbot trả lời trực tiếp.

Các file chính:
- `json/lich_hoc.json`: lịch học và lịch thi
- `json/ho_so.json`: công văn, thông tư, nghị định, luật, biểu mẫu, tổ chức
- `json/tai_lieu.json`: nhóm hỗ trợ học tập, giải thích, tóm tắt, ôn tập
- `json/thu_vien.json`: dữ liệu thư viện, đầu sách, quy định mượn trả, giờ mở cửa
- `json/tuyen_sinh.json`: chỉ tiêu, phương thức, hồ sơ, bài thi, thông tin trường
- `json/ra_vao.json`, `json/the_xe.json`: hiện có thể dùng để mở rộng tiếp trong tương lai
- `pdf/`: thư mục chứa file PDF nội bộ được frontend mở qua route `/documents/<path:filename>`

Nguyên tắc:
- nếu chỉ thay đổi nội dung nghiệp vụ, ưu tiên sửa ở `data/json/*.json`
- nếu thay đổi cách hiểu câu hỏi hoặc cách hiển thị câu trả lời, sửa ở `services/chatbot/`

### Cấu trúc dữ liệu PDF pháp lý trong `json/ho_so.json`

Các văn bản như thông tư, luật có thể khai báo thêm metadata PDF để chatbot trả về thẻ tài liệu thay vì chỉ bảng text.

Ví dụ một item:

```json
{
  "ten": "Luật An ninh mạng",
  "so_hieu": "24/2018/QH14",
  "ngay_ban_hanh": "12/06/2018",
  "ngay_hieu_luc": "01/01/2019",
  "noi_dung": "Quy định về hoạt động bảo vệ an ninh quốc gia trên không gian mạng.",
  "trang_thai": "Còn hiệu lực",
  "file_pdf": "law/luat_an_ninh_mang.pdf",
  "tu_khoa": ["luật an ninh mạng", "luat_an_ninh_mang", "24/2018/qh14"],
  "tom_tat": "Luật quy định các biện pháp bảo vệ an ninh mạng.",
  "co_quan_ban_hanh": "Quốc hội"
}
```

Ý nghĩa các field:
- `file_pdf`: đường dẫn tương đối tính từ `data/pdf/`
- `tu_khoa`: các biến thể để match câu hỏi người dùng
- `tom_tat`: nội dung hiển thị nhanh trên card/sidebar
- `ngay_hieu_luc`: dùng cho phần thông tin tóm tắt
- `co_quan_ban_hanh`: hiển thị trong sidebar tài liệu

### `templates/`

Chứa HTML giao diện Flask render ra trình duyệt.

File chính:
- `templates/index.html`: khung giao diện chat, câu hỏi gợi ý ban đầu, input gửi câu hỏi, sidebar tóm tắt tài liệu và modal xem PDF

### `static/`

Chứa tài nguyên tĩnh cho frontend.

Các file chính:
- `static/css/style.css`: giao diện chat
- `static/js/script.js`: gửi câu hỏi, nhận phản hồi, render bảng/list/text/pdf_document, hiển thị gợi ý tiếp theo, mở sidebar và modal PDF
  - hiển thị loading `Đang tìm kiếm` trong lúc đợi phản hồi
  - cuộn mượt đến phần đầu câu trả lời mới
  - bảng `THÔNG TƯ` có thao tác `Xem tóm tắt` và `Mở PDF` ngay trên từng dòng
- `static/image/*`: logo, avatar chatbot, favicon

### `services/`

Chứa logic nghiệp vụ backend.

#### `services/chatbot/`

Đây là package chính của chatbot sau refactor.

Các file quan trọng:
- `__init__.py`
  - export hàm `build_chat_response`
  - dùng lazy import để giảm coupling khi chạy test

- `chat_service.py`
  - điểm điều phối chính của chatbot
  - quyết định trả dữ liệu structured hay fallback sang LLM

- `config.py`
  - cấu hình dùng chung như `DATA_DIR`, `OLLAMA_URL`, `MODEL_NAME`

- `types.py`
  - định nghĩa type alias dùng chung như `JsonDict`, `StructuredContext`

- `utils.py`
  - helper dùng lại ở nhiều nơi
  - đọc file JSON
  - kiểm tra keyword
  - dựng `text`, `list`, `table`, `pdf_document`
  - format context cho LLM
  - tìm sách theo nhiều field

- `keywords.py`
  - gom toàn bộ keyword theo domain
  - giúp dễ bảo trì khi cần mở rộng khả năng nhận diện intent

- `context_builders.py`
  - tập hợp các context builder theo domain
  - cung cấp:
    - `build_direct_context()`: chọn câu trả lời structured trực tiếp nếu có
    - `build_context()`: tạo context text fallback để gửi sang RAG/LLM
  - hiện có 2 nhóm builder:
    - `DIRECT_CONTEXT_BUILDERS`: ưu tiên `schedule -> admission -> document -> library -> study_material`
    - `FALLBACK_CONTEXT_BUILDERS`: gom `document + study_material + library` để dựng context khi không có structured response phù hợp

- `schedule_context.py`
  - xử lý lịch học, lịch thi

- `document_context.py`
  - xử lý công văn, thông tư, nghị định, luật, đơn, tổ chức
  - match tài liệu PDF pháp lý theo `so_hieu`, `file_pdf`, `tu_khoa`
  - nếu hỏi chung `thông tư`, chatbot có thể trả bảng `THÔNG TƯ` với truy cập nhanh đến PDF
  - nếu dữ liệu `luật` hiện chỉ có 1 văn bản, câu hỏi chung như `luật ban hành` có thể trả trực tiếp `pdf_document`

- `library_context.py`
  - xử lý tra cứu sách, giờ mở cửa, liên hệ thư viện, quy định mượn trả, tài liệu đọc tại chỗ

- `admission_context.py`
  - xử lý tuyển sinh: chỉ tiêu, phương thức, điều kiện, chứng chỉ, VB2CA, hồ sơ, ngành, thông tin trường

- `study_material_context.py`
  - xử lý hỗ trợ học tập như giải thích, tóm tắt, câu hỏi ôn tập

- `suggestion_service.py`
  - sinh 4 câu hỏi gợi ý theo đúng ngữ cảnh câu trả lời

- `llm_service.py`
  - gọi Ollama
  - chỉ dùng khi không có structured response phù hợp

#### `services/lich_hoc_service.py`

Service mẫu cho hướng làm việc với MySQL.
Hiện project chính vẫn đang chạy chủ yếu theo dữ liệu JSON.

### `db/`

Chứa phần kết nối cơ sở dữ liệu.

Các file chính:
- `db/mysql.py`: tạo kết nối MySQL để dùng lại ở service khác
- `db/__init__.py`: file khởi tạo package

### `tests/`

Chứa test backend theo từng domain.

Các file chính:
- `test_schedule_context.py`
- `test_document_context.py`
- `test_library_context.py`
- `test_admission_context.py`
- `test_study_material_context.py`
- `test_chat_service.py`

Mục tiêu:
- khóa hành vi hiện tại
- giúp refactor an toàn
- hỗ trợ làm việc nhóm và review code dễ hơn

### `sandbox/`

Thư mục thử nghiệm, nháp hoặc POC.

Không nên đặt logic production quan trọng ở đây.

## Luồng vận hành chatbot

### 1. Người dùng gửi câu hỏi từ frontend

Frontend trong `static/js/script.js` gọi:

```text
POST /chat
```

Payload dạng:

```json
{
  "message": "Lịch học lớp DTHS3"
}
```

### 2. Flask nhận request

Trong `app.py`:
- đọc `message`
- gọi `build_chat_response(question)`
- phục vụ file PDF qua route `/documents/<path:filename>`

### 3. `chat_service.py` điều phối xử lý

Luồng cơ bản:
1. chuẩn hóa câu hỏi
2. gọi `build_direct_context()`
3. nếu kết quả là `table`, `list` hoặc `pdf_document` thì trả structured response thẳng cho frontend
4. nếu có `structured_data` nhưng không thuộc nhóm trả thẳng, gọi `build_rag_context(preferred_context=structured_data)` để ưu tiên dựng context từ dữ liệu đã match
5. nếu chưa có đủ context thì fallback sang `format_context_data(structured_data)` hoặc `build_context()`
6. gửi context cuối cùng sang `ask_ollama()`
7. trả về `reply`, `data`, `suggestions`, `references`, `source`

Ghi chú:
- `source="structured"` khi frontend render từ dữ liệu có cấu trúc
- `source="ollama"` khi câu trả lời được sinh từ LLM
- `references` dùng để hiển thị các nguồn RAG đã tham chiếu

### 4. Frontend render kết quả

`static/js/script.js` sẽ:
- hiển thị message người dùng
- gọi API `/chat`
- chèn trạng thái `Đang tìm kiếm` trong lúc chờ
- render kết quả theo loại:
  - `table`
  - `list`
  - `text`
  - `pdf_document`
- hiển thị 4 câu hỏi gợi ý tiếp theo
- nếu là `pdf_document` thì cho phép:
  - mở sidebar tóm tắt
  - mở modal xem PDF
- nếu là bảng `THÔNG TƯ` thì cho phép:
  - `Xem tóm tắt` ngay trên từng dòng
  - `Mở PDF` ngay trên từng dòng
- sau khi render, khung chat sẽ cuộn mượt tới phần đầu câu trả lời mới

## Dạng phản hồi của backend

Backend có thể trả về:

### Trường hợp 1: structured response

```json
{
  "reply": "LỊCH HỌC",
  "data": {
    "type": "table",
    "title": "LỊCH HỌC",
    "columns": ["Lớp", "Môn", "Giảng viên", "Phòng", "Thời gian"],
    "rows": [...]
  },
  "suggestions": [
    "Lịch học lớp THAHS",
    "Lịch học môn Luật Hình sự",
    "Lịch thi",
    "Lịch học môn Tố tụng hình sự"
  ]
}
```

### Trường hợp 1b: structured PDF document

```json
{
  "reply": "LUẬT",
  "data": {
    "type": "pdf_document",
    "title": "LUẬT",
    "document_type": "Luật",
    "name": "Luật An ninh mạng",
    "so_hieu": "24/2018/QH14",
    "ngay_ban_hanh": "12/06/2018",
    "ngay_hieu_luc": "01/01/2019",
    "trang_thai": "Còn hiệu lực",
    "tom_tat": "Luật quy định các biện pháp bảo vệ an ninh mạng.",
    "co_quan_ban_hanh": "Quốc hội",
    "file_url": "/documents/law/luat_an_ninh_mang.pdf",
    "file_name": "luat_an_ninh_mang.pdf"
  },
  "suggestions": [
    "Thông tư 62_2023",
    "Nghị định",
    "Công văn",
    "Đơn xin phép"
  ]
}
```

### Trường hợp 2: fallback qua LLM

```json
{
  "reply": "...câu trả lời từ Ollama...",
  "data": null,
  "suggestions": [],
  "references": [
    {
      "title": "Chỉ tiêu tuyển sinh năm 2026",
      "domain": "admission",
      "source_file": "tuyen_sinh.json"
    }
  ],
  "source": "ollama"
}
```

## Cách chạy chatbot

### 1. Cài Python packages

Nếu môi trường chưa có sẵn:

```bash
pip install flask requests
```

Nếu sau này project có `requirements.txt`, có thể thay bằng:

```bash
pip install -r requirements.txt
```

### 2. Cài Ollama

Tải tại:

```text
https://ollama.com/download
```

Kéo model một lần:

```bash
ollama pull qwen2:1.5b
```

Khởi động Ollama:

```bash
ollama serve
```

### 3. Chạy web app

Trong thư mục project:

```bash
python app.py
```

Mở trình duyệt:

```text
http://localhost:5000
```

## Cách chạy test

Chạy toàn bộ test:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Compile kiểm tra cú pháp:

```bash
python3 -m py_compile app.py services/chatbot/*.py tests/*.py
```

## Cách cập nhật dữ liệu

### Khi chỉ thay đổi nội dung

Sửa trực tiếp các file JSON trong `data/json/`.

Ví dụ:
- thêm đầu sách mới: sửa `data/json/thu_vien.json`
- đổi lịch học: sửa `data/json/lich_hoc.json`
- cập nhật tuyển sinh: sửa `data/json/tuyen_sinh.json`

Thông thường không cần đổi frontend nếu cấu trúc field cũ vẫn được giữ.

### Khi thêm loại câu hỏi mới

Thường sẽ cần cập nhật ở 3 nơi:

1. `services/chatbot/keywords.py`
2. file domain tương ứng trong `services/chatbot/*_context.py`
3. `services/chatbot/suggestion_service.py` hoặc `static/js/script.js`

### Khi muốn chatbot trả lời trực tiếp thay vì qua LLM

Thêm logic vào một context builder phù hợp, ví dụ:
- `library_context.py`
- `admission_context.py`
- `document_context.py`

Sau đó đảm bảo builder đó:
- được đặt đúng thứ tự trong `DIRECT_CONTEXT_BUILDERS` nếu muốn trả lời trực tiếp
- hoặc được thêm vào `FALLBACK_CONTEXT_BUILDERS` nếu chỉ muốn dùng để tạo context cho RAG/LLM

## Cách làm việc theo nhóm

Gợi ý chia việc:
- người 1: dữ liệu JSON và xác minh nghiệp vụ
- người 2: backend context builder theo domain
- người 3: frontend render và UX gợi ý
- người 4: test và review logic

Nguyên tắc nên giữ:
- sửa domain nào thì thêm test domain đó
- không nhồi thêm logic mới vào `app.py`
- ưu tiên tái sử dụng helper trong `utils.py`
- keyword mới nên đưa vào `keywords.py`
- gợi ý ngữ cảnh nên ưu tiên `suggestion_service.py`

## Điểm mở rộng tiếp theo

Một số hướng phát triển tiếp:
- tách sâu hơn `library_context.py` và `admission_context.py` thành nhiều hàm private theo intent
- thêm `requirements.txt`
- thêm test cho frontend
- thêm logging
- thêm cache dữ liệu JSON
- thêm support database thật thay vì chỉ JSON
- thêm API versioning nếu hệ thống mở rộng lớn hơn

## Tóm tắt nhanh để onboard

Nếu bạn mới vào dự án, hãy đọc theo thứ tự này:

1. `app.py`
2. `services/chatbot/chat_service.py`
3. `services/chatbot/context_builders.py`
4. domain bạn cần sửa, ví dụ `library_context.py`
5. `static/js/script.js`
6. file JSON tương ứng trong `data/json/`
7. test domain tương ứng trong `tests/`

Chỉ cần nắm chuỗi đó là đã có thể bắt đầu sửa tính năng khá an toàn.
