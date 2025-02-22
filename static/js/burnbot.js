document.getElementById("burnbot-btn").addEventListener("click", function () {
    let chatBox = document.getElementById("chat-box");

    // If the chat is empty, send the initial message with options
    if (chatBox.childElementCount === 0) {
        appendMessage(
            "BurnBot: Hello there! I am BurnBot, and I am here to help you achieve your fitness goals.\n\n"
            + "Select an option below.\n\n"
            + "0. View the menu again.\n\n"
            + "1. Tell me the food item, and I’ll fetch its calorie count for you!\n\n"
            // "2. Would you like a diet plan based on weight loss, muscle gain, or maintenance?\n\n" +
            // "3. Do you prefer home workouts or gym workouts?\n\n" +
            // "4. Ask me anything! I have a list of FAQs.\n\n"
        );
    }

    document.getElementById("burnbot-container").style.visibility = "visible";
    this.style.visibility = "hidden";
});

document.getElementById("close-btn").addEventListener("click", function () {
    document.getElementById("burnbot-container").style.visibility = "hidden";
    document.getElementById("burnbot-btn").style.visibility = "visible";
});

document.getElementById("send-btn").addEventListener("click", function () {
    sendMessage();
});

document.getElementById("chat-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    let userInput = document.getElementById("chat-input").value.trim();
    if (!userInput) return;

    appendMessage("You: " + userInput, "user");

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
        .then(response => response.json())
        .then(data => appendMessage("BurnBot: " + data.response, "bot"))
        .catch(error => console.error("Error:", error));

    document.getElementById("chat-input").value = "";
}

function appendMessage(message, sender) {
    let chatBox = document.getElementById("chat-box");
    let messageElement = document.createElement("div");
    messageElement.className = sender === "user" ? "alert alert-success" : "alert alert-secondary";

    messageElement.innerHTML = message.replace(/\n/g, "<br>");

    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}
