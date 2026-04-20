# Quy Trinh Them Du Lieu Van Ban Va PDF

Tai lieu nay dung de ghi nho nhanh cac buoc khi:
- them mot thong tu moi co PDF
- them mot luat moi co PDF
- xac dinh khi nao can sua code, khi nao chi can sua du lieu

## 1. Nguyen tac nho nhanh

Neu chi them du lieu moi theo dung cau truc cu:
- thuong chi can sua file JSON trong `data/json/`
- va chep file PDF vao `data/pdf/`

Neu muon chatbot:
- hieu cach hoi moi
- goi y cau hoi moi
- hien thi kieu moi
- uu tien tra structured khac di

thi moi can sua code trong `services/chatbot/` hoac `static/`

## 2. Them mot thong tu moi co PDF

### Buoc 1: chep file PDF vao dung thu muc

Dat file vao:

```text
data/pdf/thong_tu/
```

Vi du ten file:

```text
thong_tu_15_2026.pdf
```

### Buoc 2: sua file du lieu

Mo file:

[ho_so.json](/Users/quochuy/QH_Code/AI/dhcs_chatbot/data/json/ho_so.json)

Tim mang:

```json
"thong_tu": []
```

Them 1 object moi vao mang nay.

### Buoc 3: mau copy-paste cho thong tu moi

```json
{
  "ten": "Thong tu 15/2026/TT-BCA ve quan ly hoc vien",
  "so_hieu": "15/2026/TT-BCA",
  "ngay_ban_hanh": "10/03/2026",
  "ngay_hieu_luc": "01/05/2026",
  "noi_dung": "Quy dinh ve quan ly, ren luyen va danh gia hoc vien trong Cong an nhan dan.",
  "trang_thai": "Con hieu luc",
  "file_pdf": "thong_tu/thong_tu_15_2026.pdf",
  "tu_khoa": [
    "15/2026/tt-bca",
    "15_2026",
    "15-2026",
    "thong tu 15",
    "thong tu 15/2026",
    "quan ly hoc vien"
  ],
  "tom_tat": "Thong tu quy dinh cac noi dung ve quan ly, ren luyen va danh gia hoc vien trong luc luong Cong an nhan dan.",
  "co_quan_ban_hanh": "Bo Cong an"
}
```

### Buoc 4: kiem tra 3 diem quan trong

- `file_pdf` phai trung voi file that trong `data/pdf/thong_tu/`
- `so_hieu` phai dung dinh dang van ban
- `tu_khoa` nen co nhieu bien the de chatbot de match hon

Nen co:
- co dau hoac khong dau tuy du lieu hien tai
- dang co gach duoi `_`
- dang co gach ngang `-`
- dang rut gon theo so hieu

### Buoc 5: test nhanh tren giao dien

Thu hoi:
- `thong tu 15`
- `15/2026/TT-BCA`
- `quan ly hoc vien`

Ky vong:
- chatbot tra ve dung van ban
- co the `Xem tom tat`
- co the `Mo PDF`

### Buoc 6: khi nao can sua code

Thong thuong khong can sua code neu chi them thong tu moi dung schema cu.

Chi can sua code neu:
- chatbot khong nhan ra cach hoi moi
- muon them goi y moi
- muon doi giao dien bang/card

Nhung file co the phai sua:
- [keywords.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/keywords.py)
- [document_context.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/document_context.py)
- [suggestion_service.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/suggestion_service.py)
- [script.js](/Users/quochuy/QH_Code/AI/dhcs_chatbot/static/js/script.js)
- [style.css](/Users/quochuy/QH_Code/AI/dhcs_chatbot/static/css/style.css)

## 3. Them mot luat moi co PDF

### Buoc 1: chep file PDF vao dung thu muc

Dat file vao:

```text
data/pdf/law/
```

Vi du ten file:

```text
luat_trat_tu_an_toan_giao_thong.pdf
```

### Buoc 2: sua file du lieu

Mo file:

[ho_so.json](/Users/quochuy/QH_Code/AI/dhcs_chatbot/data/json/ho_so.json)

Tim mang:

```json
"luat": []
```

Them 1 object moi vao day.

### Buoc 3: mau copy-paste cho luat moi

