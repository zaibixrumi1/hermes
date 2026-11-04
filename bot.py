import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = str(update.message.chat_id)
    
    env = os.environ.copy()
    env["GROQ_BASE_URL"] = "https://api.groq.com/openai/v1"
    env["HERMES_MODEL"] = "llama3-70b-8192"
    
    try:
        # Remove the stale lock file before calling Hermes
        lock_file = "/root/.hermes/installs/8a4017c4cabfe15f/.install.lock"
        if os.path.exists(lock_file):
            os.remove(lock_file)

        result = subprocess.run(
            ["hermes", "-z", f"User ID: {chat_id}\nMessage: {user_text}"], 
            capture_output=True, text=True, env=env, timeout=120
        )
        reply = result.stdout.strip() or f"Error: {result.stderr}"
    except Exception as e:
        reply = f"Error: {str(e)}"
        
    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
