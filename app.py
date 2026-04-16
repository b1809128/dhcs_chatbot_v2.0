import os

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.exceptions import NotFound

from services.chatbot import build_chat_response
from services.chatbot.access_control import (
    build_access_denied_response,
    get_initial_suggestions,
    is_public_query,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dhcs-chatbot-dev-secret")
app.config["CHATBOT_USERNAME"] = os.getenv("CHATBOT_USERNAME", "hocvien")
app.config["CHATBOT_PASSWORD"] = os.getenv("CHATBOT_PASSWORD", "dhcs123")
STATIC_IMAGE_DIR = os.path.join(app.root_path, "static", "image")
DATA_PDF_DIR = os.path.join(app.root_path, "data", "pdf")


def is_authenticated() -> bool:
    return bool(session.get("is_authenticated"))


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        STATIC_IMAGE_DIR,
        "t05.png",
        mimetype="image/png",
        max_age=0,
    )


@app.route("/documents/<path:filename>")
def serve_document(filename: str):
    try:
        return send_from_directory(
            DATA_PDF_DIR,
            filename,
            mimetype="application/pdf",
            max_age=0,
        )
    except NotFound:
        return jsonify({"error": "Không tìm thấy tài liệu PDF."}), 404


@app.route("/")
def index():
    auth_state = is_authenticated()
    return render_template(
        "index.html",
        is_authenticated=auth_state,
        current_user=session.get("username", ""),
        initial_suggestions=get_initial_suggestions(auth_state),
        input_placeholder=(
            "Nhập câu hỏi của bạn..."
            if auth_state
            else "Nhập câu hỏi về tuyển sinh hoặc đăng nhập để dùng chức năng nội bộ..."
        ),
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if (
        username == app.config["CHATBOT_USERNAME"]
        and password == app.config["CHATBOT_PASSWORD"]
    ):
        session["is_authenticated"] = True
        session["username"] = username
        flash("Đăng nhập thành công.", "success")
        return redirect(url_for("index"))

    flash("Sai tên đăng nhập hoặc mật khẩu.", "error")
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Đăng xuất thành công.", "success")
    return redirect(url_for("index"))


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json() or {}
    question = payload.get("message", "")

    if not is_authenticated() and not is_public_query(question):
        return jsonify(build_access_denied_response()), 403

    response = build_chat_response(question)
    return jsonify(response)


if __name__ == "__main__":
    print("🚀 Khởi động chatbot ĐHCS tại http://localhost:5000")
    app.run(debug=True, port=5000)
