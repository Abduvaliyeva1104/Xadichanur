import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

# === SOZLAMALAR ===
BOT_TOKEN = "8995916631:AAGrN4fm1jn07MO0q69hp4Sm08faqahhJRI"
ADMIN_ID = 7057064228  # !!! Bu yerga @userinfobot bergan RAQAMLI ID ingizni yozing (qo'shtirnoqsiz)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === MA'LUMOTLAR BAZASINI YARATISH ===
def init_db():
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            sizes TEXT NOT NULL,
            price TEXT NOT NULL,
            photo_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# === ADMIN STATUSINI TEKSHIRISH (/admin buyrug'i) ===
@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👑 **Siz ADMIN rejimidasiz!**\n\n"
            "Yangi kiyim qo'shish uchun menga kiyimning **RASMINI** yuboring "
            "va rasm ostidagi izohga (caption) quyidagicha yozing:\n\n"
            "`Nomi | O'lchamlari | Narxi`\n\n"
            "Rasm ostiga yozishga namuna:\n"
            "`Yashil pijak | S, M, L | 280 000 so'm`",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"⛔ Siz admin emassiz!\nSizning ID ingiz: `{message.from_user.id}`\n"
            f"Koddagi ADMIN_ID bilan solishtirib ko'ring.",
            parse_mode="Markdown"
        )
        # === BAZADAGI BARCHA KIYIMLARNI KO'RISH ===
@dp.message(Command("list"), F.from_user.id == ADMIN_ID)
async def list_products(message: Message):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, price FROM products")
    items = cursor.fetchall()
    conn.close()

    if not items:
        await message.answer("📦 Bazada hech qanday kiyim yo'q.")
        return

    text = "📋 **Bazadagi kiyimlar ro'yxati:**\n\n"
    for item_id, title, price in items:
        text += f"🆔 **{item_id}** | {title} - {price}\n"
    
    text += "\nO'chirish uchun: `/del ID` yozing (Masalan: `/del 1`)"
    await message.answer(text, parse_mode="Markdown")

# === KIYIMNI ID BO'YICHA O'CHIRISH ===
@dp.message(Command("del"), F.from_user.id == ADMIN_ID)
async def delete_product(message: Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("⚠️ O'chirish uchun ID raqamini kiriting!\nMasalan: `/del 2`", parse_mode="Markdown")
        return

    product_id = int(args[1])

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    await message.answer(f"🗑 IDsi **{product_id}** bo'lgan kiyim bazadan o'chirildi!", parse_mode="Markdown")

# === KIYIM QO'SHISH (RASM + IZOH) ===
@dp.message(F.photo)
async def add_product(message: Message):
    if message.from_user.id != ADMIN_ID:
        return  # Oddiy foydalanuvchilar kiyim qo'sha olmaydi

    if not message.caption or "|" not in message.caption:
        await message.answer("⚠️ Xatolik! Rasm ostiga ma'lumotni quyidagi formatda kiriting:\n`Nomi | O'lchamlari | Narxi`", parse_mode="Markdown")
        return

    parts = [p.strip() for p in message.caption.split("|")]
    if len(parts) != 3:
        await message.answer("⚠️ Xatolik! 3 ta ma'lumotni `|` belgisi bilan ajratib yozing.", parse_mode="Markdown")
        return

    title, sizes, price = parts
    photo_id = message.photo[-1].file_id

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (title, sizes, price, photo_id) VALUES (?, ?, ?, ?)",
        (title, sizes, price, photo_id)
    )
    conn.commit()
    conn.close()

    await message.answer(f"✅ **'{title}'** bazaga muvaffaqiyatli qo'shildi!", parse_mode="Markdown")

# === ODDIY FOYDALANUVCHILAR UCHUN (/start va Qidiruv) ===
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Assalomu alaykum! Kiyim-kechak do'konimizga xush kelibsiz! ✨\n\n"
        "O'zingizga yoqqan kiyim nomini yozib yuboring (masalan: *pijak*, *ko'ylak*), "
        "men sizga rasmi, o'lchamlari va narxini topib beraman!",
        parse_mode="Markdown"
    )

@dp.message(F.text & ~F.text.startswith("/"))
async def search_clothes(message: Message):
    query = message.text.strip().lower()
    
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, sizes, price, photo_id FROM products WHERE LOWER(title) LIKE ?", (f"%{query}%",))
    items = cursor.fetchall()
    conn.close()

    if not items:
        await message.answer("Afsuski, bunday nomdagi kiyim topilmadi 😔")
        return

    for title, sizes, price, photo_id in items:
        caption = (
            f"👗 **Nomi:** {title}\n"
            f"📏 **O'lchamlari:** {sizes}\n"
            f"💰 **Narxi:** {price}\n\n"
            f"📞 Buyurtma berish uchun admin bilan bog'laning.Telefon raqam:889692522,Telegram:@Abduvaliyeva1104"
        )
        await message.answer_photo(photo=photo_id, caption=caption, parse_mode="Markdown")

# === ISHGA TUSHIRISH ===
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
