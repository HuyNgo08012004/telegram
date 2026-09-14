import asyncio
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ĐIỀN TOKEN TỪ BOTFATHER VÀO ĐÂY
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# URL CỦA CORE API (PORT 8000)
CORE_API_URL = "http://localhost:8000/api/v1/chat/completions"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi là Trợ lý AI Pháp lý (DAI Legal AI).\n"
        "Hãy nhập câu hỏi về các thủ tục hành chính để tôi hỗ trợ tra cứu."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    chat_id = str(update.effective_chat.id)
    
    status_msg = await update.message.reply_text("🔍 Đang tra cứu dữ liệu pháp lý...")

    payload = {
        "prompt": user_query,
        "session_id": chat_id
    }

    full_response = ""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", CORE_API_URL, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        content = line.replace("data: ", "").strip()
                        if content and content != "[DONE]":
                            full_response += content

        if full_response:
            await status_msg.edit_text(full_response)
        else:
            await status_msg.edit_text("Mình chưa tìm thấy thông tin phù hợp trong dữ liệu hiện có.")

    except Exception as e:
        await status_msg.edit_text(f"Đã xảy ra lỗi kết nối tới Core API: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Telegram Bot DAI Legal AI đang lắng nghe yêu cầu...")
    app.run_polling()
