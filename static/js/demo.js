document.addEventListener("DOMContentLoaded", () => {
  loadTickets();
  populateProductDropdown();

  document.querySelector(".send-button").addEventListener("click", sendMessage);
  document.querySelector("#userInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  document.querySelector(".new-chat-btn").addEventListener("click", () => {
    const product = prompt("Please enter a product name to start:");
    if (!product) return alert("❗ Product is required to start a new chat.");

    currentProduct = product;
    currentTicket = null;
    document.getElementById("chatBox").innerHTML = "";
    appendMessage("bot", `🆕 New chat started for "${product}". Type your message.`);
  });

  document.querySelector(".workspace-selector").addEventListener("change", (e) => {
    const product = e.target.value;
    loadTickets(product === "All" ? null : product);
  });

  document.querySelector(".feature-button.translate").addEventListener("click", () => {
    const lang = prompt("Enter target language code (e.g., en, hi, bn, ta):");
    if (!lang || !currentTicket) return alert("❌ No ticket selected.");
    const texts = Array.from(document.querySelectorAll("#chatBox .chat")).map(div => div.innerText);

    fetch(`/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: texts.join('\n'), lang: lang })
    })
      .then(res => res.json())
      .then(data => {
        if (data.translated) {
          document.getElementById("chatBox").innerHTML = "";
          appendMessage("bot", data.translated);
        }
      });
  });

  document.querySelector(".feature-button.download").addEventListener("click", () => {
    if (!currentTicket) return alert("❌ No ticket selected.");
    window.location.href = `/transcript/${currentTicket}`;
  });

  document.querySelector(".feature-button.demo").addEventListener("click", startDemo);

  document.querySelector(".feature-button.dark").addEventListener("click", () => {
    document.body.classList.toggle("dark");
  });
});

let currentTicket = null;
let currentProduct = null;

function loadTickets(productFilter = null) {
  fetch("/tickets")
    .then(res => res.json())
    .then(tickets => {
      const list = document.querySelector(".chat-list");
      list.innerHTML = "";

      tickets.forEach((ticketObj) => {
        const ticketId = ticketObj.ticket;
        fetch(`/get_ticket/${ticketId}`)
          .then(res => res.json())
          .then(data => {
            if (!productFilter || data.product === productFilter) {
              const div = document.createElement("div");
              div.className = "ticket-item";
              div.textContent = `${ticketId} - ${data.product}`;
              div.onclick = () => loadTicket(ticketId);
              list.appendChild(div);
            }
          });
      });
    });
}

function loadTicket(ticketId) {
  fetch(`/get_ticket/${ticketId}`)
    .then((res) => res.json())
    .then((data) => {
      currentTicket = ticketId;
      currentProduct = data.product;
      const box = document.getElementById("chatBox");
      box.innerHTML = "";
      data.messages.forEach((msg) => {
        appendMessage(msg.sender || msg.role || Object.keys(msg)[0], msg.text || msg.user || msg.bot);
      });
    });
}

function populateProductDropdown() {
  const dropdown = document.querySelector(".workspace-selector");
  fetch("/tickets")
    .then((res) => res.json())
    .then((tickets) => {
      const products = new Set(["All"]);
      const promises = tickets.map(t =>
        fetch(`/get_ticket/${t.ticket}`)
          .then(res => res.json())
          .then(data => products.add(data.product))
      );
      Promise.all(promises).then(() => {
        dropdown.innerHTML = "";
        products.forEach(p => {
          const opt = document.createElement("option");
          opt.value = p;
          opt.textContent = p;
          dropdown.appendChild(opt);
        });
      });
    });
}

function sendMessage() {
  const input = document.getElementById("userInput");
  const msg = input.value.trim();
  if (!msg) return;

  if (!currentProduct) {
    alert("❗ Please start a new chat and select a product first.");
    return;
  }

  appendMessage("user", msg);
  input.value = "";

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: msg,
      product: currentProduct,
      ticket: currentTicket || "new"
    })
  })
    .then((res) => res.json())
    .then((data) => {
      currentTicket = data.ticket;
      appendMessage("bot", data.reply);
    });
}

function appendMessage(sender, text) {
  const box = document.getElementById("chatBox");
  const div = document.createElement("div");
  div.className = "chat " + sender;
  div.innerText = (sender === "user" ? "You: " : "Bot: ") + text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function startDemo() {
  const box = document.getElementById("chatBox");
  currentProduct = "Wireless Mouse";
  currentTicket = "DEMO1234";
  box.innerHTML = "";

  const messages = [
    { sender: "user", text: "Hi, I need support with a product I bought." },
    { sender: "bot", text: "👋 Hello! Welcome to BotBridge Customer Support. I'm here to assist you.\n\nPlease tell me which product you're facing an issue with." },

    { sender: "user", text: "Wireless Mouse" },
    { sender: "bot", text: "Great! Could you please provide the **purchase date** of the Wireless Mouse?" },

    { sender: "user", text: "March 15, 2024" },
    { sender: "bot", text: "🔍 Checking warranty status for your Wireless Mouse..." },
    { sender: "bot", text: "✅ Good news! Your mouse is still under warranty." },

    { sender: "bot", text: "Can you briefly describe the issue you're facing?" },
    { sender: "user", text: "It suddenly stopped working. No lights. No response." },
    { sender: "bot", text: "I understand, that must be annoying 😕. Let’s troubleshoot this step by step." },

    { sender: "bot", text: "👉 First, have you tried replacing the batteries?" },
    { sender: "user", text: "Yes, still no result." },

    { sender: "bot", text: "Okay. Is the USB receiver securely connected to your device? Try different ports if possible." },
    { sender: "user", text: "I tried. Still dead." },

    { sender: "bot", text: "Got it. This might be a deeper issue. Let me escalate this to the **Mouse Bot** for advanced diagnostics..." },
    { sender: "bot", text: "⏳ Connecting to Mouse Bot...\n🤖 Mouse Bot: Hello! I'm the expert for mouse-related issues. Let’s go deeper." },

    { sender: "bot", text: "Please hold the power button on your mouse for 10 seconds. Do you see any LED blink?" },
    { sender: "user", text: "Nope. Nothing." },

    { sender: "bot", text: "Thank you for confirming. This appears to be a hardware failure.\n📦 You are eligible for a **free replacement** under warranty." },

    { sender: "bot", text: "Could you confirm your shipping address and email ID for dispatch?" },
    { sender: "user", text: "bratish@domain.com, 43/5 New Road, Kolkata" },

    { sender: "bot", text: "📬 Thank you! Your replacement order has been initiated. Tracking details will be sent via email and SMS." },

    { sender: "bot", text: "Would you like to receive SMS alerts for updates?" },
    { sender: "user", text: "Yes, please." },

    { sender: "bot", text: "✅ Done. SMS notifications have been enabled." },

    { sender: "bot", text: "Would you like to **download this chat as a PDF** transcript for your records?" },

    { sender: "user", text: "Sure, that would be helpful." },
    { sender: "bot", text: "Great! You can click on the 📄 PDF button above to download anytime." },

    { sender: "bot", text: "Would you prefer this chat in Hindi, Bengali, or Tamil?" },
    { sender: "user", text: "Try Bengali." },
    { sender: "bot", text: "🔁 Use the 🌐 Translate button above to convert this conversation to Bengali anytime." },

    { sender: "bot", text: "Now, before we end, would you like to speak to a **human agent**?" },
    { sender: "user", text: "No, you've been very helpful!" },

    { sender: "bot", text: "🙏 Thank you for your kind words." },
    { sender: "bot", text: "We’d love to know how your experience was. Could you rate us from 1⭐ to 5⭐?" },
    { sender: "user", text: "5" },

    { sender: "bot", text: "⭐️⭐️⭐️⭐️⭐️ Thank you! We're glad we could help." },

    { sender: "bot", text: "🧠 Would you like us to also **analyze your query sentiment** for training our support AI?" },
    { sender: "user", text: "Sure." },
    { sender: "bot", text: "🔍 Sentiment: Neutral → Calm and composed query." },

    { sender: "bot", text: "🎫 Ticket ID: DEMO1234 has been updated with this conversation." },
    { sender: "bot", text: "📊 Admins can view analytics of this ticket in the Admin Dashboard." },

    { sender: "bot", text: "👨‍💼 If you ever need help again, just start a new chat or search your ticket above." },
    { sender: "bot", text: "🚀 Thank you for using BotBridge. Have a productive day ahead!" }
  ];

  let index = 0;

  function typeNext() {
    if (index >= messages.length) return;

    const msg = messages[index];
    showTypingIndicator();

    setTimeout(() => {
      removeTypingIndicator();
      appendMessage(msg.sender, msg.text);
      index++;
      setTimeout(typeNext, getRandomDelay());
    }, getRandomDelay());
  }

  function showTypingIndicator() {
    const indicator = document.createElement("div");
    indicator.className = "chat bot typing-indicator";
    indicator.id = "typingIndicator";
    indicator.innerText = "Bot is typing...";
    box.appendChild(indicator);
    box.scrollTop = box.scrollHeight;
  }

  function removeTypingIndicator() {
    const typing = document.getElementById("typingIndicator");
    if (typing) typing.remove();
  }

  function getRandomDelay() {
    return Math.floor(Math.random() * 1400) + 1000; // 1000ms - 2400ms
  }

  typeNext();
}
