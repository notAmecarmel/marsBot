document.addEventListener('DOMContentLoaded', function() {
  var userInput = document.getElementById("user-input");
  var sendButton = document.getElementById("send-button");

  // Function to send message
  function sendMessage() {
    var message = userInput.value.trim();
    if (message !== "") {
      displayMessage("You", message);

      // Display loading dots
      displayLoadingDots();

      // Send message to the backend server
      fetch('/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
          'user_input': message
        })
      })
      .then(response => response.json())
      .then(data => {
        // Remove loading dots
        removeLoadingDots();

        // Update chat window with the response
        var botResponse = data.bot_response.replace(/\n/g, '<br>');
        displayMessage("Bot", botResponse);
      })
      .catch(error => {
        console.error('Error:', error);
      });

      userInput.value = "";
    }
  }

  // Function to display messages in the chat window
  function displayMessage(sender, message) {
    var chatWindow = document.getElementById("chat-window");
    var messageElement = document.createElement("div");
    messageElement.className = sender.toLowerCase() + "-message";
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;  // Scroll to the bottom
  }

  // Function to display loading dots
  function displayLoadingDots() {
    var chatWindow = document.getElementById("chat-window");
    var loadingDots = document.createElement("div");
    loadingDots.id = "loading-dots";
    loadingDots.className = "bot-message";
    loadingDots.innerHTML = `<strong>Bot:</strong> <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>`;
    chatWindow.appendChild(loadingDots);
    chatWindow.scrollTop = chatWindow.scrollHeight;  // Scroll to the bottom
  }

  // Function to remove loading dots
  function removeLoadingDots() {
    var loadingDots = document.getElementById("loading-dots");
    if (loadingDots) {
      loadingDots.remove();
    }
  }

  // Event listener for the Enter key
  userInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });

  // Event listener for the send button
  sendButton.addEventListener("click", sendMessage);
});
