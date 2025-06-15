/**
 * Freelaince Calendar Manager
 * Handles calendar display and event management with server sync
 */

class CalendarManager {
  constructor() {
    this.events = [];
    this.currentDate = new Date();
    this.viewType = 'month';
    this.selectedDate = null;
    this.selectedEvent = null;
    this.wsSocket = null;
    this.connectionStatus = 'disconnected';
    this.init();
  }

  async init() {
    try {
      this.updateConnectionStatus('connecting');
      await this.connectToServer();
      await this.loadEvents();
      this.setupEventListeners();
      this.renderCalendar();
    } catch (error) {
      this.showError('Failed to initialize calendar: ' + error.message);
      this.loadSampleData();
      this.renderCalendar();
    }
  }

  async connectToServer() {
    return new Promise((resolve, reject) => {
      try {
        if (typeof chrome !== 'undefined' && chrome.storage) {
          chrome.storage.sync.get(['apiUrl'], (result) => {
            const wsUrl = result.apiUrl || 'ws://localhost:8080';
            this.establishConnection(wsUrl, resolve, reject);
          });
        } else {
          const wsUrl = localStorage.getItem('freelaince_apiUrl') || 'ws://localhost:8080';
          this.establishConnection(wsUrl, resolve, reject);
        }
      } catch (error) {
        reject(error);
      }
    });
  }

  establishConnection(wsUrl, resolve, reject) {
    try {
      this.wsSocket = new WebSocket(wsUrl);

      this.wsSocket.onopen = () => {
        console.log('✅ Connected to Freelaince server');
        this.updateConnectionStatus('connected');
        resolve();
      };

      this.wsSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleServerMessage(data);
        } catch (error) {
          console.error('Error parsing server message:', error);
        }
      };

      this.wsSocket.onclose = () => {
        console.log('❌ Disconnected from server');
        this.updateConnectionStatus('disconnected');
      };

