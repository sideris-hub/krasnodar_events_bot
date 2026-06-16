"""Вход в Telegram по QR-коду (Telethon) — без SMS и кодов из чата.

Запуск из корня проекта:  python -m scripts.tg_login_qr

Как авторизоваться:
  1. Запусти скрипт — в терминале появится QR-код.
  2. В приложении Telegram: Настройки → Устройства → «Подключить устройство».
  3. Наведи камеру на QR в терминале.
  4. (если включена 2FA) скрипт спросит облачный пароль.
После успеха появится krasnodar_events.session — дальше парсер работает без логина.
"""
import asyncio
from getpass import getpass

import qrcode
from telethon.errors import SessionPasswordNeededError

from app.connectors.telegram import get_client


def show_qr(url: str) -> None:
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make()
    qr.print_ascii(invert=True)
    print(f"\nЕсли камера не берёт — открой эту ссылку на телефоне с Telegram:\n{url}\n")


async def main() -> None:
    client = get_client()
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Уже авторизовано: {me.first_name} (@{me.username}).")
        await client.disconnect()
        return

    qr_login = await client.qr_login()
    print("Отсканируй QR в Telegram: Настройки → Устройства → Подключить устройство\n")
    show_qr(qr_login.url)

    while True:
        try:
            await qr_login.wait(timeout=30)
            break
        except asyncio.TimeoutError:
            await qr_login.recreate()
            print("QR обновлён (предыдущий истёк):\n")
            show_qr(qr_login.url)
        except SessionPasswordNeededError:
            pw = getpass("Облачный пароль (2FA): ")
            await client.sign_in(password=pw)
            break

    me = await client.get_me()
    print(f"\nOK: вошли как {me.first_name} (@{me.username}). Сессия сохранена.")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
