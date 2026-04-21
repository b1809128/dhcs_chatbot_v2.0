const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const docSidebar = document.getElementById("doc-sidebar");
const docSidebarBackdrop = document.getElementById("doc-sidebar-backdrop");
const docSidebarCloseBtn = document.getElementById("doc-sidebar-close");
const docSidebarTitle = document.getElementById("doc-sidebar-title");
const docSidebarBody = document.getElementById("doc-sidebar-body");
const docOpenModalBtn = document.getElementById("doc-open-modal-btn");
const docOpenNewTab = document.getElementById("doc-open-new-tab");
const docDownloadLink = document.getElementById("doc-download-link");
const pdfModal = document.getElementById("pdf-modal");
const pdfModalBackdrop = document.getElementById("pdf-modal-backdrop");
const pdfModalCloseBtn = document.getElementById("pdf-modal-close");
const pdfModalTitle = document.getElementById("pdf-modal-title");
const pdfModalFrame = document.getElementById("pdf-modal-frame");
const pdfModalFallback = document.getElementById("pdf-modal-fallback");
const pdfModalDownload = document.getElementById("pdf-modal-download");

const BOT_AVATAR_SRC = "/static/image/chatbotai.png";
const MIN_LOADING_TIME = 1800;
const SMOOTH_SCROLL_DURATION = 360;
let activeDocumentData = null;
let activeScrollAnimationFrame = null;
const ADMISSION_TITLES = new Set([
  "TUYỂN SINH",
  "TUYỂN SINH VĂN BẰNG 2",
  "BÀI THI ĐÁNH GIÁ",
  "THÔNG TIN BÀI THI ĐÁNH GIÁ",
  "KIỂM TRA SƠ BỘ ĐIỀU KIỆN",
  "TÓM TẮT TUYỂN SINH VB2CA 2026",
  "TIMELINE TUYỂN SINH VB2CA 2026",
  "CHECKLIST HỒ SƠ SƠ TUYỂN",
  "SO SÁNH PHƯƠNG THỨC TUYỂN SINH",
  "TÀI LIỆU VÀ HÀNH ĐỘNG TUYỂN SINH",
  "HỒ SƠ TUYỂN SINH",
  "NGÀNH TUYỂN SINH",
  "NGÀNH ĐƯỢC PHÉP ĐĂNG KÝ",
  "THÔNG TIN TRƯỜNG",
  "LIÊN HỆ TUYỂN SINH",
  "CHỈ TIÊU TUYỂN SINH",
  "THỦ TỤC SƠ TUYỂN",
  "ƯU TIÊN TUYỂN SINH",
  "ĐÀO TẠO VÀ CHÍNH SÁCH",
  "XÉT TUYỂN VÀ CÁCH TÍNH ĐIỂM",
  "TIÊU CHUẨN SỨC KHỎE",
  "PHẠM VI TUYỂN SINH",
  "THÔNG BÁO TUYỂN SINH",
]);

