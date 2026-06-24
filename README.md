# 🤖 Telegram Username Checker Bot

Telegram username'ning **bo'sh / band / sotuvda** ekanini tekshiradigan, va band username **bo'shaganida avtomatik xabar beradigan** Telegram bot.

> **Holat:** 📐 Loyihalash bosqichi (planning). Bu README — loyihaning to'liq yo'l xaritasi (blueprint).

---

## 📑 Mundarija

1. [Loyiha haqida](#1-loyiha-haqida)
2. [Funksiyalar](#2-funksiyalar)
3. [Texnologiyalar](#3-texnologiyalar)
4. [Username bandligini qanday aniqlaymiz](#4-username-bandligini-qanday-aniqlaymiz)
5. [Arxitektura](#5-arxitektura)
6. [Loyiha tuzilishi](#6-loyiha-tuzilishi)
7. [Ma'lumotlar bazasi (DB sxema)](#7-malumotlar-bazasi-db-sxema)
8. [O'rnatish (Setup)](#8-ornatish-setup)
9. [Konfiguratsiya (.env)](#9-konfiguratsiya-env)
10. [Ishga tushirish](#10-ishga-tushirish)
11. [Bot buyruqlari](#11-bot-buyruqlari)
12. [Rivojlanish rejasi (Roadmap)](#12-rivojlanish-rejasi-roadmap)
13. [Muhim maslahatlar va ogohlantirishlar](#13-muhim-maslahatlar-va-ogohlantirishlar)
14. [Monetizatsiya (ixtiyoriy)](#14-monetizatsiya-ixtiyoriy)
15. [FAQ](#15-faq)

---

## 1. Loyiha haqida

**Muammo:** Telegram'da chiroyli, qisqa username'lar tez egallanadi. Foydalanuvchi qaysi username bo'sh ekanini bilishni xohlaydi, va band bo'lganlari bo'shasa xabar olishni istaydi.

**Yechim:** Bu bot:
- Berilgan username'ni real vaqtda tekshiradi (bo'sh/band/sotuvda).
- Band username'larni kuzatuvga oladi va bo'shaganda darhol xabar beradi.
- Bo'sh username'larni pattern bo'yicha topib beradi (generator).

**Maqsadli auditoriya:** username "huntingchi"lar, NFT-username savdosi bilan shug'ullanuvchilar, brendlar uchun nom izlovchilar.

> 🔐 **Kirish nazorati (Access control):** Bot **yopiq** — yangi foydalanuvchi `/start` bosganda adminga so'rov (ism, username, ID + Tasdiqlash/Rad etish tugmalari) keladi. Admin tasdiqlamaguncha foydalanuvchi hech qanday buyruqdan foydalana olmaydi.

---

## 2. Funksiyalar

### 🟢 MVP (1-bosqich — eng zarur)
- [ ] `/start` — salomlashish va qisqa yo'riqnoma
- [ ] Bitta username tekshiruv → `✅ Bo'sh` / `❌ Band` / `🔒 Sotuvda`
- [ ] Format validatsiya (5–32 belgi, `a–z 0–9 _`, raqam bilan boshlanmaydi)
- [ ] Xatolarni ushlash (noto'g'ri kiritma, flood-limit, tarmoq xatosi)

### 🟡 2-bosqich (asosiy qiymat)
- [ ] **Monitoring** 💎 — band username'ni kuzatish, bo'shasa avtomatik xabar
- [ ] Bulk tekshiruv — ko'p username bitta xabarda yoki fayl bilan
- [ ] Tarix — foydalanuvchi tekshirgan username'lar ro'yxati
- [ ] Kesh — takror so'rovlarni tezlashtirish

### 🔵 3-bosqich (kengaytma)
- [ ] Generator — pattern/uzunlik bo'yicha bo'sh username topish
- [ ] Qiymat bahosi — qisqalik/lug'aviy so'z → taxminiy narx
- [ ] Limit & Premium — bepul kunlik limit, pulli kengaytma
- [ ] Ko'p tillilik (i18n) — Uz / Ru / En
- [ ] Admin panel — statistika, foydalanuvchilar, broadcast

---

## 3. Texnologiyalar

| Qatlam | Tanlov | Sabab |
|--------|--------|-------|
| Til | **Python 3.11+** | Telegram ekotizimi uchun eng boy |
| Bot framework | **aiogram 3.x** | Async, zamonaviy, mashhur |
| Aniq tekshiruv | **Telethon** (MTProto) | Bandlikni 100% aniqlash |
| HTTP so'rovlar | **aiohttp** | t.me / Fragment so'rovlari |
| Ma'lumotlar | **SQLite** (keyin → PostgreSQL) | Boshlash uchun yetarli |
| ORM | **SQLAlchemy** (async) | Toza DB qatlami |
| Scheduler | **APScheduler** | Monitoring loop uchun |
| Konfiguratsiya | **pydantic-settings** + `.env` | Maxfiy kalitlarni boshqarish |
| Deploy | **Docker** + VPS / Railway / Fly.io | Doimiy ishlash |
| Loglar | **loguru** | Qulay logging |

---

## 4. Username bandligini qanday aniqlaymiz

> ⚠️ **Muhim:** Telegram **Bot API** username availability'ni **bermaydi**. Shuning uchun 3 qatlamli yondashuv ishlatamiz:

### Qatlam 1 — `t.me` sahifasini parse qilish (tez, token shart emas)
- `https://t.me/<username>` sahifasini yuklab, HTML'ni tekshiramiz.
- "If you have Telegram, you can contact..." bo'lsa → **band**.
- "username not found" bo'lsa → ehtimol **bo'sh**.
- Kamchilik: o'chirilgan/bloklangan akkauntlarni noto'g'ri ko'rsatishi mumkin.

### Qatlam 2 — Telethon `ResolveUsername` (eng aniq)
- Sizning **akkaunt sessiyangiz** orqali `functions.contacts.ResolveUsernameRequest`.
- `UsernameNotOccupiedError` → **bo'sh**.
- Aniqligi yuqori, lekin akkaunt va flood-limitga ehtiyot bo'lish kerak.

### Qatlam 3 — Fragment.com (sotuvdagilar uchun)
- Fragment — Telegram'ning rasmiy username marketplace'i.
- Username auksionda yoki sotuvda bo'lsa shu yerdan aniqlanadi.

### Yakuniy mantiq (tavsiya)
```
1. Format validatsiya  ──▶  noto'g'ri bo'lsa darrov rad et
2. t.me parse (tez)    ──▶  aniq "band" bo'lsa qaytar
3. Shubhali bo'lsa     ──▶  Telethon bilan tasdiqla
4. "Bo'sh" chiqsa      ──▶  Fragment'da sotuvda emasligini tekshir
```

---

## 5. Arxitektura

```
┌──────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│ Foydalanuvchi │─────▶│   Bot (aiogram)      │─────▶│  Checker service     │
│  (Telegram)   │◀─────│  • handlerlar        │◀─────│  • t.me parser       │
└──────────────┘      │  • validatsiya       │      │  • telethon resolver │
                      │  • javob formatlash  │      │  • fragment client   │
                      └──────────┬───────────┘      └──────────────────────┘
                                 │
                      ┌──────────▼───────────┐      ┌──────────────────────┐
                      │   Database (SQLite)  │◀─────│  Monitoring scheduler │
                      │  • users             │      │  (APScheduler)        │
                      │  • watchlist         │      │  har N daqiqada       │
                      │  • history           │      │  watchlist'ni tekshir │
                      └──────────────────────┘      └──────────────────────┘
```

---

## 6. Loyiha tuzilishi

```
username-checker-bot/
├── README.md               # ← shu fayl
├── requirements.txt        # bog'liqliklar
├── .env.example            # namuna konfiguratsiya
├── .gitignore
├── Dockerfile
├── docker-compose.yml
│
├── bot.py                  # kirish nuqtasi (entry point)
├── config.py               # sozlamalar (pydantic-settings)
│
├── handlers/               # bot buyruqlari
│   ├── __init__.py
│   ├── start.py            # /start, /help
│   ├── check.py            # username tekshiruv
│   ├── monitor.py          # kuzatuv qo'shish/o'chirish
│   └── admin.py            # admin buyruqlari
│
├── services/               # biznes mantiq
│   ├── __init__.py
│   ├── checker.py          # asosiy tekshiruv (3 qatlam)
│   ├── tme_parser.py       # t.me parse
│   ├── telethon_client.py  # telethon resolver
│   ├── fragment.py         # fragment client
│   └── validator.py        # username format validatsiya
│
├── db/                     # ma'lumotlar qatlami
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy modellar
│   └── storage.py          # CRUD funksiyalar
│
├── scheduler.py            # monitoring loop
├── keyboards.py            # inline tugmalar
├── texts.py                # matnlar (i18n uchun tayyor)
└── utils/
    ├── __init__.py
    ├── logger.py
    └── throttling.py       # flood/rate-limit himoyasi
```

---

## 7. Ma'lumotlar bazasi (DB sxema)

### `users`
| Maydon | Tip | Tavsif |
|--------|-----|--------|
| id | INTEGER PK | Telegram user ID |
| username | TEXT | Foydalanuvchi username |
| created_at | DATETIME | Ro'yxatdan o'tgan vaqt |
| is_premium | BOOLEAN | Premium holati |
| checks_today | INTEGER | Bugungi tekshiruvlar soni (limit uchun) |

### `watchlist` (monitoring)
| Maydon | Tip | Tavsif |
|--------|-----|--------|
| id | INTEGER PK | |
| user_id | INTEGER FK | Kim kuzatyapti |
| target_username | TEXT | Kuzatilayotgan username |
| status | TEXT | `taken` / `free` |
| added_at | DATETIME | Qo'shilgan vaqt |
| last_checked | DATETIME | Oxirgi tekshiruv |

### `history`
| Maydon | Tip | Tavsif |
|--------|-----|--------|
| id | INTEGER PK | |
| user_id | INTEGER FK | |
| username | TEXT | Tekshirilgan username |
| result | TEXT | `free` / `taken` / `for_sale` |
| checked_at | DATETIME | |

---

## 8. O'rnatish (Setup)

### Talablar
- Python 3.11+
- Telegram **bot token** — [@BotFather](https://t.me/BotFather)
- Telethon uchun **API ID + API HASH** — https://my.telegram.org → API development tools
- (Tavsiya) Telethon uchun alohida/zaxira telefon raqami

### Qadamlar
```bash
# 1. Loyihaga kirish
cd username-checker-bot

# 2. Virtual muhit
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Bog'liqliklar
pip install -r requirements.txt

# 4. Konfiguratsiya
cp .env.example .env
# .env faylini tahrirlab tokenlarni qo'ying

# 5. (Birinchi marta) Telethon sessiyasini yaratish
python -m services.telethon_client   # telefon + kod so'raydi
```

---

## 9. Konfiguratsiya (.env)

```env
# Bot
BOT_TOKEN=123456:ABC-DEF...           # @BotFather'dan

# Telethon (aniq tekshiruv uchun)
API_ID=1234567                        # my.telegram.org'dan
API_HASH=abcdef1234567890abcdef
TELETHON_SESSION=username_checker     # sessiya nomi

# Database
DATABASE_URL=sqlite+aiosqlite:///bot.db

# Sozlamalar
CHECK_INTERVAL_MINUTES=10             # monitoring qanchadan tekshiradi
FREE_DAILY_LIMIT=20                   # bepul kunlik limit
ADMIN_IDS=123456789                   # admin Telegram ID'lari (vergul bilan)
```

> 🔒 `.env` faylini **hech qachon** git'ga qo'shmang! `.gitignore`'da bo'lsin.

---

## 10. Ishga tushirish

> 🚀 **Serverga deploy:** to'liq yo'riqnoma — [DEPLOY.md](DEPLOY.md) (Docker yoki systemd).
> 🧪 **Testlar:** `python -m tests.test_all` — 26 ta tekshiruv (storage, checker, access, UI, error handler...).

### Lokal
```bash
python bot.py
```

### Docker
```bash
docker compose up -d --build
docker compose logs -f          # loglarni ko'rish
```

---

## 11. Bot buyruqlari

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni boshlash, yo'riqnoma |
| `/help` | Yordam |
| `/check <username>` | Username tekshirish (yoki shunchaki username yuborish) |
| `/watch <username>` | Kuzatuvga qo'shish |
| `/unwatch <username>` | Kuzatuvdan olib tashlash |
| `/list` | Kuzatuvdagi username'lar ro'yxati |
| `/history` | Tekshiruvlar tarixi |
| `/gen <pattern>` | Pattern bo'yicha bo'sh username topish |
| `/lang` | Tilni o'zgartirish (Uz/Ru/En) |
| `/stats` | *(admin)* Statistika |
| `/users` | *(admin)* Foydalanuvchilar holati (approved/pending/rejected) |
| `/pending` | *(admin)* Kutilayotgan so'rovlar + tugmalar |
| `/approve <id>` | *(admin)* ID bo'yicha tasdiqlash |
| `/revoke <id>` | *(admin)* Ruxsatni olib tashlash |
| `/broadcast <matn>` | *(admin)* Barcha foydalanuvchilarga xabar |

---

## 12. Rivojlanish rejasi (Roadmap)

### Bosqich 1 — MVP ✅
- [ ] Loyiha skeleti (papkalar, config)
- [ ] `/start` + `/help`
- [ ] Format validatsiya
- [ ] t.me parser
- [ ] Bitta username tekshiruv + javob formatlash
- [ ] Asosiy xatolarni ushlash

### Bosqich 2 — Aniqlik + Monitoring 💎
- [x] Telethon integratsiyasi (ixtiyoriy)
- [x] DB (users, watchlist, history)
- [x] `/watch`, `/unwatch`, `/list`, `/history`
- [x] APScheduler monitoring loop
- [x] Bo'shaganda avtomatik xabar
- [x] Kesh (TTL)

### Bosqich 3 — Kengaytma 🚀
- [x] Generator (`/gen`) — pattern/ro'yxatdan bo'sh username topish
- [x] Kunlik limit (premium poydevori)
- [x] Admin panel + broadcast (`/stats`, `/broadcast`)
- [x] Deploy (Docker + docker-compose)
- [x] i18n (Uz/Ru/En) — `/lang` bilan til tanlash
- [x] **Access control** — admin tasdig'isiz bot ishlamaydi 🔐
- [x] **Fragment integratsiyasi** — sotuvdagi username narxi 💎
- [x] **Global error handler** — xatolar avtomatik adminga 📜
- [ ] Premium (to'lov)

---

## 13. Muhim maslahatlar va ogohlantirishlar

1. **⚠️ Flood-limit** — Telegram ko'p so'rovni vaqtincha bloklaydi. Yechim: so'rovlar orasiga `sleep`, kesh, navbat (queue), throttling middleware.
2. **⚠️ Telethon = akkaunt** — bot token emas, haqiqiy akkaunt sessiyasi kerak. **Zaxira raqam** ishlating — asosiy akkaunt bloklanib qolmasin.
3. **🔒 Maxfiylik** — `API_ID`, `API_HASH`, `BOT_TOKEN`, `.session` fayllar — hech qachon git/public joyga qo'ymang.
4. **🎯 Aniqlik 100% emas** — t.me ba'zan o'chirilgan/bloklangan akkauntni "band" deb ko'rsatadi. Shubhali holatda telethon bilan tasdiqlang.
5. **⚖️ Qonuniylik** — Telegram ToS'ga rioya qiling. Massa-scraping, spam, suiiste'moldan saqlaning.
6. **🧱 MVP'dan boshlang** — hammasini birdan qilmang. Avval bitta tekshiruv ishlasin, keyin monitoring qo'shing.
7. **💾 Backup** — DB'ni muntazam zaxiralang (ayniqsa watchlist va premium foydalanuvchilar).
8. **📊 Logging** — har bir tekshiruv va xatoni logga yozing — debug oson bo'ladi.

---

## 14. Monetizatsiya (ixtiyoriy)

- **Bepul limit** — kuniga N ta tekshiruv (masalan 20), ko'prog'i premium.
- **Premium obuna** — cheksiz tekshiruv + ko'p monitoring slot + generator.
- **Monitoring slotlari** — bepul 3 ta, qo'shimchasi pulli.
- **Referal** — do'st taklif qilsa bonus limit.
- **To'lov** — Telegram Stars / Payments API / Crypto.

---

## 15. FAQ

**S: Bot API bilan username bandligini bilsa bo'ladimi?**
J: Yo'q. Shuning uchun t.me parse + Telethon ishlatamiz.

**S: Telethon uchun nima kerak?**
J: my.telegram.org'dan `API_ID` + `API_HASH`, va bir martalik telefon orqali login (sessiya saqlanadi).

**S: Bot meni bloklab qo'yadimi?**
J: Ko'p/tez so'rov yuborsa flood-limit bo'lishi mumkin. Throttling va kesh shuni oldini oladi. Zaxira raqam ishlating.

**S: Qaysi funksiyadan boshlash kerak?**
J: MVP — `/start` + bitta tekshiruv (t.me parser). Keyin telethon, keyin monitoring.

---

## 📌 Keyingi qadam

Loyiha skeletini va MVP kodini yozishni boshlash uchun tayyor.

> **Boshlash:** `requirements.txt` + `config.py` + `bot.py` + `/start` handler + t.me parser → birinchi ishlaydigan versiya.

---

*Tuzilgan: 2026-06-24*
