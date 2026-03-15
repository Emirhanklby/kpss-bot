"""
KPSS Telegram Bot - Gemini 2.5 Flash-Lite
==========================================
Kurulum:
  pip install python-telegram-bot google-generativeai

Çalıştırma:
  python kpss_bot.py

.env yerine doğrudan bu dosyada TELEGRAM_TOKEN ve GEMINI_API_KEY değerlerini gir.
"""

import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import google.generativeai as genai

# ─────────────────────────────────────────
# 🔑 BURAYA KENDİ KEY'LERİNİ GİR
# ─────────────────────────────────────────
TELEGRAM_TOKEN = "BURAYA_TELEGRAM_BOT_TOKEN"   # BotFather'dan al
GEMINI_API_KEY = "BURAYA_GEMINI_API_KEY"        # aistudio.google.com'dan al
# ─────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Gemini yapılandırması
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Sen bir KPSS sınav asistanısın. Görevin şunlardır:

1. **Konu Alanları:** Tarih, Coğrafya ve Vatandaşlık konularında sorular sor ve açıklama yap.

2. **Test Modu:** Kullanıcı "test" veya "soru sor" dediğinde 5 soruluk çoktan seçmeli test üret.
   - Her soruyu A) B) C) D) E) şıklarıyla ver
   - Kullanıcı cevapladıktan sonra doğru/yanlış bildir
   - Yanlış cevaplarda KISA ama net açıklama yap

3. **Özet Modu:** Kullanıcı "özet" veya "anlat" dediğinde konuyu madde madde, kısa özetle anlat.

4. **Tekrar Modu:** Kullanıcı "tekrar" dediğinde daha önce yanlış yaptığı veya zor gelen konuları tekrar sor.

5. **Serbest Soru:** Kullanıcının her sorusunu doğrudan cevapla.

6. **Telegram Formatı:** 
   - Cevapların kısa ve öz olsun (Telegram için uygun)
   - Emoji kullan ama abartma
   - Başlıkları **kalın** yaz
   - Listeler için • kullan

7. **Motivasyon:** Zaman zaman kısa motivasyon cümleleri ekle.

Kullanıcı sana Türkçe yazacak, sen de Türkçe cevap ver."""

# Kullanıcı başına konuşma geçmişi tutan sözlük
conversation_history: dict[int, list] = {}

# Menü klavyesi
MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["📝 Test Çöz", "📚 Özet İste"],
        ["🔄 Tekrar", "❓ Soru Sor"],
        ["📊 Konular", "🆘 Yardım"],
    ],
    resize_keyboard=True,
)


def get_model():
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite-preview-06-17",
        system_instruction=SYSTEM_PROMPT,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    conversation_history[user_id] = []  # Yeni konuşma başlat

    await update.message.reply_text(
        f"👋 Merhaba {user.first_name}!\n\n"
        "Ben senin **KPSS Asistanın**'ım. 🎓\n\n"
        "Tarih, Coğrafya ve Vatandaşlık konularında:\n"
        "• Test çözebilirsin\n"
        "• Konu özeti isteyebilirsin\n"
        "• Soru sorabilirsin\n"
        "• Tekrar yapabilirsin\n\n"
        "Aşağıdaki menüyü kullanabilir veya direkt yazabilirsin. Başlayalım! 💪",
        reply_markup=MAIN_MENU,
        parse_mode="Markdown",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text(
        "🔄 Konuşma geçmişi sıfırlandı. Yeni konuya başlayabiliriz!",
        reply_markup=MAIN_MENU,
    )


async def konular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 **Çalışabileceğin Konular:**\n\n"
        "📜 **TARİH**\n"
        "• Osmanlı Tarihi\n"
        "• Kurtuluş Savaşı\n"
        "• Atatürk İlke ve İnkılapları\n"
        "• Cumhuriyet Tarihi\n\n"
        "🗺️ **COĞRAFYA**\n"
        "• Türkiye'nin Coğrafi Özellikleri\n"
        "• İklim ve Bitki Örtüsü\n"
        "• Nüfus ve Yerleşme\n"
        "• Ekonomik Coğrafya\n\n"
        "⚖️ **VATANDAŞLIK**\n"
        "• Anayasa\n"
        "• Devletin Temel Organları\n"
        "• Temel Hak ve Özgürlükler\n"
        "• Seçim Sistemi\n\n"
        "Bir konu yaz veya 'test çöz' de! 🚀",
        reply_markup=MAIN_MENU,
        parse_mode="Markdown",
    )


async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 **Komutlar:**\n\n"
        "/start - Botu başlat\n"
        "/reset - Konuşmayı sıfırla\n"
        "/konular - Konu listesi\n\n"
        "**Kullanım örnekleri:**\n"
        "• *\"Osmanlıdan 5 soruluk test yap\"*\n"
        "• *\"Anayasa konusunu özetle\"*\n"
        "• *\"Atatürk ilkeleri nedir?\"*\n"
        "• *\"Tekrar soru sor\"*\n"
        "• *\"Coğrafyadan zor soru\"*",
        reply_markup=MAIN_MENU,
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Menü butonlarını doğal dile çevir
    button_map = {
        "📝 Test Çöz": "Bana 5 soruluk çoktan seçmeli KPSS testi yap. Tarih, Coğrafya veya Vatandaşlık konularından karışık olsun.",
        "📚 Özet İste": "Hangi konuyu özetlemememi istersin? Seçenekler: Tarih, Coğrafya, Vatandaşlık",
        "🔄 Tekrar": "Bana tekrar soruları sor, özellikle zor veya sık çıkan konulardan.",
        "❓ Soru Sor": "Sana bir soru sormak istiyorum, hazır mısın?",
        "📊 Konular": None,  # Özel handler
        "🆘 Yardım": None,   # Özel handler
    }

    if user_text == "📊 Konular":
        await konular(update, context)
        return
    if user_text == "🆘 Yardım":
        await yardim(update, context)
        return

    # Buton metnini natural dile çevir
    actual_text = button_map.get(user_text, user_text)

    # Konuşma geçmişini başlat
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Geçmişi al ve yeni mesajı ekle
    history = conversation_history[user_id]
    history.append({"role": "user", "parts": [actual_text]})

    # Geçmiş çok uzarsa eski mesajları at (son 20 mesaj tut)
    if len(history) > 20:
        history = history[-20:]
        conversation_history[user_id] = history

    # "Yazıyor..." göster
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        model = get_model()
        chat = model.start_chat(history=history[:-1])  # Son mesaj hariç geçmiş
        response = chat.send_message(actual_text)
        reply = response.text

        # Asistan cevabını geçmişe ekle
        history.append({"role": "model", "parts": [reply]})

        # Telegram 4096 karakter sınırı
        if len(reply) > 4000:
            # Uzun cevabı böl
            chunks = [reply[i:i+4000] for i in range(0, len(reply), 4000)]
            for chunk in chunks:
                await update.message.reply_text(
                    chunk, reply_markup=MAIN_MENU, parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(
                reply, reply_markup=MAIN_MENU, parse_mode="Markdown"
            )

    except Exception as e:
        logging.error(f"Hata: {e}")
        await update.message.reply_text(
            "⚠️ Bir hata oluştu. Lütfen tekrar dene veya /reset yaz.",
            reply_markup=MAIN_MENU,
        )


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("konular", konular))
    app.add_handler(CommandHandler("yardim", yardim))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 KPSS Bot çalışıyor... (Durdurmak için Ctrl+C)")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