const FOLLOWUP_MAP = [
  {
    match: [
      "lịch học",
      "học hôm nay",
      "thời khóa biểu",
      "dths3",
      "thahs",
      "qlhc",
      "kths",
      "phòng",
      "lớp",
      "giảng viên",
      "luật hình sự",
      "tố tụng hình sự",
      "quản lý hành chính",
      "kỹ thuật hình sự",
      "p101",
      "p105",
      "p202",
      "p303",
      "p404",
    ],
    suggestions: [
      "Lịch học lớp DTHS3",
      "Lịch học lớp THAHS",
      "Lịch học môn Luật Hình sự",
      "Lịch thi",
    ],
  },
  {
    match: [
      "lịch thi",
      "thi khi nào",
      "thi",
      "ngày thi",
      "phòng thi",
      "hội trường a",
      "hội trường b",
      "phòng thi c1",
      "phòng thi d2",
      "ca1",
      "ca2",
      "ca3",
      "ca4",
      "vb2ca",
      "bài thi đánh giá",
    ],
    suggestions: [
      "Lịch thi Luật Hình sự",
      "Lịch thi Tố tụng hình sự",
      "Lịch thi Quản lý hành chính",
      "Lịch thi Kỹ thuật hình sự",
    ],
  },
  {
    match: [
      "sách",
      "thư viện",
      "mượn",
      "kệ",
      "vị trí",
      "còn sách",
      "hết sách",
      "giờ mở cửa",
      "mở cửa",
      "liên hệ thư viện",
      "thủ thư",
      "mượn tối đa",
      "gia hạn",
      "trả trễ",
      "phạt",
      "mã tài liệu",
      "isbn",
      "tác giả",
      "đọc tại chỗ",
      "chỉ đọc tại chỗ",
      "giáo trình luật hình sự",
      "luật tố tụng hình sự",
      "nghiệp vụ công an cơ bản",
      "pháp luật đại cương",
      "giáo trình quản lý hành chính",
      "kỹ thuật hình sự cơ bản",
      "kệ a1",
      "kệ a2",
      "kệ b1",
      "kệ c1",
      "kệ c2",
      "kệ d1",
    ],
    suggestions: [
      "Giờ mở cửa thư viện",
      "Mượn tối đa",
      "Chỉ đọc tại chỗ",
      "Liên hệ thư viện",
    ],
  },
  {
    match: [
      "công văn",
      "thông tư",
      "nghị định",
      "đơn",
      "biểu mẫu",
      "đơn xin phép",
      "đơn nghỉ tranh thủ",
      "đoàn thanh niên",
      "đảng viên",
      "tổ chức",
      "công tác đoàn",
    ],
    suggestions: [
      "Công văn",
      "Thông tư",
      "Nghị định",
      "Đơn xin phép",
    ],
  },
  {
    match: [
      "tuyển sinh",
      "chỉ tiêu",
      "phương thức",
      "ngành",
      "xét tuyển",
      "điều kiện",
      "hồ sơ",
      "nhập học",
      "mã trường",
      "mã ngành",
      "ielts",
      "chứng chỉ",
      "tiếng anh",
      "liên hệ",
      "email",
      "phía nam",
      "văn bằng 2",
      "đại học chính quy",
      "xét tuyển thẳng",
      "thi tuyển",
      "ngưỡng đầu vào",
      "trường đại học cảnh sát nhân dân",
      "css",
    ],
    suggestions: [
      "Chỉ tiêu tuyển sinh",
      "Phương thức tuyển sinh",
      "Điều kiện dự tuyển",
      "Hồ sơ nhập học",
    ],
  },
  {
    match: [
      "giải đáp thắc mắc",
      "giải thích bài giảng",
      "tóm tắt giáo trình",
      "tạo câu hỏi ôn tập",
      "gợi ý phương pháp học",
      "hỗ trợ tự học",
      "ôn tập",
      "trắc nghiệm",
      "tóm tắt",
      "giải thích",
      "tự học",
    ],
    suggestions: [
      "Giải thích bài giảng",
      "Tóm tắt giáo trình",
      "Tạo câu hỏi ôn tập",
      "Gợi ý phương pháp học",
    ],
  },
];

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function nl2br(text) {
  return escapeHtml(text).replace(/\n/g, "<br>");
}

function easeOutCubic(progress) {
  return 1 - Math.pow(1 - progress, 3);
}

function cancelActiveScrollAnimation() {
  if (!activeScrollAnimationFrame) return;

  cancelAnimationFrame(activeScrollAnimationFrame);
  activeScrollAnimationFrame = null;
}

function smoothScrollTo(targetTop, duration = SMOOTH_SCROLL_DURATION) {
  if (!chatBox) return;

  cancelActiveScrollAnimation();

  const startTop = chatBox.scrollTop;
  const nextTop = Math.max(targetTop, 0);
  const distance = nextTop - startTop;

  if (Math.abs(distance) < 2) {
    chatBox.scrollTop = nextTop;
    return;
  }

  const startTime = performance.now();

  const tick = (now) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = easeOutCubic(progress);

    chatBox.scrollTop = startTop + distance * eased;

    if (progress < 1) {
      activeScrollAnimationFrame = requestAnimationFrame(tick);
      return;
    }

    chatBox.scrollTop = nextTop;
    activeScrollAnimationFrame = null;
  };

  activeScrollAnimationFrame = requestAnimationFrame(tick);
}

