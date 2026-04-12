const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// =========================
// ENTER TO SEND
// =========================
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

// =========================
// CONFIG GỢI Ý (DỄ MỞ RỘNG)
// =========================
const FOLLOWUP_CONFIG = {
  lich_hoc: {
    keywords: [
      "lịch học",
      "học hôm nay",
      "môn học",
      "dths3",
      "thahs",
      "qlhc",
      "kths",
    ],
    questions: [
      "Tuần này tôi học ở phòng nào?",
      "Lịch thi học kì này?",
      "Lịch học của lớp DTHS3 là gì?",
      "Ngày mai tôi có học không?",
    ],
  },

  tuyen_sinh: {
    keywords: ["tuyển sinh", "xét tuyển", "đăng ký", "nhập học"],
    questions: [
      "Điều kiện xét tuyển là gì?",
      "Phương thức tuyển sinh gồm những gì?",
      "Hồ sơ đăng ký gồm những gì?",
      "Thời gian nộp hồ sơ khi nào?",
    ],
  },

  thu_vien: {
    keywords: ["thư viện", "mượn sách", "trả sách", "sách", "giáo trình"],
    questions: [
      "Làm sao để mượn sách?",
      "Mượn sách tối đa bao lâu?",
      "Thư viện có những sách gì?",
      "Trả sách trễ có bị phạt không?",
    ],
  },
};

// =========================
// NHẬN DIỆN CHỦ ĐỀ
// =========================
function detectTopic(message) {
  const text = message.toLowerCase();

  for (const topic in FOLLOWUP_CONFIG) {
    const { keywords } = FOLLOWUP_CONFIG[topic];

    for (const keyword of keywords) {
      if (text.includes(keyword)) {
        return topic;
      }
    }
  }

  return "";
}

// =========================
// ADD MESSAGE
// =========================
function addMsg(text, type) {
  // BOT
  if (type === "bot") {
    const row = document.createElement("div");
    row.className = "message-row";

    row.innerHTML = `
      <div class="avatar">
        <img src="/static/image/chatbotai.png" class="bot-avatar-img" />
      </div>
      <div class="message">
        ${text}
        <hr />
      </div>
    `;

    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
    return row;
  }

  // USER + TYPING
  const div = document.createElement("div");
  div.className = `msg ${type}`;
  div.textContent = text;

  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return div;
}

// =========================
// RENDER GỢI Ý
// =========================
function clearFollowup() {
  const old = document.querySelector(".followup-dynamic");
  if (old) old.remove();
}

function renderFollowupSuggestions(topic) {
  clearFollowup();

  if (!topic || !FOLLOWUP_CONFIG[topic]) return;

  const { questions } = FOLLOWUP_CONFIG[topic];

  const box = document.createElement("div");
  box.className = "suggest-box followup-dynamic";

  const title = document.createElement("div");
  title.className = "suggest-title";
  title.textContent = "💡 Câu hỏi liên quan";

  box.appendChild(title);

  questions.forEach((q) => {
    const btn = document.createElement("button");
    btn.className = "suggest-btn";
    btn.textContent = `💡 ${q}`;

    btn.onclick = () => {
      userInput.value = q;
      sendMessage();
    };

    box.appendChild(btn);
  });

  chatBox.appendChild(box);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// =========================
// MAIN FUNCTION
// =========================
async function sendMessage() {
  const msg = userInput.value.trim();
  if (!msg) return;

  userInput.value = "";
  sendBtn.disabled = true;

  addMsg(msg, "user");
  const typing = addMsg("Đang tìm kiếm...", "typing");

  try {
    const resp = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    });

    const data = await resp.json();

    typing.remove();
    addMsg(data.reply, "bot");

    // 👉 CHỈ 1 DÒNG THAY CHO 5 IF
    const topic = detectTopic(msg);
    renderFollowupSuggestions(topic);
  } catch (e) {
    typing.remove();
    addMsg("❌ Không thể kết nối server.", "bot");
    clearFollowup();
  }

  sendBtn.disabled = false;
  userInput.focus();
}

// =========================
// QUICK BUTTON
// =========================
function sendQuick(text) {
  userInput.value = text;
  sendMessage();
}