```json
{
  "ten": "Luat Trat tu, an toan giao thong duong bo",
  "so_hieu": "36/2024/QH15",
  "ngay_ban_hanh": "27/06/2024",
  "ngay_hieu_luc": "01/01/2025",
  "noi_dung": "Quy dinh ve trat tu, an toan giao thong duong bo; quyen, nghia vu va trach nhiem cua co quan, to chuc, ca nhan lien quan.",
  "trang_thai": "Con hieu luc",
  "file_pdf": "law/luat_trat_tu_an_toan_giao_thong.pdf",
  "tu_khoa": [
    "luat trat tu an toan giao thong duong bo",
    "36/2024/qh15",
    "luat giao thong",
    "giao thong duong bo"
  ],
  "tom_tat": "Luat quy dinh ve nguyen tac bao dam trat tu, an toan giao thong duong bo va trach nhiem cua cac chu the lien quan.",
  "co_quan_ban_hanh": "Quoc hoi"
}
```

### Buoc 4: dieu can ghi nho voi nhanh `luat`

Code hien tai dang co logic:
- neu chi co 1 luat trong du lieu thi hoi chung nhu `luat ban hanh` co the tra thang van ban do
- neu co nhieu luat, he thong co the tra bang danh sach luat

Vi vay:
- truoc khi them luat thu 2, hoi `luat ban hanh` co the ra thang `Luat An ninh mang`
- sau khi them nhieu luat, hoi chung co the ra bang thay vi ra 1 file cu the

Day la hanh vi binh thuong voi code hien tai.

### Buoc 5: test nhanh tren giao dien

Thu hoi:
- `luat giao thong`
- `36/2024/QH15`
- `giao thong duong bo`

Ky vong:
- chatbot match dung van ban
- mo duoc PDF
- co tom tat neu metadata day du

### Buoc 6: khi nao can sua code

Can sua code neu ban muon:
- hoi chung `luat ban hanh` van uu tien ra 1 luat cu the
- bang `LUAT` co nut thao tac nhu bang `THONG TU`
- goi y rieng cho tung luat moi

Nhung file co the phai sua:
- [document_context.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/document_context.py)
- [keywords.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/keywords.py)
- [suggestion_service.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/suggestion_service.py)
- [script.js](/Users/quochuy/QH_Code/AI/dhcs_chatbot/static/js/script.js)
- [style.css](/Users/quochuy/QH_Code/AI/dhcs_chatbot/static/css/style.css)

## 4. Truong hop chi them du lieu, khong can sua code

Ban thuong chi can sua du lieu neu:
- them thong tu moi cung schema cu
- them luat moi cung schema cu
- them nghi dinh moi cung schema cu
- cap nhat noi dung tom tat
- doi trang thai van ban
- doi ngay ban hanh, ngay hieu luc

File thuong sua:
- [ho_so.json](/Users/quochuy/QH_Code/AI/dhcs_chatbot/data/json/ho_so.json)

Va neu co PDF:
- `data/pdf/thong_tu/...`
- `data/pdf/law/...`

## 5. Truong hop can sua code

### Can sua `keywords.py` khi

- them cach hoi moi
- muon chatbot nhan ra tu khoa moi

File:
- [keywords.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/keywords.py)

### Can sua `document_context.py` khi

- doi logic chon van ban
- doi cau truc field JSON
- muon tra bang thay vi card PDF
- muon tra card PDF thay vi bang

File:
- [document_context.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/document_context.py)

### Can sua `suggestion_service.py` khi

- muon them goi y cau hoi tiep theo
- muon doi goi y theo ngu canh

File:
- [suggestion_service.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/services/chatbot/suggestion_service.py)

### Can sua frontend khi

- doi giao dien bang
- them nut `Xem tom tat`, `Mo PDF`
- doi kieu hien thi card tai lieu

Files:
- [script.js](/Users/quochuy/QH_Code/AI/dhcs_chatbot/static/js/script.js)
- [style.css](/Users/quochuy/QH_Code/AI/dhcs_chatbot/static/css/style.css)

## 6. Checklist sieu ngan de lam that

### Neu them thong tu moi

1. Chep file vao `data/pdf/thong_tu/`
2. Them item vao `data/json/ho_so.json` trong mang `thong_tu`
3. Kiem tra `file_pdf`
4. Kiem tra `so_hieu`
5. Them `tu_khoa`
6. Thu hoi bang so hieu va ten rut gon

### Neu them luat moi

1. Chep file vao `data/pdf/law/`
2. Them item vao `data/json/ho_so.json` trong mang `luat`
3. Kiem tra `file_pdf`
4. Kiem tra `so_hieu`
5. Them `tu_khoa`
6. Thu hoi bang ten luat, so hieu va tu khong dau

## 7. File test nen xem neu muon sua cho an toan

- [test_document_context.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/tests/test_document_context.py)
- [test_chat_service.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/tests/test_chat_service.py)
- [test_app_auth.py](/Users/quochuy/QH_Code/AI/dhcs_chatbot/tests/test_app_auth.py)

Neu them logic moi, nen them test moi o day de sau nay refactor khong bi vo hanh vi.
