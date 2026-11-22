/* ========================================================
   AWS Technical Support RAG Assistant - Client Application
   ======================================================== */

// State
let currentUser = null;
let currentMessages = [];

// DOM Elements
const authSection = document.getElementById("authSection");
const chatSection = document.getElementById("chatSection");
const userProfileArea = document.getElementById("userProfileArea");
const userNameDisplay = document.getElementById("userNameDisplay");
const userRoleBadge = document.getElementById("userRoleBadge");
const logoutBtn = document.getElementById("logoutBtn");
const dbStatusBadge = document.getElementById("dbStatusBadge");

// Tabs
const tabSignInBtn = document.getElementById("tabSignInBtn");
const tabRegisterBtn = document.getElementById("tabRegisterBtn");
const tabDemoBtn = document.getElementById("tabDemoBtn");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const demoTab = document.getElementById("demoTab");

// Inputs
const loginIdentifier = document.getElementById("loginIdentifier");
const loginPassword = document.getElementById("loginPassword");
const loginError = document.getElementById("loginError");

const regUsername = document.getElementById("regUsername");
const regEmail = document.getElementById("regEmail");
const regPassword = document.getElementById("regPassword");
const regRole = document.getElementById("regRole");
const registerError = document.getElementById("registerError");
const registerSuccess = document.getElementById("registerSuccess");

const quickDemoBtn = document.getElementById("quickDemoBtn");
const quickAdminBtn = document.getElementById("quickAdminBtn");

// Chat
const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const topKRange = document.getElementById("topKRange");
const topKValue = document.getElementById("topKValue");
const thresholdRange = document.getElementById("thresholdRange");
const thresholdValue = document.getElementById("thresholdValue");
const exportHistoryBtn = document.getElementById("exportHistoryBtn");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");

// Stats
const totalUsersCount = document.getElementById("totalUsersCount");
const totalQueriesCount = document.getElementById("totalQueriesCount");

// Initialize on Load
document.addEventListener("DOMContentLoaded", async () => {
  setupTabs();
  setupSliders();
  setupQuickChips();
  await checkSystemStatus();
  
  // Check stored session
  const savedUser = localStorage.getItem("aws_support_user");
  if (savedUser) {
    try {
      currentUser = JSON.parse(savedUser);
      showChatView();
      await loadChatHistory();
    } catch (e) {
      localStorage.removeItem("aws_support_user");
    }
  }
});

// Setup Tabs
function setupTabs() {
  tabSignInBtn.addEventListener("click", () => switchTab("signin"));
  tabRegisterBtn.addEventListener("click", () => switchTab("register"));
  tabDemoBtn.addEventListener("click", () => switchTab("demo"));

  quickDemoBtn.addEventListener("click", () => executeLogin("demouser", "DemoUser123!"));
  quickAdminBtn.addEventListener("click", () => executeLogin("admin", "AdminRoot123!"));

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginError.classList.add("hidden");
    await executeLogin(loginIdentifier.value, loginPassword.value);
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    registerError.classList.add("hidden");
    registerSuccess.classList.add("hidden");

    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: regUsername.value,
          email: regEmail.value,
          password: regPassword.value,
          role: regRole.value
        })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        registerSuccess.textContent = data.message;
        registerSuccess.classList.remove("hidden");
        setTimeout(() => switchTab("signin"), 1200);
      } else {
        registerError.textContent = data.message || "Registration failed";
        registerError.classList.remove("hidden");
      }
    } catch (err) {
      registerError.textContent = "Network error: " + err.message;
      registerError.classList.remove("hidden");
    }
  });

  logoutBtn.addEventListener("click", () => {
    currentUser = null;
    localStorage.removeItem("aws_support_user");
    authSection.classList.remove("hidden");
    chatSection.classList.add("hidden");
    userProfileArea.classList.add("hidden");
  });
}

function switchTab(tab) {
  tabSignInBtn.classList.toggle("active", tab === "signin");
  tabRegisterBtn.classList.toggle("active", tab === "register");
  tabDemoBtn.classList.toggle("active", tab === "demo");

  loginForm.classList.toggle("hidden", tab !== "signin");
  registerForm.classList.toggle("hidden", tab !== "register");
  demoTab.classList.toggle("hidden", tab !== "demo");
}

// Authentication Execution
async function executeLogin(identifier, password) {
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password })
    });
    const data = await res.json();

    if (res.ok && data.success) {
      currentUser = data.user;
      localStorage.setItem("aws_support_user", JSON.stringify(currentUser));
      showChatView();
      await loadChatHistory();
    } else {
      loginError.textContent = data.message || "Invalid credentials";
      loginError.classList.remove("hidden");
    }
  } catch (err) {
    loginError.textContent = "Connection error: " + err.message;
    loginError.classList.remove("hidden");
  }
}