function scrollToBottom() {
  smoothScrollTo(chatBox.scrollHeight);
}

function scrollToElement(element) {
  if (!element) return;

  smoothScrollTo(element.offsetTop - 16);
}

function waitForStableLayout(element) {
  return new Promise((resolve) => {
    let previousTop = -1;
    let stableFrames = 0;

    const settle = () => {
      if (!element?.isConnected) {
        resolve();
        return;
      }

      const currentTop = element.offsetTop;

      if (Math.abs(currentTop - previousTop) <= 1) {
        stableFrames += 1;
      } else {
        stableFrames = 0;
      }

      previousTop = currentTop;

      if (stableFrames >= 2) {
        resolve();
        return;
      }

      requestAnimationFrame(settle);
    };

    requestAnimationFrame(settle);
  });
}

async function scrollToElementAfterRender(element) {
  if (!element) return;

  await waitForStableLayout(element);
  scrollToElement(element);
}

function updateHeaderScrollState() {
  document.body.classList.toggle("is-chat-scrolled", chatBox.scrollTop > 24);
}

function setSendingState(isSending) {
  sendBtn.disabled = isSending;
  userInput.disabled = isSending;
}

function createBotAvatarHtml() {
  return `
    <div class="avatar">
      <img src="${BOT_AVATAR_SRC}" class="bot-avatar-img" alt="Bot" />
    </div>
  `;
}

function appendRow(html) {
  chatBox.insertAdjacentHTML("beforeend", html);
  return chatBox.lastElementChild;
}

function addUserMessage(text) {
  appendRow(`
    <div class="message-row" style="justify-content:flex-end;">
      <div class="message" style="background:#1c9608;color:#fff;width:auto;max-width:80%;">
        ${escapeHtml(text)}
      </div>
    </div>
  `);
}

function buildTypingHtml() {
  return `
    <div class="message-row" id="typing-row">
      ${createBotAvatarHtml()}
      <div class="message message-loading" aria-live="polite">
        <span>Đang tìm kiếm</span>
        <span class="loading-dots" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </div>
    </div>
  `;
}

function showTyping() {
  removeTyping();
  appendRow(buildTypingHtml());
  updateHeaderScrollState();
  requestAnimationFrame(() => {
    scrollToBottom();
  });
}

function removeTyping() {
  const typingRow = document.getElementById("typing-row");
  if (typingRow) typingRow.remove();
}

function waitForNextPaint() {
  return new Promise((resolve) => {
    requestAnimationFrame(() => {
      requestAnimationFrame(resolve);
    });
  });
}

