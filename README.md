# 🤖 Telegram Username Checker Bot

Телеграм-бот, который проверяет, **свободен / занят / продаётся** ли Telegram username, и **автоматически уведомляет**, когда занятый username освобождается.

> **Статус:** ✅ **Готов и работает в проде** — на сервере 24/7, с авто-деплоем.

---

## ✅ Что реализовано

### Основные функции
- **Проверка username** — парсинг `t.me` + (опционально) Telethon, валидация формата, кэш
- **Мониторинг** 💎 — авто-уведомление, когда занятый username освобождается (планировщик, каждые 30 минут)
- **Генератор** 🎯 — поиск свободных username по шаблону (`gold*`) или из списка
- **Fragment** 💎 — показывает цену username, выставленного на продажу (кнопкой)

### Пользователи и управление
- **Контроль доступа** 🔐 — при `/start` нового пользователя админу приходит запрос (кнопки Одобрить/Отклонить); без одобрения бот не работает
- **Админ-панель** 👑 — `/stats`, `/users`, `/pending`, `/approve`, `/revoke`, `/broadcast`
- **i18n** 🌐 — узбекский / русский / английский (`/lang`)
- **UI на кнопках** — занятый username как ссылка, кнопки «Открыть / Следить / Fragment»

### Надёжность
- **Глобальный обработчик ошибок** 📜 — непредвиденные ошибки автоматически уходят админу (traceback + троттлинг)
- **Дневной лимит** — бесплатно N/день, у админов без лимита
- **Безопасность** — токен не утекает в логи (`diagnose=False`)
- **26 тестов** — `python -m tests.test_all`

### Инфраструктура
- **GitHub:** https://github.com/Ibroximjon631/username-checker-bot
- **Сервер:** systemd-сервис 24/7 (`/opt/username-checker-bot`), без Docker
- **Авто-деплой (CI/CD):** `git push` → GitHub Actions → rsync на сервер → перезапуск бота
- **Docker** тоже доступен (`docker compose`) — как альтернативный способ деплоя

---

## 🧩 Команды бота

### Пользователь
| Команда | Описание |
|---------|----------|
| `/start` | Запустить бота |
| `/check <username>` | Проверить username |
| `/gen <pattern>` | Найти свободные username (напр. `gold*`) |
| `/watch <username>` | Следить (уведомить, когда освободится) |
| `/unwatch <username>` | Убрать из слежения |
| `/list` | Список слежения |
| `/history` | Последние проверки |
| `/lang` | Сменить язык |
| `/help` | Помощь |

### Админ
| Команда | Описание |
|---------|----------|
| `/stats` | Статистика |
| `/users` | Пользователи (одобрено/ожидают/отклонено) |
| `/pending` | Ожидающие запросы + кнопки |
| `/approve <id>` | Одобрить по ID |
| `/revoke <id>` | Отозвать доступ |
| `/broadcast <текст>` | Рассылка всем пользователям |

---

## ⚙️ Технологии

| Слой | Выбор |
|------|-------|
| Язык | Python 3.10+ |
| Фреймворк бота | aiogram 3.x |
| Точная проверка | Telethon (MTProto, опционально) |
| HTTP | aiohttp |
| База данных | SQLite (aiosqlite) |
| Планировщик | APScheduler |
| Конфигурация | pydantic-settings + `.env` |
| Логи | loguru |
| Деплой | systemd + GitHub Actions (или Docker) |

---

## 🔍 Как определяется занятость username

Telegram **Bot API не отдаёт** доступность username, поэтому используется многослойный подход:

1. **Парсинг `t.me`** — страница `https://t.me/<username>`: есть профиль → занят, нет → вероятно свободен (быстро, без токена).
2. **Telethon `ResolveUsername`** (опционально) — точная проверка через MTProto-сессию аккаунта.
3. **Fragment.com** — для username, выставленных на аукцион/продажу (с ценой).

---

## 🏗 Архитектура

