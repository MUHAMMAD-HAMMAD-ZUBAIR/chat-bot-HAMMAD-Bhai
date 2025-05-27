document.addEventListener("DOMContentLoaded", function () {
  const chatMessages = document.getElementById("chat-messages");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-btn");
  const stopButton = document.getElementById("stop-btn");
  const resetButton = document.getElementById("reset-btn");

  let currentRequest = null;
  let isGenerating = false;
  let isEditMode = false;

  // Auto-resize the textarea as the user types
  userInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
  });

  // Handle form submission
  const chatForm = document.getElementById("chat-form");
  if (chatForm) {
    chatForm.addEventListener("submit", function (e) {
      e.preventDefault();
      console.log("Form submitted"); // Debug log
      sendMessage();
    });
  }

  // Send message when Enter key is pressed (without Shift)
  userInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      console.log("Enter pressed"); // Debug log
      sendMessage();
    }
  });

  // Send message when send button is clicked
  sendButton.addEventListener("click", function (e) {
    e.preventDefault();
    console.log("Send button clicked"); // Debug log
    sendMessage();
  });

  // Stop generation when stop button is clicked
  stopButton.addEventListener("click", stopGeneration);

  // Reset conversation when reset button is clicked
  resetButton.addEventListener("click", function (e) {
    e.preventDefault();
    console.log("Reset button clicked"); // Debug log
    resetConversation();
  });

  function sendMessage() {
    const message = userInput.value.trim();
    if (!message || isGenerating) return;

    console.log("Sending message:", message); // Debug log
    console.log("Edit mode:", isEditMode); // Debug log

    // Clear edit mode flag
    isEditMode = false;

    // Add user message to chat
    addMessageToChat("user", message);

    // Clear input field and reset height
    userInput.value = "";
    userInput.style.height = "auto";

    // Show typing indicator and update UI
    showTypingIndicator();
    setGeneratingState(true);

    // Send message to server
    currentRequest = fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    })
      .then((response) => {
        console.log("Response received:", response.status); // Debug log
        if (!response.ok) {
          return response.json().then((errorData) => {
            throw new Error(errorData.error || "Unknown error occurred");
          });
        }
        return response.json();
      })
      .then((data) => {
        console.log("Chat response received:", data); // Debug log
        // Remove typing indicator
        removeTypingIndicator();

        // Don't set generating state to false yet - streaming will handle it

        // Add bot response with streaming effect
        if (data.response) {
          console.log("Starting streaming for response"); // Debug log
          addMessageWithStreaming("bot", data.response);
        } else if (data.error) {
          setGeneratingState(false);
          addMessageToChat("bot-error", data.error);
        } else {
          setGeneratingState(false);
          addMessageToChat("bot-error", "No response received from AI");
        }

        // Scroll to bottom
        scrollToBottom();
      })
      .catch((error) => {
        console.error("Error:", error);
        removeTypingIndicator();
        setGeneratingState(false);

        if (error.name !== "AbortError") {
          // Display a more helpful error message
          let errorMessage = error.message;
          if (errorMessage === "Failed to fetch") {
            errorMessage =
              "Network error. Please check your internet connection and try again.";
          } else if (errorMessage === "Unknown error occurred") {
            errorMessage =
              "An unexpected error occurred. Please try again later.";
          }

          addMessageToChat("bot-error", errorMessage);
          scrollToBottom();
        }
      });
  }

  function stopGeneration() {
    if (isGenerating) {
      console.log("Stopping generation..."); // Debug log

      // Stop the streaming effect
      if (currentRequest && currentRequest.streamingInterval) {
        clearTimeout(currentRequest.streamingInterval);
        currentRequest.streamingInterval = null;
      }

      // Remove typing indicator
      removeTypingIndicator();

      // Set generating state to false
      setGeneratingState(false);

      // Add stop message
      addMessageToChat("bot", "⏹️ Generation stopped by user.");
      showToast("Generation stopped", "info");
    }
  }

  function setGeneratingState(generating) {
    isGenerating = generating;
    if (generating) {
      sendButton.style.display = "none";
      stopButton.style.display = "block";
      userInput.disabled = true;
      userInput.placeholder = "AI is generating response...";
    } else {
      sendButton.style.display = "block";
      stopButton.style.display = "none";
      userInput.disabled = false;
      userInput.placeholder = "Message HAMMAD BHAI...";
      currentRequest = null;
    }
  }

  function resetConversation() {
    console.log("Reset conversation called"); // Debug log

    // Reset UI state first
    setGeneratingState(false);
    removeTypingIndicator();

    // Send reset request to server
    fetch("/api/reset", {
      method: "POST",
    })
      .then((response) => response.json())
      .then(() => {
        console.log("Reset successful"); // Debug log

        // Clear chat messages and add welcome message
        chatMessages.innerHTML = `
          <div class="message bot-message" data-message-id="welcome_msg">
            <div class="message-content">
            Hey there! I'm <strong>HAMMAD BHAI</strong> 🤖, created by
            <strong>MUHAMMAD HAMMAD ZUBAIR</strong>, here to make your day
            smoother and brighter! 🌟 How can I assist you today? Forget the
            loading animation — just type your message.

              <div class="message-timestamp">${new Date().toLocaleTimeString(
                [],
                { hour: "2-digit", minute: "2-digit" }
              )}</div>
            </div>
            <div class="message-actions">
              <button class="action-btn copy-btn" title="Copy message" onclick="copyMessage('welcome_msg')">
                <i class="fas fa-copy"></i>
              </button>
              <button class="action-btn regenerate-btn" title="Regenerate response" onclick="regenerateMessage('welcome_msg')">
                <i class="fas fa-redo"></i>
              </button>
            </div>
          </div>
        `;

        showToast("Chat reset successfully!", "success");
      })
      .catch((error) => {
        console.error("Reset error:", error);
        showToast("Failed to reset chat. Please try again.", "error");
      });
  }

  function addMessageToChat(sender, text, messageId = null) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    // Generate unique message ID if not provided
    if (!messageId) {
      messageId =
        "msg_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
    }
    messageDiv.setAttribute("data-message-id", messageId);

    // Process markdown-like formatting in the text
    const formattedText = formatMessage(text);

    // Get current timestamp
    const timestamp = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    messageDiv.innerHTML = `
            <div class="message-content">
                ${formattedText}
                <div class="message-timestamp">${timestamp}</div>
            </div>
            <div class="message-actions">
                <button class="action-btn copy-btn" title="Copy message" onclick="copyMessage('${messageId}')">
                    <i class="fas fa-copy"></i>
                </button>
                ${
                  sender === "user"
                    ? `
                    <button class="action-btn edit-btn" title="Edit message" onclick="editMessage('${messageId}')">
                        <i class="fas fa-edit"></i>
                    </button>
                `
                    : `
                    <button class="action-btn regenerate-btn" title="Regenerate response" onclick="regenerateMessage('${messageId}')">
                        <i class="fas fa-redo"></i>
                    </button>
                `
                }
            </div>
        `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    // If this is an error message, add a retry button
    if (sender === "bot-error") {
      const retryButton = document.createElement("button");
      retryButton.className = "retry-button";
      retryButton.innerHTML = "Try Again";
      retryButton.onclick = function () {
        // Remove the error message
        messageDiv.remove();

        // Just show a message without resetting
        addMessageToChat(
          "bot",
          "I'm ready to help! Please try sending your message again."
        );
      };

      messageDiv.querySelector(".message-content").appendChild(retryButton);
    }

    return messageId;
  }

  function formatMessage(text) {
    // Convert URLs to links
    text = text.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );

    // Handle code blocks with PERFECT copy functionality
    text = text.replace(
      /```(\w+)?\n?([\s\S]*?)```/g,
      function (match, language, code) {
        const codeId = "code_" + Math.random().toString(36).substr(2, 9);
        const langLabel = language ? language.toUpperCase() : "CODE";

        // Store ORIGINAL CLEAN code for perfect copying
        const originalCode = code.trim();

        return `
        <div class="code-block" data-original-code="${originalCode
          .replace(/"/g, "&quot;")
          .replace(/\n/g, "\\n")}">
          <div class="code-header">
            <span class="code-language">${langLabel}</span>
            <button class="code-copy-btn" onclick="copyCodePerfect('${codeId}')" title="Copy code">
              <i class="fas fa-copy"></i>
            </button>
          </div>
          <pre><code id="${codeId}" class="language-${
          language || "text"
        }">${originalCode}</code></pre>
        </div>
      `;
      }
    );

    // Handle inline code (`code`)
    text = text.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

    // Handle bold text (**text**)
    text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Handle italic text (*text*)
    text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // Handle numbered lists (1. item, 2. item, etc.)
    text = text.replace(
      /^(\d+)\.\s+(.+)$/gm,
      '<div class="list-item numbered">$2</div>'
    );

    // Handle bullet points (- item or * item)
    text = text.replace(
      /^[-*]\s+(.+)$/gm,
      '<div class="list-item bullet">$1</div>'
    );

    // Handle line breaks but preserve paragraph structure
    text = text.replace(/\n\n/g, "</p><p>");
    text = text.replace(/\n/g, "<br>");

    // Wrap in paragraph if no HTML tags
    if (!/<[a-z][\s\S]*>/i.test(text)) {
      text = `<p>${text}</p>`;
    } else if (!text.startsWith("<p>") && !text.startsWith("<div>")) {
      text = `<p>${text}</p>`;
    }

    return text;
  }

  function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "typing-indicator";
    typingDiv.id = "typing-indicator";
    typingDiv.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Add message with streaming effect
  function addMessageWithStreaming(sender, text) {
    const messageId = addMessageToChat(sender, "");
    const messageDiv = document.querySelector(
      `[data-message-id="${messageId}"]`
    );
    const messageContent = messageDiv.querySelector(".message-content");

    // Remove the timestamp temporarily
    const timestamp = messageContent.querySelector(".message-timestamp");
    if (timestamp) timestamp.remove();

    let currentText = "";
    let index = 0;
    let streamingInterval;
    let userScrolled = false;

    // Store the streaming interval for stopping
    if (currentRequest) {
      currentRequest.streamingInterval = streamingInterval;
    }

    // Check if user has scrolled up
    function checkUserScroll() {
      const isAtBottom =
        chatMessages.scrollTop + chatMessages.clientHeight >=
        chatMessages.scrollHeight - 10;
      userScrolled = !isAtBottom;
    }

    // Add scroll listener to detect user scrolling
    chatMessages.addEventListener("scroll", checkUserScroll);

    function typeNextChar() {
      if (index < text.length && isGenerating) {
        // Add characters at medium speed for natural typing effect
        const charsToAdd = Math.min(5, text.length - index); // Medium speed
        currentText += text.substr(index, charsToAdd);
        index += charsToAdd;

        const formattedText = formatMessage(currentText);

        // Get current timestamp
        const currentTimestamp = new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });

        messageContent.innerHTML = `
          ${formattedText}
          <div class="message-timestamp">${currentTimestamp}</div>
        `;

        // Re-enable copy buttons for any code blocks that were just added
        const codeBlocks = messageContent.querySelectorAll(".code-copy-btn");
        codeBlocks.forEach((btn) => {
          btn.style.pointerEvents = "auto";
          btn.style.opacity = "1";
        });

        // Only auto-scroll if user hasn't scrolled up
        if (!userScrolled) {
          scrollToBottom();
        }

        // Medium typing speed for natural feel
        streamingInterval = setTimeout(typeNextChar, 25); // Medium speed
        if (currentRequest) {
          currentRequest.streamingInterval = streamingInterval;
        }
      } else {
        // Finished typing or stopped
        setGeneratingState(false);
        if (currentRequest) {
          currentRequest.streamingInterval = null;
        }
        // Remove scroll listener
        chatMessages.removeEventListener("scroll", checkUserScroll);
        // Final scroll to bottom
        if (!userScrolled) {
          scrollToBottom();
        }
      }
    }

    // Start typing effect
    typeNextChar();
    return messageId;
  }

  // PERFECT CODE COPY FUNCTION - GUARANTEED COMPLETE COPY
  window.copyCodePerfect = function (codeId) {
    console.log("🚀 PERFECT CODE COPY for ID:", codeId);

    const codeElement = document.getElementById(codeId);
    if (!codeElement) {
      console.error("❌ Code element not found:", codeId);
      showToast("Code element not found!", "error");
      return;
    }

    // Get the code block container
    const codeBlock = codeElement.closest(".code-block");
    let codeToCopy = "";

    // Method 1: Get from data-original-code attribute (BEST)
    if (codeBlock && codeBlock.dataset.originalCode) {
      console.log("✅ Found original code in data attribute");

      // Decode the stored code
      codeToCopy = codeBlock.dataset.originalCode
        .replace(/&quot;/g, '"')
        .replace(/\\n/g, "\n");

      console.log("📝 Original code:", codeToCopy);
    }

    // Method 2: Extract from element (fallback)
    if (!codeToCopy || codeToCopy.trim().length === 0) {
      console.log("⚠️ Extracting from element...");

      if (codeElement.innerText) {
        codeToCopy = codeElement.innerText;
        console.log("✅ Using innerText");
      } else if (codeElement.textContent) {
        codeToCopy = codeElement.textContent;
        console.log("✅ Using textContent");
      }
    }

    // Validate we have content
    if (!codeToCopy || codeToCopy.trim().length === 0) {
      console.error("❌ No code content found");
      showToast("No code content found!", "error");
      return;
    }

    console.log("📊 Code stats:");
    console.log("📊 Length:", codeToCopy.length);
    console.log("📊 Lines:", codeToCopy.split("\n").length);

    // PERFECT COPY PROCESS
    copyToClipboardPerfect(codeToCopy);

    function copyToClipboardPerfect(text) {
      // Try modern Clipboard API first
      if (navigator.clipboard && navigator.clipboard.writeText) {
        console.log("🚀 Using Clipboard API...");

        navigator.clipboard
          .writeText(text)
          .then(() => {
            console.log("✅ SUCCESS: Perfect copy completed!");
            showToast("✅ Code copied perfectly!", "success");
          })
          .catch((error) => {
            console.error("❌ Clipboard API failed:", error);
            fallbackCopyPerfect(text);
          });
      } else {
        console.log("⚠️ Using fallback method...");
        fallbackCopyPerfect(text);
      }
    }

    function fallbackCopyPerfect(text) {
      try {
        // Create temporary textarea
        const textarea = document.createElement("textarea");
        textarea.value = text;

        // Make invisible but functional
        textarea.style.cssText = `
          position: fixed;
          left: -9999px;
          top: -9999px;
          opacity: 0;
          pointer-events: none;
        `;

        // Add to DOM
        document.body.appendChild(textarea);

        // Select all content
        textarea.focus();
        textarea.select();
        textarea.setSelectionRange(0, text.length);

        // Copy
        const success = document.execCommand("copy");

        // Clean up
        document.body.removeChild(textarea);

        if (success) {
          console.log("✅ SUCCESS: Fallback copy worked!");
          showToast("✅ Code copied perfectly!", "success");
        } else {
          console.error("❌ Fallback failed");
          showToast("❌ Copy failed. Please try again.", "error");
        }
      } catch (error) {
        console.error("❌ Copy error:", error);
        showToast("❌ Copy failed. Please try again.", "error");
      }
    }
  };

  // Copy message functionality
  window.copyMessage = function (messageId) {
    const messageDiv = document.querySelector(
      `[data-message-id="${messageId}"]`
    );
    if (!messageDiv) return;

    const messageContent = messageDiv.querySelector(".message-content");
    let textToCopy = messageContent.innerText
      .replace(/\d{1,2}:\d{2}$/, "")
      .trim();

    navigator.clipboard
      .writeText(textToCopy)
      .then(() => {
        showToast("Message copied!", "success");
      })
      .catch(() => {
        const textArea = document.createElement("textarea");
        textArea.value = textToCopy;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
        showToast("Message copied!", "success");
      });
  };

  // Edit message functionality
  window.editMessage = function (messageId) {
    const messageDiv = document.querySelector(
      `[data-message-id="${messageId}"]`
    );
    if (!messageDiv) return;

    const messageContent = messageDiv.querySelector(".message-content");
    let currentText =
      messageContent.innerText || messageContent.textContent || "";
    currentText = currentText.replace(/\d{1,2}:\d{2}\s*$/, "").trim();

    isEditMode = true;
    setGeneratingState(false);
    removeTypingIndicator();

    userInput.value = currentText;
    userInput.focus();
    userInput.style.height = "auto";
    userInput.style.height = userInput.scrollHeight + "px";

    let nextSibling = messageDiv.nextElementSibling;
    while (nextSibling) {
      const toRemove = nextSibling;
      nextSibling = nextSibling.nextElementSibling;
      toRemove.remove();
    }

    messageDiv.remove();
    showToast("Message loaded for editing.", "info");
  };

  // Regenerate response functionality
  window.regenerateMessage = function (messageId) {
    const messageDiv = document.querySelector(
      `[data-message-id="${messageId}"]`
    );
    if (!messageDiv) return;

    let prevElement = messageDiv.previousElementSibling;
    let userMessage = null;

    while (prevElement) {
      if (prevElement.classList.contains("user-message")) {
        const messageContent = prevElement.querySelector(".message-content");
        let text = messageContent.innerText || messageContent.textContent || "";
        userMessage = text.replace(/\d{1,2}:\d{2}\s*$/, "").trim();
        break;
      }
      prevElement = prevElement.previousElementSibling;
    }

    if (!userMessage) {
      showToast("Could not find message to regenerate.", "error");
      return;
    }

    messageDiv.remove();
    showTypingIndicator();
    setGeneratingState(true);

    currentRequest = fetch("/api/regenerate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage }),
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((errorData) => {
            throw new Error(errorData.error || "Unknown error occurred");
          });
        }
        return response.json();
      })
      .then((data) => {
        removeTypingIndicator();
        if (data.error) {
          setGeneratingState(false);
          addMessageToChat("bot-error", data.error);
        } else if (data.response) {
          addMessageWithStreaming("bot", data.response);
        } else {
          setGeneratingState(false);
          addMessageToChat("bot-error", "No response received");
        }
      })
      .catch((error) => {
        removeTypingIndicator();
        setGeneratingState(false);
        if (error.name !== "AbortError") {
          addMessageToChat("bot-error", "Error occurred. Please try again.");
        }
      });
  };

  // Toast notification system
  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <i class="fas ${
        type === "success"
          ? "fa-check-circle"
          : type === "error"
          ? "fa-exclamation-circle"
          : "fa-info-circle"
      }"></i>
      <span>${message}</span>
    `;

    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add("show"), 100);
    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
  }
});
