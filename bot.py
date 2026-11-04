import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. This keeps Render awake 24/7
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_pinger():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), PingHandler).serve_forever()

# 2. This talks to Telegram and Hermes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = str(update.message.chat_id)
    
    env = os.environ.copy()
    env["OPENROUTER_BASE_URL"] = "https://openrouter.ai/api/v1"
    env["HERMES_MODEL"] = "anthropic/claude-3.5-sonnet"
    
    try:
        result = subprocess.run(
            ["hermes", "run", f"User ID: {chat_id}\nMessage: {user_text}"], 
            capture_output=True, text=True, env=env, timeout=120
        )
        reply = result.stdout.strip() or f"Error: {result.stderr}"
    except Exception as e:
        reply = f"Error: {str(e)}"
        
    await update.message.reply_text(reply)

# 3. Starts everything
if __name__ == "__main__":
    threading.Thread(target=run_pinger, daemon=True).start()
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
