/**
 * Freelaince Offers Display Page
 * Handles display and management of job offers from the Erwan system
 */

class OffersManager {
  constructor() {
    this.offers = [];
    this.filteredOffers = [];
    this.init();
  }

  async init() {
    try {
      await this.loadOffers();
      this.setupEventListeners();
      this.renderOffers();
      this.updateStats();
    } catch (error) {
      this.showError('Failed to initialize offers manager: ' + error.message);
    }
  }

  async loadOffers() {
    try {
      // First try to load from local storage (cached data)
      const cachedOffers = localStorage.getItem('freelaince_offers');
      if (cachedOffers) {
        this.offers = JSON.parse(cachedOffers);
        this.filteredOffers = [...this.offers];
        return;
      }

      // If no cached data, try to fetch from WebSocket server
      await this.fetchOffersFromServer();
    } catch (error) {
      console.error('Error loading offers:', error);
      // Load sample data for demonstration
      this.loadSampleData();
    }
  }

  async fetchOffersFromServer() {
    return new Promise((resolve, reject) => {
      try {
        // Check if chrome extension APIs are available
        if (typeof chrome !== 'undefined' && chrome.storage) {
          chrome.storage.sync.get(['apiUrl'], (result) => {
            const wsUrl = result.apiUrl || 'ws://localhost:8080';
            this.connectAndFetchOffers(wsUrl, resolve, reject);
          });
        } else {
          // Fallback for non-extension context
          const wsUrl = localStorage.getItem('freelaince_apiUrl') || 'ws://localhost:8080';
          this.connectAndFetchOffers(wsUrl, resolve, reject);
        }
      } catch (error) {
        reject(error);
      }
    });
  }

  connectAndFetchOffers(wsUrl, resolve, reject) {
    try {
      const socket = new WebSocket(wsUrl);
      let dataReceived = false;

      socket.onopen = () => {
        console.log('📡 Connected to server, requesting offers...');
        // Request offers data
        socket.send(JSON.stringify({
          type: 'get_offers',
          timestamp: new Date().toISOString()
        }));
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 Received from server:', data.type);
          
          if (data.type === 'offers_data') {
            dataReceived = true;
            this.offers = data.offers || [];
            this.filteredOffers = [...this.offers];
            
            // Cache the offers
            localStorage.setItem('freelaince_offers', JSON.stringify(this.offers));
            
            console.log(`✅ Loaded ${this.offers.length} offers from server`);
            socket.close();
            resolve();
          }
        } catch (error) {
          console.error('Error parsing offers data:', error);
          reject(error);
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(new Error('Failed to connect to server'));
      };

      socket.onclose = () => {
        if (!dataReceived) {
          console.warn('Connection closed without receiving offers data');
          reject(new Error('No data received from server'));
        }
      };

      // Timeout after 5 seconds
      setTimeout(() => {
        if (!dataReceived) {
          console.warn('Server request timeout');
          socket.close();
          reject(new Error('Server request timeout'));
        }
      }, 5000);
    } catch (error) {
      console.error('Error connecting to fetch offers:', error);
      reject(error);
    }
  }