```
┌──────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│ Пользователь │─────▶│   Бот (aiogram)      │─────▶│  Сервис проверки     │
│  (Telegram)  │◀─────│  • хендлеры          │◀─────│  • t.me parser       │
└──────────────┘      │  • middleware (i18n, │      │  • telethon resolver │
                      │    access)           │      │  • fragment client   │
                      └──────────┬───────────┘      └──────────────────────┘
                                 │
                      ┌──────────▼───────────┐      ┌──────────────────────┐
                      │   База (SQLite)      │◀─────│  Планировщик          │
                      │  • users             │      │  (APScheduler)        │
                      │  • watchlist         │      │  каждые 30 минут      │
                      │  • history           │      │  проверяет watchlist  │
                      └──────────────────────┘      └──────────────────────┘
```

---

## 📁 Структура проекта

```
username-checker-bot/
├── bot.py                  # точка входа
├── config.py               # настройки (.env)
├── locales.py              # i18n (uz/ru/en)
├── keyboards.py            # inline-клавиатуры
├── scheduler.py            # цикл мониторинга
├── handlers/               # start, check, monitor, generate, admin, access, errors
├── services/               # checker, tme_parser, telethon, fragment, generator, validator, access_service
├── db/storage.py           # слой БД
├── utils/                  # middleware (i18n, access), cache, limits, ui, logger
├── tests/test_all.py       # 26 тестов
├── Dockerfile + docker-compose.yml
├── .github/workflows/deploy.yml   # авто-деплой
├── requirements.txt
├── .env.example
├── README.md
└── DEPLOY.md
```

---

## 🗄 Схема БД

- **users** — `id`, `username`, `lang`, `status` (pending/approved/rejected), `created_at`
- **watchlist** — `id`, `user_id`, `target_username`, `status`, `added_at`, `last_checked`
- **history** — `id`, `user_id`, `username`, `result`, `checked_at`
- **daily_usage** — `user_id`, `day`, `count` (дневной лимит)

---

## 🚀 Установка (локально)

```bash
git clone git@github.com:Ibroximjon631/username-checker-bot.git
cd username-checker-bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # заполнить BOT_TOKEN, ADMIN_IDS
.venv/bin/python bot.py
```

---

## 🔧 Конфигурация (.env)

```env
BOT_TOKEN=...              # от @BotFather (обязательно)
ADMIN_IDS=7919948585      # ID админов через запятую
FREE_DAILY_LIMIT=20       # бесплатный дневной лимит

# Telethon (опционально — точная проверка)
API_ID=0
API_HASH=
TELETHON_SESSION=username_checker

# Мониторинг
CHECK_INTERVAL_MINUTES=30 # как часто проверять watchlist

# Fragment
FRAGMENT_ENABLED=true

# База
DB_PATH=bot.db
```

> 🔒 `.env` и `*.session` — никогда не коммитить (уже в `.gitignore`).

---

## ☁️ Деплой и CI/CD

Бот работает на сервере как **systemd-сервис** (без Docker, не мешает nginx/postgres сайта).

### Авто-деплой (GitHub Actions)
```bash
git add -A
git commit -m "описание изменений"
git push
# → за 30-60 секунд сервер обновляется автоматически
```
Статус деплоя: https://github.com/Ibroximjon631/username-checker-bot/actions

### Управление на сервере
```bash
ssh root@178.238.234.230
systemctl status username-bot       # статус
journalctl -u username-bot -f       # живые логи
systemctl restart username-bot      # перезапуск
```

> 📖 Полная инструкция по деплою: [DEPLOY.md](DEPLOY.md)

---

## 🧪 Тесты

```bash
python -m tests.test_all
```
26 проверок: storage, checker, generator, fragment, лимиты, middleware, поток доступа, UI, dispatcher, обработчик ошибок.

---

## ⚠️ Важные советы

1. **Flood-лимит** — Telegram временно блокирует при частых запросах. Защита: пауза 1с между проверками, кэш, троттлинг.
2. **Telethon = аккаунт** — нужна сессия аккаунта (не bot token). Используйте запасной номер.
3. **Безопасность** — `API_ID/HASH`, `BOT_TOKEN`, `*.session` держать в секрете.
4. **Точность** — результат не 100%; для надёжности используйте Telethon.
5. **Большой watchlist** — увеличьте `CHECK_INTERVAL_MINUTES`.

---

*Telegram Username Checker Bot — полностью готовый продукт: код, тесты, сервер, авто-деплой.*