function showChatView() {
  authSection.classList.add("hidden");
  chatSection.classList.remove("hidden");
  userProfileArea.classList.remove("hidden");

  userNameDisplay.textContent = currentUser.username;
  userRoleBadge.textContent = (currentUser.role || "USER").toUpperCase();
}

// System Status Check
async function checkSystemStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();

    if (data.database) {
      totalUsersCount.textContent = data.database.total_users || 0;
      totalQueriesCount.textContent = data.database.total_queries || 0;

      dbStatusBadge.innerHTML = `<span class="status-dot"></span> System Online`;
      dbStatusBadge.className = "status-badge online";
    }
  } catch (e) {
    dbStatusBadge.innerHTML = `<span class="status-dot" style="background:#ef4444"></span> Offline`;
  }
}

// Sliders & Chips
function setupSliders() {
  topKRange.addEventListener("input", (e) => topKValue.textContent = e.target.value);
  thresholdRange.addEventListener("input", (e) => thresholdValue.textContent = e.target.value);

  exportHistoryBtn.addEventListener("click", () => {
    if (!currentMessages.length) return alert("No messages to export.");
    const blob = new Blob([JSON.stringify(currentMessages, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `aws_support_history_${currentUser.username}.json`;
    a.click();
  });

  clearHistoryBtn.addEventListener("click", async () => {
    if (!confirm("Clear your conversation history in MySQL?")) return;
    await fetch("/api/chat/history", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: currentUser.id })
    });
    chatMessages.innerHTML = "";
    currentMessages = [];
  });
}

function setupQuickChips() {
  document.querySelectorAll(".chip-btn").forEach((chip) => {
    chip.addEventListener("click", () => {
      chatInput.value = chip.dataset.query;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });
}

// Chat Flow
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = chatInput.value.trim();
  if (!query) return;

  chatInput.value = "";
  appendMessage("user", query);

  // Loading indicator
  const loadingDiv = document.createElement("div");
  loadingDiv.className = "message assistant";
  loadingDiv.id = "tempLoading";
  loadingDiv.innerHTML = `<div class="message-bubble"><p>⚡ <em>Searching knowledge base & generating direct solution...</em></p></div>`;
  chatMessages.appendChild(loadingDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        user_id: currentUser.id,
        top_k: topKRange.value,
        similarity_threshold: thresholdRange.value
      })
    });
    const data = await res.json();
    loadingDiv.remove();

    appendAssistantMessage(data);
    await checkSystemStatus(); // refresh count
  } catch (err) {
    loadingDiv.remove();
    appendMessage("assistant", "⚠️ Error communicating with server: " + err.message);
  }
});

function appendMessage(role, content) {
  currentMessages.push({ role, content });
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = `<div class="message-bubble">${marked.parse(content)}</div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendAssistantMessage(data) {
  const clf = data.classification || {};
  const meta = data.metadata || {};

  const intent = clf.intent || "GENERAL";
  const service = clf.service || "AWS";
  const urgency = clf.urgency || "LOW";
  const latency = clf.latency_ms || meta.classification_latency_ms || 1.0;

  currentMessages.push({
    role: "assistant",
    content: data.answer,
    intent, service, urgency
  });

  const div = document.createElement("div");
  div.className = "message assistant";

  let sourcesHtml = "";
  if (data.sources && data.sources.length) {
    sourcesHtml = `
      <details class="sources-box">
        <summary>📚 View Supporting Documentation (${data.sources.length} cited)</summary>
        <ul>
          ${data.sources.map((s, idx) => `
            <li>
              <strong>${idx+1}. [${s.service}] ${s.title}</strong> (Relevance: ${(s.relevance_score || 0).toFixed(2)})<br>
              <small>File: <code>${s.source}</code></small>
            </li>
          `).join("")}
        </ul>
      </details>
    `;
  }

  div.innerHTML = `
    <div class="message-bubble">
      <div class="meta-badges">
        <span class="pill-intent">🎯 Intent: ${intent}</span>
        <span class="pill-service">☁️ Service: ${service}</span>
        <span class="pill-urgency">⚠️ Urgency: ${urgency}</span>
        <span class="pill-latency">⚡ Model: ${Number(latency).toFixed(1)}ms</span>
      </div>
      <div>${marked.parse(data.answer)}</div>
      ${sourcesHtml}
    </div>
  `;

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Load Chat History from MySQL
async function loadChatHistory() {
  if (!currentUser) return;
  try {
    const res = await fetch(`/api/chat/history?user_id=${currentUser.id}`);
    const data = await res.json();
    if (data.history && data.history.length) {
      chatMessages.innerHTML = "";
      data.history.forEach((item) => {
        appendMessage("user", item.query);
        appendAssistantMessage({
          answer: item.response,
          sources: item.sources || [],
          classification: {
            intent: item.intent,
            service: item.service,
            urgency: item.urgency,
            latency_ms: item.latency_ms
          }
        });
      });
    }
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}