  loadSampleData() {
    // Sample data for demonstration (matches Erwan offer structure)
    this.offers = [
      {
        offer_id: '12345678',
        job_title: 'Photography',
        client_name: 'Sarah Johnson',
        client_company: 'Johnson Events Co.',
        client_contact: 'sarah@johsonevents.com',
        date_time: new Date('2024-12-20T14:00:00'),
        location: 'Central Park, New York',
        status: 'pending',
        description: 'Wedding photography for outdoor ceremony and reception. Need professional photographer with experience in natural lighting and candid shots.',
        source_url: 'https://example.com/wedding-photographer-needed',
        created_at: new Date('2024-06-10T10:30:00'),
        payment_terms: '$2,500 for full day coverage',
        requirements: 'Professional camera equipment, 2+ years experience, portfolio required',
        duration: '8 hours',
        specific_details: {
          event_type: 'Wedding',
          photos_expected: 500,
          equipment_requirements: ['DSLR Camera', 'External Flash', 'Backup Equipment'],
          post_processing_requirements: 'Color correction, basic retouching, album-ready edits',
          delivery_format: 'Digital Download',
          delivery_timeline: '2 weeks after event',
          additional_services: ['Engagement shoot', 'Print package']
        }
      },
      {
        offer_id: '87654321',
        job_title: 'Photography',
        client_name: 'Tech Corp Inc.',
        client_company: 'Tech Corp Inc.',
        client_contact: '+1-555-0123',
        date_time: new Date('2024-06-25T09:00:00'),
        location: 'Downtown Office Building',
        status: 'accepted',
        description: 'Corporate headshots for new employees. Professional business portraits needed for company website and marketing materials.',
        source_url: 'https://example.com/corporate-headshots',
        created_at: new Date('2024-06-12T15:45:00'),
        payment_terms: '$150 per person (20 people)',
        requirements: 'Studio lighting setup, professional backdrop, business attire coordination',
        duration: '4 hours',
        specific_details: {
          event_type: 'Corporate',
          photos_expected: 60,
          equipment_requirements: ['Studio Lights', 'Backdrop', 'Professional Camera'],
          post_processing_requirements: 'Professional retouching, consistent lighting, business-appropriate editing',
          delivery_format: 'Cloud Storage',
          delivery_timeline: '1 week after shoot',
          additional_services: ['LinkedIn profile optimization']
        }
      },
      {
        offer_id: '45678901',
        job_title: 'Photography',
        client_name: 'Maria Rodriguez',
        client_company: 'Self',
        client_contact: 'maria.r@email.com',
        date_time: new Date('2024-06-18T16:00:00'),
        location: 'Beach Location, Miami',
        status: 'completed',
        description: 'Family portrait session at sunset. Looking for natural, candid shots of family of 5 including grandparents.',
        source_url: 'https://example.com/family-portraits',
        created_at: new Date('2024-06-05T12:20:00'),
        payment_terms: '$800 for 2-hour session',
        requirements: 'Experience with family photography, good with children, natural lighting expertise',
        duration: '2 hours',
        specific_details: {
          event_type: 'Family',
          photos_expected: 100,
          equipment_requirements: ['DSLR Camera', 'Prime Lens', 'Reflector'],
          post_processing_requirements: 'Natural color grading, light retouching, family-friendly editing',
          delivery_format: 'Digital Download',
          delivery_timeline: '1 week after session',
          additional_services: ['Printed album options']
        }
      }
    ];
    
    this.filteredOffers = [...this.offers];
    // Cache sample data
    localStorage.setItem('freelaince_offers', JSON.stringify(this.offers));
  }

  setupEventListeners() {
    // Filter buttons
    document.getElementById('applyFilters').addEventListener('click', () => this.applyFilters());
    document.getElementById('clearFilters').addEventListener('click', () => this.clearFilters());
    
    // Real-time search on input
    document.getElementById('clientFilter').addEventListener('input', () => this.applyFilters());
    document.getElementById('locationFilter').addEventListener('input', () => this.applyFilters());
    
    // Filter dropdowns
    document.getElementById('statusFilter').addEventListener('change', () => this.applyFilters());
    document.getElementById('typeFilter').addEventListener('change', () => this.applyFilters());
  }

  applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    const clientFilter = document.getElementById('clientFilter').value.toLowerCase();
    const locationFilter = document.getElementById('locationFilter').value.toLowerCase();

    this.filteredOffers = this.offers.filter(offer => {
      const matchesStatus = !statusFilter || offer.status === statusFilter;
      const matchesType = !typeFilter || offer.job_title === typeFilter;
      const matchesClient = !clientFilter || offer.client_name.toLowerCase().includes(clientFilter);
      const matchesLocation = !locationFilter || offer.location.toLowerCase().includes(locationFilter);

      return matchesStatus && matchesType && matchesClient && matchesLocation;
    });

