from .admission_helpers import VB2CA_EXAM_FILES


def build_vb2ca_exam_documents(items: list[dict]) -> list[dict]:
    documents = []

    for item in items:
        exam_code = item.get("ma", "")
        file_path = VB2CA_EXAM_FILES.get(exam_code)
        if not file_path:
            continue

        documents.append(
            {
                "type": "pdf_document",
                "title": "BÀI THI ĐÁNH GIÁ",
                "document_type": "Đề thi VB2CA",
                "name": f"Đề thi VB2CA {exam_code}",
                "so_hieu": exam_code,
                "noi_dung": item.get("trac_nghiem_tu_chon", ""),
                "tom_tat": (
                    f"Mã bài thi {exam_code}. "
                    f"Tự luận bắt buộc: {item.get('tu_luan_bat_buoc', '')}. "
                    f"Trắc nghiệm bắt buộc: {', '.join(item.get('trac_nghiem_bat_buoc', []))}."
                ),
                "file_url": f"/documents/{file_path}",
                "download_url": f"/documents/download/{file_path}",
                "file_name": file_path.rsplit("/", 1)[-1],
                "file_type": "pdf",
            }
        )

    return documents


def build_admission_quota_rows(items: list[dict]) -> list[dict]:
    return [
        {
            "ten_truong": item.get("ten_truong", ""),
            "ma_truong": item.get("ma_truong", ""),
            "nhom_nganh": item.get("nhom_nganh", ""),
            "ma_nganh": item.get("ma_nganh", ""),
            "dia_ban": item.get("dia_ban", ""),
            "tong_chi_tieu": item.get("tong_chi_tieu", ""),
            "pt1": (
                f"Nam {item.get('phuong_thuc_1', {}).get('nam', 0)}, "
                f"Nữ {item.get('phuong_thuc_1', {}).get('nu', 0)}"
            ),
            "pt2": (
                f"Nam {item.get('phuong_thuc_2', {}).get('nam', 0)}, "
                f"Nữ {item.get('phuong_thuc_2', {}).get('nu', 0)}"
            ),
        }
        for item in items
    ]


def build_vb2ca_overview_rows(data: dict, ts: dict) -> list[dict]:
    thong_bao = data.get("thong_bao_tuyen_sinh", {})
    chi_tieu_css = ts.get("chi_tieu", {}).get("truong_dai_hoc_canh_sat_nhan_dan", {})
    bai_thi = data.get("bai_thi_danh_gia_bo_cong_an", {})
    pham_vi = ts.get("pham_vi_tuyen_sinh", {})
    nganh = next((item for item in ts.get("nganh_tuyen_sinh", []) if item.get("ma_truong") == "CSS"), {})
    phuong_thuc = [
        f"{item.get('ma')}. {item.get('ten')}: {item.get('mo_ta')}"
        for item in ts.get("phuong_thuc_tuyen_sinh", [])
    ]

    return [
        {"muc": "Thông báo", "chi_tiet": thong_bao.get("ten_thong_bao", "")},
        {"muc": "Đối tượng chính", "chi_tiet": " ".join(ts.get("doi_tuong_du_tuyen", [])[:2])},
        {"muc": "Điều kiện nổi bật", "chi_tiet": " ".join(ts.get("dieu_kien_chung", [])[:3])},
        {"muc": "Phương thức tuyển sinh", "chi_tiet": " ".join(phuong_thuc)},
        {
            "muc": "Trường Đại học Cảnh sát nhân dân",
            "chi_tiet": (
                f"Mã trường CSS; ngành {nganh.get('ten_nganh', '')}; "
                f"mã ngành {nganh.get('ma_nganh', '')}; địa bàn {nganh.get('dia_ban', '')}; "
                f"chỉ tiêu {chi_tieu_css.get('tong_chi_tieu', '')}."
            ),
        },
        {"muc": "Phạm vi tuyển sinh", "chi_tiet": pham_vi.get("phia_nam", "")},
        {
            "muc": "Bài thi đánh giá",
            "chi_tiet": (
                f"Ngày thi {bai_thi.get('ngay_thi', '')}; "
                f"hình thức {bai_thi.get('hinh_thuc_thi', '')}; "
                f"mã bài thi: {', '.join(nganh.get('ma_bai_thi_danh_gia', []))}."
            ),
        },
    ]


