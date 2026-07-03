"""To'liq test to'plami — bitta faylda barcha asosiy mantiq.

Ishga tushirish:
    BOT_TOKEN=x ADMIN_IDS=999 DB_PATH=/tmp/t.db python -m tests.test_all

Tarmoq kerak (t.me, fragment.com). Token soxta bo'lishi mumkin —
hech qaysi test Telegram API'ga ulanmaydi.
"""
import asyncio
import os

os.environ.setdefault("BOT_TOKEN", "123:FAKE")
os.environ.setdefault("ADMIN_IDS", "999")
os.environ.setdefault("DB_PATH", "/tmp/test_all.db")
os.environ.setdefault("FREE_DAILY_LIMIT", "3")

if os.path.exists(os.environ["DB_PATH"]):
    os.remove(os.environ["DB_PATH"])

from aiogram import Dispatcher
from aiogram.types import (
    CallbackQuery, Chat, ErrorEvent, Message, Update, User,
)

from db import storage
from locales import TEXTS, t
from services import validator
from services.checker import check_username
from services.generator import generate
from services.fragment import check_fragment
from utils import limits, ui
from utils.i18n_middleware import I18nMiddleware
from utils.access_middleware import AccessMiddleware

PASS = 0


def ok(msg: str) -> None:
    global PASS
    PASS += 1
    print(f"  ✅ {msg}")


# --- Soxta obyektlar ---
class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, chat_id, text, **k):
        self.sent.append((chat_id, text))


class TMsg(Message):
    async def answer(self, text, **k):
        object.__setattr__(self, "_a", getattr(self, "_a", []) + [text])
        return self

    async def edit_text(self, text, **k):
        object.__setattr__(self, "_a", getattr(self, "_a", []) + [text])
        return self

    async def edit_reply_markup(self, reply_markup=None, **k):
        object.__setattr__(self, "_mk", reply_markup)
        return self


class TCall(CallbackQuery):
    async def answer(self, text=None, **k):
        object.__setattr__(self, "_cb", text)


def mk_user(uid, uname="u", lang="uz"):
    return User(id=uid, is_bot=False, first_name="U", username=uname, language_code=lang)


def mk_msg(user, text):
    c = Chat(id=user.id, type="private")
    return TMsg.model_construct(message_id=1, date=None, chat=c, from_user=user, text=text)


async def t_locales():
    print("[1] Locales (i18n)")
    uz = set(TEXTS["uz"])
    for lng in ("ru", "en"):
        assert uz == set(TEXTS[lng]), f"{lng} kalitlari to'liq emas"
    ok("3 til to'liq, yetishmayotgan kalit yo'q")
    assert t("de", "USAGE_CHECK") == t("uz", "USAGE_CHECK")
    ok("Noma'lum til -> default (uz)")


async def t_validator():
    print("[2] Validator")
    assert validator.normalize("https://t.me/Durov") == "durov"
    ok("normalize: havoladan username")
    assert validator.validate("ab")[1] == "ERR_SHORT"
    assert validator.validate("with__x")[1] == "ERR_DOUBLE"
    assert validator.validate("good_name")[0] is True
    ok("validatsiya: qisqa/double/to'g'ri")


async def t_storage():
    print("[3] Storage (DB)")
    await storage.init_db()
    await storage.upsert_user(100, "alice")
    assert await storage.get_status(100) == "pending"
    await storage.set_status(100, "approved")
    await storage.set_lang(100, "ru")
    await storage.upsert_user(100, "alice2")
    assert await storage.get_status(100) == "approved"
    assert await storage.get_lang(100) == "ru"
    ok("user: status/lang upsert'da saqlanadi")
    assert await storage.add_watch(100, "durov", "taken") is True
    assert await storage.add_watch(100, "durov", "taken") is False
    ok("watchlist + takror himoya")
    await storage.add_history(100, "x", "free")
    assert len(await storage.recent_history(100)) == 1
    ok("history")
    await storage.upsert_user(200, "bob")
    await storage.upsert_user(300, "eve")
    await storage.set_status(300, "rejected")
    sc = await storage.status_counts()
    assert sc == {"approved": 1, "pending": 1, "rejected": 1}, sc
    ok(f"status_counts: {sc}")


