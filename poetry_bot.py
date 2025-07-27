import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# إنشاء قاعدة البيانات
conn = sqlite3.connect("poems.db")
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS poems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    poet TEXT NOT NULL,
    text TEXT NOT NULL
)
''')
conn.commit()
conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في بوت القصائد!\n"
        "استخدم /add العنوان - الشاعر - النص\n"
        "/list لعرض القصائد"
    )

async def add_poem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = ' '.join(context.args)
    if '-' not in message:
        await update.message.reply_text("❌ الصيغة غير صحيحة. استخدم: /add العنوان - الشاعر - النص")
        return

    try:
        title, poet, text = map(str.strip, message.split('-', 2))
        conn = sqlite3.connect("poems.db")
        c = conn.cursor()
        c.execute("INSERT INTO poems (title, poet, text) VALUES (?, ?, ?)", (title, poet, text))
        conn.commit()
        conn.close()
        await update.message.reply_text("✅ تم حفظ القصيدة بنجاح!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")

async def list_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("poems.db")
    c = conn.cursor()
    c.execute("SELECT title, poet FROM poems ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("📭 لا توجد قصائد محفوظة بعد.")
    else:
        response = "📚 آخر القصائد:\n"
        for i, (title, poet) in enumerate(rows, 1):
            response += f"{i}. {title} - {poet}\n"
        await update.message.reply_text(response)

# التوكن سيتم أخذه من متغير البيئة
import os
TOKEN = os.environ.get("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_poem))
app.add_handler(CommandHandler("list", list_poems))
app.run_polling()