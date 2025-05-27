document.addEventListener("DOMContentLoaded", function () {
  const chatMessages = document.getElementById("chat-messages");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-btn");
  const resetButton = document.getElementById("reset-btn");

  // Auto-resize the textarea as the user types
  userInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
  });

  // Send message when Enter key is pressed (without Shift)
  userInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Send message when send button is clicked
  sendButton.addEventListener("click", sendMessage);

  // Reset conversation when reset button is clicked
  resetButton.addEventListener("click", resetConversation);

  function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessageToChat("user", message);

    // Clear input field and reset height
    userInput.value = "";
    userInput.style.height = "auto";

    // Show typing indicator
    showTypingIndicator();

    // Send message to server
    fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
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
        // Remove typing indicator
        removeTypingIndicator();

        // Add bot response to chat
        addMessageToChat("bot", data.response);

        // Scroll to bottom
        scrollToBottom();
      })
      .catch((error) => {
        console.error("Error:", error);
        removeTypingIndicator();

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
      });
  }

  function resetConversation() {
    // Send reset request to server
    fetch("/api/reset", {
      method: "POST",
    })
      .then((response) => response.json())
      .then(() => {
        // Clear chat messages except for the welcome message
        chatMessages.innerHTML = `
                <div class="message bot-message">
                     <div class="message-content">
            Hey there! I'm <strong>HAMMAD BHAI</strong> 🤖, created by <strong>MUHAMMAD HAMMAD ZUBAIR</strong>, here to make your day smoother and brighter! 🌟 How can I assist you today? Forget the loading animation — just type your message.
      </div>
                </div>
            `;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  function addMessageToChat(sender, text) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;

    // Process markdown-like formatting in the text
    const formattedText = formatMessage(text);

    messageDiv.innerHTML = `
            <div class="message-content">
                ${formattedText}
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

        // Reset the conversation
        fetch("/api/reset", {
          method: "POST",
        })
          .then((response) => response.json())
          .then((data) => {
            // Add a system message
            addMessageToChat(
              "bot",
              "Let's try again. What would you like to talk about?"
            );
          });
      };

      messageDiv.querySelector(".message-content").appendChild(retryButton);
    }
  }

  function formatMessage(text) {
    // Convert URLs to links
    text = text.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank">$1</a>'
    );

    // Handle code blocks (```code```)
    text = text.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");

    // Handle inline code (`code`)
    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Handle line breaks
    text = text.replace(/\n/g, "<br>");

    // If the text doesn't have any HTML tags, wrap it in a paragraph
    if (!/<[a-z][\s\S]*>/i.test(text)) {
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
});
