"""Bot konfiguratsiyasi — .env fayldan o'qiladi."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    free_daily_limit: int = 20
    admin_ids: str = ""

    # Telethon (ixtiyoriy — aniq tekshiruv uchun)
    api_id: int = 0
    api_hash: str = ""
    telethon_session: str = "username_checker"

    # Monitoring
    check_interval_minutes: int = 10

    # Fragment (sotuvdagi username narxini ko'rsatish)
    fragment_enabled: bool = True

    # Ma'lumotlar bazasi
    db_path: str = "bot.db"

    @property
    def admin_id_list(self) -> list[int]:
        """ADMIN_IDS satrini int ro'yxatiga aylantiradi."""
        if not self.admin_ids.strip():
            return []
        return [int(x) for x in self.admin_ids.split(",") if x.strip()]

    @property
    def telethon_enabled(self) -> bool:
        """API ID/HASH berilgan bo'lsa telethon yoqiladi."""
        return self.api_id > 0 and bool(self.api_hash.strip())


settings = Settings()