async def t_checker():
    print("[4] Checker + kesh")
    r = await check_username("durov")
    assert r.status == "taken"
    r2 = await check_username("durov")
    assert r2.source == "cache"
    ok("durov -> band, 2-marta keshdan")
    ri = await check_username("ab")
    assert ri.status == "invalid"
    ok("invalid aniqlanadi")


async def t_generator():
    print("[5] Generator")
    g = await generate("zxqw*")
    assert g.checked > 0
    ok(f"zxqw* -> {len(g.free)} bo'sh / {g.checked} tekshirildi")


async def t_fragment():
    print("[6] Fragment")
    f = await check_fragment("star111")
    assert f.state in ("for_sale", "taken", "sold", "unlisted", "unknown")
    ok(f"star111 -> {f.state} (narx: {f.price_ton or '—'})")


async def t_limits():
    print("[7] Kunlik limit (limit=3)")
    await storage.upsert_user(555, "x")
    res = [await limits.allow(555) for _ in range(5)]
    assert res == [True, True, True, False, False], res
    ok("3 tadan keyin bloklaydi")
    assert all([await limits.allow(999) for _ in range(5)])
    ok("admin cheksiz")


async def t_middlewares():
    print("[8] Middlewares (i18n + access)")
    i18n = I18nMiddleware()
    access = AccessMiddleware()

    async def handler(e, d):
        d["_called"] = True

    # i18n: saqlangan til
    u = mk_user(100)
    data = {"event_from_user": u}
    await i18n(handler, mk_msg(u, "/check x"), data)
    assert data["lang"] == "ru"
    ok("i18n: saqlangan til (ru)")

    # access: approved o'tadi
    u3 = mk_user(100)
    data = {"event_from_user": u3, "lang": "uz", "_called": False}
    await access(handler, mk_msg(u3, "/check x"), data)
    assert data.get("_called")
    ok("access: approved -> o'tadi")

    # access: pending bloklanadi, /start o'tadi
    await storage.upsert_user(400, "pend")  # pending
    u4 = mk_user(400)
    msg = mk_msg(u4, "/check x")
    data = {"event_from_user": u4, "lang": "uz", "_called": False}
    await access(handler, msg, data)
    assert not data.get("_called") and getattr(msg, "_a", [])
    ok("access: pending /check -> blok + xabar")
    data = {"event_from_user": u4, "lang": "uz", "_called": False}
    await access(handler, mk_msg(u4, "/start"), data)
    assert data.get("_called")
    ok("access: pending /start -> o'tadi")


async def t_flows():
    print("[9] Start + Approve oqimi")
    import handlers.start as HS
    import handlers.access as HA
    bot = FakeBot()
    # yangi (admin emas) user /start
    u = mk_user(700, "newbie")
    msg = mk_msg(u, "/start")
    await HS.cmd_start(msg, "uz", bot)
    assert await storage.get_status(700) == "pending"
    assert any(cid == 999 for cid, _ in bot.sent)
    ok("yangi user -> pending + adminga so'rov")
    # approve callback
    admin = mk_user(999, "admin")
    am = mk_msg(admin, "req")
    call = TCall.model_construct(id="1", from_user=admin, chat_instance="x",
                                 data="approve:700", message=am)
    bot.sent.clear()
    await HA.cb_approve(call, bot, "uz")
    assert await storage.get_status(700) == "approved"
    assert any(cid == 700 for cid, _ in bot.sent)
    ok("approve -> approved + userga xabar")
    # takror approve
    bot.sent.clear()
    call2 = TCall.model_construct(id="2", from_user=admin, chat_instance="x",
                                  data="approve:700", message=am)
    await HA.cb_approve(call2, bot, "uz")
    assert not any(cid == 700 for cid, _ in bot.sent)
    ok("takror approve -> bloklanadi")


async def t_ui():
    print("[10] UI klaviaturalari")
    m = await ui.result_markup("durov", "uz", "taken", watching=False)
    texts = [b.text for row in m.inline_keyboard for b in row]
    assert any("ochish" in x.lower() for x in texts)
    assert any("Kuzatuv" in x for x in texts)
    ok(f"band -> tugmalar: {texts}")
    m2 = await ui.result_markup("zxqwrand0099", "uz", "free")
    assert m2 is None
    ok("bo'sh -> tugmasiz")


