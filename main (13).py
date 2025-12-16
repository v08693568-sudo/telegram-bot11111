from random import choice, randint, shuffle
from sqlite3 import connect
from datetime import datetime

from telebot import TeleBot
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton as IB,
    InlineKeyboardMarkup as IKM,
    LabeledPrice as LP,
    Message,
)

bot = TeleBot("BOT_TOKEN")

MAIN_ADMIN_ID = 7840708129 # Замените на реальный user_id главного админа

# URL изображения, которое должно отправляться с каждым сообщением
IMAGE_URL = "https://promokod.com/wp-content/uploads/2024/07/ggsel.png"

# Сервисный процент комиссии, используется в уведомлении продавцу
SERVICE_FEE = 0.03  # 3% как в примере (1000 -> 1030)

# Простая таблица переводов
TRANSLATIONS = {
    "welcome": {
        "ru": (
            "Добро пожаловать в GGsel!\n\n"
            "💼 Надёжный сервис для безопасных сделок\n"
            " Всё автоматизировано, быстро и без лишних хлопот.\n\n"
            "🔹 Комиссия сервиса: всего 1%\n"
            "🔹 Поддержка 24/7: @Pregabolin_manager\n"
            "🔹 Ваши сделки под защитой эскроу-сервиса 🛡\n\n"
            " Выберите нужный раздел ниже:"
        ),
        "en": (
            "Welcome to GGSel!\n\n"
            "💼 A reliable escrow service for safe trades\n"
            " Fully automated, fast and hassle-free.\n\n"
            "🔹 Service fee: only 1%\n"
            "🔹 24/7 support: @Pregabolin_manager\n"
            "🔹 Your deals are protected by our escrow service 🛡\n\n"
            " Choose a section below:"
        ),
    },
    "create_order": {"ru": "🧾 Создать сделку", "en": "🧾 Create order"},
    "safety": {"ru": "🛡 Безопасность", "en": "🛡 Safety"},
    "techpod": {"ru": "🆘 Техподдержка", "en": "🆘 Support"},
    "site": {"ru": "🌐 Сайт", "en": "🌐 Website"},
    "change_lang": {"ru": "🌐 Сменить язык", "en": "🌐 Change language"},
    "back": {"ru": "⬅️ Назад", "en": "⬅️ Back"},
    "choose_payment": {"ru": "Выберите валюту сделки:", "en": "Choose payment method:"},
    "rub": {"ru": "💳Рубли", "en": "Rubles"},
    "ton": {"ru": "🪙TON", "en": "TON"},
    "star": {"ru": "⭐Звезды", "en": "Stars"},
    "enter_amount_rub": {"ru": "Введите сумму сделки в рублях:", "en": "Enter the payment amount in rubles:"},
    "enter_amount": {"ru": "Введите сумму оплаты:", "en": "Enter the payment amount:"},
    "enter_description": {
        "ru": "📝 Введите сслыку и детальное описание товара/услуги:",
        "en": "📝 Enter a link and detailed description of the item/service:"
    },
    "desc_too_long": {
        "ru": "Описание слишком длинное. Максимум 512 символов. Сократите текст и отправьте ещё раз:",
        "en": "Description too long. Maximum 512 characters. Shorten the text and send again:"
    },
    "enter_payment_details": {
        "ru": "💳 Введите реквизиты для оплаты (номер карты, номер телефона или другие платежные данные):",
        "en": "💳 Enter payment details (card number, phone number or other payment info):"
    },
    "order_created": {
        "ru": (
            "✅ Сделка #{link} создана!\n\n"
            "💰 Сумма: {amount}\n"
            "📜 Что продаётся: {disc}\n"
            "💳 Реквизиты для оплаты: {payment}\n\n"
            "🔗 Ссылка для покупателя (перешлите её покупателю):\n"
            "https://t.me/{botname}?start={link}\n\n"
            "Сохраните номер ордера: #{link}."
        ),
        "en": (
            "✅ Deal #{link} created!\n\n"
            "💰 Amount: {amount}\n"
            "📜 Item: {disc}\n"
            "💳 Payment details: {payment}\n\n"
            "🔗 Link for buyer (send it to the buyer):\n"
            "https://t.me/{botname}?start={link}\n\n"
            "Save the order number: #{link}."
        ),
    },
    # new translation key for order created without payment details (for STARS)
    "order_created_no_payment": {
        "ru": (
            "✅ Сделка #{link} созданф!\n\n"
            "💰 Сумма: {amount}\n"
            "📜 Что продаётся: {disc}\n\n"
            "🔗 Ссылка для покупателя (перешлите её покупателю):\n"
            "https://t.me/{botname}?start={link}\n\n"
            "Сохраните номер ордера: #{link}."
        ),
        "en": (
            "✅ Deal #{link} created!\n\n"
            "💰 Amount: {amount}\n"
            "📜 Item: {disc}\n\n"
            "🔗 Link for buyer (send it to the buyer):\n"
            "https://t.me/{botname}?start={link}\n\n"
            "Save the order number: #{link}."
        ),
    },
    "enter_valid_amount": {
        "ru": "❌ Пожалуйста, введите корректную сумму (например: 1000 или 1500.50)",
        "en": "❌ Please enter a valid amount (e.g., 1000 or 1500.50)"
    },
    "amount_error": {
        "ru": "❌ Произошла ошибка при обработке суммы. Пожалуйста, попробуйте снова.",
        "en": "❌ An error occurred while processing the amount. Please try again."
    },
    "user_not_found_username": {
        "ru": "Не удалось найти пользователя по этому username. Введите корректный user_id или @username:",
        "en": "Could not find the user by that username. Enter a correct user_id or @username:"
    },
    "cant_manage_main_admin": {
        "ru": "Нельзя управлять правами главного админа через эту команду.",
        "en": "You cannot manage the main admin's rights via this command."
    },
    "insufficient_balance": {"ru": "❌ Недостаотчно средств", "en": "❌ Insufficient balance"},
    "order_not_found": {"ru": "Сделка не найдена.", "en": "Deal not found."},
    "order_already_paid": {"ru": "Эта сделка уже оплачен и закрыт.", "en": "This deal is already paid and closed."},
    "pay_recorded": {"ru": "Оплата зафиксирована. Уведомления отправлены.", "en": "Payment recorded. Notifications have been sent."},
    "techpod_text": {
        "ru": "🆘 Техническая поддержка\n\nЕсли у вас возникли вопросы или сложности со сделкой, напишите в поддержку 👇",
        "en": "🆘 Technical support\n\nIf you have questions or issues with a deal, contact support 👇"
    },
    "safety_text": {
        "ru": (
            "🛡 Правила безопасности GGSel:\n\n"
            "• 🔍 Всегда сверяйте сумму и тег сделки в комментарии к платежу\n"
            "• ✅ После проверки покупатель подтверждает получение, и сделка автоматически закрывается\n\n"
            "Соблюдайте эти рекомендации, чтобы не попасть на мошенников."
        ),
        "en": (
            "🛡 GGSel safety rules:\n\n"
            "• 🔍 Always verify the amount and deal tag in the payment comment\n"
            "• ✅ After verification the buyer confirms receipt and the deal is automatically closed\n\n"
            "Follow these recommendations to avoid fraud."
        )
    },
    "admin_menu_title": {
        "ru": "Админ-панель GGSel. Выберите нужный раздел:",
        "en": "Admin panel GGSel. Choose a section:"
    },
    "admin_stats": {"ru": "📊 Общая статистика", "en": "📊 General statistics"},
    "admin_users": {"ru": "👥 Пользователи", "en": "👥 Users"},
    "admin_orders": {"ru": "📦 Сделки", "en": "📦 Orders"},
    "admin_operators": {"ru": "🧑‍💻 Операторы", "en": "🧑‍💻 Operators"},
    "admin_help": {"ru": "❓ Список текстовых команд", "en": "❓ Command list"},
    "admin_back_to_user": {"ru": "⬅️ В пользовательское меню", "en": "⬅️ Back to user menu"},
    "admin_add_prompt": {
        "ru": "Отправьте user_id или @username пользователя, которого надо добавить в операторы:",
        "en": "Send the user_id or @username of the user to add as an operator:"
    },
    "admin_del_prompt": {
        "ru": "Отправьте user_id или @username оператора, которого нужно удалить:",
        "en": "Send the user_id or @username of the operator to remove:"
    },
    "admin_help_text": {
        "ru": (
            "Команды админа:\n"
            "/admin add <user_id> — добавить админа\n"
            "/admin del <user_id> — удалить админа\n"
            "/admin list — список админов\n"
            "/admin db <table> — показать первые 20 строк таблицы (users/orders/admins)"
        ),
        "en": (
            "Admin commands:\n"
            "/admin add <user_id> — add an admin\n"
            "/admin del <user_id> — remove an admin\n"
            "/admin list — list admins\n"
            "/admin db <table> — show first 20 rows of a table (users/orders/admins)"
        )
    },
    "admin_added": {"ru": "Пользователь {target} добавлен в администраторы.", "en": "User {target} added to admins."},
    "admin_removed": {"ru": "Пользователь {target} удалён из администраторов.", "en": "User {target} removed from admins."},
    "operators_list_empty": {"ru": "🧑‍💻 Операторы не назначены.", "en": "🧑‍💻 No operators assigned."},
    "operators_list_header": {"ru": "🧑‍💻 Текущие операторы (admins):", "en": "🧑‍💻 Current operators (admins):"},
    "order_view": {
        "ru": (
            "💳 Сделка {human_id}\n"
            "👤 Продавец: {seller}\n"
            "🛍 Что вы покупаете:\n"
            "{desc}\n"
            "💰 Сумма: {amount} {currency}\n\n"
            "👇 Нажмите кнопку ниже, чтобы продолжить работу с ордером."
        ),
        "en": (
            "💳 Deal {human_id}\n"
            "👤 Seller: {seller}\n"
            "🛍 What you buy:\n"
            "{desc}\n"
            "💰 Amount: {amount} {currency}\n\n"
            "👇 Press the button below to continue with the order."
        )
    },
    "order_card_title": {
        "ru": "📦 Сделка {human_id} (ID в БД: {oid})",
        "en": "📦 Deal {human_id} (DB ID: {oid})"
    },
    "order_status_paid": {"ru": "✅ Оплачен", "en": "✅ Paid"},
    "order_status_unpaid": {"ru": "⏳ Не оплачен", "en": "⏳ Unpaid"},
    "order_field_seller": {"ru": "👤 Продавец", "en": "👤 Seller"},
    "order_field_buyer": {"ru": "🧾 Покупатель", "en": "🧾 Buyer"},
    "order_field_description": {"ru": "📝 Описание:", "en": "📝 Description:"},
    "order_created_at": {"ru": "🕒 Создан", "en": "🕒 Created"},
    "order_paid_at": {"ru": "💸 Оплачен", "en": "💸 Paid"},
    "order_time_between": {"ru": "⏱ Время между созданием и оплатой", "en": "⏱ Time between creation and payment"},
    "no_users": {"ru": "👥 Пользователей в базе пока нет.", "en": "👥 No users in database yet."},
    "last_20_users_header": {"ru": "👥 Последние 20 пользователей:\n", "en": "👥 Last 20 users:\n"},
    "db_table_empty": {"ru": "Таблица {table} пуста.", "en": "Table {table} is empty."},
    "cant_add_main_admin": {"ru": "Нельзя добавлять главного админа как оператора.", "en": "You cannot add the main admin as an operator."},
    "cant_delete_main_admin": {"ru": "Нельзя удалить главного админа.", "en": "You cannot delete the main admin."},
    "operator_added_confirm": {"ru": "Пользователь {label} (id: {id}) добавлен в операторы.", "en": "User {label} (id: {id}) added to operators."},
    "operator_removed_confirm": {"ru": "Пользователь {label} (id: {id}) удалён из операторов.", "en": "User {label} (id: {id}) removed from operators."},
    "order_paid_seller": {
        "ru": "✅ Покупатель успешно оплатил сделку {human_id}.\n\nСумма: {amount} {currency}\nОписание:\n{desc}\n\nРеквизиты для оплаты:\n{payment}",
        "en": "✅ The buyer has paid order {human_id}.\n\nAmount: {amount} {currency}\nDescription:\n{desc}\n\nPayment details:\n{payment}"
    },
    "order_paid_buyer": {
        "ru": "✅ Оплата сделки {human_id} прошла успешно.\n\nСумма: {amount} {currency}\nОписание:\n{desc}",
        "en": "✅ Payment for order {human_id} was successful.\n\nAmount: {amount} {currency}\nDescription:\n{desc}"
    },
}

