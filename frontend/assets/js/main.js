/**
 * NyayaAI Frontend - Main JavaScript
 * 
 * This file handles all frontend functionality including:
 * - Theme management
 * - Chat interface with backend integration
 * - File upload handling
 * - Conversation management
 */

// =============================================================================
// CONFIGURATION & CONSTANTS
// =============================================================================

const CONFIG = {
  API_BASE_URL: 'http://localhost:5000/api',
  HEALTH_CHECK_URL: 'http://localhost:5000/health',
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: [
    'application/pdf',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ],
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
};

// =============================================================================
// THEME MANAGEMENT
// =============================================================================

class ThemeManager {
  constructor() {
    this.init();
  }

  init() {
    // Initialize theme from localStorage or system preference
    const saved = localStorage.getItem('theme');
    if (saved) {
      this.setTheme(saved);
    } else {
      const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light');
    }

    // Setup theme toggle button
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const isDark = document.documentElement.classList.contains('dark');
        this.setTheme(isDark ? 'light' : 'dark');
      });
    }
  }

  setTheme(theme) {
  const root = document.documentElement;
    const themeBtn = document.getElementById('themeToggle');
    
    if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
    
    localStorage.setItem('theme', theme);
    
    if (themeBtn) {
      const icon = themeBtn.querySelector('span:first-child');
      if (icon) {
        icon.textContent = theme === 'dark' ? '🌞' : '🌙';
      }
    }
  }
}

// =============================================================================
// API CLIENT
// =============================================================================

class APIClient {
  constructor() {
    this.baseURL = CONFIG.API_BASE_URL;
    this.healthURL = CONFIG.HEALTH_CHECK_URL;
  }

