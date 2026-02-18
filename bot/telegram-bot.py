from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

print("=== SCRIPT STARTED ===")

PARSER_URL = "https://parser-for-azubi-hobby-project.onrender.com/parse"
PAGE_SIZE = 20


async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = requests.get(PARSER_URL)
    vacancies = response.json()  # список строк
    
    # сохраняем в память
    context.user_data["vacancies"] = vacancies
    context.user_data["page"] = 0
    
    await send_page(update, context)


async def send_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vacancies = context.user_data["vacancies"]
    page = context.user_data["page"]
    
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = vacancies[start:end]
    
    text = "\n\n".join(chunk)
    
    # есть ли ещё вакансии?
    has_more = end < len(vacancies)
    
    keyboard = []
    if has_more:
        keyboard = [[
            InlineKeyboardButton("Показать ещё", callback_data="more"),
            InlineKeyboardButton("Стоп", callback_data="stop")
        ]]
    
    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    if update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=markup)
    else:
        await update.message.reply_text(text, reply_markup=markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "more":
        context.user_data["page"] += 1
        await send_page(update, context)
    elif query.data == "stop":
        await query.message.reply_text("Окей, останавливаемся!")


def main():
    print("Starting bot...")  # добавь эту строку
    app = Application.builder().token("8301507931:AAFRIt8vfo7v82EyoaV7WFApV3Df8VkNCbM").build()

    print("Adding handlers...")  # и эту
    app.add_handler(CommandHandler("parse", parse))
    app.add_handler(CallbackQueryHandler(button))

    print("Starting polling...")  # и эту
    app.run_polling()


if __name__ == "__main__":
    main()
