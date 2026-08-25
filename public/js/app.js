const HTTP_BASE_URL = "http://localhost:8080";
const WS_BASE_URL = "ws://localhost:8080";

const channelsContainer = document.getElementById("channels");
const messagesContainer = document.getElementById("messages");
const channelName = document.getElementById("channelName");
const connectionStatus = document.getElementById("connectionStatus");

let websocket = null;
let currentChannelId = null;

const messages = new Map();

async function loadChannels() {
    try {
        const response = await fetch(`${HTTP_BASE_URL}/channels`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();

        renderChannels(result.data);
    } catch (error) {
        console.error("Error at loading channels:", error);

        channelsContainer.innerHTML = "";

        const errorMessage = document.createElement("p");
        errorMessage.className = "empty-message";
        errorMessage.textContent = "Error at loading channels.";

        channelsContainer.appendChild(errorMessage);
    }
}

function renderChannels(channels) {
    channelsContainer.innerHTML = "";

    channels.forEach(channel => {
        const button = document.createElement("button");

        button.className = "channel-button";
        button.textContent = `# ${channel.name}`;

        button.addEventListener("click", () => {
            selectChannel(channel);
        });

        channelsContainer.appendChild(button);
    });
}

async function selectChannel(channel) {
    currentChannelId = channel.id;

    closeWebSocket();

    channelName.textContent = channel.name;

    document.querySelectorAll(".channel-button").forEach(button => {
        button.classList.remove("active");
    });

    const selectedButton = [...document.querySelectorAll(".channel-button")]
        .find(button => button.textContent === `# ${channel.name}`);

    if (selectedButton) {
        selectedButton.classList.add("active");
    }

    messages.clear();
    messagesContainer.innerHTML = "";

    setConnectionStatus("connecting");

    try {
        connectWebSocket(channel.id);
    } catch (error) {
        console.error("Error at loading history:", error);

        messagesContainer.innerHTML = "";

        const errorMessage = document.createElement("p");
        errorMessage.className = "empty-message";
        errorMessage.textContent = "Error at loading history.";

        messagesContainer.appendChild(errorMessage);

        setConnectionStatus("disconnected");
    }
}

function connectWebSocket(channelId) {
    const url = `${WS_BASE_URL}/channels/${channelId}/ws`;

    setConnectionStatus("connecting");

    const socket = new WebSocket(url);

    websocket = socket;

    socket.addEventListener("open", () => {
        if (socket !== websocket || currentChannelId !== channelId) {
            return;
        }

        console.log(`WebSocket connected to channel ${channelId}`);

        setConnectionStatus("connected");
    });

    socket.addEventListener("message", event => {
        if (socket !== websocket || currentChannelId !== channelId) {
            return;
        }

        try {
            const message = JSON.parse(event.data);

            console.log("Message received:", message);

            if (message.channelId !== channelId) {
                return;
            }

            const isNewMessage = !messages.has(message.id);

            addOrUpdateMessage(message, true);

            if (isNewMessage) {
                scrollToBottom();
            }

        } catch (error) {
            console.error("Invalid WebSocket message:", error);
        }
    });

    socket.addEventListener("close", () => {
        if (socket !== websocket) {
            return;
        }

        console.log(`WebSocket disconnected from channel ${channelId}`);

        websocket = null;
        setConnectionStatus("disconnected");
    });

    socket.addEventListener("error", error => {
        if (socket !== websocket) {
            return;
        }

        console.error("WebSocket error:", error);

        setConnectionStatus("disconnected");
    });
}

function closeWebSocket() {
    if (websocket !== null) {
        websocket.close();
        websocket = null;
    }

    setConnectionStatus("disconnected");
}

function addOrUpdateMessage(message, scroll = false) {
    const existingElement = messages.get(message.id);

    if (existingElement) {
        updateMessageElement(existingElement, message);
        return;
    }

    const element = createMessageElement(message);

    messages.set(message.id, element);
    messagesContainer.appendChild(element);

    if (scroll) {
        scrollToBottom();
    }
}

function createMessageElement(message) {
    const element = document.createElement("article");

    element.className = "message";
    element.dataset.messageId = message.id;

    renderMessageElement(element, message);

    return element;
}

function updateMessageElement(element, message) {
    renderMessageElement(element, message);
}

function renderMessageElement(element, message) {
    element.innerHTML = "";

    const header = document.createElement("div");

    const author = document.createElement("span");
    author.className = "message-author";
    author.textContent = `Usuario ${message.authorId}`;

    const date = document.createElement("span");
    date.className = "message-date";
    date.textContent = formatDate(message.createdAt);

    header.appendChild(author);
    header.appendChild(date);

    if (message.editedAt) {
        const edited = document.createElement("span");
        edited.className = "edited";
        edited.textContent = "(editado)";

        header.appendChild(edited);
    }

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = message.content;

    element.appendChild(header);
    element.appendChild(content);
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatDate(date) {
    if (!date) {
        return "";
    }

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
        return date;
    }

    return parsedDate.toLocaleString("es-AR");
}

function setConnectionStatus(status) {
    connectionStatus.className = `status ${status}`;

    if (status === "connected") {
        connectionStatus.textContent = "Connected";
    } else if (status === "connecting") {
        connectionStatus.textContent = "Connecting...";
    } else {
        connectionStatus.textContent = "Disconnected";
    }
}

loadChannels();