      this.wsSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.updateConnectionStatus('disconnected');
        reject(new Error('Failed to connect to server'));
      };

      setTimeout(() => {
        if (this.wsSocket.readyState !== WebSocket.OPEN) {
          console.warn('Connection timeout');
          this.wsSocket.close();
          reject(new Error('Connection timeout'));
        }
      }, 5000);
    } catch (error) {
      console.error('Error establishing connection:', error);
      reject(error);
    }
  }

  handleServerMessage(data) {
    console.log('📨 Received from server:', data.type);
    
    switch (data.type) {
      case 'schedule_data':
      case 'events_data':
        this.events = this.parseEventsData(data.events || data.schedule || []);
        localStorage.setItem('freelaince_calendar', JSON.stringify(this.events));
        console.log(`✅ Loaded ${this.events.length} events from server`);
        this.renderCalendar();
        break;
      case 'event_added':
        if (data.success) {
          this.showSuccess('Event added successfully');
          this.requestEvents();
        } else {
          this.showError('Failed to add event: ' + (data.message || 'Unknown error'));
        }
        break;
      case 'event_updated':
        if (data.success) {
          this.showSuccess('Event updated successfully');
          this.requestEvents();
        } else {
          this.showError('Failed to update event: ' + (data.message || 'Unknown error'));
        }
        break;
      case 'event_deleted':
        if (data.success) {
          this.showSuccess('Event deleted successfully');
          this.requestEvents();
        } else {
          this.showError('Failed to delete event: ' + (data.message || 'Unknown error'));
        }
        break;
      case 'error':
        this.showError('Server error: ' + data.message);
        break;
    }
  }

  parseEventsData(serverEvents) {
    return serverEvents.map(event => ({
      id: event.id || this.generateId(),
      title: event.title,
      start: new Date(event.start_time || event.start),
      end: new Date(event.end_time || event.end),
      description: event.description || '',
      location: event.location || '',
      priority: event.priority || 1
    }));
  }

  updateConnectionStatus(status) {
    this.connectionStatus = status;
    const statusElement = document.getElementById('connectionStatus');
    
    if (status === 'connected') {
      statusElement.textContent = 'Connected';
      statusElement.className = 'connection-status connected';
    } else if (status === 'connecting') {
      statusElement.textContent = 'Connecting...';
      statusElement.className = 'connection-status disconnected';
    } else {
      statusElement.textContent = 'Disconnected';
      statusElement.className = 'connection-status disconnected';
    }
  }

  async loadEvents() {
    try {
      const cachedEvents = localStorage.getItem('freelaince_calendar');
      if (cachedEvents) {
        this.events = JSON.parse(cachedEvents).map(event => ({
          ...event,
          start: new Date(event.start),
          end: new Date(event.end)
        }));
      }

      if (this.connectionStatus === 'connected') {
        this.requestEvents();
      }
    } catch (error) {
      console.error('Error loading events:', error);
      this.loadSampleData();
    }
  }

  requestEvents() {
    if (this.wsSocket && this.wsSocket.readyState === WebSocket.OPEN) {
      console.log('📡 Requesting events from server...');
      // Try multiple message types that the server might understand
      this.wsSocket.send(JSON.stringify({
        type: 'get_schedule',
        start_date: this.formatDate(this.getMonthStart()),
        end_date: this.formatDate(this.getMonthEnd()),
        timestamp: new Date().toISOString()
      }));
    }
  }

  loadSampleData() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    this.events = [
      {
        id: '1',
        title: 'Team Meeting',
        start: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 14, 0),
        end: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 15, 0),
        description: 'Weekly team sync',
        location: 'Conference Room',
        priority: 3
      },
      {
        id: '2',
        title: 'Client Call',
        start: new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate(), 10, 0),
        end: new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate(), 11, 0),
        description: 'Discuss project requirements',
        location: 'Zoom',
        priority: 4
      },
      {
        id: '3',
        title: 'Lunch Break',
        start: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 12, 0),
        end: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 13, 0),
        description: 'Personal time',
        location: '',
        priority: 1
      }
    ];
    
    localStorage.setItem('freelaince_calendar', JSON.stringify(this.events));
  }

  setupEventListeners() {
    // View controls
    document.getElementById('monthView').addEventListener('click', () => this.setView('month'));
    document.getElementById('weekView').addEventListener('click', () => this.setView('week'));
    document.getElementById('listView').addEventListener('click', () => this.setView('list'));

    // Navigation
    document.getElementById('prevPeriod').addEventListener('click', () => this.navigatePeriod(-1));
    document.getElementById('nextPeriod').addEventListener('click', () => this.navigatePeriod(1));
    document.getElementById('todayBtn').addEventListener('click', () => this.goToToday());

    // Add event
    document.getElementById('addEventFab').addEventListener('click', () => this.showAddEventForm());

    // Sidebar
    document.getElementById('closeSidebar').addEventListener('click', () => this.closeSidebar());
    document.getElementById('cancelEvent').addEventListener('click', () => this.closeSidebar());

    // Priority selector
    document.querySelectorAll('.priority-option').forEach(option => {
      option.addEventListener('click', (e) => {
        document.querySelectorAll('.priority-option').forEach(opt => opt.classList.remove('selected'));
        e.target.classList.add('selected');
      });
    });

    // Form submission
    document.getElementById('eventForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.saveEvent();
    });

    // Delete event
    document.getElementById('deleteEvent').addEventListener('click', () => this.deleteSelectedEvent());
  }

  setView(view) {
    this.viewType = view;
    
    // Update active button
    document.querySelectorAll('.view-controls .btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(view + 'View').classList.add('active');
    
    this.renderCalendar();
  }

  navigatePeriod(direction) {
    if (this.viewType === 'month') {
      this.currentDate.setMonth(this.currentDate.getMonth() + direction);
    } else if (this.viewType === 'week') {
      this.currentDate.setDate(this.currentDate.getDate() + (direction * 7));
    }
    this.renderCalendar();
  }

  goToToday() {
    this.currentDate = new Date();
    this.renderCalendar();
  }

  renderCalendar() {
    this.updatePeriodDisplay();
    
    if (this.viewType === 'month') {
      this.renderMonthView();
    } else if (this.viewType === 'week') {
      this.renderWeekView();
    } else {
      this.renderListView();
    }
  }

  updatePeriodDisplay() {
    const periodElement = document.getElementById('currentPeriod');
    
    if (this.viewType === 'month') {
      periodElement.textContent = this.currentDate.toLocaleDateString('en-US', { 
        month: 'long', 
        year: 'numeric' 
      });
    } else if (this.viewType === 'week') {
      const weekStart = this.getWeekStart();
      const weekEnd = this.getWeekEnd();
      periodElement.textContent = `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
    } else {
      periodElement.textContent = 'Event List';
    }
  }

  renderMonthView() {
    const grid = document.getElementById('calendarGrid');
    const monthStart = this.getMonthStart();
    const monthEnd = this.getMonthEnd();
    
    // Clear existing content
    grid.innerHTML = '';
    
    // Add headers
    const headers = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    headers.forEach(header => {
      const headerElement = document.createElement('div');
      headerElement.className = 'calendar-header';
      headerElement.textContent = header;
      grid.appendChild(headerElement);
    });
    
    // Calculate calendar bounds
    const calendarStart = new Date(monthStart);
    calendarStart.setDate(calendarStart.getDate() - (calendarStart.getDay() || 7) + 1);
    
    const calendarEnd = new Date(monthEnd);
    calendarEnd.setDate(calendarEnd.getDate() + (7 - calendarEnd.getDay()) % 7);
    
    // Generate calendar days
    const currentDate = new Date(calendarStart);
    const today = new Date();
    
    while (currentDate <= calendarEnd) {
      const dayElement = this.createDayElement(currentDate, monthStart, monthEnd, today);
      grid.appendChild(dayElement);
      currentDate.setDate(currentDate.getDate() + 1);
    }
  }

  createDayElement(date, monthStart, monthEnd, today) {
    const dayElement = document.createElement('div');
    dayElement.className = 'calendar-day';
    
    // Add classes for styling
    if (date < monthStart || date > monthEnd) {
      dayElement.classList.add('other-month');
    }
    if (this.isSameDay(date, today)) {
      dayElement.classList.add('today');
    }
    
    // Day number
    const dayNumber = document.createElement('div');
    dayNumber.className = 'day-number';
    dayNumber.textContent = date.getDate();
    dayElement.appendChild(dayNumber);
    
    // Events for this day
    const dayEvents = this.getEventsForDate(date);
    dayEvents.forEach(event => {
      const eventElement = document.createElement('div');
      eventElement.className = `day-event priority-${event.priority}`;
      eventElement.textContent = `${this.formatTime(event.start)} ${event.title}`;
      eventElement.title = `${event.title} (${this.formatTime(event.start)} - ${this.formatTime(event.end)})`;
      
      // Check for conflicts
      if (this.hasConflicts(event)) {
        eventElement.classList.add('conflict');
      }
      
      eventElement.addEventListener('click', (e) => {
        e.stopPropagation();
        this.showEventDetails(event);
      });
      
      dayElement.appendChild(eventElement);
    });
    
    // Click handler for day
    dayElement.addEventListener('click', () => {
      this.selectDate(new Date(date));
    });
    
    return dayElement;
  }

  renderWeekView() {
    // For now, render week as a simplified month view
    // This could be enhanced to show hourly slots
    this.renderMonthView();
  }

  renderListView() {
    const grid = document.getElementById('calendarGrid');
    grid.innerHTML = '';
    
    if (this.events.length === 0) {
      grid.innerHTML = '<div class="loading">No events found</div>';
      return;
    }
    
    // Sort events by date
    const sortedEvents = [...this.events].sort((a, b) => a.start - b.start);
    
    // Group by date
    const eventsByDate = {};
    sortedEvents.forEach(event => {
      const dateKey = this.formatDate(event.start);
      if (!eventsByDate[dateKey]) {
        eventsByDate[dateKey] = [];
      }
      eventsByDate[dateKey].push(event);
    });
    
    // Create list view
    const listContainer = document.createElement('div');
    listContainer.style.cssText = 'max-width: 800px; margin: 0 auto; padding: 20px;';
    
    Object.entries(eventsByDate).forEach(([date, events]) => {
      const dateHeader = document.createElement('h3');
      dateHeader.style.cssText = 'color: #4299e1; margin: 30px 0 16px 0; padding-bottom: 8px; border-bottom: 2px solid #404040;';
      dateHeader.textContent = new Date(date).toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
      listContainer.appendChild(dateHeader);
      
      events.forEach(event => {
        const eventCard = this.createEventCard(event);
        listContainer.appendChild(eventCard);
      });
    });
    
    grid.appendChild(listContainer);
  }

  createEventCard(event) {
    const card = document.createElement('div');
    card.className = 'event-card';
    if (this.hasConflicts(event)) {
      card.classList.add('conflict');
    }
    
    card.innerHTML = `
      <div class="event-card-header">
        <div class="event-title">${event.title}</div>
        <div class="priority-option priority-${event.priority}">${event.priority}</div>
      </div>
      <div class="event-time">
        🕐 ${this.formatTime(event.start)} - ${this.formatTime(event.end)}
      </div>
      ${event.description ? `<div class="event-description">${event.description}</div>` : ''}
      <div class="event-meta">
        ${event.location ? `<span>📍 ${event.location}</span>` : ''}
        <span>⏱️ ${this.getEventDuration(event)}</span>
      </div>
      <div class="event-actions">
        <button class="btn btn-secondary btn-small edit-event-btn">Edit</button>
        <button class="btn btn-danger btn-small delete-event-btn">Delete</button>
      </div>
    `;
    
    // Add event listeners
    card.querySelector('.edit-event-btn').addEventListener('click', () => this.editEvent(event));
    card.querySelector('.delete-event-btn').addEventListener('click', () => this.deleteEvent(event));
    
    return card;
  }

  getEventsForDate(date) {
    return this.events.filter(event => this.isSameDay(event.start, date));
  }

  hasConflicts(targetEvent) {
    return this.events.some(event => 
      event.id !== targetEvent.id && 
      this.eventsOverlap(event, targetEvent)
    );
  }

  eventsOverlap(event1, event2) {
    return event1.start < event2.end && event1.end > event2.start;
  }

  selectDate(date) {
    this.selectedDate = date;
    const events = this.getEventsForDate(date);
    
    if (events.length > 0) {
      this.showDayEvents(date, events);
    } else {
      this.showAddEventForm(date);
    }
  }

  showDayEvents(date, events) {
    document.getElementById('selectedDate').textContent = date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    
    const eventList = document.getElementById('eventList');
    eventList.innerHTML = '';
    
    events.forEach(event => {
      const eventCard = this.createEventCard(event);
      eventList.appendChild(eventCard);
    });
    
    document.getElementById('dayEvents').style.display = 'block';
    document.getElementById('eventForm').style.display = 'none';
    document.getElementById('sidebarTitle').textContent = `Events for ${date.toLocaleDateString()}`;
    this.openSidebar();
  }

  showAddEventForm(date = null) {
    this.selectedEvent = null;
    this.resetForm();
    
    if (date) {
      document.getElementById('eventDate').value = this.formatDate(date);
    }
    
    document.getElementById('dayEvents').style.display = 'none';
    document.getElementById('eventForm').style.display = 'block';
    document.getElementById('sidebarTitle').textContent = 'Add Event';
    document.getElementById('deleteEvent').style.display = 'none';
    this.openSidebar();
  }

  showEventDetails(event) {
    this.selectedEvent = event;
    this.populateForm(event);
    
    document.getElementById('dayEvents').style.display = 'none';
    document.getElementById('eventForm').style.display = 'block';
    document.getElementById('sidebarTitle').textContent = 'Edit Event';
    document.getElementById('deleteEvent').style.display = 'inline-block';
    this.openSidebar();
  }

  editEvent(event) {
    this.showEventDetails(event);
  }

  populateForm(event) {
    document.getElementById('eventTitle').value = event.title;
    document.getElementById('eventDate').value = this.formatDate(event.start);
    document.getElementById('eventStartTime').value = this.formatTime(event.start, true);
    document.getElementById('eventEndTime').value = this.formatTime(event.end, true);
    document.getElementById('eventLocation').value = event.location;
    document.getElementById('eventDescription').value = event.description;
    
    // Set priority
    document.querySelectorAll('.priority-option').forEach(opt => opt.classList.remove('selected'));
    document.querySelector(`[data-priority="${event.priority}"]`).classList.add('selected');
  }

  resetForm() {
    document.getElementById('eventForm').reset();
    document.querySelectorAll('.priority-option').forEach(opt => opt.classList.remove('selected'));
    document.querySelector('[data-priority="3"]').classList.add('selected');
  }

  openSidebar() {
    document.getElementById('eventSidebar').classList.add('open');
  }

  closeSidebar() {
    document.getElementById('eventSidebar').classList.remove('open');
    this.selectedEvent = null;
    this.selectedDate = null;
  }

  saveEvent() {
    const formData = new FormData(document.getElementById('eventForm'));
    const selectedPriority = document.querySelector('.priority-option.selected');
    
    const eventData = {
      id: this.selectedEvent ? this.selectedEvent.id : this.generateId(),
      title: formData.get('title'),
      start: new Date(`${formData.get('date')}T${formData.get('startTime')}`),
      end: new Date(`${formData.get('date')}T${formData.get('endTime')}`),
      location: formData.get('location'),
      description: formData.get('description'),
      priority: parseInt(selectedPriority.dataset.priority)
    };

    // Validation
    if (eventData.start >= eventData.end) {
      this.showError('End time must be after start time');
      return;
    }

    if (this.selectedEvent) {
      this.updateEvent(eventData);
    } else {
      this.addEvent(eventData);
    }
  }

  addEvent(eventData) {
    if (this.wsSocket && this.wsSocket.readyState === WebSocket.OPEN) {
      this.wsSocket.send(JSON.stringify({
        type: 'add_event',
        title: eventData.title,
        start_time: eventData.start.toISOString(),
        end_time: eventData.end.toISOString(),
        description: eventData.description,
        location: eventData.location,
        priority: eventData.priority,
        timestamp: new Date().toISOString()
      }));
    } else {
      // Offline mode
      this.events.push(eventData);
      localStorage.setItem('freelaince_calendar', JSON.stringify(this.events));
      this.renderCalendar();
      this.closeSidebar();
      this.showSuccess('Event added (offline)');
    }
  }

  updateEvent(eventData) {
    if (this.wsSocket && this.wsSocket.readyState === WebSocket.OPEN) {
      this.wsSocket.send(JSON.stringify({
        type: 'update_event',
        id: eventData.id,
        title: eventData.title,
        start_time: eventData.start.toISOString(),
        end_time: eventData.end.toISOString(),
        description: eventData.description,
        location: eventData.location,
        priority: eventData.priority,
        timestamp: new Date().toISOString()
      }));
    } else {
      // Offline mode
      const index = this.events.findIndex(e => e.id === eventData.id);
      if (index !== -1) {
        this.events[index] = eventData;
        localStorage.setItem('freelaince_calendar', JSON.stringify(this.events));
        this.renderCalendar();
        this.closeSidebar();
        this.showSuccess('Event updated (offline)');
      }
    }
  }

  deleteEvent(event) {
    if (confirm(`Delete "${event.title}"?`)) {
      this.deleteEventById(event.id);
    }
  }

  deleteSelectedEvent() {
    if (this.selectedEvent && confirm(`Delete "${this.selectedEvent.title}"?`)) {
      this.deleteEventById(this.selectedEvent.id);
    }
  }

  deleteEventById(eventId) {
    if (this.wsSocket && this.wsSocket.readyState === WebSocket.OPEN) {
      this.wsSocket.send(JSON.stringify({
        type: 'delete_event',
        id: eventId,
        timestamp: new Date().toISOString()
      }));
    } else {
      // Offline mode
      this.events = this.events.filter(e => e.id !== eventId);
      localStorage.setItem('freelaince_calendar', JSON.stringify(this.events));
      this.renderCalendar();
      this.closeSidebar();
      this.showSuccess('Event deleted (offline)');
    }
  }

  // Utility functions
  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }

  formatDate(date) {
    return date.toISOString().split('T')[0];
  }

  formatTime(date, forInput = false) {
    if (forInput) {
      return date.toTimeString().slice(0, 5);
    }
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  }

  getEventDuration(event) {
    const duration = (event.end - event.start) / (1000 * 60);
    if (duration < 60) {
      return `${duration}m`;
    }
    const hours = Math.floor(duration / 60);
    const minutes = duration % 60;
    return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
  }

  isSameDay(date1, date2) {
    return date1.toDateString() === date2.toDateString();
  }

  getMonthStart() {
    return new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
  }

  getMonthEnd() {
    return new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
  }

  getWeekStart() {
    const date = new Date(this.currentDate);
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(date.setDate(diff));
  }

  getWeekEnd() {
    const start = this.getWeekStart();
    return new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
  }

  showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    errorContainer.innerHTML = `
      <div class="error">
        <strong>Error:</strong> ${message}
      </div>
    `;
    
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
    
    setTimeout(() => {
      errorContainer.innerHTML = '';
    }, 3000);
  }
}

// Initialize the calendar when the page loads
let calendarManager;
document.addEventListener('DOMContentLoaded', () => {
  calendarManager = new CalendarManager();
  
  // Add refresh functionality
  document.addEventListener('keydown', (e) => {
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
      e.preventDefault();
      window.location.reload();
    }
  });
});