# 🚀 Deploy qo'llanmasi

Botni serverda (VPS) doimiy ishlatish bo'yicha to'liq yo'riqnoma.

---

## Talablar

- Linux server (VPS) — Ubuntu/Debian tavsiya etiladi
- Bot token ([@BotFather](https://t.me/BotFather))
- (ixtiyoriy) Telethon uchun `API_ID` + `API_HASH` ([my.telegram.org](https://my.telegram.org))

---

## A variant — Docker (tavsiya etiladi) 🐳

Eng oson va ishonchli usul.

### 1. Docker o'rnatish (agar yo'q bo'lsa)
```bash
curl -fsSL https://get.docker.com | sh
```

### 2. Kodni yuklash
```bash
git clone git@github.com:Ibroximjon631/username-checker-bot.git
cd username-checker-bot
```

### 3. Konfiguratsiya
```bash
cp .env.example .env
nano .env        # BOT_TOKEN va ADMIN_IDS ni to'ldiring
```

### 4. (Ixtiyoriy) Telethon sessiyasi
Agar aniq tekshiruv (Telethon) kerak bo'lsa, sessiyani **avval lokal** yarating
(interaktiv telefon + kod kerak), so'ng `data/` papkaga ko'chiring:
```bash
python -m services.telethon_client       # username_checker.session yaratadi
mkdir -p data && mv username_checker.session data/
```
Kerak bo'lmasa — bu qadamni o'tkazib yuboring, bot t.me bilan ishlaydi.

### 5. Ishga tushirish
```bash
docker compose up -d --build
```

### 6. Boshqarish
```bash
docker compose logs -f          # loglarni ko'rish
docker compose restart          # qayta ishga tushirish
docker compose down             # to'xtatish
docker compose up -d --build    # yangilangach qayta qurish
```

> ✅ `restart: unless-stopped` — server o'chib yonsa ham bot avtomatik ishga tushadi.
> ✅ `data/` papkada `bot.db` va sessiya saqlanadi — konteyner o'chsa ham yo'qolmaydi.

---

## B variant — Docker'siz (systemd) ⚙️

Docker ishlatmasangiz.

### 1. Kod va muhit
```bash
git clone git@github.com:Ibroximjon631/username-checker-bot.git
cd username-checker-bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env
```

### 2. systemd service yaratish
`/etc/systemd/system/username-bot.service`:
```ini
[Unit]
Description=Username Checker Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/username-checker-bot
ExecStart=/home/YOUR_USER/username-checker-bot/.venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Yoqish
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now username-bot
sudo systemctl status username-bot       # holat
journalctl -u username-bot -f            # loglar
```

---

## Yangilash (har ikki variant)

```bash
cd username-checker-bot
git pull

# Docker:
docker compose up -d --build

# systemd:
.venv/bin/pip install -r requirements.txt
sudo systemctl restart username-bot
```

---

## Tekshiruv (deploydan keyin)

1. Telegram'da botga `/start` yozing
2. Admin sifatida `/stats` — statistika chiqishi kerak
3. Biror username yuboring (masalan `durov`) — natija + tugmalar

---

## Maslahatlar

- 🔒 `.env` va `*.session` fayllarni hech kimga bermang, git'ga qo'ymang (allaqachon `.gitignore`da).
- 💾 `data/bot.db` ni vaqti-vaqti bilan zaxiralang.
- 📊 Xatolar avtomatik adminlarga (ADMIN_IDS) boradi — Telegram'da kuzatib turing.
- ⏱ Watchlist katta bo'lsa, `.env`da `CHECK_INTERVAL_MINUTES` ni oshiring.
