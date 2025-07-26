from flask import Flask, request, jsonify, send_file, render_template
import os, uuid, csv
from textblob import TextBlob
from googletrans import Translator
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)

brand_bots = {
    "mouse": "Mouse Bot",
    "keyboard": "Keyboard Bot",
    "monitor": "Monitor Bot",
    "default": "Generic Bot"
}

chat_data = {}
LOG_FILE = "chat_logs.csv"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get("message")
    ticket = data.get("ticket")
    product = data.get("product", "default").lower()
    is_demo = data.get("demo", False)

    if not ticket:
        ticket = f"TICKET{str(uuid.uuid4())[:8].upper()}"
        chat_data[ticket] = {"product": product, "history": []}
    elif ticket not in chat_data:
        chat_data[ticket] = {"product": product, "history": []}

    chat = chat_data[ticket]

    if is_demo:
        bot_reply = f"👋 Hello! I'm the {brand_bots.get(product, 'Support Bot')}."
    elif not product or product == "default":
        return jsonify({"reply": "Please select a product to continue.", "ticket": ticket})
    else:
        bot_reply = f"This is a response from {brand_bots.get(product, 'Support Bot')} regarding your query: '{message}'"

    polarity = TextBlob(message).sentiment.polarity
    sentiment = "Positive" if polarity > 0.2 else "Negative" if polarity < -0.2 else "Neutral"

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), ticket, product, message, bot_reply, sentiment, ""])

    chat["history"].append({"user": message})
    chat["history"].append({"bot": bot_reply})

    return jsonify({"reply": bot_reply, "ticket": ticket, "actions": ["Approve Return", "Reject Complaint"]})

@app.route('/get_ticket/<ticket_id>')
def get_ticket(ticket_id):
    if ticket_id in chat_data:
        return jsonify({
            "ticket": ticket_id,
            "product": chat_data[ticket_id]["product"],
            "messages": chat_data[ticket_id]["history"]
        })
    else:
        return jsonify({"error": "Ticket not found"}), 404

@app.route('/tickets')
def get_tickets():
    tickets = []
    for ticket_id, chat in chat_data.items():
        tickets.append({
            "ticket": ticket_id,
            "product": chat.get("product", "Unknown"),
            "messages": chat.get("history", [])
        })
    return jsonify(tickets)

