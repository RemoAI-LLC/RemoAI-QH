const { ipcRenderer } = require('electron');

class RemoAIChat {
    constructor() {
        this.messageCount = 0;
        this.isStreaming = false;
        this.currentStreamingMessage = null;
        this.config = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadConfiguration();
        this.updateWelcomeTime();
    }

    initializeElements() {
        // Main elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.charCount = document.getElementById('charCount');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.messageCountElement = document.getElementById('messageCount');
        this.typingIndicator = document.getElementById('typingIndicator');

        // Settings modal elements
        this.settingsModal = document.getElementById('settingsModal');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.closeSettingsBtn = document.getElementById('closeSettingsBtn');
        this.cancelSettingsBtn = document.getElementById('cancelSettingsBtn');
        this.saveSettingsBtn = document.getElementById('saveSettingsBtn');
        this.clearBtn = document.getElementById('clearBtn');

        // Settings form elements
        this.apiKeyInput = document.getElementById('apiKey');
        this.workspaceSlugInput = document.getElementById('workspaceSlug');
        this.apiUrlInput = document.getElementById('apiUrl');
        this.streamingEnabledInput = document.getElementById('streamingEnabled');
    }

    setupEventListeners() {
        // Message input
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Settings modal
        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.closeSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.cancelSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());

        // Clear chat
        this.clearBtn.addEventListener('click', () => this.clearChat());

        // Modal backdrop click
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.closeSettings();
            }
        });

        // IPC listeners
        ipcRenderer.on('chat-stream-chunk', (event, chunk) => {
            this.handleStreamChunk(chunk);
        });
    }

    async loadConfiguration() {
        try {
            const result = await ipcRenderer.invoke('check-config');
            if (result.success) {
                this.config = result.config;
                this.updateStatus('connected', 'Connected');
                this.populateSettingsForm();
            } else {
                this.updateStatus('error', 'Configuration Error');
                this.showNotification('Configuration file not found. Please check your setup.', 'error');
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
            this.updateStatus('error', 'Connection Error');
        }
    }

    populateSettingsForm() {
        if (this.config) {
            this.apiKeyInput.value = this.config.api_key || '';
            this.workspaceSlugInput.value = this.config.workspace_slug || '';
            this.apiUrlInput.value = this.config.model_server_base_url || 'http://localhost:3001/api/v1';
            this.streamingEnabledInput.checked = this.config.stream !== false;
        }
    }

    handleInputChange() {
        const value = this.messageInput.value.trim();
        this.sendButton.disabled = !value || this.isStreaming;
        
        // Update character count
        this.charCount.textContent = this.messageInput.value.length;
        
        // Auto-resize textarea
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!this.sendButton.disabled) {
                this.sendMessage();
            }
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isStreaming) return;

        // Add user message to chat
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.handleInputChange();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            if (this.streamingEnabledInput.checked) {
                await this.sendStreamingMessage(message);
            } else {
                await this.sendRegularMessage(message);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            this.hideTypingIndicator();
        }
    }

    async sendStreamingMessage(message) {
        this.isStreaming = true;
        this.currentStreamingMessage = this.addMessage('assistant', '', true);
        
        try {
            const result = await ipcRenderer.invoke('send-streaming-chat-message', message);
            if (result.success) {
                this.finalizeStreamingMessage();
            } else {
                this.currentStreamingMessage.querySelector('.message-text').textContent = 
                    'Sorry, I encountered an error: ' + result.error;
            }
        } catch (error) {
            this.currentStreamingMessage.querySelector('.message-text').textContent = 
                'Sorry, I encountered an error. Please try again.';
        } finally {
            this.isStreaming = false;
            this.currentStreamingMessage = null;
        }
    }

    async sendRegularMessage(message) {
        try {
            const result = await ipcRenderer.invoke('send-chat-message', message);
            if (result.success) {
                this.addMessage('assistant', result.response);
            } else {
                this.addMessage('assistant', 'Sorry, I encountered an error: ' + result.error);
            }
        } catch (error) {
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        }
    }

    handleStreamChunk(chunk) {
        if (this.currentStreamingMessage) {
            const messageText = this.currentStreamingMessage.querySelector('.message-text');
            messageText.textContent += chunk;
            this.scrollToBottom();
        }
    }

    finalizeStreamingMessage() {
        if (this.currentStreamingMessage) {
            this.currentStreamingMessage.classList.remove('streaming');
            this.addMessageTime(this.currentStreamingMessage);
        }
    }

    addMessage(sender, content, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message new`;
        
        if (isStreaming) {
            messageDiv.classList.add('streaming');
        }

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = content;

        messageContent.appendChild(messageText);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        if (!isStreaming) {
            this.addMessageTime(messageDiv);
        }

        this.messageCount++;
        this.updateMessageCount();

        return messageDiv;
    }

    addMessageTime(messageDiv) {
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date().toLocaleTimeString();
        messageDiv.querySelector('.message-content').appendChild(messageTime);
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateMessageCount() {
        this.messageCountElement.textContent = `${this.messageCount} messages`;
    }

    updateStatus(status, text) {
        this.statusDot.className = `status-dot ${status}`;
        this.statusText.textContent = text;
    }

    updateWelcomeTime() {
        const welcomeTime = document.getElementById('welcomeTime');
        if (welcomeTime) {
            welcomeTime.textContent = new Date().toLocaleTimeString();
        }
    }

    openSettings() {
        this.settingsModal.classList.add('show');
        this.populateSettingsForm();
    }

    closeSettings() {
        this.settingsModal.classList.remove('show');
    }

    async saveSettings() {
        const newConfig = {
            api_key: this.apiKeyInput.value,
            workspace_slug: this.workspaceSlugInput.value,
            model_server_base_url: this.apiUrlInput.value,
            stream: this.streamingEnabledInput.checked,
            stream_timeout: 60
        };

        // Validate configuration
        if (!newConfig.api_key || !newConfig.workspace_slug || !newConfig.model_server_base_url) {
            this.showNotification('Please fill in all required fields.', 'error');
            return;
        }

        try {
            // Here you would typically save the configuration
            // For now, we'll just update the local config
            this.config = newConfig;
            this.closeSettings();
            this.showNotification('Settings saved successfully!', 'success');
            this.updateStatus('connected', 'Connected');
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showNotification('Error saving settings. Please try again.', 'error');
        }
    }

    async clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            try {
                const result = await ipcRenderer.invoke('clear-chat-history');
                if (result.success) {
                    // Clear the chat messages (keep welcome message)
                    const messages = this.chatMessages.querySelectorAll('.message:not(.assistant-message:first-child)');
                    messages.forEach(msg => msg.remove());
                    
                    this.messageCount = 0;
                    this.updateMessageCount();
                    this.showNotification('Chat history cleared.', 'success');
                } else {
                    this.showNotification('Error clearing chat history.', 'error');
                }
            } catch (error) {
                console.error('Error clearing chat:', error);
                this.showNotification('Error clearing chat history.', 'error');
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            animation: 'slideIn 0.3s ease-out',
            maxWidth: '300px',
            wordWrap: 'break-word'
        });

        // Set background color based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            info: '#3b82f6'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(notification);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize the chat application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RemoAIChat();
});
