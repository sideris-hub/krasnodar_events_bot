"""Разовый интерактивный вход в Telegram (Telethon) с диагностикой доставки кода.

Запуск из корня проекта:  python -m scripts.tg_login
После успеха появится krasnodar_events.session — дальше парсер работает без логина.

ВАЖНО: код приходит туда, куда укажет Telegram (обычно — в приложение, чат «Telegram»
777000). Принудительный SMS в актуальном Telegram API отключён, так что просто
найди код в приложении и введи его. Пустой ввод НЕ нажимаем.
"""
import asyncio
from getpass import getpass

from telethon.errors import SessionPasswordNeededError

from app.connectors.telegram import get_client

DELIVERY = {
    "SentCodeTypeApp": "в приложение Telegram (чат «Telegram», 777000)",
    "SentCodeTypeSms": "по SMS",
    "SentCodeTypeCall": "звонком (код продиктуют)",
    "SentCodeTypeFlashCall": "флеш-звонком",
    "SentCodeTypeMissedCall": "пропущенным звонком (код — последние цифры номера)",
}


async def main() -> None:
    client = get_client()
    await client.connect()

    phone = input("Телефон (в формате +7XXXXXXXXXX): ").strip()
    sent = await client.send_code_request(phone)
    kind = type(sent.type).__name__
    print(f"\n→ Telegram отправил код: {DELIVERY.get(kind, kind)}")
    print("  Открой Telegram на устройстве с этим номером → чат «Telegram» (служебный,")
    print("  синяя галочка) → там сообщение вида «Login code: 12345». Проверь архив/папки.\n")

    code = input("Код подтверждения: ").strip()

    try:
        await client.sign_in(phone, code)
    except SessionPasswordNeededError:
        pw = getpass("Облачный пароль (2FA): ")
        await client.sign_in(password=pw)

    me = await client.get_me()
    print(f"\nOK: вошли как {me.first_name} (@{me.username}). Сессия сохранена.")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
