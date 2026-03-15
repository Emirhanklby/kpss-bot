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
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# ─────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Gemini yapılandırması
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """Sen bir KPSS sinav asistanisin. Gorev alanlarin:

1. KONU ALANLARI - Sadece su konularda sorular sor ve aciklama yap:

   TARIH:
   - İslamiyet Oncesi Turk Tarihi
   - Turk-Islam Devletleri
   - Osmanli Devleti Siyasi Gelismeleri
   - Osmanli Kultur ve Uygarliği
   - Kurtulus Savasi Sureci
   - Ataturk İlke ve İnkilaplari
   - Ataturk Donemi İc ve Dis Politika
   - Cagdas Turk ve Dunya Tarihi

   COGRAFYA:
   - Turkiye'nin Cografi Konumu
   - Yer Sekilleri ve Dogal Ozellikler
   - İklim ve Bitki Ortusu
   - Nufus ve Yerlesme
   - Tarim ve Ekonomik Faaliyetler
   - Madenler ve Enerji Kaynaklari
   - Ulasim ve Turizm
   - Turkiye'nin Cografi Bolgeleri

   VATANDASLIK:
   - Hukukun Temel Kavramlari
   - Anayasa Hukuku
   - Yasama Organi
   - Yurutme Organi
   - Yargi Sistemi
   - Temel Hak ve Ozgurlukler
   - İdare Hukuku
   - Uluslararasi Kuruluslar

2. TEST MODU: Kullanici "test" veya "soru sor" dediginde 5 soruluk coktan secmeli test uret.
   - Her soruyu A) B) C) D) E) siklarıyla ver
   - Kullanici cevapladiktan sonra dogru/yanlis bildir
   - Yanlis cevaplarda kisa ama net aciklama yap
   - Dogru cevaplarda tebrik et

3. OZET MODU: Kullanici "ozet" veya "anlat" dediginde konuyu madde madde, kisa ozetle anlat.

4. TEKRAR MODU: Kullanici "tekrar" dediginde daha once yanlis yaptigi veya zor gelen konulari tekrar sor.

5. SERBEST SORU: Kullanicinin her sorusunu dogrudan cevapla.

6. FORMAT:
   - Cevaplar kisa ve oz olsun (Telegram icin uygun)
   - Emoji kullan ama abartma
   - Sorulari numaralandir
   - Aciklamalar net ve anlasilir olsun

7. MOTİVASYON: Zaman zaman kisa motivasyon cumleleri ekle.

Kullanici Turkce yazacak, sen de Turkce cevap ver."""

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
        model_name="gemini-2.5-flash-lite",
        system_instruction=SYSTEM_PROMPT,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    conversation_history[user_id] = []  # Yeni konuşma başlat

    await update.message.reply_text(
        f"Merhaba {user.first_name}! 👋\n\n"
        "Ben senin KPSS Asistanin! 🎓\n\n"
        "Tarih, Cografya ve Vatandaslik konularinda:\n"
        "- Test cozebilirsin\n"
        "- Konu ozeti isteyebilirsin\n"
        "- Soru sorabilirsin\n"
        "- Tekrar yapabilirsin\n\n"
        "Asagidaki menuyu kullanabilir veya direkt yazabilirsin. Baslayalim! 💪",
        reply_markup=MAIN_MENU,
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
        "📋 KPSS Konulari:\n\n"
        "📜 TARİH\n"
        "1. İslamiyet Oncesi Turk Tarihi\n"
        "2. Turk-Islam Devletleri\n"
        "3. Osmanli Devleti Siyasi Gelismeleri\n"
        "4. Osmanli Kultur ve Uygarliği\n"
        "5. Kurtulus Savasi Sureci\n"
        "6. Ataturk İlke ve İnkilaplari\n"
        "7. Ataturk Donemi İc ve Dis Politika\n"
        "8. Cagdas Turk ve Dunya Tarihi\n\n"
        "🗺 COGRAFYA\n"
        "1. Turkiye'nin Cografi Konumu\n"
        "2. Yer Sekilleri ve Dogal Ozellikler\n"
        "3. İklim ve Bitki Ortusu\n"
        "4. Nufus ve Yerlesme\n"
        "5. Tarim ve Ekonomik Faaliyetler\n"
        "6. Madenler ve Enerji Kaynaklari\n"
        "7. Ulasim ve Turizm\n"
        "8. Turkiye'nin Cografi Bolgeleri\n\n"
        "⚖ VATANDASLIK\n"
        "1. Hukukun Temel Kavramlari\n"
        "2. Anayasa Hukuku\n"
        "3. Yasama Organi\n"
        "4. Yurutme Organi\n"
        "5. Yargi Sistemi\n"
        "6. Temel Hak ve Ozgurlukler\n"
        "7. İdare Hukuku\n"
        "8. Uluslararasi Kuruluslar\n\n"
        "Bir konu yaz veya 'test coz' de! 🚀",
        reply_markup=MAIN_MENU,
    )


async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Komutlar:\n\n"
        "/start - Botu baslat\n"
        "/reset - Konusmayı sifirla\n"
        "/konular - Konu listesi\n\n"
        "Kullanim ornekleri:\n"
        "- Osmanlidan 5 soruluk test yap\n"
        "- Anayasa konusunu ozetle\n"
        "- Ataturk ilkeleri nedir?\n"
        "- Tekrar soru sor\n"
        "- Cografyadan zor soru\n"
        "- Vatandasliktan karma test",
        reply_markup=MAIN_MENU,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Menü butonlarını doğal dile çevir
    button_map = {
        "📝 Test Çöz": "Bana 5 soruluk coktan secmeli KPSS testi yap. Tarih, Cografya ve Vatandaslik konularından karisik olsun.",
        "📚 Özet İste": "Hangi konuyu ozetlemememi istersin? Tarih, Cografya veya Vatandaslik seceneklerinden birini sec.",
        "🔄 Tekrar": "Bana tekrar sorular sor, ozellikle zor veya sik cikan konulardan.",
        "❓ Soru Sor": "Sana bir soru sormak istiyorum, hazir misin?",
        "📊 Konular": None,
        "🆘 Yardım": None,
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
            chunks = [reply[i:i+4000] for i in range(0, len(reply), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk, reply_markup=MAIN_MENU)
        else:
            await update.message.reply_text(reply, reply_markup=MAIN_MENU)

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
