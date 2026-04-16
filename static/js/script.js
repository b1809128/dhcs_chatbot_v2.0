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
const pdfModal = document.getElementById("pdf-modal");
const pdfModalBackdrop = document.getElementById("pdf-modal-backdrop");
const pdfModalCloseBtn = document.getElementById("pdf-modal-close");
const pdfModalTitle = document.getElementById("pdf-modal-title");
const pdfModalFrame = document.getElementById("pdf-modal-frame");

const BOT_AVATAR_SRC = "/static/image/chatbotai.png";
let activeDocumentData = null;
const ADMISSION_TITLES = new Set([
  "TUYỂN SINH",
  "BÀI THI ĐÁNH GIÁ",
  "HỒ SƠ TUYỂN SINH",
  "NGÀNH TUYỂN SINH",
  "THÔNG TIN TRƯỜNG",
  "LIÊN HỆ TUYỂN SINH",
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

function scrollToBottom() {
  chatBox.scrollTop = chatBox.scrollHeight;
}

function scrollToElement(element) {
  if (!element) return;

  const chatBoxRect = chatBox.getBoundingClientRect();
  const elementRect = element.getBoundingClientRect();
  const targetTop =
    chatBox.scrollTop +
    (elementRect.top - chatBoxRect.top) -
    16;

  chatBox.scrollTo({
    top: Math.max(targetTop, 0),
    behavior: "smooth",
  });
}

function scrollToElementAfterRender(element) {
  if (!element) return;

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      scrollToElement(element);
    });
  });
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
      <div class="message" style="color:#666;font-style:italic;">
        Đang tìm kiếm...
      </div>
    </div>
  `;
}

function showTyping() {
  removeTyping();
  appendRow(buildTypingHtml());
  updateHeaderScrollState();
  scrollToBottom();
}

function removeTyping() {
  const typingRow = document.getElementById("typing-row");
  if (typingRow) typingRow.remove();
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
  return ADMISSION_TITLES.has(response?.data?.title) ? 8 : 4;
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

function renderTable(data) {
  if (!data || data.type !== "table") return "";

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
        <table class="reply-table">
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

function renderDocumentCard(data) {
  if (!data || data.type !== "pdf_document") return "";

  const summaryText = data.tom_tat || data.noi_dung || "Chưa có tóm tắt cho tài liệu này.";
  const encodedDocument = escapeHtml(JSON.stringify(data));

  return `
    <div class="doc-card">
      <div class="doc-card-head">
        <span class="doc-card-type">
          <i class="fa-solid fa-file-pdf"></i>
          ${escapeHtml(data.document_type || "Tài liệu PDF")}
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
          Xem file PDF
        </button>
      </div>
    </div>
  `;
}

function renderBotContent(response) {
  if (response?.data?.type === "pdf_document") {
    return renderDocumentCard(response.data);
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
  if (data.file_url) {
    docOpenNewTab.href = data.file_url;
    docOpenNewTab.setAttribute("aria-disabled", "false");
  } else {
    docOpenNewTab.href = "#";
    docOpenNewTab.setAttribute("aria-disabled", "true");
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
  updateOverlayState();
}

function openPdfModal(data) {
  if (!pdfModal || !pdfModalFrame || !pdfModalTitle || !data?.file_url) return;

  activeDocumentData = data;
  pdfModalTitle.textContent = data.name || data.title || "Nội dung PDF";
  pdfModal.hidden = false;
  pdfModal.setAttribute("aria-hidden", "false");
  pdfModalFrame.src = data.file_url;
  updateOverlayState();
}

function addBotMessage(response, originalQuestion = "") {
  const contentHtml = renderBotContent(response);
  const followupHtml = renderFollowups(
    getFollowupSuggestions(originalQuestion, response),
  );

  const messageRow = appendRow(`
    <div class="message-row">
      ${createBotAvatarHtml()}
      <div class="message">
        ${contentHtml}
        ${followupHtml}
        <hr />
      </div>
    </div>
  `);

  const newTableTitle = messageRow?.querySelector(".reply-table-title");
  if (newTableTitle) {
    scrollToElementAfterRender(newTableTitle);
    return;
  }

  const newTable = messageRow?.querySelector(".reply-table-wrap");
  if (newTable) {
    scrollToElementAfterRender(newTable);
    return;
  }

  requestAnimationFrame(() => {
    scrollToBottom();
  });
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

  try {
    const response = await fetchChatResponse(message);
    removeTyping();
    addBotMessage(response, message);
  } catch (error) {
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