    this.renderOffers();
    this.updateStats();
  }

  clearFilters() {
    document.getElementById('statusFilter').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('clientFilter').value = '';
    document.getElementById('locationFilter').value = '';
    
    this.filteredOffers = [...this.offers];
    this.renderOffers();
    this.updateStats();
  }

  renderOffers() {
    const container = document.getElementById('offersContainer');
    
    if (this.filteredOffers.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <h3>No offers found</h3>
          <p>Try adjusting your filters or check back later for new opportunities.</p>
        </div>
      `;
      return;
    }

    const offersHtml = this.filteredOffers.map(offer => this.renderOfferCard(offer)).join('');
    container.innerHTML = offersHtml;
  }

  renderOfferCard(offer) {
    const dateStr = new Date(offer.date_time).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });

    const createdStr = new Date(offer.created_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });

    const specificsHtml = offer.specific_details ? this.renderSpecificDetails(offer.specific_details) : '';

    return `
      <div class="offer-card ${offer.status}" data-offer-id="${offer.offer_id}">
        <div class="offer-header">
          <h3 class="offer-title">${offer.job_title} - ${offer.client_name}</h3>
          <span class="offer-status ${offer.status}">${offer.status}</span>
        </div>
        
        <div class="offer-meta">
          <div class="offer-meta-item">
            <span class="offer-meta-label">Date & Time</span>
            <span class="offer-meta-value">${dateStr}</span>
          </div>
          <div class="offer-meta-item">
            <span class="offer-meta-label">Location</span>
            <span class="offer-meta-value">${offer.location}</span>
          </div>
          <div class="offer-meta-item">
            <span class="offer-meta-label">Duration</span>
            <span class="offer-meta-value">${offer.duration}</span>
          </div>
          <div class="offer-meta-item">
            <span class="offer-meta-label">Payment</span>
            <span class="offer-meta-value">${offer.payment_terms}</span>
          </div>
          <div class="offer-meta-item">
            <span class="offer-meta-label">Company</span>
            <span class="offer-meta-value">${offer.client_company}</span>
          </div>
          <div class="offer-meta-item">
            <span class="offer-meta-label">Found On</span>
            <span class="offer-meta-value">${createdStr}</span>
          </div>
        </div>
        
        <div class="offer-description">
          ${offer.description}
        </div>
        
        ${specificsHtml}
        
        <div class="offer-actions">
          ${offer.source_url ? `<button class="btn btn-outline btn-small" onclick="window.open('${offer.source_url}', '_blank')">View Source</button>` : ''}
          ${offer.status === 'pending' ? `
            <button class="btn btn-outline btn-small" onclick="offersManager.updateOfferStatus('${offer.offer_id}', 'accepted')">Accept</button>
            <button class="btn btn-outline btn-small" onclick="offersManager.updateOfferStatus('${offer.offer_id}', 'declined')">Decline</button>
          ` : ''}
          ${offer.status === 'accepted' ? `
            <button class="btn btn-outline btn-small" onclick="offersManager.updateOfferStatus('${offer.offer_id}', 'completed')">Mark Complete</button>
            <button class="btn btn-outline btn-small" onclick="offersManager.updateOfferStatus('${offer.offer_id}', 'declined')">Cancel</button>
          ` : ''}
          ${offer.status === 'declined' ? `
            <button class="btn btn-outline btn-small" onclick="offersManager.updateOfferStatus('${offer.offer_id}', 'pending')">Reconsider</button>
          ` : ''}
          ${offer.status === 'completed' ? `
            <button class="btn btn-outline btn-small" onclick="offersManager.updateOfferStatus('${offer.offer_id}', 'accepted')">Reopen</button>
          ` : ''}
          <button class="btn btn-primary btn-small" onclick="offersManager.viewOfferDetails('${offer.offer_id}')">Details</button>
        </div>
      </div>
    `;
  }

  renderSpecificDetails(details) {
    if (!details) return '';

    const detailsHtml = Object.entries(details)
      .filter(([key, value]) => value && value !== 'NOT_AVAILABLE')
      .map(([key, value]) => {
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        let displayValue = value;
        
        if (Array.isArray(value)) {
          displayValue = value.join(', ');
        }
        
        return `
          <div class="specific-item">
            <span class="specific-label">${label}</span>
            <span class="specific-value">${displayValue}</span>
          </div>
        `;
      }).join('');

    return `
      <div class="offer-specifics">
        <h4>Project Specifics</h4>
        <div class="specifics-grid">
          ${detailsHtml}
        </div>
      </div>
    `;
  }

  updateStats() {
    const stats = {
      total: this.offers.length,
      pending: this.offers.filter(o => o.status === 'pending').length,
      accepted: this.offers.filter(o => o.status === 'accepted').length,
      completed: this.offers.filter(o => o.status === 'completed').length
    };

    document.getElementById('totalOffers').textContent = stats.total;
    document.getElementById('pendingOffers').textContent = stats.pending;
    document.getElementById('acceptedOffers').textContent = stats.accepted;
    document.getElementById('completedOffers').textContent = stats.completed;
  }

  async updateOfferStatus(offerId, newStatus) {
    try {
      // Show loading state
      this.setButtonLoading(offerId, true);
      
      // First try to sync with server
      const serverSuccess = await this.syncStatusWithServer(offerId, newStatus);
      
      if (serverSuccess) {
        // Update locally only if server update succeeded
        const offer = this.offers.find(o => o.offer_id === offerId);
        if (offer) {
          offer.status = newStatus;
          
          // Update cache
          localStorage.setItem('freelaince_offers', JSON.stringify(this.offers));
          
          // Re-render
          this.applyFilters();
          this.updateStats();
          
          // Show success message
          this.showSuccess(`Offer status updated to ${newStatus}`);
        }
      } else {
        // Server update failed, show error
        this.showError('Failed to update offer status on server');
      }
      
    } catch (error) {
      console.error('Error updating offer status:', error);
      this.showError('Failed to update offer status: ' + error.message);
    } finally {
      // Hide loading state
      this.setButtonLoading(offerId, false);
    }
  }

  async syncStatusWithServer(offerId, newStatus) {
    return new Promise((resolve, reject) => {
      try {
        // Check if chrome extension APIs are available
        if (typeof chrome !== 'undefined' && chrome.storage) {
          chrome.storage.sync.get(['apiUrl'], (result) => {
            const wsUrl = result.apiUrl || 'ws://localhost:8080';
            this.connectAndSendUpdate(wsUrl, offerId, newStatus, resolve);
          });
        } else {
          // Fallback for non-extension context
          const wsUrl = localStorage.getItem('freelaince_apiUrl') || 'ws://localhost:8080';
          this.connectAndSendUpdate(wsUrl, offerId, newStatus, resolve);
        }
      } catch (error) {
        console.error('Error connecting to server:', error);
        resolve(false);
      }
    });
  }

  connectAndSendUpdate(wsUrl, offerId, newStatus, resolve) {
    try {
      const socket = new WebSocket(wsUrl);
      let responseReceived = false;

      socket.onopen = () => {
        console.log(`📤 Sending status update to server: ${offerId} -> ${newStatus}`);
        socket.send(JSON.stringify({
          type: 'update_offer_status',
          offer_id: offerId,
          status: newStatus,
          timestamp: new Date().toISOString()
        }));
      };

      socket.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          console.log('📨 Server response:', response);
          
          responseReceived = true;
          socket.close();
          
          if (response.type === 'offer_status_updated' && response.success) {
            resolve(true);
          } else {
            console.error('Server update failed:', response.error || 'Unknown error');
            resolve(false);
          }
        } catch (error) {
          console.error('Error parsing server response:', error);
          resolve(false);
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (!responseReceived) {
          resolve(false);
        }
      };

      socket.onclose = () => {
        if (!responseReceived) {
          console.warn('WebSocket closed without response');
          resolve(false);
        }
      };

      // Timeout after 5 seconds
      setTimeout(() => {
        if (!responseReceived) {
          console.warn('Server request timeout');
          socket.close();
          resolve(false);
        }
      }, 5000);
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      resolve(false);
    }
  }

  viewOfferDetails(offerId) {
    const offer = this.offers.find(o => o.offer_id === offerId);
    if (!offer) return;

    // For now, just log the full offer details
    // In a real implementation, this could open a modal or navigate to a detail page
    console.log('Full offer details:', offer);
    
    // Show an alert with key details
    const details = `
Offer Details:
• Client: ${offer.client_name} (${offer.client_company})
• Contact: ${offer.client_contact}
• Date: ${new Date(offer.date_time).toLocaleString()}
• Location: ${offer.location}
• Duration: ${offer.duration}
• Payment: ${offer.payment_terms}
• Requirements: ${offer.requirements}

${offer.source_url ? 'Source: ' + offer.source_url : ''}
    `;
    
    alert(details);
  }

  showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    errorContainer.innerHTML = `
      <div class="error">
        <strong>Error:</strong> ${message}
      </div>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      errorContainer.innerHTML = '';
    }, 5000);
  }

  showSuccess(message) {
    const errorContainer = document.getElementById('errorContainer');
    errorContainer.innerHTML = `
      <div class="success">
        <strong>Success:</strong> ${message}
      </div>
    `;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      errorContainer.innerHTML = '';
    }, 3000);
  }

  setButtonLoading(offerId, loading) {
    // Find all action buttons for this offer
    const offerCard = document.querySelector(`[data-offer-id="${offerId}"]`);
    if (!offerCard) return;

    const actionButtons = offerCard.querySelectorAll('.offer-actions button');
    
    actionButtons.forEach(button => {
      if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = 'Loading...';
        button.style.opacity = '0.6';
      } else {
        button.disabled = false;
        if (button.dataset.originalText) {
          button.textContent = button.dataset.originalText;
          delete button.dataset.originalText;
        }
        button.style.opacity = '1';
      }
    });
  }

  // Refresh offers from server
  async refreshOffers() {
    try {
      document.getElementById('offersContainer').innerHTML = '<div class="loading">Refreshing offers...</div>';
      
      // Clear cache
      localStorage.removeItem('freelaince_offers');
      
      // Reload
      await this.loadOffers();
      this.renderOffers();
      this.updateStats();
    } catch (error) {
      this.showError('Failed to refresh offers');
    }
  }
}

// Initialize the offers manager when the page loads
let offersManager;
document.addEventListener('DOMContentLoaded', () => {
  offersManager = new OffersManager();
  
  // Add refresh functionality (could be triggered by a button)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
      e.preventDefault();
      offersManager.refreshOffers();
    }
  });
});