def t(user_id, key, **kwargs):
    """Return translated text for user's language (user_id)."""
    lang = get_lang(user_id)
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang) or entry.get("ru") or ""
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def ensure_db():
    conn = connect("dont_touch.db")
    cur = conn.cursor()

    # Таблица пользователей: добавляем колонку language с умолчанием 'ru'
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            ids TEXT DEFAULT "",
            state TEXT DEFAULT "start",
            language TEXT DEFAULT 'ru'
        )
        """
    )

    # Таблица ордеров
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount TEXT,
            disc TEXT,
            creator INTEGER,
            is_stars INTEGER DEFAULT 0,
            link TEXT UNIQUE,
            is_paid INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            paid_at DATETIME,
            buyer_id INTEGER,
            payment_details TEXT
        )
        """
    )

    # На случай старой схемы аккуратно добавляем недостающие колонки
    try:
        cur.execute("ALTER TABLE orders ADD COLUMN created_at DATETIME")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE orders ADD COLUMN paid_at DATETIME")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE orders ADD COLUMN buyer_id INTEGER")
    except Exception:
        pass
    # В старой БД могло не быть колонки language
    try:
        cur.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
    except Exception:
        pass

    # Таблица админов
    cur.execute(
        "CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY)"
    )

    # Лог действий админов (добавление/удаление операторов и т.п.)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            actor_id INTEGER,
            action TEXT,
            target_id INTEGER,
            via TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def ensure_admins_table():
    # Сейчас логика админов опирается на таблицу admins,
    # её создание уже гарантируется ensure_db
    ensure_db()


def is_admin(user_id: int) -> bool:
    # Главный админ всегда имеет права оператора
    if user_id == MAIN_ADMIN_ID:
        return True

    ensure_admins_table()
    conn = connect("dont_touch.db")
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM admins WHERE id = ?", [user_id])
    row = cur.fetchone()
    conn.close()
    return bool(row)


def ensure_user_balance_columns():
    # Колонки баланса создаются в ensure_db, здесь просто гарантируем, что БД и таблица users инициализированы
    ensure_db()


