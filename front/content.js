class FreelainceOverlay {
  constructor() {
    this.isVisible = false;
    this.isMinimized = false;
    this.pendingHistory = null; // Store history until DOM is ready
    this.domReady = false;
    
    this.createChatBox();
    this.setupEventListeners();
    this.loadChatState();
    this.setupStateSync();
    
    // Mark DOM as ready after creation
    setTimeout(() => {
      this.domReady = true;
      console.log('📜 DOM marked as ready');
      
      // Load any pending history
      if (this.pendingHistory) {
        console.log('📜 Loading pending history now that DOM is ready');
        this.loadConversationHistory(this.pendingHistory);
        this.pendingHistory = null;
      }
      
      // Add test message
      this.addTestMessage();
    }, 100); // Much shorter delay, just enough for DOM insertion
  }

  createChatBox() {
    this.chatContainer = document.createElement('div');
    this.chatContainer.id = 'chat-overlay-container';
    this.chatContainer.innerHTML = `
      <div id="chat-overlay-header">
        <span id="chat-overlay-title">Freelaince</span>
        <div id="chat-overlay-controls">
          <button id="chat-overlay-offers" title="View Offers">📋</button>
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

    // Ensure DOM is ready before appending
    if (document.body) {
      document.body.appendChild(this.chatContainer);
      document.body.appendChild(this.toggleButton);
      console.log('📜 Chat container and toggle button added to DOM');
    } else {
      // Wait for body to be ready
      setTimeout(() => {
        document.body.appendChild(this.chatContainer);
        document.body.appendChild(this.toggleButton);
        console.log('📜 Chat container and toggle button added to DOM (delayed)');
      }, 50);
    }
  }

  setupEventListeners() {
    const input = document.getElementById('chat-overlay-input');
    const sendButton = document.getElementById('chat-overlay-send');
    const closeButton = document.getElementById('chat-overlay-close');
    const minimizeButton = document.getElementById('chat-overlay-minimize');
    const offersButton = document.getElementById('chat-overlay-offers');

    this.toggleButton.addEventListener('click', () => this.toggleChat());
    closeButton.addEventListener('click', () => this.hideChat());
    minimizeButton.addEventListener('click', () => this.minimizeChat());
    offersButton.addEventListener('click', () => this.openOffersPage());
    sendButton.addEventListener('click', () => this.sendMessage());
    
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendMessage();
      }
    });

    chrome.runtime.onMessage.addListener((message) => {
      console.log('📨 Content script received message:', message.type, message);
      if (message.type === 'NEW_MESSAGE') {
        this.displayMessage(message.data, 'received');
      } else if (message.type === 'CONVERSATION_HISTORY') {
        console.log('📜 Received conversation history message:', message.data);
        if (this.domReady) {
          console.log('📜 DOM is ready, loading history immediately');
          this.loadConversationHistory(message.data);
        } else {
          console.log('📜 DOM not ready yet, storing history for later');
          this.pendingHistory = message.data;
        }
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
    this.saveChatState();
  }

  hideChat() {
    this.chatContainer.classList.remove('visible', 'minimized');
    this.toggleButton.style.display = 'flex';
    this.isVisible = false;
    this.isMinimized = false;
    this.saveChatState();
  }

  minimizeChat() {
    this.chatContainer.classList.add('minimized');
    this.isMinimized = true;
    this.saveChatState();
  }

  openOffersPage() {
    chrome.runtime.sendMessage({
      type: 'OPEN_OFFERS_PAGE'
    });
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

  async loadConversationHistory(history) {
    console.log('📜 Loading conversation history:', history);
    
    try {
      const messagesContainer = await this.waitForDOMElement('chat-overlay-messages');
      console.log('✅ Messages container found and ready');
    } catch (error) {
      console.error('❌ Could not find messages container:', error);
      return;
    }
    
    const messagesContainer = document.getElementById('chat-overlay-messages');
    
    console.log('📜 Messages container found, current innerHTML length:', messagesContainer.innerHTML.length);
    console.log('📜 Current children count:', messagesContainer.children.length);
    
    // Clear any existing messages first
    messagesContainer.innerHTML = '';
    console.log('📜 Cleared messages container');
    
    // Add a separator for history
    if (history && history.length > 0) {
      console.log(`📜 Displaying ${history.length} historical messages`);
      
      const separatorElement = document.createElement('div');
      separatorElement.className = 'chat-history-separator';
      separatorElement.textContent = '--- Previous Conversations ---';
      messagesContainer.appendChild(separatorElement);
      console.log('📜 Added first separator');
      
      // Display historical messages
      history.forEach((msg, index) => {
        console.log(`📜 Processing history message ${index + 1}/${history.length}:`, msg);
        const messageType = msg.type === 'user_message' ? 'sent' : 'received';
        this.displayHistoryMessage(msg.message, messageType, msg.timestamp);
      });
      
      // Add separator for new conversation
      const newSeparatorElement = document.createElement('div');
      newSeparatorElement.className = 'chat-history-separator';
      newSeparatorElement.textContent = '--- Current Session ---';
      messagesContainer.appendChild(newSeparatorElement);
      console.log('📜 Added second separator');
      
      console.log('📜 Final children count:', messagesContainer.children.length);
      console.log('📜 Final innerHTML preview:', messagesContainer.innerHTML.substring(0, 200) + '...');
      
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } else {
      console.log('📜 No conversation history to display');
    }
  }
  
  displayHistoryMessage(message, type, timestamp) {
    console.log(`📜 displayHistoryMessage called: "${message}" (${type}) at ${timestamp}`);
    const messagesContainer = document.getElementById('chat-overlay-messages');
    
    if (!messagesContainer) {
      console.error('❌ Messages container not found!');
      return;
    }
    
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
    
    console.log(`✅ Added history message to DOM. Container now has ${messagesContainer.children.length} children`);
  }

  displayMessage(message, type) {
    const messagesContainer = document.getElementById('chat-overlay-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${type}`;
    messageElement.textContent = message;
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  loadChatState() {
    // Load chat visibility state only - messages come from server history
    chrome.storage.local.get(['chatVisible', 'chatMinimized'], (result) => {
      if (result.chatVisible) {
        this.showChat();
      }
      if (result.chatMinimized) {
        this.minimizeChat();
      }
    });
  }

  saveChatState() {
    chrome.storage.local.set({
      chatVisible: this.isVisible,
      chatMinimized: this.isMinimized
    });
  }

  setupStateSync() {
    // Listen for storage changes from other tabs
    chrome.storage.onChanged.addListener((changes, namespace) => {
      if (namespace === 'local') {
        if (changes.chatVisible) {
          if (changes.chatVisible.newValue && !this.isVisible) {
            this.showChat();
          } else if (!changes.chatVisible.newValue && this.isVisible) {
            this.hideChat();
          }
        }
        
        if (changes.chatMinimized) {
          if (changes.chatMinimized.newValue && !this.isMinimized) {
            this.minimizeChat();
          } else if (!changes.chatMinimized.newValue && this.isMinimized) {
            // Restore from minimized
            this.chatContainer.classList.remove('minimized');
            this.isMinimized = false;
          }
        }
      }
    });
  }

  addTestMessage() {
    console.log('🧪 Adding test message to verify DOM is working');
    const messagesContainer = document.getElementById('chat-overlay-messages');
    if (messagesContainer) {
      const testElement = document.createElement('div');
      testElement.className = 'chat-message received';
      testElement.textContent = '🧪 TEST: DOM is working - if you see this, the chat container is functioning';
      testElement.style.background = '#ffeb3b';
      testElement.style.color = '#000';
      messagesContainer.appendChild(testElement);
      console.log('🧪 Test message added successfully');
    } else {
      console.error('🧪 Test failed: Messages container not found');
    }
  }

  waitForDOMElement(elementId, maxAttempts = 10) {
    return new Promise((resolve, reject) => {
      let attempts = 0;
      
      const checkElement = () => {
        const element = document.getElementById(elementId);
        if (element) {
          resolve(element);
        } else if (attempts < maxAttempts) {
          attempts++;
          console.log(`⏳ Waiting for ${elementId} (attempt ${attempts}/${maxAttempts})`);
          setTimeout(checkElement, 100);
        } else {
          reject(new Error(`Element ${elementId} not found after ${maxAttempts} attempts`));
        }
      };
      
      checkElement();
    });
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new FreelainceOverlay();
  });
} else {
  new FreelainceOverlay();
}