@app.route('/transcript/<ticket>')
def transcript(ticket):
    if ticket not in chat_data:
        return "Ticket not found", 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Transcript for {ticket}", ln=True, align='C')
    pdf.ln(10)

    for msg in chat_data[ticket]["history"]:
        if "user" in msg:
            pdf.multi_cell(0, 10, txt=f"You: {msg['user']}")
        elif "bot" in msg:
            pdf.multi_cell(0, 10, txt=f"Bot: {msg['bot']}")
        pdf.ln(2)

    filename = f"{ticket}_transcript.pdf"
    filepath = os.path.join("static", filename)
    pdf.output(filepath)

    return send_file(filepath, as_attachment=True)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get("text", "")
    target_lang = data.get("lang", "en")

    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_lang)
        return jsonify({"translated": translated.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def inject_dummy_chats():
    dummy_tickets = {
        "TICKET001": {
            "product": "mouse",
            "history": [
                {"user": "Hi, my wireless mouse is not working anymore."},
    {"bot": "👋 Hello! I’m here to assist you with your mouse issue. May I know when you purchased it?"},
    {"user": "March 2024"},
    {"bot": "⏳ Checking warranty status..."},
    {"bot": "✅ Your mouse is still under warranty."},
    {"bot": "Let’s troubleshoot. Is there any LED indicator lighting up on the mouse?"},
    {"user": "Nope, no lights."},
    {"bot": "Alright. Please confirm – have you tried changing the batteries or charging it?"},
    {"user": "Yes, I’ve already tried that."},
    {"bot": "Could you test it on a different computer or USB port?"},
    {"user": "Yes, still no response."},
    {"bot": "📶 Understood. Any recent drops or water spills?"},
    {"user": "No drops. I keep it safely."},
    {"bot": "Thanks. It seems like an internal hardware failure."},
    {"bot": "🔁 Transferring to Mouse Bot for deeper analysis..."},
    {"bot": "🤖 Mouse Bot: Thank you for confirming the steps. Based on the behavior, the internal sensor might be damaged."},
    {"bot": "Do you still have the invoice or bill for the purchase?"},
    {"user": "Yes, I have it saved."},
    {"bot": "📎 Please upload it using the upload option below (simulated)."},
    {"user": "Uploaded."},
    {"bot": "✅ Verified. You're eligible for a free replacement."},
    {"bot": "Please confirm your full shipping address."},
    {"user": "22, Garia Main Road, Kolkata – 700084"},
    {"bot": "📦 Replacement has been initiated. You'll receive tracking via email."},
    {"bot": "📄 You can download a PDF of this entire chat using the 'Download PDF' button."},
    {"bot": "🌐 Want to read this in Hindi or Bengali? Use the 'Translate' button."},
    {"bot": "🙋 Would you like to talk to a human agent now?"},
    {"user": "No thanks, this was perfect."},
    {"bot": "😊 Happy to help!"},
    {"bot": "⭐ How would you rate your support experience today?"},
    {"user": "5"},
    {"bot": "🎉 Thanks for your feedback!"},
    {"bot": "📌 Ticket ID: TICKET001 has been marked as **resolved with replacement issued**."},
    {"bot": "👋 You can now close the chat or continue asking more questions."}
  ]
        },
        "TICKET002": {
            "product": "keyboard",
            "history": [
                {"user": "Hi, some keys on my keyboard are stuck and won’t press down properly."},
    {"bot": "👋 Hello! I'm here to help. Which specific keys are giving you trouble?"},
    {"user": "Spacebar, Shift and A."},
    {"bot": "Got it. Was there any liquid spill or dust recently?"},
    {"user": "Just some crumbs I think."},
    {"bot": "Okay. Try turning it upside down and gently tapping it."},
    {"user": "Done. A little improvement."},
    {"bot": "Now use compressed air around the keys."},
    {"user": "Let me do that... okay, done."},
    {"bot": "Any difference now?"},
    {"user": "Yes, a bit better but still sticky."},
    {"bot": "🔁 Let me connect you to the Keyboard Bot..."},
    {"bot": "🤖 Keyboard Bot: Welcome! You may need a deep cleaning service."},
    {"bot": "Would you like to schedule a free pickup for maintenance (under warranty)?"},
    {"user": "Yes, that would help."},
    {"bot": "📍 Please provide your complete address and contact email."},
    {"user": "56 Park Street, Delhi – bratish@example.com"},
    {"bot": "🛠️ Service ticket created. Pickup scheduled in 48 hours."},
    {"bot": "✅ Confirmation will be sent to your email."},
    {"bot": "📄 Click 'Download PDF' to save this transcript."},
    {"bot": "🌍 Want to translate this chat? Hit the Translate button!"},
    {"bot": "🙋 Would you like to speak to our human support staff?"},
    {"user": "No, everything’s clear."},
    {"bot": "💬 Great!"},
    {"bot": "⭐ Could you rate this interaction from 1–5 stars?"},
    {"user": "4"},
    {"bot": "Thank you for the feedback. We’ll keep improving!"},
    {"bot": "📌 Ticket TICKET002 is now active and awaiting pickup for cleaning."},
    {"bot": "🎯 Feel free to reopen this chat if any issues remain."}
  ]
        },
        "TICKET003": {
            "product": "monitor",
            "history": [
                {"user": "My monitor is not powering on. The screen is completely black."},
    {"bot": "👋 Hi! Let’s check that together. Is the power cable plugged in tightly?"},
    {"user": "Yes, I double-checked."},
    {"bot": "Any light on the power button? Blinking or solid?"},
    {"user": "No lights at all."},
    {"bot": "Have you tried using another wall socket or a different cable?"},
    {"user": "Yes, I tried both. Still the same."},
    {"bot": "Alright. Could you try a hard reset: unplug, hold power button for 30s, then reconnect?"},
    {"user": "Doing that now... nope, no change."},
    {"bot": "🔁 Connecting you to Monitor Bot for further help..."},
    {"bot": "🤖 Monitor Bot: Thank you for the diagnostic steps."},
    {"bot": "This seems to be a power board failure."},
    {"bot": "📅 What is the date of purchase of the monitor?"},
    {"user": "Nov 2023"},
    {"bot": "✅ Great, still under warranty."},
    {"bot": "Do you still have the invoice?"},
    {"user": "Yes, I can upload it."},
    {"bot": "📎 Upload complete. Verifying..."},
    {"bot": "✅ Verification successful."},
    {"bot": "📦 Replacement pickup has been scheduled from your address. Please share your details."},
    {"user": "9th Avenue, Bangalore – bratish@demo.com"},
    {"bot": "📧 You’ll receive pickup confirmation via email."},
    {"bot": "📄 Click the PDF icon to get a copy of this chat."},
    {"bot": "🌐 Translate this conversation in your native language using Translate."},
    {"bot": "🙋 Need to escalate to a customer support executive?"},
    {"user": "No, you’ve covered everything."},
    {"bot": "😊 That’s great to hear!"},
    {"bot": "⭐ Please rate our support from 1 to 5."},
    {"user": "5"},
    {"bot": "🎉 Thank you for your rating!"},
    {"bot": "📌 Ticket TICKET003 has been logged with **replacement in progress**."},
    {"bot": "💬 You may reopen the ticket or start a new one anytime from the sidebar."}
  ]
        }
    }
    chat_data.update(dummy_tickets)
if __name__ == '__main__':
    inject_dummy_chats()
    app.run(debug=True)