# Инициализируем БД при старте модуля, чтобы бот был готов к работе сразу
ensure_db()


def add_balance(user_id: int, amount: float, currency_code: int):
    # Balance system is disabled, only return zeros
    return 0, 0, 0


def delete(chat_id):
    # Очистка чата больше не используется, функция оставлена пустой
    return


# Helper: send the configured image with caption for every outgoing message (fallback to send_message)
def send_with_image(chat_id, text, reply_markup=None):
    try:
        bot.send_photo(chat_id, IMAGE_URL, caption=text, reply_markup=reply_markup)
    except Exception:
        try:
            bot.send_message(chat_id, text, reply_markup=reply_markup)
        except Exception:
            pass


# Helper: attempt to edit the existing message; if editing fails, send a new photo message
def edit_or_send_with_image(chat_id, message_id, text, reply_markup=None):
    # Try to edit text (works for text messages)
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
        return
    except Exception:
        pass

    # Try to edit caption (works if the original message was a photo)
    try:
        bot.edit_message_caption(caption=text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
        return
    except Exception:
        pass

    # Otherwise, send a new photo message with caption
    send_with_image(chat_id, text, reply_markup=reply_markup)


def anti_spam(chat_id, text, reply_markup=None):
    # Отправляем новое сообщение с изображением, не удаляя старые и не храня их в БД
    send_with_image(chat_id, text, reply_markup=reply_markup)


def get_lang(user_id):
    try:
        conn = connect("dont_touch.db")
        row = conn.execute("SELECT language FROM users WHERE id = ?", [user_id]).fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return "ru"


def set_lang(user_id, lang_code):
    if lang_code not in ("ru", "en"):
        return
    try:
        conn = connect("dont_touch.db")
        conn.execute("INSERT OR IGNORE INTO users(id, ids, state, language) VALUES (?, ?, ?, ?)",
                     [user_id, "", "start", lang_code])
        conn.execute("UPDATE users SET language = ? WHERE id = ?", [lang_code, user_id])
        conn.commit()
        conn.close()
    except Exception:
        pass


def main_menu_markup(user_id):
    return IKM().add(
        IB(t(user_id, "create_order"), callback_data="create_order"),
        IB(t(user_id, "safety"), callback_data="safety"),
        IB(t(user_id, "techpod"), callback_data="techpod"),
        IB(t(user_id, "site"), url="https://ggsel.net/b/C1112251"),
        IB(t(user_id, "change_lang"), callback_data="lang"),
        row_width=1,
    )


def admin_base_markup(user_id):
    return IKM().add(
        IB(t(user_id, "admin_stats"), callback_data="admin]stats"),
        IB(t(user_id, "admin_users"), callback_data="admin]users"),
        IB(t(user_id, "admin_orders"), callback_data="admin]orders:all:0"),
        IB(t(user_id, "admin_operators"), callback_data="admin]operators"),
        IB(t(user_id, "admin_help"), callback_data="admin]help"),
        IB(t(user_id, "admin_back_to_user"), callback_data="start"),
        row_width=1,
    )


@bot.message_handler(chat_types=["private"], commands=["start"])
def start(message: Message):
    delete(message.chat.id)

    # Убедимся, что пользователь есть в базе
    conn = connect("dont_touch.db")
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users(id, ids, state, language) VALUES (?, ?, ?, ?)",
            [message.from_user.id, "", "start", "ru"]
        )
        conn.commit()
    except:
        pass
    conn.close()

    if message.text == "/start":
        anti_spam(
            message.chat.id,
            t(message.from_user.id, "welcome"),
            reply_markup=main_menu_markup(message.from_user.id),
        )
    else:
        # Попытка открыть ордер по ссылке /start <link>
        try:
            link_arg = message.text.split(" ")[1]
            conn = connect("dont_touch.db")
            args = conn.execute(
                "SELECT * FROM orders WHERE link = ?",
                [link_arg],
            ).fetchone()
            conn.close()

            if not args:
                raise Exception("order not found")

            order_id = args[0]
            order_link = args[5] if len(args) > 5 else str(order_id)
            human_order_id = f"#{order_link}"

            mrkp = IKM().add(
                IB("💳 Оплатить сделку " + (t(message.from_user.id, "pay") if True else t(message.from_user.id, "pay")), callback_data=f"pay]{order_id}"),
                IB(t(message.from_user.id, "back"), callback_data="start"),
                row_width=1,
            )

            # seller display
            seller_name = "—"
            try:
                seller = bot.get_chat_member(args[3], args[3]).user
                seller_name = getattr(seller, "full_name", str(args[3]))
            except Exception:
                seller_name = str(args[3])

            currency = "RUB" if args[4] == 0 else "STARS" if args[4] == 1 else "TON"

            anti_spam(
                message.chat.id,
                t(message.from_user.id, "order_view",
                  human_id=human_order_id,
                  seller=seller_name,
                  desc=args[2] or "",
                  amount=args[1] or "0",
                  currency=currency
                  ),
                reply_markup=mrkp,
            )
        except Exception as e:
            # если что-то пошло не так — показать главное меню
            anti_spam(
                message.chat.id,
                t(message.from_user.id, "welcome"),
                reply_markup=main_menu_markup(message.from_user.id),
            )
    return


