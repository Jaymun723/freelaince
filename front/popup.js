document.addEventListener('DOMContentLoaded', function() {
  const apiUrlInput = document.getElementById('apiUrl');
  const saveBtn = document.getElementById('saveBtn');
  const reconnectBtn = document.getElementById('reconnectBtn');
  const offersBtn = document.getElementById('offersBtn');
  const connectionStatus = document.getElementById('connectionStatus');

  // Load saved settings
  chrome.storage.sync.get(['apiUrl'], function(result) {
    if (result.apiUrl) {
      apiUrlInput.value = result.apiUrl;
      // Also store in localStorage for offers page access
      localStorage.setItem('freelaince_apiUrl', result.apiUrl);
    } else {
      apiUrlInput.value = 'ws://localhost:8080';
      localStorage.setItem('freelaince_apiUrl', 'ws://localhost:8080');
    }
  });

  // Check connection status
  chrome.runtime.sendMessage({ type: 'GET_CONNECTION_STATUS' }, function(response) {
    updateConnectionStatus(response && response.connected);
  });

  // Save settings
  saveBtn.addEventListener('click', function() {
    const apiUrl = apiUrlInput.value.trim();
    
    if (apiUrl) {
      chrome.storage.sync.set({ apiUrl: apiUrl }, function() {
        // Also store in localStorage for offers page access
        localStorage.setItem('freelaince_apiUrl', apiUrl);
        
        // Show saved feedback
        saveBtn.textContent = 'Saved!';
        saveBtn.style.background = '#38a169';
        
        setTimeout(() => {
          saveBtn.textContent = 'Save';
          saveBtn.style.background = '#4299e1';
        }, 2000);
        
        // Notify background script of new URL
        chrome.runtime.sendMessage({ 
          type: 'UPDATE_API_URL', 
          data: apiUrl 
        });
      });
    }
  });

  // Reconnect button
  reconnectBtn.addEventListener('click', function() {
    chrome.runtime.sendMessage({ type: 'RECONNECT' });
    reconnectBtn.textContent = 'Connecting...';
    reconnectBtn.disabled = true;
    
    setTimeout(() => {
      reconnectBtn.textContent = 'Reconnect';
      reconnectBtn.disabled = false;
      
      // Check status again
      chrome.runtime.sendMessage({ type: 'GET_CONNECTION_STATUS' }, function(response) {
        updateConnectionStatus(response && response.connected);
      });
    }, 2000);
  });

  // Open offers page
  offersBtn.addEventListener('click', function() {
    chrome.tabs.create({
      url: chrome.runtime.getURL('offers.html')
    });
  });

  function updateConnectionStatus(connected) {
    if (connected) {
      connectionStatus.classList.add('connected');
    } else {
      connectionStatus.classList.remove('connected');
    }
  }

  // Listen for connection status updates
  chrome.runtime.onMessage.addListener(function(message) {
    if (message.type === 'CONNECTION_STATUS') {
      updateConnectionStatus(message.data.connected);
    }
  });
});