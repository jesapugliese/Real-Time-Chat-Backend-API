const HTTP_BASE_URL = "http://localhost:8080";
const WS_BASE_URL = "ws://localhost:8080";

const channelsContainer = document.getElementById("channels");
const messagesContainer = document.getElementById("messages");
const channelName = document.getElementById("channelName");
const connectionStatus = document.getElementById("connectionStatus");

const channelForm = document.getElementById("channelForm");
const channelInput = document.getElementById("channelInput");

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
        console.error("Error loading channels:", error);

        channelsContainer.innerHTML = "";

        const errorMessage = document.createElement("p");
        errorMessage.className = "empty-message";
        errorMessage.textContent = "Error loading channels.";

        channelsContainer.appendChild(errorMessage);
    }
}


function renderChannels(channels) {
    channelsContainer.innerHTML = "";

    if (channels.length === 0) {
        const emptyMessage = document.createElement("p");
        emptyMessage.className = "empty-message";
        emptyMessage.textContent = "No channels available.";

        channelsContainer.appendChild(emptyMessage);
        return;
    }

    channels.forEach(channel => {
        const item = document.createElement("div");

        item.className = "channel-item";
        item.textContent = `# ${channel.name} (ID: ${channel.id})`;

        channelsContainer.appendChild(item);
    });
}


channelForm.addEventListener("submit", event => {
    event.preventDefault();

    const channelId = parseInt(channelInput.value, 10);

    if (isNaN(channelId)) {
        alert("Please enter a valid channel ID.");
        return;
    }

    messages.clear();
    messagesContainer.innerHTML = "";

    closeWebSocket();

    currentChannelId = channelId;
    channelName.textContent = `Channel ID: ${channelId}`;

    connectWebSocket(channelId);
});


function connectWebSocket(channelId) {
    const url = `${WS_BASE_URL}/channels/${channelId}/ws`;

    setConnectionStatus("connecting");

    const socket = new WebSocket(url);

    websocket = socket;

    socket.addEventListener("open", () => {
        if (socket !== websocket) {
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

            addOrUpdateMessage(message);

            if (isNewMessage) {
                scrollToBottom();
            }

        } catch (error) {
            console.error("Invalid WebSocket message:", error);
        }
    });


    socket.addEventListener("close", event => {
        if (socket !== websocket) {
            return;
        }

        console.log(
            `WebSocket disconnected from channel ${channelId}. ` +
            `Code: ${event.code}, ` +
            `Reason: ${event.reason || "No reason provided"}`
        );

        websocket = null;
        setConnectionStatus("disconnected");

        if (event.code === 1008) {
            channelName.textContent = "Select a channel";

            messagesContainer.innerHTML = "";

            const errorMessage = document.createElement("p");
            errorMessage.className = "empty-message";
            errorMessage.textContent =
                `Channel ${channelId} does not exist.`;

            messagesContainer.appendChild(errorMessage);

            currentChannelId = null;
        }
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


function addOrUpdateMessage(message) {
    const existingElement = messages.get(message.id);

    if (existingElement) {
        updateMessageElement(existingElement, message);
        return;
    }

    const element = createMessageElement(message);

    messages.set(message.id, element);
    messagesContainer.appendChild(element);
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