@bot.message_handler(chat_types=["private"], commands=["admin"])
def admin_panel(message: Message):
    # Теперь доступен всем пользователям, имеющим права администратора в таблице admins (и главному админу)
    if not is_admin(message.from_user.id):
        # можно отправлять уведомление о недостатке прав
        try:
            send_with_image(message.chat.id, "❌ " + ("Доступ запрещён" if get_lang(message.from_user.id) == "ru" else "Access denied"))
        except Exception:
            pass
        return

    delete(message.chat.id)

    text = message.text.strip()
    parts = text.split(maxsplit=3)

    user_lang = get_lang(message.from_user.id)

    if len(parts) == 1:
        mrkp = admin_base_markup(message.from_user.id)
        anti_spam(
            message.chat.id,
            t(message.from_user.id, "admin_menu_title"),
            reply_markup=mrkp,
        )
        return

    sub = parts[1].lower()

    # Улучшенная логика добавления/удаления админов через /admin add <ids...> и /admin del <ids...>
    if sub in ("add", "del"):
        tokens = text.split()[2:]  # всё, что после /admin add|del
        if not tokens:
            anti_spam(message.chat.id, "Укажите корректный user_id (число) или @username. Для добавления нескольких укажите через пробел или запятую.")
            return

        ensure_admins_table()
        conn = connect("dont_touch.db")
        cur = conn.cursor()

        added = []
        removed = []
        skipped = []
        failed = []

        for raw in tokens:
            # Обрежем возможные запятые или пробелы
            token = raw.strip().strip(",")
            if not token:
                continue

            # Попробуем распознать user_id или username
            target_id = None
            label = token
            if token.isdigit():
                target_id = int(token)
                label = str(target_id)
            else:
                username = token.lstrip("@")
                try:
                    chat = bot.get_chat(username)
                    target_id = chat.id
                    label = f"@{username}" if username else str(target_id)
                except Exception:
                    failed.append(token)
                    continue

            # Безопасность: не даём добавлять/удалять главного админа
            if target_id == MAIN_ADMIN_ID:
                skipped.append((target_id, "main_admin"))
                continue

            try:
                if sub == "add":
                    cur.execute("INSERT OR IGNORE INTO admins(id) VALUES (?)", [target_id])
                    cur.execute(
                        "INSERT INTO admin_logs(actor_id, action, target_id, via) VALUES (?, ?, ?, ?)",
                        [message.from_user.id, "add_admin", target_id, "command"],
                    )
                    conn.commit()
                    added.append((label, target_id))
                else:  # del
                    cur.execute("DELETE FROM admins WHERE id = ?", [target_id])
                    cur.execute(
                        "INSERT INTO admin_logs(actor_id, action, target_id, via) VALUES (?, ?, ?, ?)",
                        [message.from_user.id, "del_admin", target_id, "command"],
                    )
                    conn.commit()
                    removed.append((label, target_id))
            except Exception as e:
                failed.append(f"{label} ({e})")

        # Сформируем итоговое сообщение в языке админа
        lang = get_lang(message.from_user.id)
        lines = []
        if sub == "add":
            if added:
                if lang == "ru":
                    lines.append("Добавлены в администраторы:")
                    for lbl, tid in added:
                        lines.append(f"- {lbl} (id: {tid})")
                else:
                    lines.append("Added to admins:")
                    for lbl, tid in added:
                        lines.append(f"- {lbl} (id: {tid})")
            if removed:
                # shouldn't happen for add, but just in case
                if lang == "ru":
                    lines.append("Удалены из администраторов:")
                    for lbl, tid in removed:
                        lines.append(f"- {lbl} (id: {tid})")
                else:
                    lines.append("Removed from admins:")
                    for lbl, tid in removed:
                        lines.append(f"- {lbl} (id: {tid})")
        else:
            if removed:
                if lang == "ru":
                    lines.append("Удалены из администраторов:")
                    for lbl, tid in removed:
                        lines.append(f"- {lbl} (id: {tid})")
                else:
                    lines.append("Removed from admins:")
                    for lbl, tid in removed:
                        lines.append(f"- {lbl} (id: {tid})")
            if added:
                if lang == "ru":
                    lines.append("Добавлены в администраторы (вместо удаления):")
                    for lbl, tid in added:
                        lines.append(f"- {lbl} (id: {tid})")
                else:
                    lines.append("Added to admins (instead of deletion):")
                    for lbl, tid in added:
                        lines.append(f"- {lbl} (id: {tid})")

        if skipped:
            if lang == "ru":
                lines.append("Пропущены (главный админ не может быть изменён):")
                for tid, reason in skipped:
                    lines.append(f"- {tid}")
            else:
                lines.append("Skipped (main admin cannot be modified):")
                for tid, reason in skipped:
                    lines.append(f"- {tid}")

        if failed:
            if lang == "ru":
                lines.append("Не удалось обработать следующие записи:")
            else:
                lines.append("Failed to process the following entries:")
            for f in failed:
                lines.append(f"- {f}")

        if not lines:
            if lang == "ru":
                lines = ["Ничего не изменено."]
            else:
                lines = ["No changes made."]

        # Покажем также текущий список админов для наглядности
        try:
            cur.execute("SELECT id FROM admins ORDER BY id")
            current = cur.fetchall()
            if current:
                if lang == "ru":
                    lines.append("\nТекущие администраторы:")
                else:
                    lines.append("\nCurrent admins:")
                for (aid,) in current:
                    try:
                        ch = bot.get_chat(aid)
                        uname = getattr(ch, "username", None)
                    except Exception:
                        uname = None
                    if uname:
                        lines.append(f"- {aid} (@{uname})")
                    else:
                        lines.append(f"- {aid}")
            else:
                if lang == "ru":
                    lines.append("\nСписок администраторов пуст.")
                else:
                    lines.append("\nAdmins list is empty.")
        except Exception:
            pass

        conn.close()

        anti_spam(message.chat.id, "\n".join(lines))
        return

    if sub == "list":
        ensure_admins_table()
        conn = connect("dont_touch.db")
        cur = conn.cursor()
        cur.execute("SELECT id FROM admins ORDER BY id")
        rows = cur.fetchall()
        conn.close()
        if not rows:
            anti_spam(message.chat.id, "Список администраторов пуст.")
            return
        text_rows = "\n".join(str(r[0]) for r in rows)
        anti_spam(message.chat.id, "Администраторы:\n" + text_rows)
        return

    if sub == "db":
        if len(parts) < 3:
            anti_spam(message.chat.id, "Укажите таблицу: users, orders или admins.")
            return
        table = parts[2].lower()
        if table not in ("users", "orders", "admins"):
            anti_spam(message.chat.id, "Неизвестная таблица. Доступны: users, orders, admins.")
            return
        conn = connect("dont_touch.db")
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT * FROM {table} LIMIT 20")
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description]
        except Exception as e:
            conn.close()
            anti_spam(message.chat.id, f"Ошибка при чтении таблицы: {e}")
            return
        conn.close()
        if not rows:
            anti_spam(message.chat.id, t(message.from_user.id, "db_table_empty", table=table))
            return
        header = ", ".join(columns)
        lines = [header]
        for r in rows:
            lines.append(", ".join(str(v) for v in r))
        text_out = "\n".join(lines)
        if len(text_out) > 3800:
            text_out = text_out[:3800] + "\n... (обрезано)"
        anti_spam(
            message.chat.id,
            text_out,
        )
        return

    anti_spam(message.chat.id, "Неизвестная подкоманда /admin. Введите /admin для справки.")