function delay(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function normalizeSuggestionText(text) {
  return String(text || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

function extractResponseContextValues(response) {
  if (!Array.isArray(response?.data?.rows)) {
    return [];
  }

  return response.data.rows.flatMap((row) => Object.values(row || {}));
}

function getSuggestionLimit(response) {
  const title = response?.data?.title;
  const source = String(response?.source || "").toLowerCase();
  const hasAdmissionSuggestion = Array.isArray(response?.suggestions)
    && response.suggestions.some((item) => normalizeSuggestionText(item).includes("tuyển sinh"));

  if (ADMISSION_TITLES.has(title) || (source === "ollama" && hasAdmissionSuggestion)) {
    return 12;
  }

  return 4;
}

function uniqueSuggestions(suggestions, question, limit) {
  const seen = new Set();
  const normalizedQuestion = normalizeSuggestionText(question);

  return suggestions
    .filter((item) => {
      const normalizedItem = normalizeSuggestionText(item);

      if (!normalizedItem || normalizedItem === normalizedQuestion) {
        return false;
      }

      if (seen.has(normalizedItem)) {
        return false;
      }

      seen.add(normalizedItem);
      return true;
    })
    .slice(0, limit);
}

function getFollowupSuggestions(question, response) {
  const directSuggestions = Array.isArray(response?.suggestions)
    ? response.suggestions
    : [];

  if (directSuggestions.length > 0) {
    return uniqueSuggestions(
      directSuggestions,
      question,
      getSuggestionLimit(response),
    );
  }

  const contextParts = [
    question,
    response?.reply,
    response?.data?.title,
    ...(response?.data?.columns || []),
    ...extractResponseContextValues(response),
  ];

  const contextText = contextParts.join(" ").toLowerCase();
  const mergedSuggestions = [...directSuggestions];

  FOLLOWUP_MAP.forEach((group) => {
    const isMatched = group.match.some((keyword) => contextText.includes(keyword));
    if (isMatched) {
      mergedSuggestions.push(...group.suggestions);
    }
  });

  return uniqueSuggestions(
    mergedSuggestions,
    question,
    getSuggestionLimit(response),
  );
}

function renderFollowups(suggestions) {
  if (!Array.isArray(suggestions) || suggestions.length === 0) return "";

  const buttons = suggestions
    .map(
      (item) => `
        <button
          type="button"
          class="followup-suggest-btn"
          data-suggestion="${escapeHtml(item)}"
        >
          ${escapeHtml(item)}
        </button>
      `,
    )
    .join("");

  return `
    <div class="followup-suggest-box">
      <div class="followup-suggest-title">Câu hỏi liên quan:</div>
      ${buttons}
    </div>
  `;
}

function renderResponseMeta(response) {
  const source = String(response?.source || "").trim();
  const references = Array.isArray(response?.references) ? response.references : [];

  const sourceLabel = source === "ollama" ? "Ollama RAG" : "Structured";
  const referenceItems = references
    .map((item) => {
      const title = String(item?.title || "").trim();
      const sourceFile = String(item?.source_file || "").trim();
      const note = String(item?.note || "").trim();
      const fileUrl = String(item?.file_url || "").trim();
      const downloadUrl = String(item?.download_url || fileUrl).trim();
      const label = title || sourceFile;

      if (!label) return "";

      return `
        <div class="response-reference-card">
          <div class="response-reference-main">
            <div class="response-reference-name">${escapeHtml(label)}</div>
            ${sourceFile && sourceFile !== label ? `<div class="response-reference-file">${escapeHtml(sourceFile)}</div>` : ""}
            ${note ? `<div class="response-reference-file">${escapeHtml(note)}</div>` : ""}
          </div>
          ${
            fileUrl
              ? `
                <div class="response-reference-actions">
                  <a href="${escapeHtml(fileUrl)}" target="_blank" rel="noopener noreferrer">Xem</a>
                  <a href="${escapeHtml(downloadUrl)}" download>Tải</a>
                </div>
              `
              : ""
          }
        </div>
      `;
    })
    .filter(Boolean)
    .join("");

  return `
    <div class="response-meta">
      ${source ? `<div class="response-source">Nguồn xử lý: <span class="response-source-badge">${escapeHtml(sourceLabel)}</span></div>` : ""}
      <div class="response-references">
        <div class="response-references-title">Tài liệu tham khảo</div>
        ${
          referenceItems
            ? referenceItems
            : `<div class="response-reference-empty">Chưa có tài liệu tham khảo.</div>`
        }
      </div>
    </div>
  `;
}

function renderTable(data) {
  if (!data || data.type !== "table") return "";

  const tableClassName =
    data.title === "THÔNG TƯ" ? "reply-table reply-table-documents" : "reply-table";

  const headers = (data.columns || [])
    .map((col) => `<th>${escapeHtml(col)}</th>`)
    .join("");

  const rows = (data.rows || [])
    .map((row) => {
      if (data.title === "LỊCH HỌC") {
        return `
          <tr>
            <td>${escapeHtml(row.lop)}</td>
            <td>${escapeHtml(row.mon)}</td>
            <td>${escapeHtml(row.giang_vien)}</td>
            <td>${escapeHtml(row.phong)}</td>
            <td>${escapeHtml(row.thoi_gian)}</td>
          </tr>
        `;
      }

      if (data.title === "LỊCH THI") {
        return `
          <tr>
            <td>${escapeHtml(row.mon)}</td>
            <td>${escapeHtml(row.ngay_thi)}</td>
            <td>${escapeHtml(row.phong)}</td>
          </tr>
        `;
      }

      if (data.title === "THÔNG TƯ") {
        const documentPayload = {
          type: "pdf_document",
          title: "THÔNG TƯ",
          document_type: row.document_type || "Thông tư",
          name: row.ten || "",
          so_hieu: row.so_hieu || "",
          ngay_ban_hanh: row.ngay_ban_hanh || "",
          ngay_hieu_luc: row.ngay_hieu_luc || "",
          trang_thai: row.trang_thai || "",
          tom_tat: row.tom_tat || "",
          noi_dung: row.noi_dung || "",
          co_quan_ban_hanh: row.co_quan_ban_hanh || "",
          file_url: row.file_url || "",
          file_name: row.file_name || "",
        };
        const encodedDocument = escapeHtml(JSON.stringify(documentPayload));
        const quickAction = row.file_url
          ? `
            <div class="reply-table-action-group">
              <button
                type="button"
                class="doc-card-btn is-secondary reply-table-action-btn"
                data-doc-action="sidebar"
                data-document="${encodedDocument}"
              >
                Xem tóm tắt
              </button>
              <button
                type="button"
                class="doc-card-btn is-primary reply-table-action-btn"
                data-doc-action="modal"
                data-document="${encodedDocument}"
              >
                Mở PDF
              </button>
            </div>
          `
          : `<span class="reply-table-action-empty">Chưa có file</span>`;

        return `
          <tr>
            <td>${escapeHtml(row.ten)}</td>
            <td>${escapeHtml(row.so_hieu)}</td>
            <td>${escapeHtml(row.ngay_ban_hanh)}</td>
            <td>
              <div
                class="reply-table-content-cell"
                title="${escapeHtml(row.noi_dung || "")}"
              >
                ${escapeHtml(row.noi_dung)}
              </div>
            </td>
            <td>${escapeHtml(row.trang_thai)}</td>
            <td>${quickAction}</td>
          </tr>
        `;
      }

      const cells = Object.values(row)
        .map((value) => `<td>${escapeHtml(value)}</td>`)
        .join("");

      return `<tr>${cells}</tr>`;
    })
    .join("");

  return `
    <div class="reply-table-wrap">
      ${data.title ? `<div class="reply-table-title">${escapeHtml(data.title)}</div>` : ""}
      <div class="reply-table-scroll">
        <table class="${tableClassName}">
          <thead>
            <tr>${headers}</tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function renderList(data) {
  if (!data || data.type !== "list") return "";

  const items = (data.items || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  return `
    <div class="reply-table-wrap">
      ${data.title ? `<div class="reply-table-title">${escapeHtml(data.title)}</div>` : ""}
      <ul class="reply-list">
        ${items}
      </ul>
    </div>
  `;
}

function renderTextBlock(data) {
  if (!data || data.type !== "text") return "";

  return `
    <div class="reply-table-wrap">
      ${data.title ? `<div class="reply-table-title">${escapeHtml(data.title)}</div>` : ""}
      <div class="reply-text-block">${nl2br(data.message || "")}</div>
    </div>
  `;
}

function getDocumentDownloadUrl(data) {
  return data?.download_url || data?.file_url || "#";
}

function getDocumentFileType(data) {
  const explicitType = String(data?.file_type || "").toLowerCase();
  if (explicitType) return explicitType;

  const fileName = String(data?.file_name || data?.file_url || "").toLowerCase();
  if (fileName.endsWith(".docx")) return "docx";
  if (fileName.endsWith(".doc")) return "doc";
  if (fileName.endsWith(".pdf")) return "pdf";

  return "file";
}

function getDocumentIconClass(data) {
  const fileType = getDocumentFileType(data);
  if (fileType === "pdf") return "fa-solid fa-file-pdf";
  if (fileType === "doc" || fileType === "docx") return "fa-solid fa-file-word";
  return "fa-solid fa-file-lines";
}

function getDocumentPreviewLabel(data) {
  return getDocumentFileType(data) === "pdf" ? "Xem file PDF" : "Xem nhanh";
}

function renderDocumentCard(data) {
  if (!data || !["pdf_document", "document_file"].includes(data.type)) return "";

  const summaryText = data.tom_tat || data.noi_dung || "Chưa có tóm tắt cho tài liệu này.";
  const encodedDocument = escapeHtml(JSON.stringify(data));
  const downloadUrl = getDocumentDownloadUrl(data);

  return `
    <div class="doc-card">
      <div class="doc-card-head">
        <span class="doc-card-type">
          <i class="${getDocumentIconClass(data)}"></i>
          ${escapeHtml(data.document_type || "Tài liệu")}
        </span>
        ${data.trang_thai ? `<span class="doc-card-status">${escapeHtml(data.trang_thai)}</span>` : ""}
      </div>

      <div class="doc-card-title">${escapeHtml(data.name || data.title || "Tài liệu pháp lý")}</div>

      <div class="doc-card-meta">
        <div class="doc-meta-item">
          <div class="doc-meta-label">Số hiệu</div>
          <div class="doc-meta-value">${escapeHtml(data.so_hieu || "Chưa cập nhật")}</div>
        </div>
        <div class="doc-meta-item">
          <div class="doc-meta-label">Ngày hiệu lực</div>
          <div class="doc-meta-value">${escapeHtml(data.ngay_hieu_luc || "Chưa cập nhật")}</div>
        </div>
      </div>

      <div class="doc-card-summary">${escapeHtml(summaryText)}</div>

      <div class="doc-card-actions">
        <button
          type="button"
          class="doc-card-btn is-secondary"
          data-doc-action="sidebar"
          data-document="${encodedDocument}"
        >
          Xem tóm tắt
        </button>
        <button
          type="button"
          class="doc-card-btn is-primary"
          data-doc-action="modal"
          data-document="${encodedDocument}"
        >
          ${escapeHtml(getDocumentPreviewLabel(data))}
        </button>
        <a
          class="doc-card-btn is-secondary"
          href="${escapeHtml(downloadUrl)}"
          download
        >
          Tải về
        </a>
      </div>
    </div>
  `;
}

function renderDocumentCollection(data) {
  if (!data || data.type !== "document_collection") return "";

  const documents = Array.isArray(data.documents) ? data.documents : [];
  const cards = documents
    .map((document) => renderDocumentCard(document))
    .join("");

  return `
    <div class="doc-collection">
      ${data.title ? `<div class="reply-table-title">${escapeHtml(data.title)}</div>` : ""}
      ${data.description ? `<div class="doc-collection-description">${escapeHtml(data.description)}</div>` : ""}
      <div class="doc-collection-grid">
        ${cards}
      </div>
    </div>
  `;
}

function renderBotContent(response) {
  if (["pdf_document", "document_file"].includes(response?.data?.type)) {
    return renderDocumentCard(response.data);
  }

  if (response?.data?.type === "document_collection") {
    return renderDocumentCollection(response.data);
  }

  if (response?.data?.type === "table") {
    return renderTable(response.data);
  }

  if (response?.data?.type === "list") {
    return renderList(response.data);
  }

  if (response?.data?.type === "text") {
    return renderTextBlock(response.data);
  }

  return nl2br(response?.reply || "Không có phản hồi.");
}

function parseDocumentPayload(rawValue) {
  if (!rawValue) return null;

  try {
    return JSON.parse(rawValue);
  } catch (error) {
    console.error("Không thể đọc dữ liệu tài liệu.", error);
    return null;
  }
}

function buildSidebarSection(title, value) {
  if (!value) return "";

  return `
    <section class="doc-sidebar-section">
      <div class="doc-sidebar-section-title">${escapeHtml(title)}</div>
      <div class="doc-sidebar-section-value">${nl2br(value)}</div>
    </section>
  `;
}

function updateOverlayState() {
  const hasOverlay = docSidebar?.classList.contains("is-open") || !pdfModal?.hidden;
  document.body.classList.toggle("doc-overlay-open", Boolean(hasOverlay));
}

function closeSidebar() {
  if (!docSidebar || !docSidebarBackdrop) return;

  docSidebar.classList.remove("is-open");
  docSidebar.setAttribute("aria-hidden", "true");
  docSidebarBackdrop.hidden = true;
  updateOverlayState();
}

function openSidebar(data) {
  if (!docSidebar || !docSidebarBackdrop || !docSidebarTitle || !docSidebarBody) return;

  activeDocumentData = data;
  docSidebarTitle.textContent = data.name || data.title || "Thông tin văn bản";
  docSidebarBody.innerHTML = [
    buildSidebarSection("Loại văn bản", data.document_type || ""),
    buildSidebarSection("Số hiệu", data.so_hieu || ""),
    buildSidebarSection("Ngày ban hành", data.ngay_ban_hanh || ""),
    buildSidebarSection("Ngày có hiệu lực", data.ngay_hieu_luc || ""),
    buildSidebarSection("Cơ quan ban hành", data.co_quan_ban_hanh || ""),
    buildSidebarSection("Nội dung tóm tắt", data.tom_tat || data.noi_dung || ""),
    buildSidebarSection("Tên file", data.file_name || ""),
  ]
    .filter(Boolean)
    .join("");

  docOpenModalBtn.disabled = !data.file_url;
  docOpenModalBtn.textContent = getDocumentPreviewLabel(data);
  if (data.file_url) {
    docOpenNewTab.href = data.file_url;
    docOpenNewTab.setAttribute("aria-disabled", "false");
  } else {
    docOpenNewTab.href = "#";
    docOpenNewTab.setAttribute("aria-disabled", "true");
  }

  if (docDownloadLink) {
    const downloadUrl = getDocumentDownloadUrl(data);
    docDownloadLink.href = downloadUrl;
    docDownloadLink.setAttribute("aria-disabled", downloadUrl === "#" ? "true" : "false");
  }

  docSidebarBackdrop.hidden = false;
  docSidebar.classList.add("is-open");
  docSidebar.setAttribute("aria-hidden", "false");
  updateOverlayState();
}

function closePdfModal() {
  if (!pdfModal || !pdfModalFrame) return;

  pdfModal.hidden = true;
  pdfModal.setAttribute("aria-hidden", "true");
  pdfModalFrame.removeAttribute("src");
  pdfModalFrame.hidden = false;
  if (pdfModalFallback) {
    pdfModalFallback.hidden = true;
    pdfModalFallback.innerHTML = "";
  }
  updateOverlayState();
}

function openPdfModal(data) {
  if (!pdfModal || !pdfModalFrame || !pdfModalTitle || !data?.file_url) return;

  activeDocumentData = data;
  const fileType = getDocumentFileType(data);
  const downloadUrl = getDocumentDownloadUrl(data);

  pdfModalTitle.textContent = data.name || data.title || "Nội dung tài liệu";
  pdfModal.hidden = false;
  pdfModal.setAttribute("aria-hidden", "false");

  if (pdfModalDownload) {
    pdfModalDownload.href = downloadUrl;
    pdfModalDownload.hidden = downloadUrl === "#";
  }

  if (fileType === "pdf") {
    pdfModalFrame.hidden = false;
    pdfModalFrame.src = data.file_url;
    if (pdfModalFallback) {
      pdfModalFallback.hidden = true;
      pdfModalFallback.innerHTML = "";
    }
  } else {
    pdfModalFrame.hidden = true;
    pdfModalFrame.removeAttribute("src");
    if (pdfModalFallback) {
      pdfModalFallback.hidden = false;
      pdfModalFallback.innerHTML = `
        <div class="document-preview-fallback">
          <div class="document-preview-icon">
            <i class="${getDocumentIconClass(data)}"></i>
          </div>
          <div class="document-preview-title">${escapeHtml(data.name || "Tài liệu Word")}</div>
          <div class="document-preview-text">
            Trình duyệt thường không xem trực tiếp file Word trong khung chat.
            Bạn có thể mở tab mới hoặc tải file về để chỉnh sửa.
          </div>
          ${
            data.tom_tat || data.noi_dung
              ? `<div class="document-preview-summary">${nl2br(data.tom_tat || data.noi_dung)}</div>`
              : ""
          }
          <div class="document-preview-actions">
            <a class="doc-primary-btn" href="${escapeHtml(data.file_url)}" target="_blank" rel="noopener noreferrer">
              Mở tab mới
            </a>
            <a class="doc-secondary-btn" href="${escapeHtml(downloadUrl)}" download>
              Tải về
            </a>
          </div>
        </div>
      `;
    }
  }

  updateOverlayState();
}

function addBotMessage(response, originalQuestion = "") {
  const contentHtml = renderBotContent(response);
  const metaHtml = renderResponseMeta(response);
  const followupHtml = renderFollowups(
    getFollowupSuggestions(originalQuestion, response),
  );

  const messageRow = appendRow(`
    <div class="message-row">
      ${createBotAvatarHtml()}
      <div class="message">
        <span class="bot-answer-anchor" aria-hidden="true"></span>
        ${contentHtml}
        ${metaHtml}
        ${followupHtml}
        <hr />
      </div>
    </div>
  `);

  const answerStart = messageRow?.querySelector(".bot-answer-anchor") || messageRow;
  scrollToElementAfterRender(answerStart);
}

async function fetchChatResponse(message) {
  const response = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    if (data) return data;
    throw new Error(`HTTP ${response.status}`);
  }

  return data;
}

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  addUserMessage(message);
  userInput.value = "";
  showTyping();
  setSendingState(true);
  const loadingStartedAt = Date.now();

  try {
    await waitForNextPaint();
    const response = await fetchChatResponse(message);
    const elapsed = Date.now() - loadingStartedAt;

    if (elapsed < MIN_LOADING_TIME) {
      await delay(MIN_LOADING_TIME - elapsed);
    }

    removeTyping();
    addBotMessage(response, message);
  } catch (error) {
    const elapsed = Date.now() - loadingStartedAt;

    if (elapsed < MIN_LOADING_TIME) {
      await delay(MIN_LOADING_TIME - elapsed);
    }

    removeTyping();
    addBotMessage({ reply: "❌ Có lỗi xảy ra khi gửi câu hỏi." }, message);
    console.error(error);
  } finally {
    setSendingState(false);
    userInput.focus();
  }
}

function sendQuick(text) {
  userInput.value = text;
  sendMessage();
}

function handleInputKeydown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

function handleSuggestionClick(event) {
  const button = event.target.closest("[data-suggestion]");
  if (!button) return;

  sendQuick(button.dataset.suggestion || "");
}

function handleDocumentAction(event) {
  const button = event.target.closest("[data-doc-action]");
  if (!button) return;

  const data = parseDocumentPayload(button.dataset.document || "");
  if (!data) return;

  if (button.dataset.docAction === "sidebar") {
    openSidebar(data);
    return;
  }

  if (button.dataset.docAction === "modal") {
    openPdfModal(data);
  }
}

function handleEscape(event) {
  if (event.key !== "Escape") return;

  if (pdfModal && !pdfModal.hidden) {
    closePdfModal();
    return;
  }

  if (docSidebar?.classList.contains("is-open")) {
    closeSidebar();
  }
}

userInput.addEventListener("keydown", handleInputKeydown);
sendBtn.addEventListener("click", sendMessage);
chatBox.addEventListener("scroll", updateHeaderScrollState, { passive: true });
chatBox.addEventListener("click", handleSuggestionClick);
chatBox.addEventListener("click", handleDocumentAction);
docSidebarCloseBtn?.addEventListener("click", closeSidebar);
docSidebarBackdrop?.addEventListener("click", closeSidebar);
docOpenModalBtn?.addEventListener("click", () => {
  if (activeDocumentData) {
    openPdfModal(activeDocumentData);
  }
});
pdfModalCloseBtn?.addEventListener("click", closePdfModal);
pdfModalBackdrop?.addEventListener("click", closePdfModal);
document.addEventListener("keydown", handleEscape);
window.addEventListener("load", updateHeaderScrollState);

window.sendMessage = sendMessage;
window.sendQuick = sendQuick;
