import logging
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# إعدادات التسجيل لمراقبة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- قاعدة بيانات وهمية في الذاكرة (لتجربة البوت) ---
users_db = {}

# --- إعدادات البوت والقيم ---
BOT_TOKEN = "8850940491:AAGJry4qihFiJbwOFI6mjWSphRqiiP5jWLg"
POINTS_PER_TASK = 50  # النقاط لكل مشاهدة
MIN_WITHDRAW_POINTS = 5000  # الحد الأدنى للسحب

# فيديوهات تيك توك عشوائية
TIKTOK_VIDEOS = [
    "https://www.tiktok.com/@explore/video/1",
    "https://www.tiktok.com/@explore/video/2",
    "https://www.tiktok.com/@explore/video/3"
]

# --- لوحات المفاتيح (الأزرار) ---
def main_menu_keyboard():
    keyboard = [
        ["💰 حسابي ورصيدي", "🎯 كسب النقاط"],
        ["💳 سحب الأرباح (كي كارد)", "ℹ️ حول البوت"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- دالات البوت الأساسية ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in users_db:
        users_db[user.id] = {"username": user.username, "points": 0, "balance": 0.0}
    
    welcome_text = f"🎯 أهلاً بك يا {user.first_name} في **بوت زيتونة** للربح!\n\nجمع النقاط الآن من خلال مشاهدة الفيديوهات والإعلانات وحولها إلى أموال حقيقية تسحبها عبر الكي كارد."
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if user_id not in users_db:
        users_db[user_id] = {"username": update.effective_user.username, "points": 0, "balance": 0.0}

    if text == "💰 حسابي ورصيدي":
        points = users_db[user_id]["points"]
        balance = points * 1 
        await update.message.reply_text(
            f"📊 **تفاصيل حسابك:**\n\n"
            f"👤 الاسم: {update.effective_user.first_name}\n"
            f"🪙 نقاطك الحالية: {points} نقطة\n"
            f"💵 رصيدك التقديري: {balance:,} دينار عراقي",
            parse_mode="Markdown"
        )

    elif text == "🎯 كسب النقاط":
        keyboard = [
            [InlineKeyboardButton("🎬 مشاهدة فيديو تيك توك عشوائي", callback_data="watch_tiktok")],
            [InlineKeyboardButton("📺 مشاهدة إعلان سريع", callback_data="watch_ad")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("اختر الطريقة التي تريد كسب النقاط بها الآن:", reply_markup=reply_markup)

    elif text == "💳 سحب الأرباح (كي كارد)":
        points = users_db[user_id]["points"]
        if points < MIN_WITHDRAW_POINTS:
            await update.message.reply_text(
                f"❌ عذراً! الحد الأدنى للسحب هو **{MIN_WITHDRAW_POINTS} نقطة**.\n"
                f"أنت تملك الآن {points} نقطة فقط. استمر في المشاهدة لتصل للحد المطلوب!",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "📥 للبدء بعملية السحب، يرجى كتابة رقم بطاقة **الكي كارد (Qi Card)** الخاصة بك المكون من 16 رقماً، متبوعاً باسمك الكامل.\n\n"
                "مثال للإرسال:\n`4000123456789012 - ابراهيم حاتم`",
                parse_mode="Markdown"
            )
            context.user_data['awaiting_withdraw'] = True

    elif text == "ℹ️ حول البوت":
        await update.message.reply_text(
            "🤖 **بوت زيتونة الذكي**\n\n"
            "منصة عراقية مصغرة لربح المال عبر تجميع النقاط من المهام اليومية البسيطة مثل مشاهدة الفيديوهات والإعلانات.\n"
            "يتم تحويل الأرباح يدوياً عبر الكي كارد بعد مراجعة الطلبات لضمان الأمان.",
            parse_mode="Markdown"
        )
    
    elif context.user_data.get('awaiting_withdraw'):
        card_details = text
        points = users_db[user_id]["points"]
        balance = points * 1
        
        users_db[user_id]["points"] = 0
        context.user_data['awaiting_withdraw'] = False
        
        await update.message.reply_text(
            f"✅ **تم استلام طلب السحب بنجاح!**\n\n"
            f"💳 تفاصيل البطاقة: {card_details}\n"
            f"💵 المبلغ المستحق: {balance:,} دينار عراقي\n\n"
            f"سيتم مراجعة الطلب وتحويل المبلغ إلى حسابك خلال 24 ساعة. شكراً لك!",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        print(f"🚨 [طلب سحب جديد] المستخدم {user_id} طلب سحب بمبلغ {balance} دينار على البيانات: {card_details}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "watch_tiktok":
        video_url = random.choice(TIKTOK_VIDEOS)
        users_db[user_id]["points"] += POINTS_PER_TASK
        
        keyboard = [[InlineKeyboardButton("🔗 اضغط هنا لمشاهدة الفيديو", url=video_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎬 شاهد الفيديو عبر الرابط بالأسفل لمدة 15 ثانية على الأقل.\n\n"
            f"💰 تم إضافة **{POINTS_PER_TASK} نقطة** إلى حسابك تلقائياً!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif query.data == "watch_ad":
        users_db[user_id]["points"] += POINTS_PER_TASK
        await query.edit_message_text(
            f"📺 **إعلان مدعوم:**\n"
            f"موقع زيتونة للتصميم والخدمات الرقمية يقدم لكم أفضل الحلول!\n\n"
            f"💰 شكرًا لمشاهدتك الإعلان، تم إضافة **{POINTS_PER_TASK} نقطة** لحسابك.",
            parse_mode="Markdown"
        )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 بوت زيتونة يعمل الآن بنجاح...")
    application.run_polling()

if __name__ == '__main__':
    main()
