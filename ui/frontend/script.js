// Configuration
const API_URL = "http://localhost:8000";

// State
let conversationHistory = [];
let isLoading = false;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initializeApp();
  loadTheme();
});

function initializeApp() {
  // Set welcome message time
  document.getElementById("welcomeTime").textContent = getCurrentTime();

  // Add event listeners
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");

  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  userInput.addEventListener("input", autoResize);

  sendBtn.addEventListener("click", sendMessage);
}

function autoResize() {
  const textarea = document.getElementById("userInput");
  textarea.style.height = "auto";
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
}

function getCurrentTime() {
  return new Date().toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function setQuery(query) {
  const userInput = document.getElementById("userInput");
  userInput.value = query;
  userInput.focus();
  autoResize();
}

async function sendMessage() {
  const userInput = document.getElementById("userInput");
  const query = userInput.value.trim();

  if (!query || isLoading) return;

  // Hide example questions
  const exampleQuestions = document.getElementById("exampleQuestions");
  if (exampleQuestions) {
    exampleQuestions.classList.add("hidden");
  }

  // Clear input
  userInput.value = "";
  autoResize();

  // Add user message
  addUserMessage(query);

  // Show loading
  isLoading = true;
  updateSendButton();
  showLoading();

  try {
    // Call API
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: query,
        conversation_history: conversationHistory,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to get response from server");
    }

    const data = await response.json();

    // Remove loading
    removeLoading();

    // Add assistant message
    addAssistantMessage(data.answer, data.sources, data.rephrased_query);
  } catch (error) {
    console.error("Error:", error);
    removeLoading();
    addErrorMessage("Sorry, I encountered an error. Please try again.");
  } finally {
    isLoading = false;
    updateSendButton();
  }
}

function addUserMessage(content) {
  const messagesArea = document.getElementById("messagesArea");
  const timestamp = new Date();

  const messageDiv = document.createElement("div");
  messageDiv.className = "message user-message";
  messageDiv.innerHTML = `
        <div class="message-header">
            <div class="avatar user-avatar">Y</div>
            <span class="message-sender">You</span>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
        <div class="message-content">${marked.parse(content)}</div>

    `;

  messagesArea.appendChild(messageDiv);
  scrollToBottom();

  // Add to history
  conversationHistory.push({
    type: "user",
    content: content,
    timestamp: timestamp.toISOString(),
  });

  // Keep only last 10 messages (5 exchanges)
  if (conversationHistory.length > 10) {
    conversationHistory = conversationHistory.slice(-10);
  }
}

function addAssistantMessage(content, sources = [], rephrasedQuery = null) {
  const messagesArea = document.getElementById("messagesArea");
  const timestamp = new Date();

  const messageDiv = document.createElement("div");
  messageDiv.className = "message assistant-message";

  let sourcesHtml = "";
  if (sources && sources.length > 0) {
    const sourcesId = `sources-${Date.now()}`;
    sourcesHtml = `
            <div class="sources-container">
                <button class="sources-toggle" onclick="toggleSources('${sourcesId}')">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M14 2v6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span>${sources.length} source${
      sources.length > 1 ? "s" : ""
    } referenced</span>
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
                <div class="sources-list" id="${sourcesId}" style="display: none;">
                    ${sources
                      .map(
                        (source) => `
                        <div class="source-item">
                            <div class="source-header">
                                <div class="source-title">${escapeHtml(
                                  source.title
                                )}</div>
                                <div class="source-relevance">${Math.round(
                                  source.relevance * 100
                                )}% match</div>
                            </div>
                            <div class="source-meta">
                                Section ${escapeHtml(
                                  source.section_id
                                )} • Chunk ${escapeHtml(source.chunk_id)}
                            </div>
                        </div>
                    `
                      )
                      .join("")}
                </div>
            </div>
        `;
  }

  messageDiv.innerHTML = `
        <div class="message-header">
            <div class="avatar assistant-avatar">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="currentColor"/>
                </svg>
            </div>
            <span class="message-sender">PolicyPal</span>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
        <div class="message-content">${marked.parse(
          formatMarkdown(content)
        )}</div>
        ${sourcesHtml}
    `;

  messagesArea.appendChild(messageDiv);
  scrollToBottom();

  // Add to history
  conversationHistory.push({
    type: "assistant",
    content: content,
    sources: sources,
    timestamp: timestamp.toISOString(),
  });

  // Keep only last 10 messages
  if (conversationHistory.length > 10) {
    conversationHistory = conversationHistory.slice(-10);
  }
}

function addErrorMessage(content) {
  const messagesArea = document.getElementById("messagesArea");

  const messageDiv = document.createElement("div");
  messageDiv.className = "message assistant-message";
  messageDiv.innerHTML = `
        <div class="message-header">
            <div class="avatar assistant-avatar">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="currentColor"/>
                </svg>
            </div>
            <span class="message-sender">PolicyPal</span>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;

  messagesArea.appendChild(messageDiv);
  scrollToBottom();
}

function showLoading() {
  const messagesArea = document.getElementById("messagesArea");

  const loadingDiv = document.createElement("div");
  loadingDiv.id = "loadingMessage";
  loadingDiv.className = "message assistant-message";
  loadingDiv.innerHTML = `
        <div class="loading-message">
            <div class="loading-spinner"></div>
            <span class="loading-text">PolicyPal is thinking...</span>
        </div>
    `;

  messagesArea.appendChild(loadingDiv);
  scrollToBottom();
}

function removeLoading() {
  const loadingMessage = document.getElementById("loadingMessage");
  if (loadingMessage) {
    loadingMessage.remove();
  }
}

function updateSendButton() {
  const sendBtn = document.getElementById("sendBtn");
  sendBtn.disabled = isLoading;
}

function toggleSources(sourcesId) {
  const sourcesList = document.getElementById(sourcesId);
  const toggleBtn = sourcesList.previousElementSibling;

  if (sourcesList.style.display === "none") {
    sourcesList.style.display = "flex";
    toggleBtn.classList.add("expanded");
  } else {
    sourcesList.style.display = "none";
    toggleBtn.classList.remove("expanded");
  }
}

function scrollToBottom() {
  const messagesArea = document.getElementById("messagesArea");
  setTimeout(() => {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }, 100);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Check API health on load
async function checkApiHealth() {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) {
      console.warn("API health check failed");
    }
  } catch (error) {
    console.error("Cannot connect to API:", error);
  }
}

function formatMarkdown(text) {
  // 1. Normalize bold headings spacing
  text = text.replace(/\s*\*\*(.*?)\*\*\s*/g, "\n\n**$1**\n");

  // 2. Remove standalone bullet symbols (THIS FIXES YOUR ISSUE)
  text = text.replace(/^\s*\*\s*$/gm, "");

  // 3. Convert inline bullets only when real text follows
  text = text.replace(/\s\*\s+(?!\*\*)([^\n]+)/g, "\n- $1");

  // 4. Fix numbered list formatting
  text = text.replace(/(\d+)\.\s+/g, "\n$1. ");

  // 5. Remove orphan markdown bullets
  text = text.replace(/^\s*-\s*$/gm, "");

  // 6. Clean excessive spacing
  text = text.replace(/\n{3,}/g, "\n\n");

  return text.trim();
}

const themeToggle = document.getElementById("themeToggle");

// Load saved theme
function loadTheme() {
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
    themeToggle.textContent = "☀️";
  }
}

// Toggle theme
themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");

  const isDark = document.body.classList.contains("dark-mode");

  localStorage.setItem("theme", isDark ? "dark" : "light");

  themeToggle.textContent = isDark ? "☀️" : "🌙";
});

checkApiHealth();
