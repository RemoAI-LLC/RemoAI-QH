// const { ipcRenderer } = require("electron"); // No longer needed - using unified API

class RemoAIChat {
  constructor() {
    this.messageCount = 0;
    this.isStreaming = false;
    this.currentStreamingMessage = null;
    this.config = null;
    this.isRecording = false;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.ttsEnabled = true; // TTS is enabled by default

    this.initializeElements();
    this.setupEventListeners();
    this.loadConfiguration();
    this.updateWelcomeTime();
    this.initializeTTS();
  }

  initializeElements() {
    // Main elements
    this.chatMessages = document.getElementById("conversation-messages");
    this.messageInput = document.getElementById("text-input");
    this.sendButton = document.getElementById("send-btn");
    this.charCount = document.getElementById("charCount");
    this.statusDot = document.getElementById("statusDot");
    this.statusText = document.getElementById("statusText");
    this.messageCountElement = document.getElementById("messageCount");
    this.typingIndicator = document.getElementById("typingIndicator");

    // Settings modal elements
    this.settingsModal = document.getElementById("settingsModal");
    this.settingsBtn = document.getElementById("settingsBtn");
    this.closeSettingsBtn = document.getElementById("closeSettingsBtn");
    this.cancelSettingsBtn = document.getElementById("cancelSettingsBtn");
    this.saveSettingsBtn = document.getElementById("saveSettingsBtn");
    this.clearBtn = document.getElementById("clearBtn");

    // Settings form elements
    this.apiKeyInput = document.getElementById("apiKey");
    this.workspaceSlugInput = document.getElementById("workspaceSlug");
    this.apiUrlInput = document.getElementById("apiUrl");
    this.streamingEnabledInput = document.getElementById("streamingEnabled");

    // Voice input elements
    this.voiceBtn = document.getElementById("mic-btn");
    this.ttsBtn = document.getElementById("speaker-btn");
  }

