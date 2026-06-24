"""Ko'p tillilik (i18n) — O'zbek, Rus, Ingliz.

Foydalanish:  t(lang, "KEY", **kwargs)
Til topilmasa yoki kalit yo'q bo'lsa — DEFAULT_LANG ga qaytadi.
"""
from __future__ import annotations

DEFAULT_LANG = "uz"

# Til tanlash menyusi uchun
LANG_NAMES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

TEXTS: dict[str, dict[str, str]] = {
    # ============================ O'ZBEK ============================
    "uz": {
        "START": (
            "👋 <b>Salom, {name}!</b>\n\n"
            "Men Telegram username'larni tekshiraman.\n\n"
            "Menga username yuboring (masalan <code>durov</code>) — uning "
            "<b>bo'sh</b> yoki <b>band</b> ekanini aytaman.\n\n"
            "📌 <b>Buyruqlar:</b>\n"
            "/check &lt;username&gt; — tekshirish\n"
            "/gen &lt;pattern&gt; — bo'sh username topish (masalan <code>gold*</code>)\n"
            "/watch &lt;username&gt; — kuzatish (bo'shasa xabar)\n"
            "/list — kuzatuv ro'yxati\n"
            "/history — oxirgi tekshiruvlar\n"
            "/lang — tilni o'zgartirish\n"
            "/help — yordam"
        ),
        "HELP": (
            "ℹ️ <b>Yordam</b>\n\n"
            "Shunchaki username yuboring yoki <code>/check username</code> deb yozing.\n\n"
            "✅ <b>Bo'sh</b> — username ishlatilmayapti\n"
            "❌ <b>Band</b> — username egallangan\n"
            "⚠️ <b>Noto'g'ri</b> — format xato\n\n"
            "<i>Eslatma: natija 100% kafolat emas.</i>"
        ),
        "CHECKING": "🔎 <code>{username}</code> tekshirilmoqda…",
        "RESULT_FREE": (
            "✅ <b>Bo'sh!</b>\n\n<code>@{username}</code> — ehtimol mavjud.\n"
            "Telegram sozlamalarida band qilib olishingiz mumkin."
        ),
        "RESULT_TAKEN": "❌ <b>Band</b>\n\n👤 <a href=\"https://t.me/{username}\">@{username}</a> — egasi bor.",
        "RESULT_INVALID": "⚠️ <b>Noto'g'ri username</b>\n\n{reason}",
        "RESULT_UNKNOWN": (
            "🤔 <b>Aniqlab bo'lmadi</b>\n\n<code>{username}</code> holatini hozir "
            "tekshira olmadim. Birozdan keyin qayta urinib ko'ring."
        ),
        "USAGE_CHECK": "Foydalanish: <code>/check username</code>",
        "WATCH_ADDED": (
            "👁 <b>Kuzatuvga qo'shildi!</b>\n\n<code>@{username}</code> hozir <b>band</b>. "
            "Bo'shashi bilan sizga darhol xabar beraman."
        ),
        "WATCH_ALREADY": "ℹ️ <code>@{username}</code> allaqachon kuzatuvingizda.",
        "WATCH_FREE_NOW": (
            "✅ <code>@{username}</code> hozir <b>bo'sh</b>! "
            "Kuzatishga hojat yo'q — darrov band qiling."
        ),
        "WATCH_INVALID": "⚠️ Kuzatib bo'lmadi.\n\n{reason}",
        "UNWATCH_OK": "🗑 <code>@{username}</code> kuzatuvdan olib tashlandi.",
        "UNWATCH_NONE": "ℹ️ <code>@{username}</code> kuzatuvingizda yo'q edi.",
        "LIST_EMPTY": (
            "📭 Kuzatuv ro'yxatingiz bo'sh.\n\n"
            "Kuzatish uchun: <code>/watch username</code>"
        ),
        "LIST_HEADER": "👁 <b>Kuzatuvdagi username'lar:</b>\n\n",
        "USAGE_WATCH": "Foydalanish: <code>/watch username</code>",
        "USAGE_UNWATCH": "Foydalanish: <code>/unwatch username</code>",
        "NOTIFY_FREE": (
            "🎉 <b>BO'SHADI!</b>\n\nSiz kuzatayotgan <code>@{username}</code> endi "
            "<b>bo'sh</b>!\nTezda band qilib oling. ⚡️"
        ),
        "HISTORY_EMPTY": "📭 Tarix bo'sh. Biror username tekshiring.",
        "HISTORY_HEADER": "🕘 <b>Oxirgi tekshiruvlar:</b>\n\n",
        "GEN_USAGE": (
            "🎯 <b>Generator</b> — bo'sh username topadi.\n\n<b>Misollar:</b>\n"
            "<code>/gen gold*</code> — gold + 1 belgi\n"
            "<code>/gen co**</code> — co + 2 belgi\n"
            "<code>/gen alfa beta gamma</code> — ro'yxatdan\n\n"
            "<i>Bir martada ko'pi bilan 40 ta tekshiriladi.</i>"
        ),
        "GEN_SEARCHING": "🎯 <code>{q}</code> bo'yicha qidirilmoqda…",
        "GEN_NONE": "😕 <b>{checked}</b> ta tekshirildi — bo'sh username topilmadi.",
        "GEN_FOUND": "✅ <b>{count}</b> ta bo'sh topildi ({checked} tekshirildi):\n\n{names}",
        "GEN_TRUNCATED": "\n\n<i>⚠️ Nomzodlar ko'p edi — dastlabki 40 tasi tekshirildi.</i>",
        "GEN_NO_VALID": "To'g'ri nomzod topilmadi. Misol: <code>/gen gold*</code>",
        "LIMIT_REACHED": (
            "🚫 <b>Kunlik limit tugadi</b>\n\nBugun {limit} ta tekshiruv ishlatdingiz. "
            "Ertaga yangilanadi.\n\n<i>Cheksiz — tez orada premiumda.</i>"
        ),
        "ADMIN_ONLY": "⛔️ Bu buyruq faqat adminlar uchun.",
        "STATS": (
            "📊 <b>Statistika</b>\n\n👥 Foydalanuvchilar: <b>{users}</b>\n"
            "👁 Kuzatuvlar: <b>{watches}</b>\n🔎 Jami tekshiruvlar: <b>{checks_total}</b>\n"
            "📅 Bugun: <b>{checks_today}</b> tekshiruv, <b>{active_today}</b> faol"
        ),
        "BROADCAST_USAGE": "Foydalanish: <code>/broadcast xabar matni</code>",
        "BROADCAST_START": "📣 Yuborilmoqda… ({total} foydalanuvchi)",
        "BROADCAST_DONE": "✅ Yuborildi: <b>{ok}</b> / {total}\n❌ Yetib bormadi: {failed}",
        "LANG_CHOOSE": "🌐 Tilni tanlang:",
        "LANG_SET": "✅ Til o'zgartirildi: O'zbekcha",
        "BTN_OPEN": "🔗 Telegramda ochish",
        "BTN_WATCH": "👁 Kuzatuvga qo'shish",
        "BTN_UNWATCH": "🗑 Kuzatuvdan olish",
        "CB_WATCH_ADDED": "👁 Kuzatuvga qo'shildi!",
        "CB_WATCH_ALREADY": "Allaqachon kuzatuvingizda.",
        "CB_UNWATCH_OK": "🗑 Olib tashlandi.",
        "CB_UNWATCH_NONE": "Kuzatuvingizda yo'q.",
        # Access control
        "ACCESS_REQUESTED": (
            "👋 <b>Salom!</b>\n\nBotdan foydalanish uchun <b>ruxsat</b> kerak. "
            "So'rovingiz adminga yuborildi ⏳\n\nTasdiqlangach, sizga xabar beraman."
        ),
        "ACCESS_PENDING": (
            "⏳ <b>So'rovingiz ko'rib chiqilmoqda</b>\n\n"
            "Admin tasdiqlashini kuting. Tasdiqlangach xabar beraman."
        ),
        "ACCESS_REJECTED": (
            "🚫 <b>Ruxsat berilmadi</b>\n\nKechirasiz, botdan foydalanishingiz rad etildi."
        ),
        "APPROVED_NOTIFY": (
            "✅ <b>Tasdiqlandingiz!</b>\n\nEndi botdan to'liq foydalanishingiz mumkin. "
            "Boshlash uchun /start bosing."
        ),
        "REJECTED_NOTIFY": "🚫 <b>Ruxsat rad etildi</b>\n\nAfsuski, so'rovingiz rad etildi.",
        "ADMIN_NEW_REQUEST": (
            "🔔 <b>Yangi ruxsat so'rovi</b>\n\n"
            "👤 Ism: {name}\n"
            "🔗 Username: {username}\n"
            "🆔 ID: <code>{uid}</code>\n\n"
            "Ruxsat berasizmi?"
        ),
        "BTN_APPROVE": "✅ Tasdiqlash",
        "BTN_REJECT": "🚫 Rad etish",
        "ADMIN_APPROVED_DONE": "✅ Tasdiqlandi: {name} (<code>{uid}</code>)",
        "ADMIN_REJECTED_DONE": "🚫 Rad etildi: {name} (<code>{uid}</code>)",
        "CB_APPROVED": "✅ Tasdiqlandi",
        "CB_REJECTED": "🚫 Rad etildi",
        "CB_ALREADY_HANDLED": "Bu so'rov allaqachon ko'rib chiqilgan.",
        # Admin boshqaruvi
        "USERS_STATS": (
            "👥 <b>Foydalanuvchilar</b>\n\n✅ Tasdiqlangan: <b>{approved}</b>\n"
            "⏳ Kutilmoqda: <b>{pending}</b>\n🚫 Rad etilgan: <b>{rejected}</b>"
        ),
        "PENDING_EMPTY": "✅ Kutilayotgan so'rov yo'q.",
        "PENDING_HEADER": "⏳ <b>Kutilayotgan so'rovlar ({count}):</b>",
        "PENDING_ITEM": "👤 {name} — <code>{uid}</code>",
        "APPROVE_USAGE": "Foydalanish: <code>/approve user_id</code>",
        "REVOKE_USAGE": "Foydalanish: <code>/revoke user_id</code>",
        "USER_NOT_FOUND": "❌ Foydalanuvchi topilmadi: <code>{uid}</code>",
        "APPROVED_OK": "✅ Tasdiqlandi: <code>{uid}</code>",
        "REVOKED_OK": "🚫 Ruxsat olib tashlandi: <code>{uid}</code>",
        "FRAGMENT_FORSALE": (
            "\n\n💎 <b>Fragment'da sotuvda!</b>\n{status} — <b>{price} TON</b>\n"
            "🔗 <a href=\"{url}\">Fragment'da ochish</a>"
        ),
        # Validator sabablari
        "ERR_EMPTY": "Username bo'sh.",
        "ERR_SHORT": "Juda qisqa — kamida 5 belgi bo'lishi kerak.",
        "ERR_LONG": "Juda uzun — ko'pi bilan 32 belgi.",
        "ERR_DOUBLE": "Ketma-ket ikkita pastki chiziq (__) bo'lmaydi.",
        "ERR_FORMAT": (
            "Noto'g'ri format. Faqat a-z, 0-9, _ ishlatiladi; "
            "harf bilan boshlanadi va raqam/harf bilan tugaydi."
        ),
    },
    # ============================ RUS ============================
    "ru": {
        "START": (
            "👋 <b>Привет, {name}!</b>\n\n"
            "Я проверяю Telegram username'ы.\n\n"
            "Отправьте мне username (например <code>durov</code>) — я скажу, "
            "<b>свободен</b> он или <b>занят</b>.\n\n"
            "📌 <b>Команды:</b>\n"
            "/check &lt;username&gt; — проверить\n"
            "/gen &lt;pattern&gt; — найти свободные (например <code>gold*</code>)\n"
            "/watch &lt;username&gt; — следить (уведомлю когда освободится)\n"
            "/list — список слежения\n"
            "/history — последние проверки\n"
            "/lang — сменить язык\n"
            "/help — помощь"
        ),
        "HELP": (
            "ℹ️ <b>Помощь</b>\n\n"
            "Просто отправьте username или напишите <code>/check username</code>.\n\n"
            "✅ <b>Свободен</b> — username не используется\n"
            "❌ <b>Занят</b> — username занят\n"
            "⚠️ <b>Неверный</b> — ошибка формата\n\n"
            "<i>Примечание: результат не даёт 100% гарантии.</i>"
        ),
        "CHECKING": "🔎 Проверяю <code>{username}</code>…",
        "RESULT_FREE": (
            "✅ <b>Свободен!</b>\n\n<code>@{username}</code> — вероятно доступен.\n"
            "Можете занять его в настройках Telegram."
        ),
        "RESULT_TAKEN": "❌ <b>Занят</b>\n\n👤 <a href=\"https://t.me/{username}\">@{username}</a> — уже занят.",
        "RESULT_INVALID": "⚠️ <b>Неверный username</b>\n\n{reason}",
        "RESULT_UNKNOWN": (
            "🤔 <b>Не удалось определить</b>\n\nСейчас не смог проверить "
            "<code>{username}</code>. Попробуйте позже."
        ),
        "USAGE_CHECK": "Использование: <code>/check username</code>",
        "WATCH_ADDED": (
            "👁 <b>Добавлено в слежение!</b>\n\n<code>@{username}</code> сейчас <b>занят</b>. "
            "Как только освободится — сразу сообщу."
        ),
        "WATCH_ALREADY": "ℹ️ <code>@{username}</code> уже в вашем слежении.",
        "WATCH_FREE_NOW": (
            "✅ <code>@{username}</code> сейчас <b>свободен</b>! "
            "Следить не нужно — занимайте скорее."
        ),
        "WATCH_INVALID": "⚠️ Не удалось добавить.\n\n{reason}",
        "UNWATCH_OK": "🗑 <code>@{username}</code> убран из слежения.",
        "UNWATCH_NONE": "ℹ️ <code>@{username}</code> не был в слежении.",
        "LIST_EMPTY": (
            "📭 Список слежения пуст.\n\nЧтобы следить: <code>/watch username</code>"
        ),
        "LIST_HEADER": "👁 <b>Отслеживаемые username'ы:</b>\n\n",
        "USAGE_WATCH": "Использование: <code>/watch username</code>",
        "USAGE_UNWATCH": "Использование: <code>/unwatch username</code>",
        "NOTIFY_FREE": (
            "🎉 <b>ОСВОБОДИЛСЯ!</b>\n\nОтслеживаемый <code>@{username}</code> теперь "
            "<b>свободен</b>!\nЗанимайте скорее. ⚡️"
        ),
        "HISTORY_EMPTY": "📭 История пуста. Проверьте какой-нибудь username.",
        "HISTORY_HEADER": "🕘 <b>Последние проверки:</b>\n\n",
        "GEN_USAGE": (
            "🎯 <b>Генератор</b> — находит свободные username'ы.\n\n<b>Примеры:</b>\n"
            "<code>/gen gold*</code> — gold + 1 символ\n"
            "<code>/gen co**</code> — co + 2 символа\n"
            "<code>/gen alfa beta gamma</code> — из списка\n\n"
            "<i>За раз проверяется до 40.</i>"
        ),
        "GEN_SEARCHING": "🎯 Ищу по <code>{q}</code>…",
        "GEN_NONE": "😕 Проверено <b>{checked}</b> — свободных не найдено.",
        "GEN_FOUND": "✅ Найдено <b>{count}</b> свободных (проверено {checked}):\n\n{names}",
        "GEN_TRUNCATED": "\n\n<i>⚠️ Кандидатов было много — проверены первые 40.</i>",
        "GEN_NO_VALID": "Подходящих кандидатов нет. Пример: <code>/gen gold*</code>",
        "LIMIT_REACHED": (
            "🚫 <b>Дневной лимит исчерпан</b>\n\nСегодня вы сделали {limit} проверок. "
            "Завтра обновится.\n\n<i>Безлимит — скоро в premium.</i>"
        ),
        "ADMIN_ONLY": "⛔️ Команда только для админов.",
        "STATS": (
            "📊 <b>Статистика</b>\n\n👥 Пользователи: <b>{users}</b>\n"
            "👁 Слежений: <b>{watches}</b>\n🔎 Всего проверок: <b>{checks_total}</b>\n"
            "📅 Сегодня: <b>{checks_today}</b> проверок, <b>{active_today}</b> активных"
        ),
        "BROADCAST_USAGE": "Использование: <code>/broadcast текст</code>",
        "BROADCAST_START": "📣 Отправляю… ({total} пользователей)",
        "BROADCAST_DONE": "✅ Отправлено: <b>{ok}</b> / {total}\n❌ Не дошло: {failed}",
        "LANG_CHOOSE": "🌐 Выберите язык:",
        "LANG_SET": "✅ Язык изменён: Русский",
        "BTN_OPEN": "🔗 Открыть в Telegram",
        "BTN_WATCH": "👁 Следить",
        "BTN_UNWATCH": "🗑 Не следить",
        "CB_WATCH_ADDED": "👁 Добавлено в слежение!",
        "CB_WATCH_ALREADY": "Уже в слежении.",
        "CB_UNWATCH_OK": "🗑 Убрано.",
        "CB_UNWATCH_NONE": "Нет в слежении.",
        # Access control
        "ACCESS_REQUESTED": (
            "👋 <b>Привет!</b>\n\nДля использования бота нужен <b>доступ</b>. "
            "Ваш запрос отправлен админу ⏳\n\nКак одобрят — сообщу."
        ),
        "ACCESS_PENDING": (
            "⏳ <b>Ваш запрос на рассмотрении</b>\n\n"
            "Дождитесь одобрения админа. Как только одобрят — сообщу."
        ),
        "ACCESS_REJECTED": (
            "🚫 <b>Доступ не предоставлен</b>\n\nК сожалению, в доступе отказано."
        ),
        "APPROVED_NOTIFY": (
            "✅ <b>Вы одобрены!</b>\n\nТеперь бот доступен полностью. "
            "Нажмите /start, чтобы начать."
        ),
        "REJECTED_NOTIFY": "🚫 <b>Доступ отклонён</b>\n\nК сожалению, ваш запрос отклонён.",
        "ADMIN_NEW_REQUEST": (
            "🔔 <b>Новый запрос доступа</b>\n\n"
            "👤 Имя: {name}\n"
            "🔗 Username: {username}\n"
            "🆔 ID: <code>{uid}</code>\n\n"
            "Предоставить доступ?"
        ),
        "BTN_APPROVE": "✅ Одобрить",
        "BTN_REJECT": "🚫 Отклонить",
        "ADMIN_APPROVED_DONE": "✅ Одобрен: {name} (<code>{uid}</code>)",
        "ADMIN_REJECTED_DONE": "🚫 Отклонён: {name} (<code>{uid}</code>)",
        "CB_APPROVED": "✅ Одобрено",
        "CB_REJECTED": "🚫 Отклонено",
        "CB_ALREADY_HANDLED": "Этот запрос уже обработан.",
        # Admin управление
        "USERS_STATS": (
            "👥 <b>Пользователи</b>\n\n✅ Одобрено: <b>{approved}</b>\n"
            "⏳ Ожидают: <b>{pending}</b>\n🚫 Отклонено: <b>{rejected}</b>"
        ),
        "PENDING_EMPTY": "✅ Нет ожидающих запросов.",
        "PENDING_HEADER": "⏳ <b>Ожидающие запросы ({count}):</b>",
        "PENDING_ITEM": "👤 {name} — <code>{uid}</code>",
        "APPROVE_USAGE": "Использование: <code>/approve user_id</code>",
        "REVOKE_USAGE": "Использование: <code>/revoke user_id</code>",
        "USER_NOT_FOUND": "❌ Пользователь не найден: <code>{uid}</code>",
        "APPROVED_OK": "✅ Одобрен: <code>{uid}</code>",
        "REVOKED_OK": "🚫 Доступ отозван: <code>{uid}</code>",
        "FRAGMENT_FORSALE": (
            "\n\n💎 <b>Продаётся на Fragment!</b>\n{status} — <b>{price} TON</b>\n"
            "🔗 <a href=\"{url}\">Открыть на Fragment</a>"
        ),
        "ERR_EMPTY": "Username пустой.",
        "ERR_SHORT": "Слишком короткий — минимум 5 символов.",
        "ERR_LONG": "Слишком длинный — максимум 32 символа.",
        "ERR_DOUBLE": "Два подряд подчёркивания (__) недопустимы.",
        "ERR_FORMAT": (
            "Неверный формат. Только a-z, 0-9, _; начинается с буквы "
            "и заканчивается буквой/цифрой."
        ),
    },
    # ============================ ENGLISH ============================
    "en": {
        "START": (
            "👋 <b>Hi, {name}!</b>\n\n"
            "I check Telegram usernames.\n\n"
            "Send me a username (e.g. <code>durov</code>) and I'll tell you if it's "
            "<b>free</b> or <b>taken</b>.\n\n"
            "📌 <b>Commands:</b>\n"
            "/check &lt;username&gt; — check\n"
            "/gen &lt;pattern&gt; — find free ones (e.g. <code>gold*</code>)\n"
            "/watch &lt;username&gt; — watch (notify when it frees up)\n"
            "/list — watchlist\n"
            "/history — recent checks\n"
            "/lang — change language\n"
            "/help — help"
        ),
        "HELP": (
            "ℹ️ <b>Help</b>\n\n"
            "Just send a username or type <code>/check username</code>.\n\n"
            "✅ <b>Free</b> — username is not in use\n"
            "❌ <b>Taken</b> — username is taken\n"
            "⚠️ <b>Invalid</b> — format error\n\n"
            "<i>Note: the result is not a 100% guarantee.</i>"
        ),
        "CHECKING": "🔎 Checking <code>{username}</code>…",
        "RESULT_FREE": (
            "✅ <b>Free!</b>\n\n<code>@{username}</code> — likely available.\n"
            "You can claim it in Telegram settings."
        ),
        "RESULT_TAKEN": "❌ <b>Taken</b>\n\n👤 <a href=\"https://t.me/{username}\">@{username}</a> — already taken.",
        "RESULT_INVALID": "⚠️ <b>Invalid username</b>\n\n{reason}",
        "RESULT_UNKNOWN": (
            "🤔 <b>Couldn't determine</b>\n\nCouldn't check <code>{username}</code> "
            "right now. Try again later."
        ),
        "USAGE_CHECK": "Usage: <code>/check username</code>",
        "WATCH_ADDED": (
            "👁 <b>Added to watchlist!</b>\n\n<code>@{username}</code> is <b>taken</b> now. "
            "I'll notify you the moment it frees up."
        ),
        "WATCH_ALREADY": "ℹ️ <code>@{username}</code> is already on your watchlist.",
        "WATCH_FREE_NOW": (
            "✅ <code>@{username}</code> is <b>free</b> right now! "
            "No need to watch — grab it quickly."
        ),
        "WATCH_INVALID": "⚠️ Couldn't add.\n\n{reason}",
        "UNWATCH_OK": "🗑 <code>@{username}</code> removed from watchlist.",
        "UNWATCH_NONE": "ℹ️ <code>@{username}</code> wasn't on your watchlist.",
        "LIST_EMPTY": (
            "📭 Your watchlist is empty.\n\nTo watch: <code>/watch username</code>"
        ),
        "LIST_HEADER": "👁 <b>Watched usernames:</b>\n\n",
        "USAGE_WATCH": "Usage: <code>/watch username</code>",
        "USAGE_UNWATCH": "Usage: <code>/unwatch username</code>",
        "NOTIFY_FREE": (
            "🎉 <b>IT'S FREE!</b>\n\nThe username you're watching, <code>@{username}</code>, "
            "is now <b>free</b>!\nGrab it quickly. ⚡️"
        ),
        "HISTORY_EMPTY": "📭 History is empty. Check a username first.",
        "HISTORY_HEADER": "🕘 <b>Recent checks:</b>\n\n",
        "GEN_USAGE": (
            "🎯 <b>Generator</b> — finds free usernames.\n\n<b>Examples:</b>\n"
            "<code>/gen gold*</code> — gold + 1 char\n"
            "<code>/gen co**</code> — co + 2 chars\n"
            "<code>/gen alfa beta gamma</code> — from a list\n\n"
            "<i>Up to 40 checked at once.</i>"
        ),
        "GEN_SEARCHING": "🎯 Searching <code>{q}</code>…",
        "GEN_NONE": "😕 Checked <b>{checked}</b> — no free usernames found.",
        "GEN_FOUND": "✅ Found <b>{count}</b> free ({checked} checked):\n\n{names}",
        "GEN_TRUNCATED": "\n\n<i>⚠️ Too many candidates — only the first 40 were checked.</i>",
        "GEN_NO_VALID": "No valid candidates. Example: <code>/gen gold*</code>",
        "LIMIT_REACHED": (
            "🚫 <b>Daily limit reached</b>\n\nYou've used {limit} checks today. "
            "Resets tomorrow.\n\n<i>Unlimited — coming soon in premium.</i>"
        ),
        "ADMIN_ONLY": "⛔️ This command is admin-only.",
        "STATS": (
            "📊 <b>Statistics</b>\n\n👥 Users: <b>{users}</b>\n"
            "👁 Watches: <b>{watches}</b>\n🔎 Total checks: <b>{checks_total}</b>\n"
            "📅 Today: <b>{checks_today}</b> checks, <b>{active_today}</b> active"
        ),
        "BROADCAST_USAGE": "Usage: <code>/broadcast message text</code>",
        "BROADCAST_START": "📣 Sending… ({total} users)",
        "BROADCAST_DONE": "✅ Sent: <b>{ok}</b> / {total}\n❌ Failed: {failed}",
        "LANG_CHOOSE": "🌐 Choose your language:",
        "LANG_SET": "✅ Language changed: English",
        "BTN_OPEN": "🔗 Open in Telegram",
        "BTN_WATCH": "👁 Watch",
        "BTN_UNWATCH": "🗑 Unwatch",
        "CB_WATCH_ADDED": "👁 Added to watchlist!",
        "CB_WATCH_ALREADY": "Already watching.",
        "CB_UNWATCH_OK": "🗑 Removed.",
        "CB_UNWATCH_NONE": "Not on your watchlist.",
        # Access control
        "ACCESS_REQUESTED": (
            "👋 <b>Hi!</b>\n\nThis bot requires <b>access</b>. "
            "Your request has been sent to the admin ⏳\n\nI'll notify you once approved."
        ),
        "ACCESS_PENDING": (
            "⏳ <b>Your request is under review</b>\n\n"
            "Please wait for admin approval. I'll notify you once approved."
        ),
        "ACCESS_REJECTED": (
            "🚫 <b>Access not granted</b>\n\nSorry, your access has been denied."
        ),
        "APPROVED_NOTIFY": (
            "✅ <b>You're approved!</b>\n\nThe bot is now fully available. "
            "Press /start to begin."
        ),
        "REJECTED_NOTIFY": "🚫 <b>Access denied</b>\n\nUnfortunately, your request was rejected.",
        "ADMIN_NEW_REQUEST": (
            "🔔 <b>New access request</b>\n\n"
            "👤 Name: {name}\n"
            "🔗 Username: {username}\n"
            "🆔 ID: <code>{uid}</code>\n\n"
            "Grant access?"
        ),
        "BTN_APPROVE": "✅ Approve",
        "BTN_REJECT": "🚫 Reject",
        "ADMIN_APPROVED_DONE": "✅ Approved: {name} (<code>{uid}</code>)",
        "ADMIN_REJECTED_DONE": "🚫 Rejected: {name} (<code>{uid}</code>)",
        "CB_APPROVED": "✅ Approved",
        "CB_REJECTED": "🚫 Rejected",
        "CB_ALREADY_HANDLED": "This request was already handled.",
        # Admin management
        "USERS_STATS": (
            "👥 <b>Users</b>\n\n✅ Approved: <b>{approved}</b>\n"
            "⏳ Pending: <b>{pending}</b>\n🚫 Rejected: <b>{rejected}</b>"
        ),
        "PENDING_EMPTY": "✅ No pending requests.",
        "PENDING_HEADER": "⏳ <b>Pending requests ({count}):</b>",
        "PENDING_ITEM": "👤 {name} — <code>{uid}</code>",
        "APPROVE_USAGE": "Usage: <code>/approve user_id</code>",
        "REVOKE_USAGE": "Usage: <code>/revoke user_id</code>",
        "USER_NOT_FOUND": "❌ User not found: <code>{uid}</code>",
        "APPROVED_OK": "✅ Approved: <code>{uid}</code>",
        "REVOKED_OK": "🚫 Access revoked: <code>{uid}</code>",
        "FRAGMENT_FORSALE": (
            "\n\n💎 <b>For sale on Fragment!</b>\n{status} — <b>{price} TON</b>\n"
            "🔗 <a href=\"{url}\">Open on Fragment</a>"
        ),
        "ERR_EMPTY": "Username is empty.",
        "ERR_SHORT": "Too short — at least 5 characters.",
        "ERR_LONG": "Too long — at most 32 characters.",
        "ERR_DOUBLE": "Two consecutive underscores (__) are not allowed.",
        "ERR_FORMAT": (
            "Invalid format. Only a-z, 0-9, _; must start with a letter "
            "and end with a letter/digit."
        ),
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    """Tarjima oladi. Til/kalit topilmasa default tilga qaytadi."""
    table = TEXTS.get(lang or DEFAULT_LANG, TEXTS[DEFAULT_LANG])
    s = table.get(key) or TEXTS[DEFAULT_LANG].get(key, key)
    return s.format(**kwargs) if kwargs else s
