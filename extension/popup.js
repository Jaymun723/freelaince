document.addEventListener('DOMContentLoaded', function() {
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendButton = document.getElementById('sendButton');
  const connectionStatus = document.getElementById('connectionStatus');
  const settingsBtn = document.getElementById('settingsBtn');
  const offersBtn = document.getElementById('offersBtn');

  let isConnected = false;
  let messageHistory = [];

  // Initialize the chat
  init();

  function init() {
    loadSettings();
    setupEventListeners();
    checkConnectionStatus();
    loadConversationHistory();
  }

  function loadSettings() {
    chrome.storage.sync.get(['apiUrl'], function(result) {
      if (!result.apiUrl) {
        // Set default URL if not configured
        chrome.storage.sync.set({ apiUrl: 'ws://localhost:8080' });
      }
    });
  }

  function setupEventListeners() {
    // Send message on button click
    sendButton.addEventListener('click', sendMessage);

    // Send message on Enter (but not Shift+Enter)
    chatInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 80) + 'px';
    });

    // Settings button
    settingsBtn.addEventListener('click', showSettings);

    // Offers button
    offersBtn.addEventListener('click', openOffersPage);

    // Listen for messages from background script
    chrome.runtime.onMessage.addListener(handleBackgroundMessage);
  }

  function checkConnectionStatus() {
    chrome.runtime.sendMessage({ type: 'GET_CONNECTION_STATUS' }, function(response) {
      updateConnectionStatus(response && response.connected);
    });
  }

  function loadConversationHistory() {
    chrome.runtime.sendMessage({ type: 'REQUEST_HISTORY' });
  }

  function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !isConnected) return;

    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Send to background script
    chrome.runtime.sendMessage({
      type: 'SEND_MESSAGE',
      data: message
    });

    // Disable send button temporarily
    sendButton.disabled = true;
    setTimeout(() => {
      sendButton.disabled = false;
    }, 1000);
  }

  function addMessage(content, type, timestamp = null) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    
    const messageContent = document.createElement('div');
    messageContent.textContent = content;
    messageElement.appendChild(messageContent);

    if (timestamp || type === 'user') {
      const timeElement = document.createElement('div');
      timeElement.className = 'message-time';
      timeElement.textContent = formatTime(timestamp || new Date());
      messageElement.appendChild(timeElement);
    }

    // Remove welcome message if it exists
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
      welcomeMessage.remove();
    }

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Store message in history
    messageHistory.push({
      content,
      type,
      timestamp: timestamp || new Date().toISOString()
    });
  }

  function handleBackgroundMessage(message) {
    switch (message.type) {
      case 'NEW_MESSAGE':
        addMessage(message.data, 'bot');
        break;
      case 'SYSTEM_MESSAGE':
        addMessage(message.data, 'system');
        break;
      case 'CONNECTION_STATUS':
        updateConnectionStatus(message.data.connected);
        break;
      case 'CONVERSATION_HISTORY':
        loadHistoryMessages(message.data);
        break;
      case 'ERROR':
        addMessage(message.data.message, 'system');
        break;
    }
  }

  function loadHistoryMessages(history) {
    if (!history || history.length === 0) return;

    // Clear existing messages except welcome
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());

    // Add historical messages
    history.forEach(msg => {
      if (msg.sender === 'user') {
        addMessage(msg.message, 'user', new Date(msg.timestamp));
      } else if (msg.sender === 'bot') {
        addMessage(msg.message, 'bot', new Date(msg.timestamp));
      }
    });
  }

  function updateConnectionStatus(connected) {
    isConnected = connected;
    if (connected) {
      connectionStatus.classList.add('connected');
      sendButton.disabled = false;
      chatInput.disabled = false;
      chatInput.placeholder = "Ask me anything about freelancing...";
    } else {
      connectionStatus.classList.remove('connected');
      sendButton.disabled = true;
      chatInput.disabled = true;
      chatInput.placeholder = "Connecting to server...";
    }
  }

  function formatTime(date) {
    return new Date(date).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  function showSettings() {
    // Create a simple settings modal
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    `;

    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
      background: #2d2d2d;
      padding: 24px;
      border-radius: 12px;
      width: 300px;
      color: white;
    `;

    modalContent.innerHTML = `
      <h3 style="margin: 0 0 16px 0; color: white;">Settings</h3>
      <label style="display: block; margin-bottom: 8px; font-size: 14px; color: #ccc;">WebSocket URL:</label>
      <input type="url" id="modalApiUrl" style="width: 100%; padding: 8px; border: 1px solid #404040; border-radius: 6px; background: #1a1a1a; color: white; box-sizing: border-box;" placeholder="ws://localhost:8080">
      <div style="display: flex; gap: 8px; margin-top: 16px;">
        <button id="modalCancel" style="flex: 1; padding: 8px; background: #666; border: none; border-radius: 6px; color: white; cursor: pointer;">Cancel</button>
        <button id="modalSave" style="flex: 1; padding: 8px; background: #4299e1; border: none; border-radius: 6px; color: white; cursor: pointer;">Save</button>
      </div>
    `;

    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    // Load current URL
    chrome.storage.sync.get(['apiUrl'], function(result) {
      document.getElementById('modalApiUrl').value = result.apiUrl || 'ws://localhost:8080';
    });

    // Handle modal actions
    document.getElementById('modalCancel').onclick = () => {
      document.body.removeChild(modal);
    };

    document.getElementById('modalSave').onclick = () => {
      const newUrl = document.getElementById('modalApiUrl').value.trim();
      if (newUrl) {
        chrome.storage.sync.set({ apiUrl: newUrl }, function() {
          chrome.runtime.sendMessage({ 
            type: 'UPDATE_API_URL', 
            data: newUrl 
          });
          addMessage('Settings saved! Reconnecting...', 'system');
        });
      }
      document.body.removeChild(modal);
    };

    // Close on background click
    modal.onclick = (e) => {
      if (e.target === modal) {
        document.body.removeChild(modal);
      }
    };
  }

  function openOffersPage() {
    chrome.tabs.create({
      url: chrome.runtime.getURL('offers.html')
    });
  }

  // Request connection status updates periodically
  setInterval(checkConnectionStatus, 5000);
});