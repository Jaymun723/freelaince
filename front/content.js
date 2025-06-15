class FreelainceOverlay {
  constructor() {
    this.isVisible = false;
    this.isMinimized = false;
    this.createChatBox();
    this.setupEventListeners();
  }

  createChatBox() {
    this.chatContainer = document.createElement('div');
    this.chatContainer.id = 'chat-overlay-container';
    this.chatContainer.innerHTML = `
      <div id="chat-overlay-header">
        <span id="chat-overlay-title">Freelaince</span>
        <div id="chat-overlay-controls">
          <button id="chat-overlay-minimize">−</button>
          <button id="chat-overlay-close">×</button>
        </div>
      </div>
      <div id="chat-overlay-messages"></div>
      <div id="chat-overlay-input-container">
        <input type="text" id="chat-overlay-input" placeholder="Type your message..." />
        <button id="chat-overlay-send">Send</button>
      </div>
    `;

    this.toggleButton = document.createElement('div');
    this.toggleButton.id = 'chat-overlay-toggle';
    this.toggleButton.innerHTML = '💬';
    this.toggleButton.title = 'Open Freelaince';

    document.body.appendChild(this.chatContainer);
    document.body.appendChild(this.toggleButton);
  }

  setupEventListeners() {
    const input = document.getElementById('chat-overlay-input');
    const sendButton = document.getElementById('chat-overlay-send');
    const closeButton = document.getElementById('chat-overlay-close');
    const minimizeButton = document.getElementById('chat-overlay-minimize');

    this.toggleButton.addEventListener('click', () => this.toggleChat());
    closeButton.addEventListener('click', () => this.hideChat());
    minimizeButton.addEventListener('click', () => this.minimizeChat());
    sendButton.addEventListener('click', () => this.sendMessage());
    
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendMessage();
      }
    });

    chrome.runtime.onMessage.addListener((message) => {
      if (message.type === 'NEW_MESSAGE') {
        this.displayMessage(message.data, 'received');
      } else if (message.type === 'CONVERSATION_HISTORY') {
        this.loadConversationHistory(message.data);
      }
    });
  }

  toggleChat() {
    if (this.isVisible) {
      this.hideChat();
    } else {
      this.showChat();
    }
  }

  showChat() {
    this.chatContainer.classList.add('visible');
    this.toggleButton.style.display = 'none';
    this.isVisible = true;
    this.isMinimized = false;
  }

  hideChat() {
    this.chatContainer.classList.remove('visible', 'minimized');
    this.toggleButton.style.display = 'flex';
    this.isVisible = false;
    this.isMinimized = false;
  }

  minimizeChat() {
    this.chatContainer.classList.add('minimized');
    this.isMinimized = true;
  }

  sendMessage() {
    const input = document.getElementById('chat-overlay-input');
    const message = input.value.trim();
    
    if (message) {
      this.displayMessage(message, 'sent');
      chrome.runtime.sendMessage({
        type: 'SEND_MESSAGE',
        data: message
      });
      input.value = '';
    }
  }

  loadConversationHistory(history) {
    const messagesContainer = document.getElementById('chat-overlay-messages');
    
    // Add a separator for history
    if (history.length > 0) {
      const separatorElement = document.createElement('div');
      separatorElement.className = 'chat-history-separator';
      separatorElement.textContent = '--- Previous Conversations ---';
      messagesContainer.appendChild(separatorElement);
      
      // Display historical messages
      history.forEach(msg => {
        const messageType = msg.type === 'user_message' ? 'sent' : 'received';
        this.displayHistoryMessage(msg.message, messageType, msg.timestamp);
      });
      
      // Add separator for new conversation
      const newSeparatorElement = document.createElement('div');
      newSeparatorElement.className = 'chat-history-separator';
      newSeparatorElement.textContent = '--- Current Session ---';
      messagesContainer.appendChild(newSeparatorElement);
      
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }
  
  displayHistoryMessage(message, type, timestamp) {
    const messagesContainer = document.getElementById('chat-overlay-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${type} history`;
    
    // Create message content with timestamp
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = message;
    
    const timeElement = document.createElement('div');
    timeElement.className = 'message-timestamp';
    const date = new Date(timestamp);
    timeElement.textContent = date.toLocaleTimeString();
    
    messageElement.appendChild(messageContent);
    messageElement.appendChild(timeElement);
    messagesContainer.appendChild(messageElement);
  }

  displayMessage(message, type) {
    const messagesContainer = document.getElementById('chat-overlay-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${type}`;
    messageElement.textContent = message;
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new FreelainceOverlay();
  });
} else {
  new FreelainceOverlay();
}