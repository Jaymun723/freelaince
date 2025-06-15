class WebSocketManager {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.apiUrl = 'ws://localhost:8080';
    
    this.setupMessageListener();
    this.loadSettings();
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.sync.get(['apiUrl']);
      if (result.apiUrl) {
        this.apiUrl = result.apiUrl;
      }
      this.connect();
    } catch (error) {
      console.error('Failed to load settings:', error);
      this.connect();
    }
  }

  connect() {
    if (this.isConnected || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      console.log('🚫 Already connected or connecting, skipping new connection');
      return;
    }
    
    if (this.ws && this.ws.readyState !== WebSocket.CLOSED) {
      console.log('🔄 Closing existing connection before creating new one');
      this.ws.close();
    }
    
    try {
      console.log('🔗 Creating new WebSocket connection to', this.apiUrl);
      this.ws = new WebSocket(this.apiUrl);
      
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyPopup('CONNECTION_STATUS', { connected: true });
        
        // Request conversation history
        this.sendMessage('sync_history', 'sync_history');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 Received message from server:', data);
          this.handleServerMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('❌ WebSocket disconnected');
        this.isConnected = false;
        this.notifyPopup('CONNECTION_STATUS', { connected: false });
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnected = false;
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.attemptReconnect();
    }
  }

  attemptReconnect() {
    if (this.isConnected || this.ws?.readyState === WebSocket.CONNECTING) {
      console.log('🚫 Skipping reconnect - already connected or connecting');
      return;
    }
    
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        if (!this.isConnected) {
          this.connect();
        }
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.log('❌ Max reconnection attempts reached');
    }
  }

  sendMessage(message, type = 'user_message') {
    if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      const payload = {
        type: type,
        message: message,
        timestamp: Date.now()
      };
      
      this.ws.send(JSON.stringify(payload));
      console.log('📤 Sent message:', payload);
    } else {
      console.error('WebSocket is not connected');
      this.notifyPopup('ERROR', { message: 'Connection lost. Trying to reconnect...' });
    }
  }

  handleServerMessage(data) {
    console.log('🔄 Processing message type:', data.type);
    switch (data.type) {
      case 'bot_response':
      case 'chat_answer':
        console.log('📤 Sending bot response to popup');
        this.notifyPopup('NEW_MESSAGE', data.message);
        break;
      case 'open_tab':
        console.log('🔗 Opening tab:', data.url);
        this.handleTabOpen(data);
        break;
      case 'conversation_history':
        console.log('📜 Received conversation history:', data.history?.length || 0, 'messages');
        this.notifyPopup('CONVERSATION_HISTORY', data.history);
        break;
      case 'system_message':
        console.log('⚠️ Sending system message to popup');
        this.notifyPopup('SYSTEM_MESSAGE', data.message);
        break;
      default:
        console.error('❌ Unknown message type:', data.type, 'Full data:', data);
    }
  }

  handleTabOpen(data) {
    chrome.tabs.create({ url: data.url }, (newTab) => {
      console.log('✅ Successfully opened new tab:', data.url);
      
      if (data.message) {
        this.notifyPopup('NEW_MESSAGE', data.message);
      }
    });
  }

  notifyPopup(type, data) {
    console.log('📤 Notifying popup:', type, data);
    // Since we're working with popup, we need to send to all extension contexts
    chrome.runtime.sendMessage({
      type: type,
      data: data
    }).catch((error) => {
      // Popup might be closed, that's okay
      console.log('Popup not open, message not delivered:', error.message);
    });
  }

  setupMessageListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      console.log('📨 Background received message:', message);
      
      switch (message.type) {
        case 'SEND_MESSAGE':
          this.sendMessage(message.data);
          sendResponse({ success: true });
          break;
        case 'GET_CONNECTION_STATUS':
          sendResponse({ connected: this.isConnected });
          break;
        case 'RECONNECT':
          console.log('🔄 Manual reconnect requested');
          this.isConnected = false;
          if (this.ws) {
            this.ws.close();
          }
          setTimeout(() => this.connect(), 100);
          sendResponse({ success: true });
          break;
        case 'UPDATE_API_URL':
          console.log('🔧 Updating API URL to:', message.data);
          this.apiUrl = message.data;
          this.isConnected = false;
          if (this.ws) {
            this.ws.close();
          }
          setTimeout(() => this.connect(), 100);
          sendResponse({ success: true });
          break;
        case 'REQUEST_HISTORY':
          console.log('📜 History requested, sending sync_history');
          this.sendMessage('sync_history', 'sync_history');
          sendResponse({ success: true });
          break;
      }
      
      return true; // Will respond asynchronously
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }
}

let wsManager = null;

function initializeManager() {
  if (!wsManager) {
    console.log('🔧 Initializing WebSocket Manager');
    wsManager = new WebSocketManager();
  } else {
    console.log('⚠️ WebSocket Manager already exists, skipping initialization');
  }
}

chrome.runtime.onStartup.addListener(() => {
  console.log('🚀 Extension startup');
  initializeManager();
});

chrome.runtime.onInstalled.addListener(() => {
  console.log('🔧 Extension installed/updated');
  initializeManager();
});

// Fallback initialization
initializeManager();