from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import random

user_tasks = {}
adding_tasks = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Ира — твой планировщик задач 💛 С моей помощью ты с легкостью будешь всё успевать и ничего не забывать! Давай приступим к делу 🤓\n\n"
        "Используй команды:\n"
        "/add – добавить задачи\n"
        "/list – показать список задач"
    )

# Команда /add
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    adding_tasks[user_id] = True
    await update.message.reply_text(
        "Напиши свои задачи в столбик🩷\nКаждая строка — новая задача."
    )

# Обработка текстовых сообщений
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if adding_tasks.get(user_id):
        user_tasks.setdefault(user_id, [])
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        for line in lines:
            user_tasks[user_id].append({"task": line, "done": False})

        await update.message.reply_text(f"Добавлено {len(lines)} задач! Чтобы посмотреть на список используй /list")
        return

    await update.message.reply_text("Используй /add, чтобы добавить задачи 💛")

# Команда /list
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = user_tasks.get(user_id, [])

    if not tasks:
        await update.message.reply_text("У тебя пока нет задач 💛\nИспользуй /add, чтобы добавить.")
        return

    message = "📋 Твой список задач:\n\n"
    keyboard = []

    for i, t in enumerate(tasks):
        status = "✅" if t["done"] else "❌"
        message += f"{i+1}. {t['task']} {status}\n"
        keyboard.append([InlineKeyboardButton(f"{status} {t['task']}", callback_data=f"toggle_{i}")])

    # Добавляем кнопку создать новый список
    keyboard.append([InlineKeyboardButton("🆕 Создать новый список", callback_data="new_list")])

    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

# Обработка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data

    # Создать новый список
    if data == "new_list":
        user_tasks[user_id] = []
        adding_tasks[user_id] = True
        await query.edit_message_text(
            "Начинаем новый список!\nНапиши задачи в столбик 💛"
        )
        return

    # Тоггл задачи
    if data.startswith("toggle_"):
        index = int(data.split("_")[1])
        tasks = user_tasks.get(user_id, [])

        if 0 <= index < len(tasks):
            tasks[index]["done"] = not tasks[index]["done"]

        # Проверка: все выполнены?
        if tasks and all(t["done"] for t in tasks):
            await query.edit_message_text(
                "✨✨Все задачи выполнены! Я горжусь тобой!💛✨ Продолжай в том же духе! \n \n\n"
                "Если уже хочешь создать новый список, нажми /list и выбери кнопку 🆕"
            )
            return

        # Обновляем список
        message = "📋 Твой список задач:\n\n"
        keyboard = []
        for i, t in enumerate(tasks):
            status = "✅" if t["done"] else "❌"
            message += f"{i+1}. {t['task']} {status}\n"
            keyboard.append([InlineKeyboardButton(f"{status} {t['task']}", callback_data=f"toggle_{i}")])

        keyboard.append([InlineKeyboardButton("🆕 Создать новый список", callback_data="new_list")])

        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token("8543352426:AAG7PLWD44yFrUvrBwHrDcVdIMIORjhP8nk").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling(poll_interval=0.5)