  async checkHealth() {
    try {
      console.log('🔍 Checking backend health at:', this.healthURL);
      const response = await fetch(this.healthURL, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors'
      });
      
      console.log('📊 Health check response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Backend is healthy:', data);
      }
      return response.ok;
    } catch (error) {
      console.error('❌ Health check failed:', error);
      return false;
    }
  }

  async sendMessage(query, sessionId = null, context = null) {
    const payload = {
      query: query,
      session_id: sessionId,
      context: context
    };

    return this.makeRequest('/chat', payload);
  }

  async intelligentChat(query, sessionId = null, context = null) {
    const payload = {
      query: query,
      session_id: sessionId,
      context: context
    };

    return this.makeRequest('/chat/intelligent', payload);
  }

  async forceSearchChat(query, sessionId = null, context = null) {
    const payload = {
      query: query,
      session_id: sessionId,
      context: context
    };

    return this.makeRequest('/chat/force-search', payload);
  }

  async search(query, searchType = 'synthesized', maxResults = null, context = null) {
    const payload = {
      query: query,
      search_type: searchType,
      max_results: maxResults,
      context: context
    };

    return this.makeRequest('/search', payload);
  }

  async clearMemory(sessionId = null) {
    const payload = {
      action: 'clear',
      session_id: sessionId
    };

    return this.makeRequest('/chat/memory', payload);
  }

  async uploadDocument(file) {
    const url = this.baseURL + '/chat/upload';
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        // Let the browser set multipart/form-data boundary
        mode: 'cors'
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error || 'Upload failed');
      }
      return data.data; // { filename, text, characters, truncated }
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  async getMemoryHistory(sessionId = null) {
    const payload = {
      action: 'get_history',
      session_id: sessionId
    };

    return this.makeRequest('/chat/memory', payload);
  }

  async makeRequest(endpoint, payload, retries = CONFIG.RETRY_ATTEMPTS) {
    const url = this.baseURL + endpoint;
    
    try {
      console.log(`🚀 Making API request to: ${url}`, payload);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        mode: 'cors'
      });

      console.log(`📊 API response status: ${response.status} for ${endpoint}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API error response:`, errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`✅ API success response for ${endpoint}:`, data);
      
      if (!data.success) {
        throw new Error(data.error || 'API request failed');
      }

      return data.data;
    } catch (error) {
      console.error(`❌ API request failed (${endpoint}):`, error);
      
      if (retries > 0 && this.isRetryableError(error)) {
        console.log(`🔄 Retrying request... (${CONFIG.RETRY_ATTEMPTS - retries + 1}/${CONFIG.RETRY_ATTEMPTS})`);
        await this.delay(CONFIG.RETRY_DELAY);
        return this.makeRequest(endpoint, payload, retries - 1);
      }
      
      throw error;
    }
  }

  isRetryableError(error) {
    // Retry on network errors or 5xx status codes
    return error.name === 'TypeError' || 
           (error.message && error.message.includes('5'));
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// =============================================================================
// CONVERSATION MANAGER
// =============================================================================

class ConversationManager {
  constructor() {
    this.storageKey = 'nyaya_threads';
    this.activeThreadKey = 'nyaya_active_thread';
    this.init();
  }

  init() {
    // Initialize default thread if none exists
    if (!this.getActiveThreadId()) {
      this.createThread('New Chat');
    }
    this.renderHistory();
  }

  loadThreads() {
    try {
      return JSON.parse(localStorage.getItem(this.storageKey) || '[]');
    } catch (error) {
      console.error('Failed to load threads:', error);
      return [];
    }
  }

  saveThreads(threads) {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(threads));
    } catch (error) {
      console.error('Failed to save threads:', error);
    }
  }

  getActiveThreadId() {
    return localStorage.getItem(this.activeThreadKey);
  }

  setActiveThreadId(id) {
    localStorage.setItem(this.activeThreadKey, id);
    // Notify listeners (e.g., ChatInterface) that the active thread changed
    try {
      window.dispatchEvent(new CustomEvent('nyaya:active-thread-changed', { detail: { id } }));
    } catch (e) {
      console.warn('Failed to dispatch active-thread-changed event', e);
    }
  }

  createThread(title) {
    const id = 't_' + Date.now();
    const thread = {
      id: id,
      title: title || 'New Chat',
      messages: [],
      createdAt: new Date().toISOString()
    };
    
    const threads = this.loadThreads();
    threads.unshift(thread);
    this.saveThreads(threads);
    this.setActiveThreadId(id);
    return thread;
  }

  getActiveThread() {
    const id = this.getActiveThreadId();
    if (!id) return null;
    return this.loadThreads().find(t => t.id === id) || null;
  }

  updateActiveThread(updater) {
    const threads = this.loadThreads();
    const id = this.getActiveThreadId();
    const idx = threads.findIndex(t => t.id === id);
    
    if (idx >= 0) {
      updater(threads[idx]);
      this.saveThreads(threads);
    }
  }

  deleteThread(threadId) {
    const threads = this.loadThreads().filter(t => t.id !== threadId);
    this.saveThreads(threads);
    
    if (threadId === this.getActiveThreadId()) {
      if (threads.length > 0) {
        this.setActiveThreadId(threads[0].id);
      } else {
        this.createThread('New Chat');
      }
    }
  }

  renderHistory() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;

    const threads = this.loadThreads();
    historyList.innerHTML = '';

    threads.forEach((thread) => {
      const li = document.createElement('li');
      const isActive = thread.id === this.getActiveThreadId();
      
      li.className = `rounded-lg border border-slate-200 dark:border-slate-800 p-2 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer transition-colors ${
        isActive ? 'ring-1 ring-royal/30 bg-royal/5' : ''
      }`;
      
      li.innerHTML = `
        <div class="font-medium text-sm truncate" title="${thread.title}">${thread.title}</div>
        <div class="text-xs text-slate-500 mt-1">${thread.messages.length} messages</div>
      `;
      
      li.addEventListener('click', () => {
        this.setActiveThreadId(thread.id);
        this.renderHistory();
      });
      
      historyList.appendChild(li);
    });
  }
}

// =============================================================================
// CHAT INTERFACE
// =============================================================================

class ChatInterface {
  constructor(apiClient, conversationManager) {
    this.apiClient = apiClient;
    this.conversationManager = conversationManager;
    this.isLoading = false;
    this.searchEnabled = false; // Track search toggle state
    this.attachedContext = null; // { filename, text }
    this.init();
  }

  autoResizeTextarea(textareaEl) {
    if (!textareaEl) return;
    textareaEl.style.height = 'auto';
    const maxHeight = parseInt(getComputedStyle(textareaEl).maxHeight || '0', 10);
    const newHeight = Math.min(textareaEl.scrollHeight, maxHeight || textareaEl.scrollHeight);
    textareaEl.style.height = newHeight + 'px';
  }

  updateInputCounter(textareaEl) {
    const counter = document.getElementById('inputCounter');
    if (!counter || !textareaEl) return;
    const length = textareaEl.value.length;
    counter.textContent = length > 0 ? `${length}` : '';
  }