async def t_dispatcher():
    print("[11] Dispatcher + routerlar")
    from handlers import (
        access, admin, check, errors, generate as gen, monitor, start,
    )
    dp = Dispatcher()
    dp.message.middleware(I18nMiddleware())
    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(I18nMiddleware())
    dp.callback_query.middleware(AccessMiddleware())
    for r in (errors.router, start.router, access.router, admin.router,
              monitor.router, gen.router, check.router):
        dp.include_router(r)
    assert len(dp.sub_routers) == 7
    ok("7 router + 4 middleware ulandi")


async def t_errors():
    print("[12] Error handler")
    import handlers.errors as HE
    HE._last_sent.clear()
    bot = FakeBot()
    u = mk_user(700, "bad")
    c = Chat(id=700, type="private")
    msg = Message.model_construct(message_id=1, date=None, chat=c, from_user=u, text="/x")
    upd = Update.model_construct(update_id=1, message=msg)
    try:
        raise ValueError("test xato")
    except Exception as exc:
        ev = ErrorEvent.model_construct(update=upd, exception=exc)
        await HE.on_error(ev, bot)
        assert {cid for cid, _ in bot.sent} == {999}
        ok("xato adminga ketdi (traceback bilan)")
        bot.sent.clear()
        await HE.on_error(ev, bot)
        assert len(bot.sent) == 0
        ok("throttling: takror yuborilmadi")


async def _clear_watch_state():
    await storage._conn().execute("DELETE FROM watchlist")
    await storage._conn().execute("DELETE FROM bot_state")
    await storage._conn().commit()


async def t_monitoring():
    print("[13] Monitoring — soxta 'bo'shadi' himoyasi (ko'p-sikl tasdiq)")
    from types import SimpleNamespace
    import scheduler
    from services.checker import CheckResult

    seq: list[str] = []

    async def fake_cu(u, use_cache=False):
        return CheckResult(username=u, status=seq.pop(0))

    async def nosleep(*a, **k):
        return None

    real_cu, real_aio = scheduler.check_username, scheduler.asyncio
    scheduler.check_username = fake_cu
    scheduler.asyncio = SimpleNamespace(sleep=nosleep)
    try:
        await storage.set_lang(5000, "uz")

        # A: bo'sh-blip -> band => soxta xabar YO'Q (throttle bug)
        await _clear_watch_state()
        await storage.add_watch(5000, "monx", "taken")
        bot = FakeBot()
        seq[:] = ["free"]; await scheduler._check_watchlist(bot)
        seq[:] = ["taken"]; await scheduler._check_watchlist(bot)
        assert len(bot.sent) == 0, bot.sent
        ok("bo'sh-blip -> band: soxta xabar yuborilmadi")

        # B: 2 marta ketma-ket bo'sh => aynan 1 xabar
        await _clear_watch_state()
        await storage.add_watch(5000, "mony", "taken")
        bot = FakeBot()
        seq[:] = ["free"]; await scheduler._check_watchlist(bot)
        assert len(bot.sent) == 0
        seq[:] = ["free"]; await scheduler._check_watchlist(bot)
        assert len(bot.sent) == 1
        ok("2 marta bo'sh -> aynan 1 xabar")

        # C: oradagi 'unknown' streak'ni buzmaydi
        await _clear_watch_state()
        await storage.add_watch(5000, "monz", "taken")
        bot = FakeBot()
        seq[:] = ["free"]; await scheduler._check_watchlist(bot)
        seq[:] = ["unknown"]; await scheduler._check_watchlist(bot)
        seq[:] = ["free"]; await scheduler._check_watchlist(bot)
        assert len(bot.sent) == 1
        ok("'unknown' streak'ni buzmadi -> 1 xabar")
    finally:
        scheduler.check_username = real_cu
        scheduler.asyncio = real_aio
        await _clear_watch_state()


