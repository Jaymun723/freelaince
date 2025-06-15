class WebSocketManager {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.apiUrl = 'ws://localhost:8080';
    
    this.setupMessageListener();
    this.connect();
  }

  connect() {
    // Don't create new connection if already connected or connecting
    if (this.isConnected || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      console.log('🚫 Already connected or connecting, skipping new connection');
      return;
    }
    
    // Close existing connection if any
    if (this.ws && this.ws.readyState !== WebSocket.CLOSED) {
      console.log('🔄 Closing existing connection before creating new one');
      this.ws.close();
    }
    
    try {
      console.log('🔗 Creating new WebSocket connection to', this.apiUrl);
      this.ws = new WebSocket(this.apiUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyContentScript('CONNECTION_STATUS', { connected: true });
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
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.notifyContentScript('CONNECTION_STATUS', { connected: false });
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
    // Don't reconnect if we're already connected or trying to connect
    if (this.isConnected || this.ws?.readyState === WebSocket.CONNECTING) {
      console.log('🚫 Skipping reconnect - already connected or connecting');
      return;
    }
    
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        if (!this.isConnected) {  // Double check before reconnecting
          this.connect();
        }
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.log('❌ Max reconnection attempts reached');
    }
  }

  sendMessage(message) {
    if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      const payload = {
        type: 'user_message',
        message: message,
        timestamp: Date.now()
      };
      
      this.ws.send(JSON.stringify(payload));
    } else {
      console.error('WebSocket is not connected');
      this.notifyContentScript('ERROR', { message: 'Connection lost. Trying to reconnect...' });
    }
  }

  handleServerMessage(data) {
    console.log('🔄 Processing message type:', data.type);
    switch (data.type) {
      case 'bot_response':
        console.log('📤 Sending bot_response to content script');
        this.notifyContentScript('NEW_MESSAGE', data.message);
        break;
      case 'chat_answer':
        console.log('📤 Sending chat_answer to content script');
        this.notifyContentScript('NEW_MESSAGE', data.message);
        break;
      case 'open_tab':
        console.log('🔗 Opening tab:', data.url);
        this.handleTabOpen(data);
        break;
      case 'conversation_history':
        console.log('📜 Received conversation history:', data.history.length, 'messages');
        this.notifyContentScript('CONVERSATION_HISTORY', data.history);
        break;
      case 'system_message':
        console.log('⚠️  Sending system_message to content script');
        this.notifyContentScript('SYSTEM_MESSAGE', data.message);
        break;
      default:
        console.error('❌ Unknown message type:', data.type, 'Full data:', data);
    }
  }

  handleTabOpen(data) {
    // Get current tab BEFORE opening new one
    chrome.tabs.query({ active: true, currentWindow: true }, (currentTabs) => {
      const originalTabId = currentTabs[0]?.id;
      
      // Open new tab with the specified URL
      console.log('🌐 Creating new tab with URL:', data.url);
      chrome.tabs.create({ url: data.url }, (newTab) => {
        console.log('✅ Successfully opened new tab:', data.url);
        
        // Send message to the ORIGINAL tab where the chat is open
        if (data.message && originalTabId) {
          console.log('📤 Sending tab open message to original tab:', originalTabId);
          chrome.tabs.sendMessage(originalTabId, {
            type: 'NEW_MESSAGE',
            data: data.message
          }).catch((error) => {
            console.log('⚠️ Could not send message to original tab:', error);
          });
        }
      });
    });
  }

  notifyContentScript(type, data) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          type: type,
          data: data
        }).catch(() => {
          // Content script may not be ready, ignore error
        });
      }
    });
  }

  setupMessageListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      switch (message.type) {
        case 'SEND_MESSAGE':
          this.sendMessage(message.data);
          break;
        case 'GET_CONNECTION_STATUS':
          sendResponse({ connected: this.isConnected });
          break;
        case 'RECONNECT':
          console.log('🔄 Manual reconnect requested');
          // Force disconnect first, then reconnect
          this.isConnected = false;
          if (this.ws) {
            this.ws.close();
          }
          setTimeout(() => this.connect(), 100);
          break;
      }
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