@bot.callback_query_handler(func=lambda call: call.data.split("]")[0] == "admin")
def admin_menu_callback(call: CallbackQuery):
    # Теперь доступ ко всем админским callback'ам имеют пользователи из таблицы admins и главный админ
    if not is_admin(call.from_user.id):
        try:
            bot.answer_callback_query(call.id, text=t(call.from_user.id, "insufficient_balance"), show_alert=True)
        except Exception:
            pass
        return

    data = call.data
    parts = data.split("]", 1)
    action = parts[1] if len(parts) > 1 else "panel"

    ensure_db()
    conn = connect("dont_touch.db")
    cur = conn.cursor()

    base_markup = admin_base_markup(call.from_user.id)

    try:
        if action == "panel":
            edit_or_send_with_image(
                call.from_user.id,
                call.message.id,
                t(call.from_user.id, "admin_menu_title"),
                reply_markup=base_markup,
            )

        elif action == "stats":
            try:
                cur.execute("SELECT COUNT(*) FROM users")
                users_count = cur.fetchone()[0]
            except Exception:
                users_count = 0

            try:
                cur.execute("SELECT COUNT(*) FROM orders")
                orders_total = cur.fetchone()[0]
            except Exception:
                orders_total = 0

            try:
                cur.execute("SELECT COUNT(*) FROM orders WHERE is_paid = 1")
                orders_paid = cur.fetchone()[0]
            except Exception:
                orders_paid = 0

            orders_unpaid = max(0, orders_total - orders_paid)

            try:
                cur.execute("SELECT COUNT(*) FROM admins")
                admins_count = cur.fetchone()[0]
            except Exception:
                admins_count = 0

            text = (
                f"{t(call.from_user.id, 'admin_stats')}\n\n"
                f"👥 {t(call.from_user.id, 'admin_users')}: {users_count}\n"
                f"📦 {t(call.from_user.id, 'admin_orders')}: {orders_total}\n"
                f"✅ Оплаченных сделок: {orders_paid}\n"
                f"⏳ Неоплаченных сделок: {orders_unpaid}\n"
                f"🧑‍💻 {t(call.from_user.id, 'admin_operators')}: {admins_count}"
            )

            edit_or_send_with_image(
                call.from_user.id,
                call.message.id,
                text,
                reply_markup=base_markup,
            )

        elif action == "users":
            try:
                cur.execute(
                    "SELECT id, state, balance_rub, balance_star, balance_ton FROM users ORDER BY id DESC LIMIT 20"
                )
                rows = cur.fetchall()
            except Exception:
                rows = []

            if not rows:
                text = t(call.from_user.id, "no_users")
            else:
                lines = [t(call.from_user.id, "last_20_users_header")]
                for uid, state, br, bs, bt in rows:
                    br = br or 0
                    bs = bs or 0
                    bt = bt or 0
                    lines.append(
                        f"ID: {uid} | state: {state} | RUB: {br} | STARS: {bs} | TON: {bt}"
                    )
                text = "\n".join(lines)

            edit_or_send_with_image(
                call.from_user.id,
                call.message.id,
                text,
                reply_markup=base_markup,
            )

        elif action.startswith("orders"):
            # Карточный просмотр ордеров с пролистыванием и фильтрами
            parts_orders = action.split(":")
            mode = "all"
            index = 0
            if len(parts_orders) >= 2 and parts_orders[1] in ("all", "paid", "unpaid"):
                mode = parts_orders[1]
            if len(parts_orders) >= 3:
                try:
                    index = int(parts_orders[2])
                except ValueError:
                    index = 0

            if index < 0:
                index = 0

            # WHERE для фильтра
            where_clause = ""
            where_params = []
            if mode == "paid":
                where_clause = "WHERE is_paid = 1"
            elif mode == "unpaid":
                where_clause = "WHERE is_paid = 0"

            try:
                cur.execute(f"SELECT COUNT(*) FROM orders {where_clause}", where_params)
                total_orders = cur.fetchone()[0]
            except Exception:
                total_orders = 0

            if total_orders == 0:
                if mode == "paid":
                    text = "📦 Оплаченных сделок пока нет." if get_lang(call.from_user.id) == "ru" else "📦 No paid orders yet."
                elif mode == "unpaid":
                    text = "📦 Неоплаченных сделок пока нет." if get_lang(call.from_user.id) == "ru" else "📦 No unpaid orders yet."
                else:
                    text = "📦 сделок пока нет." if get_lang(call.from_user.id) == "ru" else "📦 No orders yet."
                mrkp = base_markup
                edit_or_send_with_image(call.from_user.id, call.message.id, text, reply_markup=mrkp)
            else:
                if index >= total_orders:
                    index = total_orders - 1

                try:
                    cur.execute(
                        "SELECT id, amount, disc, creator, is_stars, link, is_paid, created_at, paid_at, buyer_id "
                        f"FROM orders {where_clause} ORDER BY id DESC LIMIT 1 OFFSET ?",
                        where_params + [index],
                    )
                    row = cur.fetchone()
                except Exception:
                    row = None

                if not row:
                    text = "Не удалось загрузить сделку." if get_lang(call.from_user.id) == "ru" else "Could not load the order."
                    mrkp = base_markup
                    edit_or_send_with_image(call.from_user.id, call.message.id, text, reply_markup=mrkp)
                else:
                    (
                        oid,
                        amount,
                        disc,
                        creator_id,
                        is_stars,
                        link,
                        is_paid,
                        created_at,
                        paid_at,
                        buyer_id,
                    ) = row

                    currency = "RUB" if is_stars == 0 else "STARS" if is_stars == 1 else "TON"
                    status = t(call.from_user.id, "order_status_paid") if is_paid else t(call.from_user.id, "order_status_unpaid")
                    human_id = f"#{link if link else oid}"

                    # Информация о продавце
                    seller_username = "нет"
                    try:
                        ch = bot.get_chat(creator_id)
                        if getattr(ch, "username", None):
                            seller_username = f"@{ch.username}"
                    except Exception:
                        seller_username = "не удалось получить" if get_lang(call.from_user.id) == "ru" else "unable to fetch"

                    # Информация о покупателе
                    buyer_info = "—"
                    if buyer_id:
                        buyer_username = "нет"
                        try:
                            chb = bot.get_chat(buyer_id)
                            if getattr(chb, "username", None):
                                buyer_username = f"@{chb.username}"
                        except Exception:
                            buyer_username = "не удалось получить" if get_lang(call.from_user.id) == "ru" else "unable to fetch"
                        buyer_info = f"{buyer_id} ({buyer_username})"

                    created_str = created_at if created_at else ("нет данных" if get_lang(call.from_user.id) == "ru" else "no data")
                    paid_str = paid_at if paid_at else ( "ещё не оплачен" if get_lang(call.from_user.id) == "ru" else "not paid yet")

                    delta_str = "—"
                    if created_at and paid_at:
                        try:
                            dt_created = datetime.fromisoformat(str(created_at))
                            dt_paid = datetime.fromisoformat(str(paid_at))
                            delta = dt_paid - dt_created
                            total_sec = int(delta.total_seconds())
                            hours = total_sec // 3600
                            minutes = (total_sec % 3600) // 60
                            if hours > 0:
                                delta_str = f"{hours} ч {minutes} мин" if get_lang(call.from_user.id) == "ru" else f"{hours} h {minutes} min"
                            else:
                                delta_str = f"{minutes} мин" if get_lang(call.from_user.id) == "ru" else f"{minutes} min"
                        except Exception:
                            delta_str = "недоступно" if get_lang(call.from_user.id) == "ru" else "unavailable"

                    text = (
                        f"{t(call.from_user.id, 'order_card_title', human_id=human_id, oid=oid)}\n\n"
                        f"📌 {t(call.from_user.id, 'order_status_paid') if is_paid else t(call.from_user.id, 'order_status_unpaid')}\n"
                        f"💰 {amount} {currency}\n\n"
                        f"👤 {t(call.from_user.id, 'order_field_seller')}: {creator_id} ({seller_username})\n"
                        f"🧾 {t(call.from_user.id, 'order_field_buyer')}: {buyer_info}\n\n"
                        f"{t(call.from_user.id, 'order_field_description')}\n{disc}\n\n"
                        f"{t(call.from_user.id, 'order_created_at')}: {created_str}\n"
                        f"{t(call.from_user.id, 'order_paid_at')}: {paid_str}\n"
                        f"{t(call.from_user.id, 'order_time_between')}: {delta_str}\n\n"
                        f"Ордер {index + 1} из {total_orders} (по ID убыванию, фильтр: {mode})."
                    )

                    # Кнопки фильтров и пролистки
                    mrkp = IKM()

                    # Фильтры (в одной строке)
                    mode_labels = {
                        "all": "Все" if get_lang(call.from_user.id) == "ru" else "All",
                        "paid": "Оплаченные" if get_lang(call.from_user.id) == "ru" else "Paid",
                        "unpaid": "Неоплаченные" if get_lang(call.from_user.id) == "ru" else "Unpaid",
                    }
                    row_filters = []
                    for m in ("all", "paid", "unpaid"):
                        label = mode_labels[m]
                        if m == mode:
                            label = "✅ " + label
                        row_filters.append(
                            IB(
                                label,
                                callback_data=f"admin]orders:{m}:{0}",
                            )
                        )
                    mrkp.row(*row_filters)

                    # Стрелки
                    nav_row = []
                    if index > 0:
                        nav_row.append(
                            IB(
                                "⬅️ Предыдущий" if get_lang(call.from_user.id) == "ru" else "⬅️ Previous",
                                callback_data=f"admin]orders:{mode}:{index - 1}",
                            )
                        )
                    if index < total_orders - 1:
                        nav_row.append(
                            IB(
                                "Следующий ➡️" if get_lang(call.from_user.id) == "ru" else "Next ➡️",
                                callback_data=f"admin]orders:{mode}:{index + 1}",
                            )
                        )
                    if nav_row:
                        mrkp.row(*nav_row)

                    mrkp.add(IB(t(call.from_user.id, "back"), callback_data="admin]panel"))

                    edit_or_send_with_image(
                        call.from_user.id,
                        call.message.id,
                        text,
                        reply_markup=mrkp,
                    )

        elif action == "operators":
            try:
                cur.execute("SELECT id FROM admins ORDER BY id")
                rows = cur.fetchall()
            except Exception:
                rows = []

            if not rows:
                text = t(call.from_user.id, "operators_list_empty")
            else:
                lines = [t(call.from_user.id, "operators_list_header")]
                for (aid,) in rows:
                    uname = None
                    try:
                        ch = bot.get_chat(aid)
                        uname = ch.username
                    except Exception:
                        uname = None

                    if uname:
                        lines.append(f"{aid} (@{uname})")
                    else:
                        lines.append(f"{aid} (username: нет)" if get_lang(call.from_user.id) == "ru" else f"{aid} (username: none)")

                text = "\n".join(lines)

            mrkp = IKM().add(
                IB("➕ " + (t(call.from_user.id, "admin_stats") if False else "➕ Добавить оператора"), callback_data="admin]op_add"),
                IB("➖ " + (t(call.from_user.id, "admin_stats") if False else "➖ Удалить оператора"), callback_data="admin]op_del"),
                IB(t(call.from_user.id, "back"), callback_data="admin]panel"),
                row_width=1,
            )

            edit_or_send_with_image(
                call.from_user.id,
                call.message.id,
                text,
                reply_markup=mrkp,
            )

        elif action == "op_add":
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO users(id, ids, state, balance_rub, balance_star, balance_ton) VALUES (?, ?, ?, 0, 0, 0)",
                    [call.from_user.id, "", "start"],
                )
                conn.commit()
            except Exception:
                pass

            try:
                conn.execute(
                    "UPDATE users SET state = ? WHERE id = ?",
                    ["admin_add]", call.from_user.id],
                )
                conn.commit()
            except Exception:
                pass

            send_with_image(
                call.from_user.id,
                t(call.from_user.id, "admin_add_prompt"),
            )

            try:
                bot.answer_callback_query(call.id)
            except Exception:
                pass

        elif action == "op_del":
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO users(id, ids, state) VALUES (?, ?, ?)",
                    [call.from_user.id, "", "start"],
                )
                conn.commit()
            except Exception:
                pass

            try:
                conn.execute(
                    "UPDATE users SET state = ? WHERE id = ?",
                    ["admin_del]", call.from_user.id],
                )
                conn.commit()
            except Exception:
                pass

            send_with_image(
                call.from_user.id,
                t(call.from_user.id, "admin_del_prompt"),
            )

            try:
                bot.answer_callback_query(call.id)
            except Exception:
                pass

        elif action == "help":
            text = t(call.from_user.id, "admin_help_text")

            edit_or_send_with_image(
                call.from_user.id,
                call.message.id,
                text,
                reply_markup=base_markup,
            )

        else:
            try:
                bot.answer_callback_query(call.id, text="Неизвестное действие.")
            except Exception:
                pass

    finally:
        conn.close()


