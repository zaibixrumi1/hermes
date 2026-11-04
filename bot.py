import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. Pinger (Keeps Render awake)
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_pinger():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), PingHandler).serve_forever()

# 2. Telegram + Hermes Logic
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = str(update.message.chat_id)
    
    env = os.environ.copy()
    env["GROQ_BASE_URL"] = "https://api.groq.com/openai/v1"
    env["HERMES_MODEL"] = "llama3-70b-8192"
    
    try:
        # Using -z for one-shot script mode instead of 'run'
        result = subprocess.run(
            ["hermes", "-z", f"User ID: {chat_id}\nMessage: {user_text}"], 
            capture_output=True, text=True, env=env, timeout=120
        )
        reply = result.stdout.strip() or f"Error: {result.stderr}"
    except Exception as e:
        reply = f"Error: {str(e)}"
        
    await update.message.reply_text(reply)

# 3. Start Bot
if __name__ == "__main__":
    threading.Thread(target=run_pinger, daemon=True).start()
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