  init() {
    this.setupEventListeners();
    this.renderMessages();
    this.checkBackendConnection();
    // Re-render messages when active thread changes from sidebar clicks
    window.addEventListener('nyaya:active-thread-changed', () => {
      this.renderMessages();
      this.clearError();
    });
  }

  setupEventListeners() {
    // Chat form submission
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    
    if (chatForm && chatInput) {
      chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (message && !this.isLoading) {
          chatInput.value = '';
          this.autoResizeTextarea(chatInput);
          this.sendMessage(message);
        }
      });

      // Allow Enter key to send message
      chatInput.addEventListener('keydown', (e) => {
        // Enter to send, Shift+Enter for new line
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          chatForm.dispatchEvent(new Event('submit'));
        }
      });

      // Auto-resize textarea on input and update counter
      chatInput.addEventListener('input', () => {
        this.autoResizeTextarea(chatInput);
        this.updateInputCounter(chatInput);
      });
      // Initialize height and counter
      this.autoResizeTextarea(chatInput);
      this.updateInputCounter(chatInput);
    }

    // New chat button
    const newChatBtn = document.getElementById('newChat');
  if (newChatBtn) {
    newChatBtn.addEventListener('click', async () => {
        const activeThread = this.conversationManager.getActiveThread();
        if (activeThread) {
          // Clear backend memory for the current session
          try {
            await this.apiClient.clearMemory(activeThread.id);
          } catch (error) {
            console.warn('Failed to clear backend memory:', error);
          }
        }
        
        this.conversationManager.createThread('New Chat');
        this.conversationManager.renderHistory();
        this.renderMessages();
        this.clearError();
      });
    }

    // Rename chat button
    const renameChatBtn = document.getElementById('renameChat');
  if (renameChatBtn) {
    renameChatBtn.addEventListener('click', () => {
        this.renameActiveThread();
    });
  }

    // Delete chat button
    const deleteChatBtn = document.getElementById('deleteChat');
    if (deleteChatBtn) {
      deleteChatBtn.addEventListener('click', () => {
        this.deleteActiveThread();
      });
    }

    // Test connection button
    const testConnectionBtn = document.getElementById('testConnection');
    if (testConnectionBtn) {
      testConnectionBtn.addEventListener('click', () => {
        this.testConnection();
      });
    }

    // Search toggle button
    const searchToggle = document.getElementById('searchToggle');
    if (searchToggle) {
      searchToggle.addEventListener('click', () => {
        if (this.attachedContext) {
          // Prevent enabling web search when a document is attached
          return;
        }
        this.toggleSearch();
      });
      console.log('✅ Search toggle initialized');
    } else {
      console.warn('⚠️ Search toggle button not found');
    }

    // Listen for document attach/remove events from FileUploadHandler
    window.addEventListener('nyaya:doc-attached', (e) => {
      this.onDocumentAttached(e.detail);
    });
    window.addEventListener('nyaya:doc-removed', () => {
      this.onDocumentRemoved();
    });
  }

  async checkBackendConnection() {
    console.log('🔍 Checking backend connection...');
    const isHealthy = await this.apiClient.checkHealth();
    if (!isHealthy) {
      console.error('❌ Backend health check failed');
      this.showError('⚠️ Backend server is not responding. Please make sure the server is running on port 5000.');
    } else {
      console.log('✅ Backend connection successful');
      this.clearError();
    }
  }

  async testConnection() {
    console.log('🧪 Testing backend connection...');
    this.showError('Testing connection...');
    
    try {
      // Test health endpoint
      const isHealthy = await this.apiClient.checkHealth();
      
      if (isHealthy) {
        // Test a simple chat message
        const response = await this.apiClient.sendMessage('Hello, are you working?');
        this.showError('✅ Connection test successful! Backend is responding correctly.');
        console.log('✅ Connection test successful:', response);
        
        // Clear the success message after 3 seconds
        setTimeout(() => {
          this.clearError();
        }, 3000);
      } else {
        this.showError('❌ Health check failed. Backend server is not responding.');
      }
    } catch (error) {
      this.showError(`❌ Connection test failed: ${error.message}`);
      console.error('❌ Connection test failed:', error);
    }
  }

  async sendMessage(message) {
    if (this.isLoading) return;
    
    this.isLoading = true;
    this.clearError();

    // Add user message to UI
    this.addMessage('user', message);
    
    // Show loading indicator
    const loadingElement = this.showLoading();

    try {
      const activeThread = this.conversationManager.getActiveThread();
      const sessionId = activeThread ? activeThread.id : null;

      // Send message to backend using appropriate method based on search toggle
      let response;
      if (this.attachedContext) {
        // When a document is attached, always use context-aware chat and disable web search
        response = await this.apiClient.sendMessage(message, sessionId, this.attachedContext.text);
      } else if (this.searchEnabled) {
        response = await this.apiClient.forceSearchChat(message, sessionId);
      } else {
        response = await this.apiClient.intelligentChat(message, sessionId);
      }
      
      // Remove loading indicator
      loadingElement.remove();
      
      // Add AI response to UI with search information
      const messageOptions = {
        sessionId: response.session_id,
        model: response.model,
        timestamp: response.timestamp
      };

      if (this.attachedContext) {
        messageOptions.searchUsed = false;
        messageOptions.searchReason = 'document_context';
      }

      // Add search information if available
      if (response.search_decision) {
        messageOptions.searchUsed = response.search_used;
        messageOptions.searchReason = response.search_decision.reason;
        messageOptions.enhanced = response.enhanced;
        messageOptions.sources = response.sources || [];
        messageOptions.searchMethod = response.search_method;
      }

      this.addMessage('assistant', response.response, messageOptions);

      // Update conversation thread
      this.updateConversationThread(message, response.response, response);

    } catch (error) {
      loadingElement.remove();
      this.handleError(error);
    } finally {
      this.isLoading = false;
    }
  }

  addMessage(role, content, metadata = {}) {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;

    const messageElement = this.createMessageElement(role, content, metadata);
    chatContainer.appendChild(messageElement);
    this.scrollToBottom(chatContainer);
  }

  createMessageElement(role, content, metadata = {}) {
    const wrapper = document.createElement('div');
    wrapper.className = `p-4 rounded-2xl border border-slate-200 dark:border-slate-800 flex items-start gap-3 ${
      role === 'user' 
        ? 'bg-slate-50 dark:bg-white/5 ml-8' 
        : 'bg-white dark:bg-white/5 mr-8'
    }`;

    // Avatar
    const avatar = document.createElement('div');
    avatar.className = `w-8 h-8 rounded-full grid place-items-center text-sm font-semibold ${
      role === 'user' 
        ? 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300' 
        : 'bg-gradient-to-br from-royal to-blue-800 text-white'
    }`;
    avatar.textContent = role === 'user' ? 'U' : 'AI';

    // Content container
    const contentContainer = document.createElement('div');
    contentContainer.className = 'flex-1 min-w-0';

    // Label
    const label = document.createElement('div');
    label.className = `text-xs font-medium ${
      role === 'user' 
        ? 'text-slate-500 dark:text-slate-400' 
        : 'text-royal dark:text-blue-300'
    }`;
    label.textContent = role === 'user' ? 'You' : 'NyayaAI';

    // Message body
    const body = document.createElement('div');
    body.className = 'mt-1 whitespace-pre-wrap break-words';
    body.textContent = content;

    // Search information display for assistant messages
    if (role === 'assistant' && metadata.searchUsed !== undefined) {
      const searchInfo = document.createElement('div');
      searchInfo.className = 'mt-2 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2';
      
      if (metadata.searchUsed) {
        const isForced = metadata.searchReason === 'user_requested';
        searchInfo.innerHTML = `
          <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full ${isForced ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300' : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'}">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path>
            </svg>
            ${isForced ? 'Forced web search' : 'Enhanced with web search'}
          </span>
          <span class="text-slate-400 dark:text-slate-500">(${metadata.searchReason})</span>
        `;
      } else {
        searchInfo.innerHTML = `
          <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
            </svg>
            AI knowledge only
          </span>
          <span class="text-slate-400 dark:text-slate-500">(${metadata.searchReason})</span>
        `;
      }
      
      contentContainer.appendChild(searchInfo);
      
      // Display sources if available
      if (metadata.sources && metadata.sources.length > 0) {
        const sourcesContainer = document.createElement('div');
        sourcesContainer.className = 'mt-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700';
        
        const sourcesTitle = document.createElement('div');
        sourcesTitle.className = 'text-xs font-medium text-slate-600 dark:text-slate-400 mb-2';
        sourcesTitle.textContent = 'Sources consulted:';
        sourcesContainer.appendChild(sourcesTitle);
        
        const sourcesList = document.createElement('div');
        sourcesList.className = 'space-y-1';
        
        metadata.sources.forEach((source, index) => {
          const sourceItem = document.createElement('div');
          sourceItem.className = 'flex items-start gap-2 text-xs';
          
          const sourceLink = document.createElement('a');
          sourceLink.href = source.url;
          sourceLink.target = '_blank';
          sourceLink.rel = 'noopener noreferrer';
          sourceLink.className = 'text-blue-600 dark:text-blue-400 hover:underline truncate flex-1';
          sourceLink.textContent = source.title || source.url;
          sourceLink.title = source.url;
          
          const sourceIcon = document.createElement('svg');
          sourceIcon.className = 'w-3 h-3 text-slate-400 mt-0.5 flex-shrink-0';
          sourceIcon.fill = 'none';
          sourceIcon.stroke = 'currentColor';
          sourceIcon.viewBox = '0 0 24 24';
          sourceIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>';
          
          sourceItem.appendChild(sourceIcon);
          sourceItem.appendChild(sourceLink);
          sourcesList.appendChild(sourceItem);
        });
        
        sourcesContainer.appendChild(sourcesList);
        contentContainer.appendChild(sourcesContainer);
      }
    }

    contentContainer.appendChild(label);
    contentContainer.appendChild(body);
    wrapper.appendChild(avatar);
    wrapper.appendChild(contentContainer);

    return wrapper;
  }

  showLoading() {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return null;

    const loadingElement = document.createElement('div');
    loadingElement.className = 'p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-white/5 flex items-start gap-3 mr-8';
    loadingElement.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-royal to-blue-800 text-white grid place-items-center text-sm font-semibold">AI</div>
      <div class="flex-1">
        <div class="text-xs font-medium text-royal dark:text-blue-300 mb-1">NyayaAI</div>
        <div class="flex items-center gap-2 text-slate-500">
          <span class="h-2 w-2 rounded-full bg-slate-400 animate-bounce"></span>
          <span class="h-2 w-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 120ms;"></span>
          <span class="h-2 w-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 240ms;"></span>
          <span class="ml-2">Thinking...</span>
        </div>
      </div>
    `;

    chatContainer.appendChild(loadingElement);
    this.scrollToBottom(chatContainer);
    return loadingElement;
  }

  updateConversationThread(userMessage, aiResponse, responseData) {
    this.conversationManager.updateActiveThread(thread => {
      // Update thread title if it's the first message
      if (thread.messages.length === 0) {
        thread.title = userMessage.slice(0, 40) + (userMessage.length > 40 ? '…' : '');
      }

      // Add messages
      thread.messages.push({ 
        role: 'user', 
        content: userMessage,
        timestamp: new Date().toISOString()
      });
      
      thread.messages.push({ 
        role: 'assistant', 
        content: aiResponse,
        metadata: responseData,
        timestamp: new Date().toISOString()
      });

      thread.updatedAt = new Date().toISOString();
    });

    this.conversationManager.renderHistory();
  }

  renderMessages() {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;

    const activeThread = this.conversationManager.getActiveThread();
    
    chatContainer.innerHTML = '';
    
    if (!activeThread || activeThread.messages.length === 0) {
      chatContainer.innerHTML = `
        <div class="text-center py-8">
          <div class="text-4xl mb-4">⚖️</div>
          <div class="text-lg font-medium text-slate-700 dark:text-slate-300 mb-2">Welcome to NyayaAI</div>
          <div class="text-sm text-slate-500 dark:text-slate-400">
            Start a conversation by typing your legal question below.
          </div>
        </div>
      `;
      return;
    }

    activeThread.messages.forEach(message => {
      const messageElement = this.createMessageElement(
        message.role, 
        message.content, 
        message.metadata || {}
      );
      chatContainer.appendChild(messageElement);
    });

    this.scrollToBottom(chatContainer);
  }

  scrollToBottom(container) {
    setTimeout(() => {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth'
      });
    }, 100);
  }

  toggleSearch() {
    this.searchEnabled = !this.searchEnabled;
    const searchToggle = document.getElementById('searchToggle');
    
    if (searchToggle) {
      if (this.searchEnabled) {
        // Enable search - make it more prominent
        searchToggle.classList.add('text-royal', 'dark:text-blue-300', 'bg-royal/20', 'dark:bg-blue-900/30', 'ring-2', 'ring-royal/30', 'dark:ring-blue-400/30');
        searchToggle.classList.remove('text-slate-400', 'hover:bg-slate-100', 'dark:hover:bg-slate-700');
        searchToggle.title = 'Web search enabled - Click to disable';
        
        // Add a subtle animation
        searchToggle.style.transform = 'scale(1.1)';
        setTimeout(() => {
          searchToggle.style.transform = 'scale(1)';
        }, 200);
      } else {
        // Disable search - return to normal state
        searchToggle.classList.remove('text-royal', 'dark:text-blue-300', 'bg-royal/20', 'dark:bg-blue-900/30', 'ring-2', 'ring-royal/30', 'dark:ring-blue-400/30');
        searchToggle.classList.add('text-slate-400', 'hover:bg-slate-100', 'dark:hover:bg-slate-700');
        searchToggle.title = 'Web search disabled - Click to enable';
        
        // Reset any transform
        searchToggle.style.transform = 'scale(1)';
      }
    }
    
    console.log(`Search ${this.searchEnabled ? 'enabled' : 'disabled'}`);
  }

  onDocumentAttached(detail) {
    // detail: { filename, text }
    this.attachedContext = { filename: detail.filename, text: detail.text };
    // Ensure web search is visually disabled
    if (this.searchEnabled) {
      this.searchEnabled = false;
      const searchToggle = document.getElementById('searchToggle');
      if (searchToggle) {
        searchToggle.classList.remove('text-royal', 'dark:text-blue-300', 'bg-royal/20', 'dark:bg-blue-900/30', 'ring-2', 'ring-royal/30', 'dark:ring-blue-400/30');
        searchToggle.classList.add('text-slate-400', 'hover:bg-slate-100', 'dark:hover:bg-slate-700');
        searchToggle.title = 'Web search disabled while a document is attached';
      }
    }
  }

  onDocumentRemoved() {
    this.attachedContext = null;
    const searchToggle = document.getElementById('searchToggle');
    if (searchToggle) {
      searchToggle.title = 'Web search disabled - Click to enable';
    }
  }

  renameActiveThread() {
    const activeThread = this.conversationManager.getActiveThread();
    if (!activeThread) return;

    const newTitle = prompt('Rename chat:', activeThread.title);
    if (newTitle && newTitle.trim()) {
      this.conversationManager.updateActiveThread(thread => {
        thread.title = newTitle.trim();
        thread.updatedAt = new Date().toISOString();
      });
      this.conversationManager.renderHistory();
    }
  }

  async deleteActiveThread() {
    const activeThread = this.conversationManager.getActiveThread();
    if (!activeThread) return;

    if (confirm(`Delete "${activeThread.title}"? This action cannot be undone.`)) {
      // Clear backend memory for this thread
      try {
        await this.apiClient.clearMemory(activeThread.id);
      } catch (error) {
        console.warn('Failed to clear backend memory:', error);
      }
      
      this.conversationManager.deleteThread(activeThread.id);
      this.conversationManager.renderHistory();
      this.renderMessages();
    }
  }

  showError(message) {
    const chatError = document.getElementById('chatError');
    if (chatError) {
      chatError.textContent = message;
      chatError.classList.remove('hidden');
    }
  }

  clearError() {
    const chatError = document.getElementById('chatError');
    if (chatError) {
      chatError.classList.add('hidden');
    }
  }

  handleError(error) {
    console.error('Chat error:', error);
    
    let errorMessage = 'An error occurred. Please try again.';
    
    if (error.message.includes('Failed to fetch') || error.message.includes('Network')) {
      errorMessage = 'Unable to connect to the server. Please make sure the backend is running.';
    } else if (error.message.includes('HTTP')) {
      errorMessage = 'Server error occurred. Please try again later.';
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    this.showError(errorMessage);
  }
}

// =============================================================================
// FILE UPLOAD HANDLER
// =============================================================================

class FileUploadHandler {
  constructor() {
    this.init();
  }

  init() {
    const fileUpload = document.getElementById('fileUpload');
    const fileUploadBtn = document.getElementById('fileUploadBtn');
    const removeFile = document.getElementById('removeFile');
    const uploadedFile = document.getElementById('uploadedFile');

    if (fileUpload) {
      fileUpload.addEventListener('change', (e) => this.handleFileUpload(e));
    }

    if (fileUploadBtn) {
      fileUploadBtn.addEventListener('click', () => {
        fileUpload.click();
      });
    }

    if (removeFile) {
      removeFile.addEventListener('click', () => this.removeFile());
    }
  }

  async handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file size
    if (file.size > CONFIG.MAX_FILE_SIZE) {
      this.showUploadStatus('File size must be less than 10MB', 'error');
      return;
    }

    // Validate file type
    if (!CONFIG.ALLOWED_FILE_TYPES.includes(file.type)) {
      this.showUploadStatus('Please upload PDF, TXT, DOC, or DOCX files only', 'error');
      return;
    }

    this.showUploadStatus('Uploading and analyzing document...', 'uploading');

    try {
      // Note: Document upload endpoint is not implemented in the current backend
      // This is a placeholder for future implementation
      await this.uploadDocument(file);
      
    } catch (error) {
      console.error('File upload error:', error);
      this.showUploadStatus('Upload failed. Please try again.', 'error');
    }
  }

  async uploadDocument(file) {
    try {
      const api = new APIClient();
      const result = await api.uploadDocument(file);
      // Notify chat interface
      window.dispatchEvent(new CustomEvent('nyaya:doc-attached', { detail: { filename: result.filename, text: result.text } }));
      this.showUploadStatus('Document added. Web search disabled while attached.', 'success');
      this.showUploadedFile(result.filename);
    } catch (error) {
      this.showUploadStatus('Upload failed. Please try again.', 'error');
      throw error;
    }
  }

  showUploadedFile(filename) {
    const uploadedFile = document.getElementById('uploadedFile');
    const uploadedFileName = document.getElementById('uploadedFileName');
    
    if (uploadedFile && uploadedFileName) {
      uploadedFileName.textContent = filename;
        uploadedFile.classList.remove('hidden');
    }
  }

  removeFile() {
    const fileUpload = document.getElementById('fileUpload');
    const uploadedFile = document.getElementById('uploadedFile');
    const uploadStatus = document.getElementById('uploadStatus');
    
    if (fileUpload) fileUpload.value = '';
    if (uploadedFile) uploadedFile.classList.add('hidden');
    if (uploadStatus) uploadStatus.classList.add('hidden');
    // Notify chat interface
    window.dispatchEvent(new CustomEvent('nyaya:doc-removed'));
  }

  showUploadStatus(message, type) {
    const uploadStatus = document.getElementById('uploadStatus');
    if (!uploadStatus) return;
    
    uploadStatus.classList.remove('hidden');
    uploadStatus.textContent = message;
    
    // Remove existing classes
    uploadStatus.classList.remove('text-green-600', 'text-red-600', 'text-blue-600');
    
    // Add appropriate class
    if (type === 'success') {
      uploadStatus.classList.add('text-green-600');
    } else if (type === 'error') {
      uploadStatus.classList.add('text-red-600');
    } else if (type === 'uploading') {
      uploadStatus.classList.add('text-blue-600');
    }
    
    // Auto-hide success messages
    if (type === 'success') {
      setTimeout(() => {
        uploadStatus.classList.add('hidden');
      }, 3000);
    }
  }
}

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Initialize theme manager
  new ThemeManager();
  
  // Initialize API client
  const apiClient = new APIClient();
  
  // Initialize conversation manager
  const conversationManager = new ConversationManager();
  
  // Initialize chat interface
  const chatInterface = new ChatInterface(apiClient, conversationManager);
  
  // Initialize file upload handler
  const fileUploadHandler = new FileUploadHandler();
  
  // Handle logo navigation
  document.querySelectorAll('a.logo-link').forEach((el) => {
    el.addEventListener('click', (e) => {
      const isHome = /(^|\/)index\.html$/.test(location.pathname) || /\/frontend\/?$/.test(location.pathname) || location.pathname === '/';
      if (isHome) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  });

  // Contact form handling (if exists)
  const contactForm = document.getElementById('contactForm');
  const contactStatus = document.getElementById('contactStatus');
  if (contactForm && contactStatus) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
        contactStatus.textContent = 'Thanks! We\'ll get back to you soon.';
        contactStatus.className = 'text-sm text-green-600 mt-2';
      contactForm.reset();
    });
  }

  console.log('✅ NyayaAI Frontend initialized successfully');
});