@bot.message_handler(
    chat_types=["private"],
    content_types=["text"],
    func=lambda message: False,
)
def get_someshit(message: Message):
    # Зарезервировано, не используется в текущей логике
    return


@bot.message_handler(
    chat_types=["private"],
    content_types=["text"],
    func=lambda message: get_state(message.chat.id).startswith("admin_add]"),
)
def admin_add_operator(message: Message):
    delete(message.chat.id)

    raw = message.text.strip()

    # Если введены только цифры — трактуем как user_id
    target_id = None
    label = None
    if raw.isdigit():
        target_id = int(raw)
        label = str(target_id)
    else:
        # Пытаемся трактовать как username
        username = raw.lstrip("@")
        try:
            chat = bot.get_chat(username)
            target_id = chat.id
            label = f"@{username}" if username else str(target_id)
        except Exception:
            anti_spam(
                message.chat.id,
                t(message.from_user.id, "user_not_found_username"),
            )
            return

    # Безопасность: не даём добавлять главного админа
    if target_id == MAIN_ADMIN_ID:
        anti_spam(message.chat.id, t(message.from_user.id, "cant_add_main_admin"))
        return

    ensure_admins_table()
    conn = connect("dont_touch.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT OR IGNORE INTO admins(id) VALUES (?)", [target_id])
        cur.execute(
            "INSERT INTO admin_logs(actor_id, action, target_id, via) VALUES (?, ?, ?, ?)",
            [message.from_user.id, "add_admin", target_id, "inline"],
        )
        conn.commit()
    finally:
        conn.close()

    conn = connect("dont_touch.db")
    try:
        conn.execute(
            "UPDATE users SET state = 'start' WHERE id = ?",
            [message.from_user.id],
        )
        conn.commit()
    finally:
        conn.close()

    anti_spam(
        message.chat.id,
        t(message.from_user.id, "operator_added_confirm", label=label, id=target_id),
    )


@bot.message_handler(
    chat_types=["private"],
    content_types=["text"],
    func=lambda message: get_state(message.chat.id).startswith("admin_del]"),
)
def admin_del_operator(message: Message):
    delete(message.chat.id)

    raw = message.text.strip()

    target_id = None
    label = None
    if raw.isdigit():
        target_id = int(raw)
        label = str(target_id)
    else:
        username = raw.lstrip("@")
        try:
            chat = bot.get_chat(username)
            target_id = chat.id
            label = f"@{username}" if username else str(target_id)
        except Exception:
            anti_spam(
                message.chat.id,
                t(message.from_user.id, "user_not_found_username"),
            )
            return

    # Безопасность: не даём удалять главного админа
    if target_id == MAIN_ADMIN_ID:
        anti_spam(message.chat.id, t(message.from_user.id, "cant_delete_main_admin"))
        return

    ensure_admins_table()
    conn = connect("dont_touch.db")
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM admins WHERE id = ?", [target_id])
        cur.execute(
            "INSERT INTO admin_logs(actor_id, action, target_id, via) VALUES (?, ?, ?, ?)",
            [message.from_user.id, "del_admin", target_id, "inline"],
        )
        conn.commit()
    finally:
        conn.close()

    conn = connect("dont_touch.db")
    try:
        conn.execute(
            "UPDATE users SET state = 'start' WHERE id = ?",
            [message.from_user.id],
        )
        conn.commit()
    finally:
        conn.close()

    anti_spam(
        message.chat.id,
        t(message.from_user.id, "operator_removed_confirm", label=label, id=target_id),
    )