def build_admission_summary_rows(data: dict, ts: dict) -> list[dict]:
    thong_bao = data.get("thong_bao_tuyen_sinh", {})
    chi_tieu = ts.get("chi_tieu", {})
    bai_thi = data.get("bai_thi_danh_gia_bo_cong_an", {})
    thu_tuc = ts.get("thu_tuc_dang_ky", {})
    css_quota = chi_tieu.get("truong_dai_hoc_canh_sat_nhan_dan", {})

    return [
        {"muc": "Tên thông báo", "chi_tiet": thong_bao.get("ten_thong_bao", "")},
        {"muc": "Số hiệu", "chi_tiet": thong_bao.get("so_hieu", "")},
        {"muc": "Tổng chỉ tiêu", "chi_tiet": chi_tieu.get("tong_chi_tieu", "")},
        {"muc": "Chỉ tiêu CSS", "chi_tiet": css_quota.get("tong_chi_tieu", "")},
        {"muc": "Phương thức", "chi_tiet": "Xét tuyển thẳng hoặc thi tuyển bằng Bài thi đánh giá của Bộ Công an."},
        {"muc": "Ngày thi", "chi_tiet": bai_thi.get("ngay_thi", "")},
        {"muc": "Hạn đăng ký sơ tuyển", "chi_tiet": thu_tuc.get("thoi_gian_dang_ky", "")},
        {"muc": "Lệ phí sơ tuyển", "chi_tiet": thu_tuc.get("le_phi_so_tuyen", "")},
    ]


def build_admission_timeline_rows(data: dict, ts: dict) -> list[dict]:
    thong_bao = data.get("thong_bao_tuyen_sinh", {})
    thu_tuc = ts.get("thu_tuc_dang_ky", {})
    bai_thi = data.get("bai_thi_danh_gia_bo_cong_an", {})
    return [
        {"moc": thong_bao.get("ngay_ban_hanh", ""), "noi_dung": "Ban hành thông báo tuyển sinh VB2CA năm 2026."},
        {"moc": thu_tuc.get("thoi_gian_dang_ky", ""), "noi_dung": "Thí sinh đăng ký sơ tuyển tại Công an cấp xã nơi thường trú."},
        {"moc": "20/08/2026", "noi_dung": "Sinh viên năm cuối phải có bằng tốt nghiệp hoặc giấy xác nhận/công nhận tốt nghiệp để xét tuyển."},
        {"moc": bai_thi.get("ngay_thi", ""), "noi_dung": f"Thi Bài thi đánh giá của Bộ Công an; hình thức {bai_thi.get('hinh_thuc_thi', '')}."},
        {"moc": "Thời gian nhập học", "noi_dung": "Thí sinh phải hoàn thiện văn bằng, hồ sơ theo yêu cầu khi nhập học."},
    ]


def build_method_comparison_rows(ts: dict, data: dict) -> list[dict]:
    pt1 = ts.get("dieu_kien_theo_phuong_thuc", {}).get("phuong_thuc_1", [])
    pt2 = ts.get("dieu_kien_theo_phuong_thuc", {}).get("phuong_thuc_2", {})
    bai_thi = data.get("bai_thi_danh_gia_bo_cong_an", {})
    return [
        {
            "tieu_chi": "Bản chất",
            "phuong_thuc_1": "Xét tuyển thẳng theo điều kiện ưu tiên.",
            "phuong_thuc_2": pt2.get("ten", "Thi tuyển bằng Bài thi đánh giá của Bộ Công an."),
        },
        {
            "tieu_chi": "Điều kiện chính",
            "phuong_thuc_1": " ".join(pt1[:3]),
            "phuong_thuc_2": " ".join(pt2.get("yeu_cau_chung", [])[:2]),
        },
        {
            "tieu_chi": "Bài thi",
            "phuong_thuc_1": "Không thi bài đánh giá nếu đủ điều kiện xét tuyển thẳng.",
            "phuong_thuc_2": f"{bai_thi.get('thoi_gian_lam_bai', '')}; {bai_thi.get('hinh_thuc_thi', '')}; ngày thi {bai_thi.get('ngay_thi', '')}.",
        },
        {
            "tieu_chi": "Điểm/ưu tiên",
            "phuong_thuc_1": "Ưu tiên theo xếp loại tốt nghiệp, chứng chỉ ngoại ngữ và diện con Công an.",
            "phuong_thuc_2": f"{bai_thi.get('cong_thuc_tinh_diem', '')}; {bai_thi.get('nguong_dau_vao', '')}.",
        },
    ]


def build_admission_action_documents(data: dict) -> list[dict]:
    thong_bao = data.get("thong_bao_tuyen_sinh", {})
    documents = [
        {
            "type": "pdf_document",
            "title": "THÔNG BÁO TUYỂN SINH",
            "document_type": "Thông báo tuyển sinh",
            "name": thong_bao.get("ten_thong_bao", "Thông báo tuyển sinh VB2CA 2026"),
            "so_hieu": thong_bao.get("so_hieu", ""),
            "ngay_ban_hanh": thong_bao.get("ngay_ban_hanh", ""),
            "tom_tat": "Thông báo tuyển sinh VB2CA năm 2026.",
            "file_url": "/documents/thong_tu/tuyen_sinh_2026.pdf",
            "download_url": "/documents/download/thong_tu/tuyen_sinh_2026.pdf",
            "file_name": "tuyen_sinh_2026.pdf",
            "file_type": "pdf",
        }
    ]
    documents.extend(build_vb2ca_exam_documents(data.get("bai_thi_danh_gia_bo_cong_an", {}).get("cac_ma_bai_thi", [])))
    return documents