  setupEventListeners() {
    // Message input
    if (this.messageInput) {
      this.messageInput.addEventListener("input", () => this.handleInputChange());
      this.messageInput.addEventListener("keydown", (e) => this.handleKeyDown(e));
    }
    
    if (this.sendButton) {
      this.sendButton.addEventListener("click", () => this.sendMessage());
    }

    // Settings modal (only if elements exist)
    if (this.settingsBtn) {
      this.settingsBtn.addEventListener("click", () => this.openSettings());
    }
    if (this.closeSettingsBtn) {
      this.closeSettingsBtn.addEventListener("click", () => this.closeSettings());
    }
    if (this.cancelSettingsBtn) {
      this.cancelSettingsBtn.addEventListener("click", () => this.closeSettings());
    }
    if (this.saveSettingsBtn) {
      this.saveSettingsBtn.addEventListener("click", () => this.saveSettings());
    }

    // Clear chat
    if (this.clearBtn) {
      this.clearBtn.addEventListener("click", () => this.clearChat());
    }

    // Voice input
    if (this.voiceBtn) {
      this.voiceBtn.addEventListener("click", () => this.toggleVoiceRecording());
    }
    
    // TTS toggle
    if (this.ttsBtn) {
      this.ttsBtn.addEventListener("click", () => this.toggleTTS());
    }

    // Modal backdrop click
    if (this.settingsModal) {
      this.settingsModal.addEventListener("click", (e) => {
        if (e.target === this.settingsModal) {
          this.closeSettings();
        }
      });
    }

    // Close button
    const closeBtn = document.getElementById("close-btn");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        // Close the application
        if (window.electronAPI) {
          window.electronAPI.closeApp();
        } else {
          window.close();
        }
      });
    }

    // IPC listeners removed - using unified API instead
  }

  async loadConfiguration() {
    try {
      // Check if unified API is available
      const response = await fetch("http://localhost:8000/health");
      if (response.ok) {
        const result = await response.json();
        this.config = {
          api_key: "configured",
          workspace_slug: "configured",
          model_server_base_url: "http://localhost:8000",
          stream: true,
        };
        this.updateStatus("connected", "Connected to Unified API");
        this.populateSettingsForm();
      } else {
        this.updateStatus("error", "API Server Not Running");
        this.showNotification(
          "Unified API server not running. Please start it first.",
          "error"
        );
      }
    } catch (error) {
      console.error("Error loading configuration:", error);
      this.updateStatus("error", "Connection Error");
      this.showNotification(
        "Cannot connect to API server. Make sure it's running on port 5001.",
        "error"
      );
    }
  }

  populateSettingsForm() {
    if (this.config) {
      this.apiKeyInput.value = this.config.api_key || "";
      this.workspaceSlugInput.value = this.config.workspace_slug || "";
      this.apiUrlInput.value =
        this.config.model_server_base_url || "http://localhost:3001/api/v1";
      this.streamingEnabledInput.checked = this.config.stream !== false;
    }
  }

  handleInputChange() {
    const value = this.messageInput.value.trim();
    if (this.sendButton) {
      this.sendButton.disabled = !value || this.isStreaming;
    }

    // Update character count if element exists
    if (this.charCount) {
      this.charCount.textContent = this.messageInput.value.length;
    }

    // Auto-resize textarea (if it's a textarea)
    if (this.messageInput.tagName === 'TEXTAREA') {
      this.messageInput.style.height = "auto";
      this.messageInput.style.height =
        Math.min(this.messageInput.scrollHeight, 120) + "px";
    }
  }

  handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (this.sendButton && !this.sendButton.disabled) {
        this.sendMessage();
      }
    }
  }

  async sendMessage() {
    const message = this.messageInput.value.trim();
    if (!message || this.isStreaming) return;

    // Add user message to chat
    this.addMessage("user", message);
    this.messageInput.value = "";
    this.handleInputChange();

    // Show typing indicator
    this.showTypingIndicator();

    try {
      // Default to streaming for text messages
      await this.sendStreamingMessage(message);
    } catch (error) {
      console.error("Error sending message:", error);
      this.addMessage(
        "assistant",
        "Sorry, I encountered an error. Please try again."
      );
    } finally {
      this.hideTypingIndicator();
    }
  }

  async sendStreamingMessage(message) {
    this.isStreaming = true;
    this.currentStreamingMessage = this.addMessage("assistant", "", true);

    try {
      // Use unified API instead of IPC
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        // Display the complete response
        this.currentStreamingMessage.querySelector(
          ".message-content"
        ).textContent = result.message;
        this.finalizeStreamingMessage();
      } else {
        this.currentStreamingMessage.querySelector(
          ".message-content"
        ).textContent = "Sorry, I encountered an error: " + result.error;
      }
    } catch (error) {
      console.error("Error sending message:", error);
      this.currentStreamingMessage.querySelector(".message-content").textContent =
        "Sorry, I encountered an error. Please try again.";
    } finally {
      this.isStreaming = false;
      this.currentStreamingMessage = null;
    }
  }

  async sendRegularMessage(message) {
    try {
      // Use unified API instead of IPC
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        this.addMessage("assistant", result.message);
      } else {
        this.addMessage(
          "assistant",
          "Sorry, I encountered an error: " + result.error
        );
      }
    } catch (error) {
      console.error("Error sending message:", error);
      this.addMessage(
        "assistant",
        "Sorry, I encountered an error. Please try again."
      );
    }
  }

  handleStreamChunk(chunk) {
    if (this.currentStreamingMessage) {
      const messageContent =
        this.currentStreamingMessage.querySelector(".message-content");
      messageContent.textContent += chunk;
      this.scrollToBottom();
    }
  }

  finalizeStreamingMessage() {
    if (this.currentStreamingMessage) {
      this.currentStreamingMessage.classList.remove("streaming");
      this.addMessageTime(this.currentStreamingMessage);
    }
  }

  addMessage(sender, content, isStreaming = false) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    const messageContent = document.createElement("div");
    messageContent.className = "message-content";
    messageContent.textContent = content;

    messageDiv.appendChild(messageContent);

    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();

    this.messageCount++;
    this.updateMessageCount();

    return messageDiv;
  }

  addMessageTime(messageDiv) {
    const messageTime = document.createElement("div");
    messageTime.className = "message-time";
    messageTime.textContent = new Date().toLocaleTimeString();
    messageDiv.querySelector(".message-content").appendChild(messageTime);
  }

  showTypingIndicator() {
    if (this.typingIndicator) {
      this.typingIndicator.style.display = "flex";
      this.scrollToBottom();
    }
  }

  hideTypingIndicator() {
    if (this.typingIndicator) {
      this.typingIndicator.style.display = "none";
    }
  }

  scrollToBottom() {
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }

  updateMessageCount() {
    if (this.messageCountElement) {
      this.messageCountElement.textContent = `${this.messageCount} messages`;
    }
  }

  updateStatus(status, text) {
    if (this.statusDot) {
      this.statusDot.className = `status-dot ${status}`;
    }
    if (this.statusText) {
      this.statusText.textContent = text;
    }
  }

  updateWelcomeTime() {
    const welcomeTime = document.getElementById("welcomeTime");
    if (welcomeTime) {
      welcomeTime.textContent = new Date().toLocaleTimeString();
    }
  }

  openSettings() {
    this.settingsModal.classList.add("show");
    this.populateSettingsForm();
  }

  closeSettings() {
    this.settingsModal.classList.remove("show");
  }

  async saveSettings() {
    const newConfig = {
      api_key: this.apiKeyInput.value,
      workspace_slug: this.workspaceSlugInput.value,
      model_server_base_url: this.apiUrlInput.value,
      stream: this.streamingEnabledInput.checked,
      stream_timeout: 60,
    };

    // Validate configuration
    if (
      !newConfig.api_key ||
      !newConfig.workspace_slug ||
      !newConfig.model_server_base_url
    ) {
      this.showNotification("Please fill in all required fields.", "error");
      return;
    }

    try {
      // Here you would typically save the configuration
      // For now, we'll just update the local config
      this.config = newConfig;
      this.closeSettings();
      this.showNotification("Settings saved successfully!", "success");
      this.updateStatus("connected", "Connected");
    } catch (error) {
      console.error("Error saving settings:", error);
      this.showNotification(
        "Error saving settings. Please try again.",
        "error"
      );
    }
  }

  async clearChat() {
    if (confirm("Are you sure you want to clear the chat history?")) {
      try {
        // Use unified API instead of IPC
        const response = await fetch("http://localhost:8000/clear-history", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
          // Clear the chat messages (keep welcome message)
          const messages = this.chatMessages.querySelectorAll(
            ".message:not(.assistant-message:first-child)"
          );
          messages.forEach((msg) => msg.remove());

          this.messageCount = 0;
          this.updateMessageCount();
          this.showNotification("Chat history cleared.", "success");
        } else {
          this.showNotification("Error clearing chat history.", "error");
        }
      } catch (error) {
        console.error("Error clearing chat:", error);
        this.showNotification("Error clearing chat history.", "error");
      }
    }
  }

  async toggleVoiceRecording() {
    console.log("Voice button clicked, current recording state:", this.isRecording);
    if (this.isRecording) {
      console.log("Stopping voice recording...");
      await this.stopVoiceRecording();
    } else {
      console.log("Starting voice recording...");
      await this.startVoiceRecording();
    }
  }

  async startVoiceRecording() {
    try {
      console.log("Requesting microphone access...");
      
      // Check if MediaRecorder is supported
      if (!window.MediaRecorder) {
        throw new Error("MediaRecorder API not supported in this browser");
      }
      
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("getUserMedia API not supported in this browser");
      }
      
      // Stop any current TTS when starting recording
      if (this.ttsEnabled) {
        await this.stopTTS();
      }

      // Check if microphone access is available
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      
      console.log("Microphone access granted, creating MediaRecorder...");

      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });
      
      console.log("MediaRecorder created, setting up event handlers...");

      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        console.log("Audio data available, size:", event.data.size);
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        console.log("Recording stopped, processing audio...");
        this.processAudioRecording();
        stream.getTracks().forEach((track) => track.stop());
      };

      this.mediaRecorder.start();
      console.log("Recording started successfully");
      this.isRecording = true;
      this.updateVoiceButton();
      this.showNotification("Recording... Click to stop", "info");
    } catch (error) {
      console.error("Error starting voice recording:", error);
      this.showNotification(
        "Microphone access denied or not available",
        "error"
      );
    }
  }

  async stopVoiceRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      this.updateVoiceButton();
      this.showNotification("Processing audio...", "info");
    }
  }

  async processAudioRecording() {
    try {
      if (this.audioChunks.length === 0) {
        this.showNotification("No audio recorded", "error");
        return;
      }

      // Convert audio chunks to blob
      const audioBlob = new Blob(this.audioChunks, { type: "audio/webm" });

      // Convert to WAV format for better Whisper compatibility
      const wavBlob = await this.convertToWav(audioBlob);

      // Send to backend for transcription and LLM processing
      await this.sendVoiceMessage(wavBlob);
    } catch (error) {
      console.error("Error processing audio recording:", error);
      this.showNotification("Error processing audio", "error");
    }
  }

  async convertToWav(audioBlob) {
    // For now, we'll send the webm blob directly
    // In a production app, you might want to convert to WAV using a library like lamejs
    return audioBlob;
  }

  async sendVoiceMessage(audioBlob) {
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      formData.append("stream", "true"); // Default to streaming enabled

      // Show typing indicator
      this.showTypingIndicator();

      // Send to unified API
      const response = await fetch("http://localhost:8000/speak-and-chat", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        // Add transcribed text as user message
        this.addMessage("user", result.transcribed_text);

        // Add LLM response (always use streaming for voice messages)
        this.currentStreamingMessage = this.addMessage("assistant", "", true);
        this.currentStreamingMessage.querySelector(
          ".message-content"
        ).textContent = result.llm_response;
        this.finalizeStreamingMessage();
      } else {
        this.addMessage(
          "assistant",
          "Sorry, I encountered an error processing your voice message: " +
            result.error
        );
      }
    } catch (error) {
      console.error("Error sending voice message:", error);
      this.addMessage(
        "assistant",
        "Sorry, I encountered an error processing your voice message. Please try again."
      );
    } finally {
      this.hideTypingIndicator();
    }
  }

  updateVoiceButton() {
    if (this.isRecording) {
      this.voiceBtn.classList.add("recording");
      this.voiceBtn.title = "Stop Recording";
    } else {
      this.voiceBtn.classList.remove("recording");
      this.voiceBtn.title = "Voice Input";
    }
  }

  async toggleTTS() {
    try {
      const response = await fetch("http://localhost:8000/tts/toggle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          enabled: !this.ttsEnabled
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        this.ttsEnabled = result.enabled;
        this.updateTTSButton();
        this.showNotification(
          result.enabled ? "TTS enabled" : "TTS disabled",
          "success"
        );
      } else {
        this.showNotification("Error toggling TTS", "error");
      }
    } catch (error) {
      console.error("Error toggling TTS:", error);
      this.showNotification("Error toggling TTS", "error");
    }
  }

  async stopTTS() {
    try {
      const response = await fetch("http://localhost:8000/tts/stop", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        console.log("TTS stopped successfully");
      }
    } catch (error) {
      console.error("Error stopping TTS:", error);
    }
  }

  async initializeTTS() {
    try {
      const response = await fetch("http://localhost:8000/tts/status");
      if (response.ok) {
        const result = await response.json();
        this.ttsEnabled = result.status.enabled;
        this.updateTTSButton();
      }
    } catch (error) {
      console.error("Error initializing TTS:", error);
      // Keep default state (enabled)
    }
  }

  updateTTSButton() {
    if (this.ttsEnabled) {
      this.ttsBtn.classList.add("active");
      this.ttsBtn.title = "TTS Enabled - Click to disable";
    } else {
      this.ttsBtn.classList.remove("active");
      this.ttsBtn.title = "TTS Disabled - Click to enable";
    }
  }

  showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style the notification
    Object.assign(notification.style, {
      position: "fixed",
      top: "20px",
      right: "20px",
      padding: "1rem 1.5rem",
      borderRadius: "8px",
      color: "white",
      fontWeight: "500",
      zIndex: "10000",
      animation: "slideIn 0.3s ease-out",
      maxWidth: "300px",
      wordWrap: "break-word",
    });

    // Set background color based on type
    const colors = {
      success: "#10b981",
      error: "#ef4444",
      info: "#3b82f6",
    };
    notification.style.backgroundColor = colors[type] || colors.info;

    document.body.appendChild(notification);

    // Remove notification after 3 seconds
    setTimeout(() => {
      notification.style.animation = "slideOut 0.3s ease-in";
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }
}

// Add CSS for notifications
const style = document.createElement("style");
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
document.addEventListener("DOMContentLoaded", () => {
  new RemoAIChat();
});