@bot.message_handler(
    chat_types=["private"],
    content_types=["text"],
    func=lambda message: get_state(message.chat.id).startswith("a]"),
)
def get_amount(message: Message):
    try:
        # Validate and parse the amount
        amount = message.text.strip().replace(',', '.').replace(' ', '')
        amount_float = float(amount)

        if amount_float <= 0:
            raise ValueError("Amount must be positive")

        conn = connect("dont_touch.db")
        link = get_state(message.chat.id).split("]")[1]

        # Update the order with the amount
        conn.execute(
            "UPDATE orders SET amount = ? WHERE link = ?",
            (str(amount_float), link)
        )
        conn.commit()

        # Update user state to ask for description
        conn.execute(
            "UPDATE users SET state = ? WHERE id = ?",
            (f"d]{link}", message.chat.id)
        )
        conn.commit()
        conn.close()

        anti_spam(message.chat.id, t(message.from_user.id, "enter_description"))

    except ValueError as e:
        # If conversion to number fails, ask to enter a valid amount
        anti_spam(message.chat.id, t(message.from_user.id, "enter_valid_amount"))
    except Exception as e:
        print(f"Error in get_amount: {e}")
        anti_spam(message.chat.id, t(message.from_user.id, "amount_error"))


@bot.message_handler(
    chat_types=["private"],
    content_types=["text"],
    func=lambda message: get_state(message.chat.id).startswith("d]"),
)
def get_description(message: Message):

    delete(message.chat.id)
    # Ограничение длины описания
    if len(message.text) > 512:
        anti_spam(message.chat.id, t(message.from_user.id, "desc_too_long"))
        return

    conn = connect("dont_touch.db")
    state = conn.execute(
        "SELECT state FROM users WHERE id = ?",
        [message.chat.id]
    ).fetchone()[0]
    link = state.split("]", 1)[1]
    conn.execute(
        "UPDATE orders SET disc = ? WHERE link = ?",
        [message.text, link],
    )
    conn.commit()

    # Проверим тип валюты сделки — если STARS (is_stars == 1), не спрашиваем реквизиты, сразу создаём ордер
    try:
        is_stars = conn.execute("SELECT is_stars, amount, disc FROM orders WHERE link = ?", [link]).fetchone()
        if is_stars:
            is_stars_val = is_stars[0]
            amount_val = is_stars[1] or ""
            disc_val = is_stars[2] or ""
        else:
            is_stars_val = 0
            amount_val = ""
            disc_val = message.text
    except Exception:
        is_stars_val = 0
        amount_val = ""
        disc_val = message.text

    if is_stars_val == 1:
        # Для STARS: не запрашиваем реквизиты — сразу завершаем создание ордера (без блока реквизитов)
        try:
            conn.execute(
                "UPDATE users SET state = ? WHERE id = ?",
                ["start", message.from_user.id]
            )
            conn.commit()
        finally:
            conn.close()

        # Используем шаблон без показа реквизитов
        anti_spam(
            message.chat.id,
            t(message.from_user.id, "order_created_no_payment",
              link=link,
              amount=amount_val,
              disc=disc_val,
              botname=bot.user.username or "bot"
              ),
        )
        return

    # Для всех остальных типов валют — просим реквизиты как раньше
    try:
        conn.execute(
            "UPDATE users SET state = ? WHERE id = ?",
            [f"p{link}", message.from_user.id]
        )
        conn.commit()
    finally:
        conn.close()

    anti_spam(message.chat.id, t(message.from_user.id, "enter_payment_details"))


@bot.message_handler(
    chat_types=["private"],
    content_types=["text"],
    func=lambda message: get_state(message.chat.id).startswith("p"),
)
def get_payment_details(message: Message):
    delete(message.chat.id)
    payment_details = message.text.strip()

    if len(payment_details) < 5:  # Минимальная длина для реквизитов
        anti_spam(message.chat.id, t(message.from_user.id, "enter_payment_details"))
        return

    conn = connect("dont_touch.db")
    state = conn.execute(
        "SELECT state FROM users WHERE id = ?",
        [message.chat.id]
    ).fetchone()[0]
    link = state[1:]  # Убираем первый символ 'p' из состояния

    # Обновляем реквизиты в заказе
    conn.execute(
        "UPDATE orders SET payment_details = ? WHERE link = ?",
        [payment_details, link],
    )

    # Получаем данные для подтверждения
    order_info = conn.execute(
        "SELECT amount, disc FROM orders WHERE link = ?",
        [link],
    ).fetchone()

    amount_val, disc_val = order_info if order_info else ("", "")

    # Возвращаем пользователя в начальное состояние
    conn.execute(
        "UPDATE users SET state = ? WHERE id = ?",
        ["start", message.from_user.id]
    )
    conn.commit()
    conn.close()

    # Отправляем подтверждение с реквизитами
    anti_spam(
        message.chat.id,
        t(message.from_user.id, "order_created",
          link=link,
          amount=amount_val,
          disc=disc_val,
          payment=payment_details,
          botname=bot.user.username or "bot"
          ),
    )


@bot.callback_query_handler(func=lambda call: call.data.split("]")[0] == "pay")
def pay(call: CallbackQuery):
    # Только админы-операторы могут фиксировать предоплату
    try:
        if not is_admin(call.from_user.id):
            try:
                bot.answer_callback_query(
                    call.id,
                    text=t(call.from_user.id, "insufficient_balance"),
                    show_alert=True,
                )
            except Exception:
                pass
            return
    except Exception:
        return

    order_id = call.data.split("]")[1]
    conn = connect("dont_touch.db")
    try:
        row = conn.execute(
            "SELECT id, amount, disc, creator, is_stars, link, is_paid, payment_details FROM orders WHERE id = ?",
            [order_id],
        ).fetchone()
    except Exception:
        row = None

    if not row:
        conn.close()
        try:
            bot.answer_callback_query(call.id, text=t(call.from_user.id, "order_not_found"), show_alert=True)
        except Exception:
            pass
        return

    order_id, amount, disc, creator_id, is_stars, link, is_paid, payment_details = row

    # Если ордер уже оплачен — больше не даём его закрывать повторно
    if is_paid:
        conn.close()
        try:
            bot.answer_callback_query(
                call.id,
                text=t(call.from_user.id, "order_already_paid"),
                show_alert=True,
            )
        except Exception:
            pass
        return

    human_order_id = f"#{link}"

    try:
        amount_value = float(amount)
    except Exception:
        amount_value = 0.0

    buyer_id = call.from_user.id
    currency_name = "RUB" if is_stars == 0 else "STARS" if is_stars == 1 else "TON"

    # --- New: send seller a message in the format similar to the provided screenshot ---
    # Compute amount with service fee
    try:
        total_with_fee = amount_value * (1 + SERVICE_FEE)
    except Exception:
        total_with_fee = amount_value

    # Build seller notification in RU (if seller lang ru) or EN
    seller_lang = get_lang(creator_id)
    if seller_lang == "ru":
        seller_text = (
            f"✅ Оплата по сделке #{link} подтверждена.\n\n"
            f"👤 Продавец:\n"
            f"💰 Сумма сделки: {amount_value:.2f} {currency_name} ({total_with_fee:.2f} {currency_name})\n"
            f"📝 Описание:\n{disc}\n\n"
            f"Можете спокойно передавать подарок на @Pregabolin_manager\n\n"
            f"⚙️ Подтверждение получения товара - автоматически."
        )
    else:
        seller_text = (
            f"✅ Payment for deal #{link} confirmed.\n\n"
            f"👤 Seller:\n"
            f"💰 Deal amount: {amount_value:.2f} {currency_name} ({total_with_fee:.2f} {currency_name})\n"
            f"📝 Description:\n{disc}\n\n"
            f"Feel free to send the item to @Pregabolin_manager\n\n"
            f"⚙️ Receipt confirmation is automatic."
        )

    # Send the crafted seller message (with image)
    try:
        send_with_image(creator_id, seller_text)
    except Exception:
        pass

    # Сообщение покупателю (на языке покупателя) — оставляем как раньше
    buyer_lang = get_lang(buyer_id)
    buyer_text = TRANSLATIONS["order_paid_buyer"].get(buyer_lang, TRANSLATIONS["order_paid_buyer"]["ru"]).format(
        human_id=human_order_id,
        amount=amount_value,
        currency=currency_name,
        desc=disc
    )

    try:
        send_with_image(buyer_id, buyer_text)
    except Exception:
        pass

    # Помечаем ордер как оплаченный/закрытый и фиксируем покупателя/время оплаты
    try:
        conn.execute(
            "UPDATE orders SET is_paid = 1, buyer_id = ?, paid_at = CURRENT_TIMESTAMP WHERE id = ?",
            [buyer_id, order_id],
        )
        conn.commit()
    except Exception as e:
        print(f"Error updating order: {e}")
    finally:
        conn.close()

    try:
        bot.answer_callback_query(
            call.id,
            text=t(call.from_user.id, "pay_recorded"),
            show_alert=False,
        )
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: call.data.split("]")[0] == "techpod")
def techpod(call: CallbackQuery):

    try:
        bot.answer_callback_query(call.id, text=" " + ("" if get_lang(call.from_user.id) == "ru" else "Site section is under development. Please try later."), show_alert=True)
    except Exception:
        pass

    

    edit_or_send_with_image(
        call.from_user.id,
        call.message.id,
        t(call.from_user.id, "techpod_text"),
        reply_markup=IKM().add(
            IB(t(call.from_user.id, "back"), callback_data="start"),
            IB("✉️ " + ("Написать в поддержку" if get_lang(call.from_user.id) == "ru" else "Contact support"), url="https://t.me/Pregabolin_manager"),
            row_width=1,
        ),
    )

    return


