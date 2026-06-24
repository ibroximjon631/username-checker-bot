FROM python:3.12-slim

# Loglar darrov chiqsin, .pyc yozilmasin
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Avval bog'liqliklar (Docker kesh qatlamidan foydalanish uchun)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keyin kod
COPY . .

# Ma'lumotlar (bot.db, *.session) uchun papka
VOLUME ["/data"]
ENV DB_PATH=/data/bot.db \
    TELETHON_SESSION=/data/username_checker

CMD ["python", "bot.py"]
