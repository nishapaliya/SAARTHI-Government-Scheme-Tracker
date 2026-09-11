/* Chatbot Widget JS - SAARTHI Rule-Based Assistant */
function toggleChatbot() {
    const modal = document.getElementById("chatbotModal");

    if (modal.style.display === "none" || modal.style.display === "") {
        modal.classList.remove("fade-in");
        void modal.offsetWidth;
        modal.style.display = "flex";
        modal.classList.add("fade-in");
    } else {
        modal.style.display = "none";
    }
}



function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const logs = document.getElementById('chatLogs');
    if(!input || !logs) return;

    const msg = input.value.trim();
    if(!msg) return;

    // Append user message
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-message user-msg p-3 rounded-4 bg-primary-blue text-white shadow-xs ms-auto mb-3 fs-7';
    userDiv.style.maxWidth = '80%';
    userDiv.textContent = msg;
    logs.appendChild(userDiv);

    input.value = '';
    logs.scrollTop = logs.scrollHeight;

    // Call backend rule-based chatbot API
    fetch('/chatbot/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg })
})
.then(r => r.json())
.then(data => {
    const botDiv = document.createElement('div');
    botDiv.className = 'chat-message bot-msg p-3 rounded-4 bg-white shadow-xs border mb-3 fs-7';
    botDiv.style.lineHeight = "1.6";
    botDiv.style.fontSize = "14px";
    botDiv.innerHTML = marked.parse(data.reply);
    logs.appendChild(botDiv);
    logs.scrollTop = logs.scrollHeight;
})
.catch(error => {
    console.error(error);

    const botDiv = document.createElement('div');
    botDiv.className = 'chat-message bot-msg p-3 rounded-4 bg-white shadow-xs border mb-3 fs-7';
    botDiv.innerHTML = "⚠️ Unable to contact the chatbot server.";
    logs.appendChild(botDiv);
});
}

function sendQuickChat(text) {
    document.getElementById('chatInput').value = text;
    sendChatMessage();
}