@bot.callback_query_handler(func=lambda call: call.data == "safety")
def security(call: CallbackQuery):
    edit_or_send_with_image(
        call.from_user.id,
        call.message.id,
        t(call.from_user.id, "safety_text"),
        reply_markup=IKM().add(
            IB(t(call.from_user.id, "back"), callback_data="start"),
            row_width=1,
        ),
    )

    return


@bot.callback_query_handler(func=lambda call: call.data == "start")
def _start(call: CallbackQuery):
    edit_or_send_with_image(
        call.from_user.id,
        call.message.id,
        t(call.from_user.id, "welcome"),
        reply_markup=main_menu_markup(call.from_user.id),
    )


@bot.callback_query_handler(func=lambda call: call.data == "create_order")
def create_order(call: CallbackQuery):
    edit_or_send_with_image(
        call.from_user.id,
        call.message.id,
        t(call.from_user.id, "choose_payment"),
        reply_markup=IKM().add(
            IB(t(call.from_user.id, "rub"), callback_data="create]rub"),
            IB(t(call.from_user.id, "ton"), callback_data="create]ton"),
            IB(t(call.from_user.id, "star"), callback_data="create]star"),
            IB(t(call.from_user.id, "back"), callback_data="start"),
            row_width=1,
        ),
    )


@bot.callback_query_handler(func=lambda call: call.data.split("]")[0] == "create")
def create(call: CallbackQuery):
    currency = call.data.split("]")[1]
    prompt = t(call.from_user.id, "enter_amount_rub") if currency == "rub" else t(call.from_user.id, "enter_amount")

    edit_or_send_with_image(
        call.message.chat.id,
        call.message.id,
        prompt,
    )

    # Убедимся, что пользователь есть в базе
    conn = connect("dont_touch.db")
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users(id, ids, state, language) VALUES (?, ?, ?, ?)",
            [call.from_user.id, "", "start", get_lang(call.from_user.id)]
        )
        conn.commit()
    except:
        pass

    link = string()
    # Определяем is_stars: 0 для rub, 1 для star, 2 для ton
    is_stars = 0 if currency == "rub" else 1 if currency == "star" else 2
    conn.execute(
        "INSERT INTO orders(creator, is_stars, link) VALUES (?, ?, ?)",
        (call.from_user.id, is_stars, link)
    )
    conn.commit()
    conn.execute(
        "UPDATE users SET state = ? WHERE id = ?",
        (f"a]{link}", call.from_user.id)
    )
    conn.commit()
    conn.close()


def string():
    res = ""
    letters = "qwertyuiopasdfghjklzxcvbnm"
    numbers = "1234567890"

    for _ in range(randint(5, 9)):
        # 1 — буква, 0 — цифра
        if randint(0, 1):
            ch = choice(letters)
            # 1 — сделать заглавной
            if randint(0, 1):
                ch = ch.upper()
            res += ch
        else:
            res += choice(numbers)

    return res


def get_state(chat_id):
    try:
        conn = connect("dont_touch.db")
        res = conn.execute(
            "SELECT state FROM users WHERE id = ?",
            [chat_id]
        ).fetchone()[0]
        conn.close()
    except:
        res = "start"
    return res


# Новые обработчики для смены языка
@bot.callback_query_handler(func=lambda call: call.data == "lang")
def lang_menu(call: CallbackQuery):
    mrkp = IKM().add(
        IB("🇷🇺 Русский", callback_data="setlang]ru"),
        IB("🇬🇧 English", callback_data="setlang]en"),
        IB(t(call.from_user.id, "back"), callback_data="start"),
        row_width=1,
    )
    try:
        edit_or_send_with_image(
            call.from_user.id,
            call.message.id,
            "Выберите язык / Choose language",
            reply_markup=mrkp,
        )
    except Exception:
        try:
            send_with_image(call.from_user.id, "Выберите язык / Choose language", reply_markup=mrkp)
        except Exception:
            pass


@bot.callback_query_handler(func=lambda call: call.data.split("]")[0] == "setlang")
def set_language(call: CallbackQuery):
    parts = call.data.split("]")
    if len(parts) < 2:
        try:
            bot.answer_callback_query(call.id, text="Invalid selection")
        except Exception:
            pass
        return
    lang = parts[1]
    if lang not in ("ru", "en"):
        try:
            bot.answer_callback_query(call.id, text="Invalid selection")
        except Exception:
            pass
        return

    set_lang(call.from_user.id, lang)
    try:
        bot.answer_callback_query(call.id, text=("Язык изменён" if lang == "ru" else "Language changed"))
    except Exception:
        pass

    # Перерисуем главное меню сразу на выбранном языке
    try:
        edit_or_send_with_image(
            call.from_user.id,
            call.message.id,
            t(call.from_user.id, "welcome"),
            reply_markup=main_menu_markup(call.from_user.id),
        )
    except Exception:
        try:
            send_with_image(call.from_user.id, t(call.from_user.id, "welcome"), reply_markup=main_menu_markup(call.from_user.id))
        except Exception:
            pass


bot.infinity_polling()