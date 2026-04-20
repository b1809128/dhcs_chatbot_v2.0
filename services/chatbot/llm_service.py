from .config import MODEL_NAME, OLLAMA_URL


def ask_ollama(question: str, context: str | None) -> str:
    import requests

    system_prompt = (
        "Bạn là trợ lý thông tin của Trường Đại học Cảnh sát nhân dân. "
        "Chỉ được trả lời dựa trên dữ liệu tham chiếu được cung cấp. "
        "Nếu dữ liệu chưa đủ để kết luận, hãy nói 'Tôi chưa có thông tin về vấn đề này.' "
        "Không được bịa thêm thông tin ngoài dữ liệu tham chiếu. "
        "Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng, đúng văn phong hành chính."
    )

    prompt_parts = [system_prompt]
    if context:
        prompt_parts.append(f"Dữ liệu tham chiếu nội bộ:\n{context}")
    prompt_parts.append(f"Câu hỏi: {question}\nTrả lời:")
    prompt = "\n\n".join(prompt_parts)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 512},
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "❌ Không kết nối được Ollama. Hãy chắc chắn Ollama đang chạy (ollama serve)."
    except Exception as exc:
        return f"❌ Lỗi: {exc}"