async def t_autoclaim():
    print("[14] Auto-egallash — churn/spam/rezerv himoyasi")
    from types import SimpleNamespace
    import scheduler

    st = {"ct": [], "claim": (False, "occupied"), "create": 0, "claims": 0}

    async def f_ct(u):
        return st["ct"].pop(0)

    async def f_create(title="Reserved"):
        st["create"] += 1
        return (1000 + st["create"], 7)

    async def f_claim(cid, ch, u):
        st["claims"] += 1
        return st["claim"]

    async def nosleep(*a, **k):
        return None

    real_tc, real_aio = scheduler.telethon_client, scheduler.asyncio
    scheduler.telethon_client = SimpleNamespace(
        is_enabled=lambda: True, check_telethon=f_ct,
        create_holding_channel=f_create, claim_username_on=f_claim,
    )
    scheduler.asyncio = SimpleNamespace(sleep=nosleep)
    try:
        await storage.set_lang(5001, "uz")

        # D: Telethon 'free' demasa CLAIM urinilmaydi (t.me'ga ishonmaslik)
        await _clear_watch_state()
        await storage.add_auto_claim(5001, "acx", "taken")
        bot = FakeBot()
        st["ct"] = ["unknown"]; await scheduler._auto_claim_loop(bot)
        st["ct"] = ["taken"]; await scheduler._auto_claim_loop(bot)
        assert st["claims"] == 0
        ok("Telethon 'free' demasa claim urinilmaydi")

        # E: occupied(rezerv) => holding QAYTA ishlatiladi, 1 xabar (churn/spam yo'q)
        await _clear_watch_state()
        st["create"] = st["claims"] = 0
        st["claim"] = (False, "occupied")
        await storage.add_auto_claim(5001, "ace", "taken")
        bot = FakeBot()
        for _ in range(3):
            st["ct"] = ["free"]; await scheduler._auto_claim_loop(bot)
        assert st["create"] == 1, st["create"]      # kanal churn yo'q
        assert st["claims"] == 3                      # qayta urindi
        assert len(bot.sent) == 1                     # spam yo'q
        ok("occupied(rezerv): churn yo'q, aynan 1 xabar")

        # F: muvaffaqiyat => claimed + EGALLANDI xabari
        await _clear_watch_state()
        st["create"] = st["claims"] = 0
        st["claim"] = (True, "<a>@z</a>")
        await storage.add_auto_claim(5001, "acok", "taken")
        bot = FakeBot()
        st["ct"] = ["free"]; await scheduler._auto_claim_loop(bot)
        assert len(bot.sent) == 1 and "EGALLANDI" in bot.sent[0][1]
        # Egallangach yozuv ro'yxatdan O'CHIRILADI (qolib ketmasin).
        assert not any(
            r["target_username"] == "acok" for r in await storage.list_watch(5001)
        )
        ok("muvaffaqiyat: EGALLANDI + ro'yxatdan o'chirildi")

        # G: Telethon o'chiq => loop hech narsa qilmaydi
        await _clear_watch_state()
        st["create"] = st["claims"] = 0
        scheduler.telethon_client.is_enabled = lambda: False
        await storage.add_auto_claim(5001, "acoff", "taken")
        bot = FakeBot()
        st["ct"] = ["free"]; await scheduler._auto_claim_loop(bot)
        assert st["create"] == 0 and st["claims"] == 0
        ok("Telethon o'chiq: loop no-op")

        # H: monitoring auto-egallash yozuvini KO'RMAYDI (ikki xabar ziddiyati yo'q)
        await _clear_watch_state()
        await storage.add_watch(5001, "purewatch", "taken")
        await storage.add_auto_claim(5001, "achidden", "taken")
        watches = await storage.all_watches()
        names = {r["target_username"] for r in watches}
        assert "achidden" not in names and "purewatch" in names
        ok("monitoring auto-egallash yozuvini ko'rmaydi")
    finally:
        scheduler.telethon_client = real_tc
        scheduler.asyncio = real_aio
        await _clear_watch_state()


async def main():
    tests = [
        t_locales, t_validator, t_storage, t_checker, t_generator,
        t_fragment, t_limits, t_middlewares, t_flows, t_ui,
        t_dispatcher, t_errors, t_monitoring, t_autoclaim,
    ]
    for fn in tests:
        await fn()
    await storage.close_db()
    print(f"\n🎉 BARCHA TESTLAR O'TDI — {PASS} ta tekshiruv muvaffaqiyatli")
    if os.path.exists(os.environ["DB_PATH"]):
        os.remove(os.environ["DB_PATH"])


if __name__ == "__main__":
    asyncio.run(main())
